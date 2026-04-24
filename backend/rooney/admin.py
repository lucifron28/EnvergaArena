from django.contrib import admin
from .models import RooneyQueryLog


@admin.register(RooneyQueryLog)
class RooneyQueryLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'question_preview', 'grounded', 'source_labels']
    list_filter = ['grounded']
    readonly_fields = [
        'question', 'answer_text', 'grounded',
        'source_labels', 'refusal_reason', 'created_at'
    ]

    def question_preview(self, obj):
        return obj.question[:80]
    question_preview.short_description = 'Question'
