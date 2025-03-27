from rest_framework import serializers

from flashcard_workshop.flashcards.models import FlashCard, FlashCardSet


class FlashCardSetSerializer(serializers.ModelSerializer):
    flashcard_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = FlashCardSet
        fields = ["id", "title", "flashcard_count"]


class FlashCardSetCountersSerializer(serializers.Serializer):
    known = serializers.IntegerField()
    unknown = serializers.IntegerField()


class FlashCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashCard
        fields = "__all__"


class UserSerializer(serializers.Serializer):
    user = serializers.CharField(max_length=100)
