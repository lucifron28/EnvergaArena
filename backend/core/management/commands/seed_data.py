import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Department, Venue, VenueArea
from events.models import EventCategory, Event
from tournaments.models import EventSchedule, MatchResult, PodiumResult, MedalRecord, MedalTally

class Command(BaseCommand):
    help = 'Seeds the database with realistic Enverga Arena test data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing existing data...")
        MedalRecord.objects.all().delete()
        MedalTally.objects.all().delete()
        PodiumResult.objects.all().delete()
        MatchResult.objects.all().delete()
        EventSchedule.objects.all().delete()
        Event.objects.all().delete()
        EventCategory.objects.all().delete()
        VenueArea.objects.all().delete()
        Venue.objects.all().delete()
        Department.objects.all().delete()

        self.stdout.write("Seeding Departments...")
        departments_data = [
            ("College of Architecture and Fine Arts", "CAFA", "#800000"),
            ("College of Arts and Sciences", "CAS", "#000080"),
            ("College of Business and Accountancy", "CBA", "#FFD700"),
            ("College of Computing and Multimedia Studies", "CCMS", "#FF8C00"),
            ("College of Criminal Justice and Criminology", "CCJC", "#8B0000"),
            ("College of Education", "CED", "#4169E1"),
            ("College of Engineering", "CENG", "#A52A2A"),
            ("College of International Hospitality and Tourism Management", "CIHTM", "#FF69B4"),
            ("College of Maritime Education", "CME", "#0000CD"),
            ("College of Nursing and Allied Health Sciences", "CNAHS", "#008000"),
        ]
        
        departments = {}
        for name, acronym, color in departments_data:
            dept = Department.objects.create(name=name, acronym=acronym, color_code=color)
            departments[acronym] = dept

        self.stdout.write("Seeding Venues...")
        v_gym = Venue.objects.create(name="University Gymnasium")
        va_gym_a = VenueArea.objects.create(venue=v_gym, name="Court A")
        va_gym_b = VenueArea.objects.create(venue=v_gym, name="Court B")

        v_pool = Venue.objects.create(name="Olympic-sized Swimming Pool")
        va_pool = VenueArea.objects.create(venue=v_pool, name="Pool Lane Set")

        v_complex = Venue.objects.create(name="Covered sports complex")
        va_complex_tennis = VenueArea.objects.create(venue=v_complex, name="Tennis Court 1")
        va_complex_tt = VenueArea.objects.create(venue=v_complex, name="Table Tennis Area")

        v_ccms = Venue.objects.create(name="CCMS Building")
        va_ccms_esports = VenueArea.objects.create(venue=v_ccms, name="Esports Room A")

        self.stdout.write("Seeding Categories & Events...")
        cat_ball = EventCategory.objects.create(name="Ball Games")
        cat_aqua = EventCategory.objects.create(name="Aquatics")
        cat_cult = EventCategory.objects.create(name="Cultural")
        cat_esp = EventCategory.objects.create(name="E-Sports")

        evt_bball = Event.objects.create(category=cat_ball, name="Men's Basketball", result_family="match_based")
        evt_vball = Event.objects.create(category=cat_ball, name="Women's Volleyball", result_family="match_based")
        evt_tt = Event.objects.create(category=cat_ball, name="Men's Table Tennis Team", result_family="match_based")
        
        evt_swim = Event.objects.create(category=cat_aqua, name="200m Freestyle", result_family="rank_based")
        evt_dance = Event.objects.create(category=cat_cult, name="Dancesport Latin", result_family="rank_based")
        evt_esports = Event.objects.create(category=cat_esp, name="Valorant Tournament", result_family="match_based")

        now = timezone.now()

        self.stdout.write("Seeding Schedules...")
        sched_bball = EventSchedule.objects.create(event=evt_bball, venue=v_gym, venue_area=va_gym_a, scheduled_start=now - timedelta(days=1), scheduled_end=now - timedelta(days=1) + timedelta(hours=2))
        sched_vball = EventSchedule.objects.create(event=evt_vball, venue=v_gym, venue_area=va_gym_b, scheduled_start=now + timedelta(hours=2), scheduled_end=now + timedelta(hours=4))
        sched_tt = EventSchedule.objects.create(event=evt_tt, venue=v_complex, venue_area=va_complex_tt, scheduled_start=now + timedelta(days=1), scheduled_end=now + timedelta(days=1, hours=2))
        
        sched_swim = EventSchedule.objects.create(event=evt_swim, venue=v_pool, venue_area=va_pool, scheduled_start=now - timedelta(hours=5), scheduled_end=now - timedelta(hours=3))
        sched_dance = EventSchedule.objects.create(event=evt_dance, venue=v_gym, venue_area=va_gym_a, scheduled_start=now + timedelta(days=2), scheduled_end=now + timedelta(days=2, hours=3))
        sched_esports = EventSchedule.objects.create(event=evt_esports, venue=v_ccms, venue_area=va_ccms_esports, scheduled_start=now, scheduled_end=now + timedelta(hours=3))

        self.stdout.write("Seeding Standings (Medal Records)...")
        # Synthetic data from prompt:
        # CAFA: 18 G, 14 S, 9 B
        # CCMS: 12 G, 15 S, 10 B
        # CENG: 10 G, 12 S, 18 B
        # CBA: 8 G, 9 S, 12 B
        # CAS: 7 G, 11 S, 15 B
        
        synthetic_standings = {
            "CAFA": {"gold": 18, "silver": 14, "bronze": 9},
            "CCMS": {"gold": 12, "silver": 15, "bronze": 10},
            "CENG": {"gold": 10, "silver": 12, "bronze": 18},
            "CBA": {"gold": 8, "silver": 9, "bronze": 12},
            "CAS": {"gold": 7, "silver": 11, "bronze": 15},
        }

        # To fake these medals without creating 100 events, we just inject them into the MedalTally directly,
        # but wait, the instructions say: "Medal standings should be computed from an immutable MedalRecord ledger".
        # So we must create MedalRecords. We can create dummy events to attach them to.
        cat_dummy = EventCategory.objects.create(name="Previous Events (Seeded)")
        
        for dept_acronym, medals in synthetic_standings.items():
            dept = departments[dept_acronym]
            for medal_type in ['gold', 'silver', 'bronze']:
                count = medals[medal_type]
                for i in range(count):
                    dummy_event = Event.objects.create(category=cat_dummy, name=f"Dummy Event {dept_acronym} {medal_type} {i}", result_family="rank_based")
                    # Emulate post_save by creating MedalRecord
                    MedalRecord.objects.create(department=dept, event=dummy_event, medal=medal_type)

        self.stdout.write("Seeding some active results...")
        # Match Result for Basketball
        MatchResult.objects.create(
            schedule=sched_bball,
            home_department=departments["CAFA"],
            away_department=departments["CENG"],
            home_score=85,
            away_score=82,
            winner=departments["CAFA"],
            is_final=True
        )
        
        # Podium Result for Swimming
        PodiumResult.objects.create(schedule=sched_swim, department=departments["CCMS"], rank=1, medal='gold', is_final=True)
        PodiumResult.objects.create(schedule=sched_swim, department=departments["CAS"], rank=2, medal='silver', is_final=True)
        PodiumResult.objects.create(schedule=sched_swim, department=departments["CBA"], rank=3, medal='bronze', is_final=True)

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with realistic data!'))
