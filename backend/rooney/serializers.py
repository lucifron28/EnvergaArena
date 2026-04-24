from rest_framework import serializers


class RooneyQuerySerializer(serializers.Serializer):
    question = serializers.CharField(max_length=500, min_length=3)


class RooneyResponseSerializer(serializers.Serializer):
    answer_text = serializers.CharField(allow_blank=True)
    grounded = serializers.BooleanField()
    source_labels = serializers.ListField(child=serializers.CharField())
    refusal_reason = serializers.CharField(allow_blank=True)
