import pytest

from flashcard_workshop.flashcards.factories import FlashCardFactory, FlashCardSetFactory


@pytest.fixture
def flashcard_set():
    return FlashCardSetFactory.create()


@pytest.fixture
def flashcard(flashcard_set):
    return FlashCardFactory.create(flashcard_set=flashcard_set)
