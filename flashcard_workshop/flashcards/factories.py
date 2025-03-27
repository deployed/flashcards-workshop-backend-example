import factory

from flashcard_workshop.flashcards.models import FlashCard, FlashCardResult, FlashCardSet


class FlashCardSetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FlashCardSet


class FlashCardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FlashCard


class FlashCardResultFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FlashCardResult
