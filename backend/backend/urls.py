from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import DepartmentViewSet, VenueViewSet, VenueAreaViewSet
from events.views import EventCategoryViewSet, EventViewSet
from tournaments.views import (
    EventScheduleViewSet, MatchResultViewSet, AthleteViewSet, EventRegistrationViewSet,
    PodiumResultViewSet, MedalRecordViewSet, MedalTallyViewSet,
)

router = DefaultRouter()

# Core
router.register(r'departments', DepartmentViewSet)
router.register(r'venues', VenueViewSet)
router.register(r'venue-areas', VenueAreaViewSet)

# Events
router.register(r'events', EventViewSet)
router.register(r'event-categories', EventCategoryViewSet)

# Tournaments
router.register(r'athletes', AthleteViewSet, basename='athlete')
router.register(r'registrations', EventRegistrationViewSet, basename='eventregistration')
router.register(r'schedules', EventScheduleViewSet)
router.register(r'match-results', MatchResultViewSet)
router.register(r'podium-results', PodiumResultViewSet)
router.register(r'medal-records', MedalRecordViewSet)
router.register(r'medal-tally', MedalTallyViewSet)

from rest_framework_simplejwt.views import TokenRefreshView
from core.serializers import CustomTokenObtainPairView

from rooney.views import RooneyQueryView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/public/rooney/query/', RooneyQueryView.as_view(), name='rooney_query'),
    path('api/public/', include(router.urls)),
]
