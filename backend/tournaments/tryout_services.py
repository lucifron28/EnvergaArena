import json
import logging
import secrets
import ipaddress
from datetime import timedelta
from urllib import parse, request
from urllib.error import HTTPError, URLError

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import EmailVerificationCode


TURNSTILE_VERIFY_URL = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
BREVO_EMAIL_URL = 'https://api.brevo.com/v3/smtp/email'
logger = logging.getLogger(__name__)


def get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def get_user_agent(request):
    return request.META.get('HTTP_USER_AGENT', '')[:1000]


def validate_school_email(email):
    allowed_domain = settings.TRYOUT_ALLOWED_EMAIL_DOMAIN.lower()
    normalized = email.strip().lower()
    if not normalized.endswith(allowed_domain):
        raise ValidationError(f'Use your official student email ending in {allowed_domain}.')
    return normalized


def enforce_rate_limit(scope, identifier, limit, window_seconds=3600):
    key = f'tryout-rate:{scope}:{identifier}'
    current = cache.get(key, 0)
    if current >= limit:
        raise ValidationError('Too many attempts. Please wait before trying again.')
    if current == 0:
        cache.set(key, 1, timeout=window_seconds)
    else:
        cache.incr(key)


def _public_remote_ip(remote_ip):
    if not remote_ip:
        return None
    try:
        parsed = ipaddress.ip_address(remote_ip)
    except ValueError:
        return None
    if not parsed.is_global:
        return None
    return str(parsed)


def _turnstile_unavailable_error(detail):
    message = 'Unable to verify Turnstile right now. Please try again.'
    if settings.DEBUG and detail:
        message = f'{message} Debug: {detail}'
    return ValidationError(message)


def verify_turnstile_token(token, remote_ip=None):
    if not token:
        raise ValidationError('Complete the Turnstile challenge before requesting an OTP.')
    if not settings.TURNSTILE_SECRET_KEY:
        raise ValidationError('Turnstile is not configured. Add TURNSTILE_SECRET_KEY on the backend.')

    payload = {
        'secret': settings.TURNSTILE_SECRET_KEY,
        'response': token,
    }
    public_remote_ip = _public_remote_ip(remote_ip)
    if public_remote_ip:
        payload['remoteip'] = public_remote_ip

    encoded = parse.urlencode(payload).encode()
    req = request.Request(
        TURNSTILE_VERIFY_URL,
        data=encoded,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        method='POST',
    )

    try:
        with request.urlopen(req, timeout=8) as response:
            result = json.loads(response.read().decode('utf-8'))
    except HTTPError as exc:
        body = exc.read().decode('utf-8', errors='replace')[:500]
        logger.warning('Turnstile Siteverify HTTP error %s: %s', exc.code, body)
        raise _turnstile_unavailable_error(f'Cloudflare Siteverify returned HTTP {exc.code}.') from exc
    except URLError as exc:
        logger.warning('Turnstile Siteverify connection error: %s', exc.reason)
        raise _turnstile_unavailable_error(f'Could not connect to Cloudflare Siteverify: {exc.reason}.') from exc
    except TimeoutError as exc:
        logger.warning('Turnstile Siteverify timed out.')
        raise _turnstile_unavailable_error('Cloudflare Siteverify timed out.') from exc
    except json.JSONDecodeError as exc:
        logger.warning('Turnstile Siteverify returned invalid JSON.')
        raise _turnstile_unavailable_error('Cloudflare Siteverify returned an invalid response.') from exc

    if not result.get('success'):
        error_codes = ', '.join(result.get('error-codes', []))
        suffix = f' Error: {error_codes}.' if error_codes else ''
        raise ValidationError(f'Turnstile verification failed. Please refresh the challenge and try again.{suffix}')

    return result


def generate_otp():
    return f'{secrets.randbelow(1_000_000):06d}'


def create_email_verification_code(email, student_number, department, schedule, request_ip, user_agent):
    code = generate_otp()
    record = EmailVerificationCode.objects.create(
        email=email,
        student_number=student_number.strip(),
        department=department,
        schedule=schedule,
        code_hash=make_password(code),
        expires_at=timezone.now() + timedelta(minutes=settings.TRYOUT_OTP_EXPIRY_MINUTES),
        request_ip=request_ip,
        user_agent=user_agent,
    )
    return record, code


def send_tryout_otp_email(email, full_name, code):
    if not settings.BREVO_API_KEY:
        raise ValidationError('Brevo is not configured. Add BREVO_API_KEY on the backend.')
    if not settings.BREVO_SENDER_EMAIL:
        raise ValidationError('Brevo sender is not configured. Add BREVO_SENDER_EMAIL on the backend.')

    payload = {
        'sender': {
            'name': settings.BREVO_SENDER_NAME,
            'email': settings.BREVO_SENDER_EMAIL,
        },
        'to': [{'email': email, 'name': full_name or email}],
        'subject': 'Your Enverga Arena tryout verification code',
        'textContent': (
            'Your Enverga Arena tryout application verification code is '
            f'{code}. This code expires in {settings.TRYOUT_OTP_EXPIRY_MINUTES} minutes.'
        ),
    }
    body = json.dumps(payload).encode('utf-8')
    req = request.Request(
        BREVO_EMAIL_URL,
        data=body,
        headers={
            'accept': 'application/json',
            'api-key': settings.BREVO_API_KEY,
            'content-type': 'application/json',
        },
        method='POST',
    )

    try:
        with request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8') or '{}')
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ValidationError('Unable to send OTP email right now. Please try again later.') from exc


def verify_email_code(email, student_number, department, schedule, code):
    record = EmailVerificationCode.objects.filter(
        email=email,
        student_number=student_number,
        department=department,
        schedule=schedule,
        used_at__isnull=True,
    ).order_by('-created_at').first()

    if not record:
        raise ValidationError('No active OTP request was found for this email and event.')
    if record.expires_at <= timezone.now():
        raise ValidationError('This OTP has expired. Please request a new code.')
    if record.attempt_count >= settings.TRYOUT_MAX_VERIFY_ATTEMPTS:
        raise ValidationError('Too many incorrect OTP attempts. Please request a new code.')

    if not check_password(code, record.code_hash):
        record.attempt_count += 1
        record.save(update_fields=['attempt_count'])
        raise ValidationError('The OTP code is incorrect.')

    record.used_at = timezone.now()
    record.save(update_fields=['used_at'])
    return record


def get_recent_verified_code(email, student_number, department, schedule):
    cutoff = timezone.now() - timedelta(minutes=settings.TRYOUT_VERIFIED_APPLICATION_WINDOW_MINUTES)
    return EmailVerificationCode.objects.filter(
        email=email,
        student_number=student_number,
        department=department,
        schedule=schedule,
        used_at__isnull=False,
        used_at__gte=cutoff,
    ).order_by('-used_at').first()
