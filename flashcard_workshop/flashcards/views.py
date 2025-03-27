from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from flashcard_workshop.flashcards.models import FlashCard, FlashCardSet
from flashcard_workshop.flashcards.serializers import (
    FlashCardSerializer,
    FlashCardSetCountersSerializer,
    FlashCardSetSerializer,
    UserSerializer,
)


class FlashCardSetViewSet(viewsets.ModelViewSet):
    queryset = FlashCardSet.objects.annotate_flashcard_count()
    serializer_class = FlashCardSetSerializer

    @extend_schema(
        description="Get cards to learn",
        responses={
            200: FlashCardSerializer(many=True),
        },
        parameters=[UserSerializer],
    )
    @action(detail=True, methods=["get"], url_path="learn", url_name="learn")
    def get_cards_to_learn(self, request, pk=None):
        flashcard_set = self.get_object()
        user_serializer = UserSerializer(data=request.GET)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.validated_data["user"]
        serializer = FlashCardSerializer(flashcard_set.get_cards_to_learn(user), many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Count known and unknown flashcards",
        responses={
            200: FlashCardSetCountersSerializer(),
        },
        parameters=[UserSerializer],
    )
    @action(detail=True, methods=["get"], url_path="counters", url_name="counters")
    def get_counters(self, request, pk=None):
        flashcard_set = self.get_object()
        user_serializer = UserSerializer(data=request.GET)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.validated_data["user"]
        known_flashcards = flashcard_set.flashcards.filter(
            results__user=user, results__score__gte=settings.FLASHCARD_KNOWN_THRESHOLD
        ).count()
        serializer = FlashCardSetCountersSerializer(
            {
                "known": known_flashcards,
                "unknown": flashcard_set.flashcard_count - known_flashcards,
            }
        )
        return Response(serializer.data)


class FlashCardViewSet(viewsets.ModelViewSet):
    serializer_class = FlashCardSerializer

    def get_queryset(self):
        return FlashCard.objects.filter(flashcard_set=self.kwargs["flash_card_set_pk"])

    @extend_schema(description="Mark flashcard as known", responses={200: ""})
    @action(
        methods=["post"],
        detail=True,
        url_path="mark-as-known",
        url_name="mark_as_known",
        serializer_class=UserSerializer,
    )
    def mark_as_known(self, request, pk=None, flash_card_set_pk=None):
        flashcard = self.get_object()
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        flashcard.mark_as_known(user)
        return Response({})

    @extend_schema(description="Mark flashcard as unknown", responses={200: ""})
    @action(
        methods=["post"],
        detail=True,
        url_path="mark-as-unknown",
        url_name="mark_as_unknown",
        serializer_class=UserSerializer,
    )
    def mark_as_unknown(self, request, pk=None, flash_card_set_pk=None):
        flashcard = self.get_object()
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        flashcard.mark_as_unknown(user)
        return Response({})
