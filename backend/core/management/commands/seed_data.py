from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Department, NewsArticle, UserProfile, Venue, VenueArea
from events.models import Event, EventCategory
from rooney.models import AIRecap
from tournaments.models import (
    Athlete,
    EmailVerificationCode,
    EventRegistration,
    EventSchedule,
    MatchResult,
    MatchSetScore,
    MedalRecord,
    MedalTally,
    PodiumResult,
    RosterEntry,
    TryoutApplication,
)
from tournaments.services import apply_final_match_result, apply_final_podium_result


DEMO_PASSWORD = "demo1234"
DEPARTMENT_ACRONYMS = [
    "CAFA",
    "CAS",
    "CBA",
    "CCMS",
    "CCJC",
    "CED",
    "CENG",
    "CIHTM",
    "CME",
    "CNAHS",
]
DEMO_USERNAMES = ["admin", *[f"{acronym.lower()}_rep" for acronym in DEPARTMENT_ACRONYMS]]
SEEDED_NEWS_SLUGS = [
    "verified-tryout-applications-open-for-department-teams",
    "department-representatives-reminded-to-review-pending-registrations",
    "womens-volleyball-finals-moved-to-indoor-court-b",
    "badminton-team-qualifiers-confirmed-covered-sports-complex",
    "dancesport-latin-category-strong-college-support",
    "esports-semifinal-roster-checks-completed",
    "mens-table-tennis-team-final-result-added",
    "200m-freestyle-final-podium-reflected-in-medal-tally",
    "mens-basketball-finals-live-pending-final-confirmation",
    "schedules-results-medal-standings-available-public-viewing",
    "womens-volleyball-finals-recap",
    # Old seed slugs removed by the news-only refresh path.
    "intramurals-week-operations-desk-reminders",
    "badminton-tennis-qualifiers-schedule-release",
]
SEEDED_AI_RECAP_SCOPE_KEYS = [
    "seed-match-volleyball",
    "seed-match-table-tennis",
    "seed-podium-swimming",
    "seed-leaderboard-summary",
]


class Command(BaseCommand):
    help = "Seeds the database with context-aligned Enverga Arena demo data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--news-only",
            action="store_true",
            help="Refresh only seeded news articles and AI recap drafts without rebuilding the full demo database.",
        )

    def handle(self, *args, **kwargs):
        if kwargs.get("news_only"):
            self.seed_news_only()
            self.stdout.write(self.style.SUCCESS("Successfully refreshed seeded news and AI recap demo content."))
            return

        self.stdout.write("Clearing existing data...")
        User.objects.filter(username__in=DEMO_USERNAMES).delete()
        AIRecap.objects.all().delete()
        NewsArticle.objects.all().delete()
        MedalRecord.objects.all().delete()
        MedalTally.objects.all().delete()
        PodiumResult.objects.all().delete()
        MatchSetScore.objects.all().delete()
        MatchResult.objects.all().delete()
        RosterEntry.objects.all().delete()
        EventRegistration.objects.all().delete()
        EmailVerificationCode.objects.all().delete()
        TryoutApplication.objects.all().delete()
        Athlete.objects.all().delete()
        EventSchedule.objects.all().delete()
        Event.objects.all().delete()
        EventCategory.objects.all().delete()
        VenueArea.objects.all().delete()
        Venue.objects.all().delete()
        Department.objects.all().delete()

        departments = self.seed_departments()
        users = self.seed_demo_users(departments)
        venue_areas = self.seed_venues()
        categories = self.seed_categories()
        events = self.seed_events(categories)
        schedules = self.seed_schedules(events, venue_areas)
        athletes = self.seed_athletes(departments)
        self.seed_tryout_applications(schedules, departments)
        self.seed_registrations(schedules, departments, users, athletes)
        self.seed_results(schedules, departments)
        self.seed_remaining_medal_records(categories, departments)
        self.seed_news_and_ai_recaps(schedules, departments, users)

        self.stdout.write(self.style.SUCCESS("Successfully seeded context-aligned Enverga Arena demo data."))
        rep_logins = ", ".join(f"{acronym.lower()}_rep/{DEMO_PASSWORD}" for acronym in DEPARTMENT_ACRONYMS)
        self.stdout.write(self.style.SUCCESS(f"Demo admin login: admin/{DEMO_PASSWORD}"))
        self.stdout.write(self.style.SUCCESS(f"Demo department rep logins: {rep_logins}"))

    def seed_news_only(self):
        admin_user = User.objects.filter(username="admin").first() or User.objects.filter(is_superuser=True).first()
        if not admin_user:
            raise RuntimeError("No admin user found. Run `python manage.py seed_data` first.")

        departments = {
            department.acronym: department
            for department in Department.objects.filter(acronym__in=DEPARTMENT_ACRONYMS)
        }
        missing_departments = [acronym for acronym in DEPARTMENT_ACRONYMS if acronym not in departments]
        if missing_departments:
            raise RuntimeError(f"Missing departments for news seed: {', '.join(missing_departments)}")

        event_names = {
            "basketball": "Men's Basketball Finals",
            "volleyball": "Women's Volleyball Finals",
            "badminton": "Badminton Team Qualifiers",
            "table_tennis": "Men's Table Tennis Team Final",
            "swimming": "200m Freestyle Final",
            "dancesport": "Dancesport Latin Category",
            "esports": "Esports Semifinal Title A",
        }
        schedules = {}
        missing_events = []
        for key, event_name in event_names.items():
            schedule = EventSchedule.objects.select_related("event").filter(event__name=event_name).order_by("id").first()
            if not schedule:
                missing_events.append(event_name)
            else:
                schedules[key] = schedule
        if missing_events:
            raise RuntimeError(f"Missing schedules for news seed: {', '.join(missing_events)}")

        AIRecap.objects.filter(scope_key__in=SEEDED_AI_RECAP_SCOPE_KEYS).delete()
        NewsArticle.objects.filter(slug__in=SEEDED_NEWS_SLUGS).delete()
        self.seed_news_and_ai_recaps(schedules, departments, {"admin": admin_user})

    def seed_departments(self):
        self.stdout.write("Seeding official departments...")
        departments_data = [
            ("College of Architecture and Fine Arts", "CAFA", "#7A1114"),
            ("College of Arts and Sciences", "CAS", "#1D3557"),
            ("College of Business and Accountancy", "CBA", "#9A6500"),
            ("College of Computing and Multimedia Studies", "CCMS", "#0F766E"),
            ("College of Criminal Justice and Criminology", "CCJC", "#5B1113"),
            ("College of Education", "CED", "#2563EB"),
            ("College of Engineering", "CENG", "#A52A2A"),
            ("College of International Hospitality and Tourism Management", "CIHTM", "#BE185D"),
            ("College of Maritime Education", "CME", "#1E40AF"),
            ("College of Nursing and Allied Health Sciences", "CNAHS", "#166534"),
        ]

        departments = {}
        for name, acronym, color in departments_data:
            departments[acronym] = Department.objects.create(
                name=name,
                acronym=acronym,
                color_code=color,
            )
        return departments

    def seed_demo_users(self, departments):
        self.stdout.write("Creating demo accounts...")
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@enverga.demo",
            password=DEMO_PASSWORD,
        )
        UserProfile.objects.create(user=admin, role="admin")

        users = {"admin": admin}
        for acronym in DEPARTMENT_ACRONYMS:
            username = f"{acronym.lower()}_rep"
            user = User.objects.create_user(
                username=username,
                email=f"{acronym.lower()}@enverga.demo",
                password=DEMO_PASSWORD,
            )
            UserProfile.objects.create(
                user=user,
                role="department_rep",
                department=departments[acronym],
            )
            users[username] = user

        return users

    def seed_venues(self):
        self.stdout.write("Seeding venues and venue areas...")
        gym = Venue.objects.create(name="University Gymnasium", location="MSEUF Lucena main campus")
        covered_complex = Venue.objects.create(name="Covered Sports Complex", location="MSEUF Lucena main campus")
        pool = Venue.objects.create(name="Olympic-sized Swimming Pool", location="MSEUF Lucena main campus")
        tennis_area = Venue.objects.create(name="Tennis Court Area", location="MSEUF Lucena main campus")
        ccms = Venue.objects.create(name="CCMS Building", location="MSEUF Lucena main campus")
        tba = Venue.objects.create(name="Venue TBA", location="Pending OSCR confirmation")

        return {
            "gym_court_a": VenueArea.objects.create(venue=gym, name="Court A"),
            "gym_court_b": VenueArea.objects.create(venue=gym, name="Court B"),
            "covered_badminton": VenueArea.objects.create(venue=covered_complex, name="Badminton Court"),
            "covered_pickleball": VenueArea.objects.create(venue=covered_complex, name="Pickleball Court"),
            "table_tennis": VenueArea.objects.create(venue=gym, name="Table Tennis Area"),
            "tennis_1": VenueArea.objects.create(venue=tennis_area, name="Tennis Court 1"),
            "pool_lanes": VenueArea.objects.create(venue=pool, name="Pool Lane Set"),
            "esports_room": VenueArea.objects.create(venue=ccms, name="Esports Room A"),
            "venue_tba": VenueArea.objects.create(venue=tba, name="To be assigned"),
        }

    def seed_categories(self):
        self.stdout.write("Seeding event categories...")
        return {
            "ball": EventCategory.objects.create(name="Ball Games"),
            "aquatics": EventCategory.objects.create(name="Aquatics"),
            "cultural": EventCategory.objects.create(name="Cultural"),
            "esports": EventCategory.objects.create(name="E-Sports"),
            "athletics": EventCategory.objects.create(name="Athletics"),
            "martial": EventCategory.objects.create(name="Martial Arts"),
            "mind": EventCategory.objects.create(name="Mind Sports"),
            "others": EventCategory.objects.create(name="Others", is_medal_bearing=False),
            "previous": EventCategory.objects.create(name="Previous Events (Seeded)", is_medal_bearing=False),
        }

    def seed_events(self, categories):
        self.stdout.write("Seeding context-approved v1 events...")
        event_specs = {
            "basketball": ("Men's Basketball Finals", "ball", "match_based", "live"),
            "volleyball": ("Women's Volleyball Finals", "ball", "match_based", "completed"),
            "badminton": ("Badminton Team Qualifiers", "ball", "match_based", "scheduled"),
            "table_tennis": ("Men's Table Tennis Team Final", "ball", "match_based", "completed"),
            "tennis": ("Tennis Doubles Qualifiers", "ball", "match_based", "scheduled"),
            "pickleball": ("Pickleball Mixed Doubles", "ball", "match_based", "scheduled"),
            "swimming": ("200m Freestyle Final", "aquatics", "rank_based", "completed"),
            "dancesport": ("Dancesport Latin Category", "cultural", "rank_based", "completed"),
            "esports": ("Esports Semifinal Title A", "esports", "match_based", "scheduled"),
            "athletics_track": ("Athletics Track Events (Configurable)", "athletics", "rank_based", "postponed"),
            "athletics_field": ("Athletics Field Events (Configurable)", "athletics", "rank_based", "postponed"),
            "taekwondo_kyorugi": ("Taekwondo Kyorugi (Format TBA)", "martial", "match_based", "postponed"),
            "taekwondo_poomsae": ("Taekwondo Poomsae / Karatedo (Format TBA)", "martial", "rank_based", "postponed"),
            "solo_voice": ("Solo Voice / Vocal Solo (Configurable)", "cultural", "rank_based", "postponed"),
            "oratorical": ("Oratorical Competition (Configurable)", "cultural", "rank_based", "postponed"),
            "pageant": ("Mr. & Ms. Intramurals / Mutya (Configurable)", "cultural", "rank_based", "postponed"),
            "hiphop": ("Hip-Hop / Street Dance (Configurable)", "cultural", "rank_based", "postponed"),
            "chess": ("Chess Tournament (Optional v2)", "mind", "rank_based", "postponed"),
        }

        events = {}
        for key, (name, category_key, result_family, status) in event_specs.items():
            events[key] = Event.objects.create(
                category=categories[category_key],
                name=name,
                result_family=result_family,
                status=status,
            )

        # Program activities are schedulable but not medal-bearing. The current schema still
        # requires a result family, so these are marked as program events and never produce results.
        for key, name in {
            "opening": "Opening Ceremony and Parade",
            "solidarity": "Solidarity Meeting",
            "fun_run": "Fun Run and Booths",
        }.items():
            events[key] = Event.objects.create(
                category=categories["others"],
                name=name,
                result_family="rank_based",
                is_program_event=True,
                status="scheduled",
            )

        return events

    def seed_schedules(self, events, venue_areas):
        self.stdout.write("Seeding schedules...")
        now = timezone.now().replace(minute=0, second=0, microsecond=0)
        schedule_specs = {
            "opening": ("opening", "gym_court_a", now - timedelta(days=1, hours=3), 2, "Program event"),
            "basketball": ("basketball", "gym_court_a", now - timedelta(minutes=30), 2, ""),
            "volleyball": ("volleyball", "gym_court_b", now - timedelta(days=1), 2, ""),
            "table_tennis": ("table_tennis", "table_tennis", now - timedelta(hours=6), 2, ""),
            "swimming": ("swimming", "pool_lanes", now - timedelta(hours=4), 2, ""),
            "dancesport": ("dancesport", "gym_court_b", now - timedelta(hours=4), 2, ""),
            "badminton": ("badminton", "covered_badminton", now + timedelta(hours=2), 2, ""),
            "tennis": ("tennis", "tennis_1", now + timedelta(days=1, hours=1), 2, ""),
            "pickleball": ("pickleball", "covered_pickleball", now + timedelta(days=1, hours=4), 2, ""),
            "esports": (
                "esports",
                "esports_room",
                now + timedelta(days=2),
                3,
                "Exact esports title is configurable because no official title list is confirmed in the context.",
            ),
            "solidarity": ("solidarity", "gym_court_b", now + timedelta(days=2, hours=4), 1, "Program event"),
            "fun_run": ("fun_run", "gym_court_a", now + timedelta(days=3, hours=6), 2, "Program event"),
            "athletics_track": (
                "athletics_track",
                "venue_tba",
                None,
                None,
                "Phase-gated: add after athletics venue and heat format are confirmed by OSCR.",
            ),
            "athletics_field": (
                "athletics_field",
                "venue_tba",
                None,
                None,
                "Phase-gated: add after athletics venue and field-event equipment are confirmed by OSCR.",
            ),
            "taekwondo_kyorugi": (
                "taekwondo_kyorugi",
                "venue_tba",
                None,
                None,
                "Phase-gated: taekwondo activity is supported by context, but intramural divisions/rules need confirmation.",
            ),
            "taekwondo_poomsae": (
                "taekwondo_poomsae",
                "venue_tba",
                None,
                None,
                "Optional future martial-arts event; keep configurable until rules and divisions are confirmed.",
            ),
            "solo_voice": (
                "solo_voice",
                "venue_tba",
                None,
                None,
                "Configurable cultural event; enable only if it counts toward the same championship.",
            ),
            "oratorical": (
                "oratorical",
                "venue_tba",
                None,
                None,
                "Configurable cultural event; enable only if it counts toward the same championship.",
            ),
            "pageant": (
                "pageant",
                "venue_tba",
                None,
                None,
                "Configurable cultural event; championship inclusion still needs confirmation.",
            ),
            "hiphop": (
                "hiphop",
                "venue_tba",
                None,
                None,
                "Optional future judged event; not enabled by default without OSCR confirmation.",
            ),
            "chess": (
                "chess",
                "venue_tba",
                None,
                None,
                "Optional v2 mind-sports event; direct MSEUF intramurals confirmation is still low.",
            ),
        }

        schedules = {}
        for key, (event_key, area_key, start, duration_hours, notes) in schedule_specs.items():
            area = venue_areas[area_key]
            schedules[key] = EventSchedule.objects.create(
                event=events[event_key],
                venue=area.venue,
                venue_area=area,
                scheduled_start=start,
                scheduled_end=start + timedelta(hours=duration_hours) if start and duration_hours else None,
                notes=notes,
            )
        return schedules

    def seed_athletes(self, departments):
        self.stdout.write("Seeding participant records...")
        program_by_dept = {
            "CAFA": "BS Architecture",
            "CAS": "BS Psychology",
            "CBA": "BS Accountancy",
            "CCMS": "BS Information Technology",
            "CCJC": "BS Criminology",
            "CED": "BSEd English",
            "CENG": "BS Civil Engineering",
            "CIHTM": "BS Hospitality Management",
            "CME": "BS Marine Transportation",
            "CNAHS": "BS Nursing",
        }
        names_by_dept = {
            "CAFA": ["Arielle Mendoza", "Luis Santiago", "Mika Reyes", "Gian Flores"],
            "CAS": ["Sofia Garcia", "Kenji Ramos", "Angelica Flores", "Noel Bautista"],
            "CBA": ["Trisha Mercado", "Harvey Gonzales", "Elaine Torres", "Miguel Uy"],
            "CCMS": ["Rafael Cruz", "Nina Villanueva", "Paolo Tan", "Janelle Uy"],
            "CCJC": ["Andrea Manalo", "Jonas Perez", "Rhea Castillo"],
            "CED": ["Camille Austria", "Bryan Mallari", "Faith Mendoza"],
            "CENG": ["Marco Lim", "Bianca Santos", "Jerome Dela Cruz", "Iris Navarro"],
            "CIHTM": ["Patricia Lopez", "Enzo Ramos", "Mara Delos Santos"],
            "CME": ["Aldrin Reyes", "Kurt Villasis", "Shane Bautista"],
            "CNAHS": ["Nica Salazar", "Dean Carpio", "Jules De Vera"],
        }

        athletes = {}
        for dept_acronym, names in names_by_dept.items():
            athletes[dept_acronym] = []
            for index, full_name in enumerate(names, 1):
                athletes[dept_acronym].append(Athlete.objects.create(
                    student_number=f"{dept_acronym}-2026-{index:03}",
                    full_name=full_name,
                    department=departments[dept_acronym],
                    program_course=program_by_dept[dept_acronym],
                    year_level=["1st Year", "2nd Year", "3rd Year", "4th Year"][index % 4],
                    is_enrolled=True,
                    medical_cleared=not (dept_acronym == "CCMS" and index == 4),
                ))
        return athletes

    def seed_tryout_applications(self, schedules, departments):
        self.stdout.write("Seeding verified public tryout applications...")
        program_by_dept = {
            "CAFA": "BS Architecture",
            "CAS": "BS Psychology",
            "CBA": "BS Accountancy",
            "CCMS": "BS Information Technology",
            "CCJC": "BS Criminology",
            "CED": "BSEd English",
            "CENG": "BS Civil Engineering",
            "CIHTM": "BS Hospitality Management",
            "CME": "BS Marine Transportation",
            "CNAHS": "BS Nursing",
        }
        applicant_names = {
            "CAFA": ["Althea Prado", "Nolan Ferrer"],
            "CAS": ["Ivy Macaraig", "Cedric Villanueva"],
            "CBA": ["Rochelle Ong", "Martin Chua"],
            "CCMS": ["Elijah Soriano", "Kyla Evangelista"],
            "CCJC": ["Joanne Macalalad", "Renz Tolentino"],
            "CED": ["Mira Angeles", "Paulo Manabat"],
            "CENG": ["Theo Aguilar", "Sam Reyes"],
            "CIHTM": ["Hannah Rivera", "Lance Abella"],
            "CME": ["Mark Angelo Dizon", "Gia Fortes"],
            "CNAHS": ["Clara Buenaventura", "Ethan Molina"],
        }
        schedule_keys = ["badminton", "tennis", "pickleball", "esports", "swimming"]
        statuses = ["submitted", "under_review", "selected", "waitlisted"]
        verified_at = timezone.now() - timedelta(hours=8)

        for dept_index, dept_acronym in enumerate(DEPARTMENT_ACRONYMS):
            for applicant_index, full_name in enumerate(applicant_names[dept_acronym], 1):
                schedule = schedules[schedule_keys[(dept_index + applicant_index) % len(schedule_keys)]]
                email_name = full_name.lower().replace(" ", ".")
                TryoutApplication.objects.create(
                    department=departments[dept_acronym],
                    schedule=schedule,
                    student_number=f"TRY-{dept_acronym}-2026-{applicant_index:03}",
                    full_name=full_name,
                    school_email=f"{email_name}.{dept_acronym.lower()}@mseuf.edu.ph",
                    contact_number=f"09{dept_index + 10:02}{applicant_index}555010",
                    program_course=program_by_dept[dept_acronym],
                    year_level=["1st Year", "2nd Year", "3rd Year", "4th Year"][applicant_index % 4],
                    prior_experience="Submitted varsity or intramurals interest notes through the verified public form.",
                    notes="Verified school-email application seeded for representative review.",
                    email_verified=True,
                    verified_at=verified_at + timedelta(minutes=dept_index + applicant_index),
                    status=statuses[(dept_index + applicant_index) % len(statuses)],
                    submitted_at=verified_at + timedelta(minutes=dept_index + applicant_index),
                    created_ip="127.0.0.1",
                    user_agent="seed-data",
                )

    def seed_registrations(self, schedules, departments, users, athletes):
        self.stdout.write("Seeding registrations and rosters...")
        demo_registrations = [
            ("basketball", "CBA", "approved", "cba_rep", athletes["CBA"][:4], ""),
            ("basketball", "CAS", "approved", "cas_rep", athletes["CAS"][:4], ""),
            ("volleyball", "CAFA", "approved", "cafa_rep", athletes["CAFA"][:4], ""),
            ("volleyball", "CENG", "approved", "ceng_rep", athletes["CENG"][:4], ""),
            ("table_tennis", "CCMS", "approved", "ccms_rep", athletes["CCMS"][:3], ""),
            ("table_tennis", "CAS", "approved", "cas_rep", athletes["CAS"][:3], ""),
            ("swimming", "CAFA", "approved", "cafa_rep", athletes["CAFA"][:2], ""),
            ("swimming", "CCMS", "approved", "ccms_rep", athletes["CCMS"][:2], ""),
            ("swimming", "CENG", "approved", "ceng_rep", athletes["CENG"][:2], ""),
            ("dancesport", "CCMS", "approved", "ccms_rep", athletes["CCMS"][:2], ""),
            ("dancesport", "CAFA", "approved", "cafa_rep", athletes["CAFA"][:2], ""),
            ("dancesport", "CBA", "approved", "cba_rep", athletes["CBA"][:2], ""),
            ("badminton", "CNAHS", "submitted", "cnahs_rep", athletes["CNAHS"][:2], ""),
            (
                "badminton",
                "CCJC",
                "needs_revision",
                "ccjc_rep",
                athletes["CCJC"][:2],
                "Upload updated medical clearance before admin review.",
            ),
            ("tennis", "CME", "pending", "cme_rep", athletes["CME"][:2], ""),
            ("tennis", "CED", "submitted", "ced_rep", athletes["CED"][:2], ""),
            ("pickleball", "CIHTM", "submitted", "cihtm_rep", athletes["CIHTM"][:2], ""),
            ("esports", "CENG", "submitted", "ceng_rep", athletes["CENG"][:3], ""),
            ("esports", "CBA", "submitted", "cba_rep", athletes["CBA"][:3], ""),
        ]

        for schedule_key, dept_acronym, status, submitted_by_key, roster, admin_notes in demo_registrations:
            registration = EventRegistration.objects.create(
                schedule=schedules[schedule_key],
                department=departments[dept_acronym],
                status=status,
                submitted_by=users.get(submitted_by_key) if submitted_by_key else None,
                admin_notes=admin_notes,
            )
            RosterEntry.objects.bulk_create([
                RosterEntry(registration=registration, athlete=athlete)
                for athlete in roster
            ])

    def seed_results(self, schedules, departments):
        self.stdout.write("Seeding finalized and live results...")
        basketball = MatchResult.objects.create(
            schedule=schedules["basketball"],
            home_department=departments["CBA"],
            away_department=departments["CAS"],
            home_score=68,
            away_score=72,
            winner=departments["CAS"],
            is_final=False,
        )
        MatchSetScore.objects.bulk_create([
            MatchSetScore(match=basketball, set_number=1, home_score=18, away_score=17),
            MatchSetScore(match=basketball, set_number=2, home_score=16, away_score=19),
            MatchSetScore(match=basketball, set_number=3, home_score=17, away_score=18),
            MatchSetScore(match=basketball, set_number=4, home_score=17, away_score=18),
        ])

        volleyball = MatchResult.objects.create(
            schedule=schedules["volleyball"],
            home_department=departments["CAFA"],
            away_department=departments["CENG"],
            home_score=3,
            away_score=1,
            winner=departments["CAFA"],
            is_final=True,
        )
        MatchSetScore.objects.bulk_create([
            MatchSetScore(match=volleyball, set_number=1, home_score=25, away_score=21),
            MatchSetScore(match=volleyball, set_number=2, home_score=23, away_score=25),
            MatchSetScore(match=volleyball, set_number=3, home_score=25, away_score=19),
            MatchSetScore(match=volleyball, set_number=4, home_score=25, away_score=22),
        ])
        apply_final_match_result(volleyball)

        table_tennis = MatchResult.objects.create(
            schedule=schedules["table_tennis"],
            home_department=departments["CCMS"],
            away_department=departments["CAS"],
            home_score=3,
            away_score=1,
            winner=departments["CCMS"],
            is_final=True,
        )
        MatchSetScore.objects.bulk_create([
            MatchSetScore(match=table_tennis, set_number=1, home_score=3, away_score=0),
            MatchSetScore(match=table_tennis, set_number=2, home_score=2, away_score=3),
            MatchSetScore(match=table_tennis, set_number=3, home_score=3, away_score=1),
            MatchSetScore(match=table_tennis, set_number=4, home_score=3, away_score=2),
        ])
        apply_final_match_result(table_tennis)

        podium_results = [
            (schedules["swimming"], "CAFA", 1, "gold"),
            (schedules["swimming"], "CCMS", 2, "silver"),
            (schedules["swimming"], "CENG", 3, "bronze"),
            (schedules["dancesport"], "CCMS", 1, "gold"),
            (schedules["dancesport"], "CAFA", 2, "silver"),
            (schedules["dancesport"], "CBA", 3, "bronze"),
        ]
        for schedule, dept_acronym, rank, medal in podium_results:
            podium = PodiumResult.objects.create(
                schedule=schedule,
                department=departments[dept_acronym],
                rank=rank,
                medal=medal,
                is_final=True,
            )
            apply_final_podium_result(podium)

    def seed_remaining_medal_records(self, categories, departments):
        self.stdout.write("Seeding context sample standings from the medal ledger...")
        target_standings = {
            "CAFA": {"gold": 18, "silver": 14, "bronze": 9},
            "CCMS": {"gold": 12, "silver": 15, "bronze": 10},
            "CENG": {"gold": 10, "silver": 12, "bronze": 18},
            "CBA": {"gold": 8, "silver": 9, "bronze": 12},
            "CAS": {"gold": 7, "silver": 11, "bronze": 15},
        }

        previous_category = categories["previous"]
        for dept_acronym, targets in target_standings.items():
            dept = departments[dept_acronym]
            existing = {
                medal: MedalRecord.objects.filter(department=dept, medal=medal).count()
                for medal in ["gold", "silver", "bronze"]
            }
            for medal_type, target_count in targets.items():
                remaining = target_count - existing[medal_type]
                for index in range(remaining):
                    event = Event.objects.create(
                        category=previous_category,
                        name=f"Seeded {medal_type.title()} Result {dept_acronym} {index + 1}",
                        result_family="rank_based",
                        status="completed",
                    )
                    MedalRecord.objects.create(
                        department=dept,
                        event=event,
                        medal=medal_type,
                    )

        for dept in departments.values():
            MedalTally.objects.get_or_create(
                department=dept,
                defaults={
                    "gold": 0,
                    "silver": 0,
                    "bronze": 0,
                },
            )

    def seed_news_and_ai_recaps(self, schedules, departments, users):
        self.stdout.write("Seeding official news articles and AI recap drafts...")
        admin_user = users["admin"]
        now = timezone.now()

        def create_article(
            key,
            title,
            slug,
            summary,
            body_md,
            article_type,
            source_label,
            days_ago,
            hours_ago=0,
            event_key=None,
            department_key=None,
            ai_generated=False,
        ):
            return NewsArticle.objects.create(
                title=title,
                slug=slug,
                summary=summary,
                body_md=body_md,
                article_type=article_type,
                source_label=source_label,
                event=schedules[event_key].event if event_key else None,
                department=departments[department_key] if department_key else None,
                status="published",
                published_at=now - timedelta(days=days_ago, hours=hours_ago),
                ai_generated=ai_generated,
                created_by=admin_user,
                reviewed_by=admin_user,
            )

        articles = {
            "tryouts_open": create_article(
                key="tryouts_open",
                title="Verified tryout applications open for department teams",
                slug="verified-tryout-applications-open-for-department-teams",
                summary="Students may now submit verified tryout applications for eligible intramurals events through the public Enverga Arena form.",
                body_md=(
                    "The Sports Coordinator's Office has opened the verified tryout application period for department teams participating in MSEUF Intramurals. "
                    "Students must use their official student email address and complete OTP verification before submitting an application. "
                    "Department Representatives will review verified applications and coordinate selections for official rosters."
                ),
                article_type="announcement",
                source_label="MSEUF Sports Coordinator",
                days_ago=7,
            ),
            "rep_reminder": create_article(
                key="rep_reminder",
                title="Department representatives reminded to review pending registrations",
                slug="department-representatives-reminded-to-review-pending-registrations",
                summary="Department representatives are reminded to check returned rosters and registration statuses before the next review block.",
                body_md=(
                    "All Department Representatives are requested to review pending tryout selections, participant records, and event registrations in the department portal. "
                    "Registrations marked for revision should be updated as soon as possible so the Sports Coordinator can complete eligibility and roster checks before scheduled matches."
                ),
                article_type="announcement",
                source_label="Tournament Secretariat",
                days_ago=6,
                hours_ago=2,
            ),
            "volleyball_schedule": create_article(
                key="volleyball_schedule",
                title="Women's Volleyball Finals moved to Indoor Court B",
                slug="womens-volleyball-finals-moved-to-indoor-court-b",
                summary="The Women's Volleyball Finals venue assignment has been updated in the official schedule.",
                body_md=(
                    "The Women's Volleyball Finals will now be played at Indoor Court B to accommodate venue preparation and officiating requirements. "
                    "Teams, officials, and department representatives are advised to follow the latest schedule posted in Enverga Arena before proceeding to the venue."
                ),
                article_type="schedule_update",
                source_label="Schedule Operations",
                days_ago=5,
                event_key="volleyball",
            ),
            "badminton_schedule": create_article(
                key="badminton_schedule",
                title="Badminton Team Qualifiers confirmed at the Covered Sports Complex",
                slug="badminton-team-qualifiers-confirmed-covered-sports-complex",
                summary="The Badminton Team Qualifiers will proceed at the assigned covered court according to the current schedule.",
                body_md=(
                    "The latest schedule confirms the Badminton Team Qualifiers at the Covered Sports Complex. "
                    "Participating departments should review their roster status and report to the venue within the posted call time. "
                    "Any roster questions should be coordinated through the assigned Department Representative."
                ),
                article_type="schedule_update",
                source_label="Venue Operations Team",
                days_ago=4,
                hours_ago=5,
                event_key="badminton",
            ),
            "dancesport_highlight": create_article(
                key="dancesport_highlight",
                title="Dancesport Latin Category brings strong support from participating colleges",
                slug="dancesport-latin-category-strong-college-support",
                summary="The Dancesport Latin Category highlighted preparation, coordination, and department support during the cultural events block.",
                body_md=(
                    "The Dancesport Latin Category featured participants and supporters from several MSEUF departments, including the College of Architecture and Fine Arts (CAFA) "
                    "and the College of International Hospitality and Tourism Management (CIHTM). The event reflected steady preparation from performers and orderly coordination from the cultural events committee."
                ),
                article_type="highlight",
                source_label="Cultural Events Committee",
                days_ago=4,
                event_key="dancesport",
                department_key="CIHTM",
            ),
            "esports_highlight": create_article(
                key="esports_highlight",
                title="Esports Semifinal roster checks completed for participating departments",
                slug="esports-semifinal-roster-checks-completed",
                summary="Roster verification for the Esports Semifinal has been completed ahead of the scheduled match block.",
                body_md=(
                    "Roster checks for the Esports Semifinal have been completed for the participating departments. "
                    "The College of Computing and Multimedia Studies (CCMS), College of Business and Accountancy (CBA), and College of Engineering (CENG) representatives are advised to monitor schedule updates and final call times in Enverga Arena."
                ),
                article_type="highlight",
                source_label="Esports Committee",
                days_ago=3,
                hours_ago=4,
                event_key="esports",
                department_key="CCMS",
            ),
            "table_tennis_recap": create_article(
                key="table_tennis_recap",
                title="Men's Table Tennis Team Final result added to official records",
                slug="mens-table-tennis-team-final-result-added",
                summary="The finalized table tennis result has been recorded and reflected in the official results workflow.",
                body_md=(
                    "The Men's Table Tennis Team Final has been finalized by the event officials. "
                    "The result is now recorded in Enverga Arena and may be viewed through the public results page. "
                    "Any related medal impact follows the official medal-priority ranking rule used by the system."
                ),
                article_type="result_recap",
                source_label="AI Recap, reviewed by Sports Coordinator",
                days_ago=2,
                hours_ago=6,
                event_key="table_tennis",
                department_key="CCMS",
                ai_generated=True,
            ),
            "swimming_recap": create_article(
                key="swimming_recap",
                title="200m Freestyle Final podium reflected in medal tally",
                slug="200m-freestyle-final-podium-reflected-in-medal-tally",
                summary="The finalized 200m Freestyle Final placements have been added to the official medal tally.",
                body_md=(
                    "The 200m Freestyle Final has been finalized and the podium results are now reflected in the official medal tally. "
                    "The standings continue to follow the medal-priority rule: gold first, then silver, then bronze, with department name used only as a stable final sort."
                ),
                article_type="result_recap",
                source_label="AI Recap, reviewed by Sports Coordinator",
                days_ago=2,
                hours_ago=2,
                event_key="swimming",
                department_key="CAFA",
                ai_generated=True,
            ),
            "basketball_update": create_article(
                key="basketball_update",
                title="Men's Basketball Finals remains live pending final confirmation",
                slug="mens-basketball-finals-live-pending-final-confirmation",
                summary="The Men's Basketball Finals is being monitored through the results workflow and will update once finalized.",
                body_md=(
                    "The Men's Basketball Finals remains in active monitoring through the Enverga Arena results workflow. "
                    "Only finalized results will affect official medal records and leaderboard standings. "
                    "Departments should refer to the public results page for confirmed updates."
                ),
                article_type="general_news",
                source_label="Results Desk",
                days_ago=1,
                hours_ago=7,
                event_key="basketball",
                department_key="CAS",
            ),
            "public_info": create_article(
                key="public_info",
                title="Schedules, results, and medal standings available for public viewing",
                slug="schedules-results-medal-standings-available-public-viewing",
                summary="Students, faculty, and guests may view official intramurals updates through the public Enverga Arena pages.",
                body_md=(
                    "The public Enverga Arena pages provide access to official schedules, results, medal tally, leaderboard, published news, and Rooney AI. "
                    "Draft articles, internal recap drafts, registration review notes, and department-private workflow records remain protected."
                ),
                article_type="general_news",
                source_label="Enverga Arena Secretariat",
                days_ago=1,
                hours_ago=1,
            ),
            "volleyball_recap": create_article(
                key="volleyball_recap",
                title="Women's Volleyball Finals recap published after official final result",
                slug="womens-volleyball-finals-recap",
                summary="The final volleyball result is now reflected in the official standings and public recap flow.",
                body_md=(
                    "The Women's Volleyball Finals concluded with an official final score and corresponding medal update. "
                    "The public recap summarizes the finalized result, source event, and effect on the current standings after Sports Coordinator review."
                ),
                article_type="result_recap",
                source_label="AI Recap, reviewed by Sports Coordinator",
                days_ago=0,
                hours_ago=6,
                event_key="volleyball",
                department_key="CAFA",
                ai_generated=True,
            ),
        }

        AIRecap.objects.create(
            trigger_type="event_completion",
            scope_type="match_result",
            scope_key="seed-match-volleyball",
            event=schedules["volleyball"].event,
            department=departments["CAFA"],
            input_snapshot_json={
                "event_title": schedules["volleyball"].event.name,
                "scoreline": "CAFA 3 - 1 CENG",
                "winner": departments["CAFA"].name,
            },
            generated_title="Women's Volleyball Finals recap ready for editorial review",
            generated_summary="A grounded recap draft is available for the official volleyball finals result.",
            generated_body="The Women's Volleyball Finals are finalized in the system and ready for editorial publishing after admin review.",
            model_name="template-grounded-v1",
            prompt_version="recap_v1",
            citation_map_json={"sources": ["final_match_result", "official_medal_tally"]},
            status="published",
            generated_at=now - timedelta(hours=2, minutes=10),
            reviewed_at=now - timedelta(hours=2, minutes=2),
            reviewed_by=admin_user,
            linked_news_article=articles["volleyball_recap"],
        )

        AIRecap.objects.create(
            trigger_type="event_completion",
            scope_type="match_result",
            scope_key="seed-match-table-tennis",
            event=schedules["table_tennis"].event,
            department=departments["CCMS"],
            input_snapshot_json={
                "event_title": schedules["table_tennis"].event.name,
                "scoreline": "CCMS 3 - 1 CAS",
                "winner": departments["CCMS"].name,
            },
            generated_title="Men's Table Tennis Team Final recap approved",
            generated_summary="A grounded table tennis recap was reviewed and published as official news.",
            generated_body="The Men's Table Tennis Team Final was finalized in the system and published after admin review.",
            model_name="template-grounded-v1",
            prompt_version="recap_v1",
            citation_map_json={"sources": ["final_match_result", "official_results"]},
            status="published",
            generated_at=now - timedelta(days=2, hours=6, minutes=20),
            reviewed_at=now - timedelta(days=2, hours=6, minutes=5),
            reviewed_by=admin_user,
            linked_news_article=articles["table_tennis_recap"],
        )

        AIRecap.objects.create(
            trigger_type="medal_update",
            scope_type="podium_schedule",
            scope_key="seed-podium-swimming",
            event=schedules["swimming"].event,
            department=departments["CAFA"],
            input_snapshot_json={
                "event_title": schedules["swimming"].event.name,
                "placements": [
                    {"rank": 1, "department": departments["CAFA"].name, "medal": "gold"},
                    {"rank": 2, "department": departments["CCMS"].name, "medal": "silver"},
                    {"rank": 3, "department": departments["CENG"].name, "medal": "bronze"},
                ],
            },
            generated_title="Swimming podium recap generated after final placements",
            generated_summary="The aquatics podium draft is ready for admin approval using the finalized ranked result data.",
            generated_body="Final podium placements for the swimming final have been recorded, and this AI recap draft is waiting at the review desk.",
            model_name="template-grounded-v1",
            prompt_version="recap_v1",
            citation_map_json={"sources": ["final_podium_results", "official_medal_tally"]},
            status="published",
            generated_at=now - timedelta(days=2, hours=2, minutes=15),
            reviewed_at=now - timedelta(days=2, hours=2, minutes=3),
            reviewed_by=admin_user,
            linked_news_article=articles["swimming_recap"],
        )

        AIRecap.objects.create(
            trigger_type="manual",
            scope_type="leaderboard",
            scope_key="seed-leaderboard-summary",
            department=departments["CCMS"],
            input_snapshot_json={
                "headline_scope": "top medal table movement",
                "departments": [department.name for department in departments.values()],
            },
            generated_title="Leaderboard movement recap drafted for admin review",
            generated_summary="A manual recap draft summarizes current leaderboard movement using the latest medal tally.",
            generated_body="This draft highlights current leaderboard movement and remains in review until the admin editorial desk confirms the framing.",
            model_name="template-grounded-v1",
            prompt_version="recap_v1",
            citation_map_json={"sources": ["official_medal_tally"]},
            status="approved",
            generated_at=now - timedelta(minutes=35),
            reviewed_at=now - timedelta(minutes=20),
            reviewed_by=admin_user,
        )
