from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Department, Venue, VenueArea, UserProfile

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class VenueAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueArea
        fields = '__all__'

class VenueSerializer(serializers.ModelSerializer):
    areas = VenueAreaSerializer(many=True, read_only=True)

    class Meta:
        model = Venue
        fields = ['id', 'name', 'location', 'areas', 'created_at', 'updated_at']
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        
        # Check for UserProfile
        try:
            profile = user.profile
            token['role'] = profile.role
            token['department_id'] = profile.department_id if profile.department else None
            token['department_acronym'] = profile.department.acronym if profile.department else None
        except UserProfile.DoesNotExist:
            token['role'] = 'admin' if user.is_staff or user.is_superuser else 'none'
            token['department_id'] = None
            token['department_acronym'] = None

        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
