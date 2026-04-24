from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import RooneyQuerySerializer
from .services.grounding import build_grounding_context
from .services.llm import query_rooney
from .models import RooneyQueryLog


class RooneyQueryView(APIView):
    """
    POST /api/public/rooney/query/
    Public endpoint — no auth required.
    Body: {"question": "Who is leading?"}
    """

    def post(self, request):
        serializer = RooneyQuerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        question = serializer.validated_data['question']

        # 1. Build grounding context from live DB
        grounding = build_grounding_context()

        # 2. Call Gemini with grounded context
        result = query_rooney(question, grounding['text'])

        # Merge source labels: from grounding + from LLM response
        all_sources = list(set(grounding['source_labels'] + result.get('source_labels', [])))
        result['source_labels'] = all_sources

        # 3. Log the query
        RooneyQueryLog.objects.create(
            question=question,
            answer_text=result.get('answer_text', ''),
            grounded=result.get('grounded', False),
            source_labels=result.get('source_labels', []),
            refusal_reason=result.get('refusal_reason', ''),
        )

        return Response(result, status=status.HTTP_200_OK)
