"""
grounding.py — Fetches live system data and builds a grounding context string
for Rooney. This context is injected into the LLM system prompt so the AI
can only answer from real data.
"""
from django.utils import timezone
from tournaments.models import MedalTally, EventSchedule, MatchResult, PodiumResult


def build_grounding_context() -> dict:
    """
    Returns a dict with:
        - text: plain-text grounding context string
        - source_labels: list of source names used
    """
    lines = []
    source_labels = []
    today = timezone.localdate()

    # 1. Medal Tally (top 8)
    tally = (
        MedalTally.objects
        .select_related('department')
        .order_by('-gold', '-silver', '-bronze', '-total_points')[:8]
    )
    if tally:
        source_labels.append('Medal Tally')
        lines.append("=== CURRENT MEDAL TALLY (Gold > Silver > Bronze) ===")
        for rank, row in enumerate(tally, 1):
            lines.append(
                f"  #{rank}. {row.department.name} ({row.department.acronym}): "
                f"G{row.gold} S{row.silver} B{row.bronze} | {row.total_points} pts"
            )

    # 2. Today's schedules
    todays_schedules = (
        EventSchedule.objects
        .select_related('event', 'venue', 'venue_area')
        .filter(scheduled_start__date=today)
        .order_by('scheduled_start')
    )
    if todays_schedules:
        source_labels.append('Today\'s Schedule')
        lines.append(f"\n=== TODAY'S EVENTS ({today}) ===")
        for sched in todays_schedules:
            venue_str = sched.venue.name if sched.venue else 'TBA'
            area_str = f" / {sched.venue_area.name}" if sched.venue_area else ''
            time_str = sched.scheduled_start.strftime('%I:%M %p') if sched.scheduled_start else 'TBA'
            lines.append(f"  - {sched.event.name} at {time_str} | {venue_str}{area_str}")

    # 3. Upcoming schedules (next 3 days, excluding today)
    from datetime import timedelta
    upcoming = (
        EventSchedule.objects
        .select_related('event', 'venue')
        .filter(
            scheduled_start__date__gt=today,
            scheduled_start__date__lte=today + timedelta(days=3)
        )
        .order_by('scheduled_start')[:10]
    )
    if upcoming:
        source_labels.append('Upcoming Schedule')
        lines.append("\n=== UPCOMING EVENTS (Next 3 Days) ===")
        for sched in upcoming:
            date_str = sched.scheduled_start.strftime('%a, %b %d') if sched.scheduled_start else 'TBA'
            venue_str = sched.venue.name if sched.venue else 'TBA'
            lines.append(f"  - {sched.event.name} on {date_str} | {venue_str}")

    # 4. Recent final match results (last 5)
    recent_matches = (
        MatchResult.objects
        .select_related('schedule__event', 'home_department', 'away_department', 'winner')
        .filter(is_final=True)
        .order_by('-recorded_at')[:5]
    )
    if recent_matches:
        source_labels.append('Match Results')
        lines.append("\n=== RECENT MATCH RESULTS (Final) ===")
        for match in recent_matches:
            winner_str = f" | Winner: {match.winner.name}" if match.winner else (" | Draw" if match.is_draw else "")
            lines.append(
                f"  - {match.schedule.event.name}: "
                f"{match.home_department.acronym} {match.home_score} - "
                f"{match.away_score} {match.away_department.acronym}{winner_str}"
            )

    # 5. Recent final podium results (last 5)
    recent_podiums = (
        PodiumResult.objects
        .select_related('schedule__event', 'department')
        .filter(is_final=True)
        .order_by('-recorded_at')[:5]
    )
    if recent_podiums:
        source_labels.append('Podium Results')
        lines.append("\n=== RECENT RANKED RESULTS (Final) ===")
        for podium in recent_podiums:
            lines.append(
                f"  - {podium.schedule.event.name}: "
                f"Rank {podium.rank} → {podium.department.name} ({podium.medal.upper()})"
            )

    context_text = "\n".join(lines) if lines else "No live data available at this time."

    return {
        "text": context_text,
        "source_labels": source_labels,
    }
