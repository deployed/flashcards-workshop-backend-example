import pytest
from django.test import override_settings
from django.urls import reverse

from flashcard_workshop.flashcards.factories import FlashCardFactory, FlashCardResultFactory
from flashcard_workshop.flashcards.models import FlashCard, FlashCardResult, FlashCardSet

pytestmark = pytest.mark.django_db


class TestFlashCardSetViewSet:
    def test_list(self, api_client, flashcard_set):
        response = api_client.get(reverse("flashcardset-list"))
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": flashcard_set.id,
                "title": flashcard_set.title,
                "flashcardCount": flashcard_set.flashcard_count,
            }
        ]

    def test_retrieve(self, api_client, flashcard_set):
        response = api_client.get(reverse("flashcardset-detail", args=[flashcard_set.id]))
        assert response.status_code == 200
        assert response.json() == {
            "id": flashcard_set.id,
            "title": flashcard_set.title,
            "flashcardCount": flashcard_set.flashcard_count,
        }

    def test_create(self, api_client):
        response = api_client.post(
            reverse("flashcardset-list"),
            data={"title": "Test Title"},
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Test Title"

    def test_update(self, api_client, flashcard_set):
        response = api_client.put(
            reverse("flashcardset-detail", args=[flashcard_set.id]),
            data={"title": "Updated Title"},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    def test_partial_update(self, api_client, flashcard_set):
        response = api_client.patch(
            reverse("flashcardset-detail", args=[flashcard_set.id]), data={"title": "Updated Title"}
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    def test_destroy(self, api_client, flashcard_set):
        response = api_client.delete(reverse("flashcardset-detail", args=[flashcard_set.id]))
        assert response.status_code == 204
        assert not response.content
        assert FlashCardSet.objects.count() == 0

    @override_settings(FLASHCARD_MAX_COUNT=3)
    def test_get_cards_to_learn(self, api_client, flashcard_set, user):
        flashcards = FlashCardFactory.create_batch(10, flashcard_set=flashcard_set)
        FlashCardResultFactory.create(flashcard=flashcards[0], user=user, score=-10)
        known_result = FlashCardResultFactory.create(flashcard=flashcards[1], user=user, score=10)
        response = api_client.get(reverse("flashcardset-learn", args=[flashcard_set.id]), data={"user": user})
        assert response.status_code == 200
        assert len(response.json()) == 3
        assert known_result.flashcard_id not in [flashcard["id"] for flashcard in response.json()]

    @override_settings(FLASHCARD_KNOWN_THRESHOLD=5)
    def test_get_counters(self, api_client, flashcard_set, user):
        flashcards = FlashCardFactory.create_batch(10, flashcard_set=flashcard_set)
        FlashCardResultFactory.create(flashcard=flashcards[0], user=user, score=-10)
        FlashCardResultFactory.create(flashcard=flashcards[1], user=user, score=10)
        response = api_client.get(reverse("flashcardset-counters", args=[flashcard_set.id]), data={"user": user})
        assert response.status_code == 200
        assert response.json() == {"known": 1, "unknown": 9}


class TestFlashCardViewSet:
    def test_list(self, api_client, flashcard):
        response = api_client.get(reverse("flashcard-list", args=[flashcard.flashcard_set_id]))
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": flashcard.id,
                "question": flashcard.question,
                "answer": flashcard.answer,
                "flashcardSet": flashcard.flashcard_set_id,
            }
        ]

    def test_retrieve(self, api_client, flashcard):
        response = api_client.get(reverse("flashcard-detail", args=[flashcard.flashcard_set_id, flashcard.id]))
        assert response.status_code == 200
        assert response.json() == {
            "id": flashcard.id,
            "question": flashcard.question,
            "answer": flashcard.answer,
            "flashcardSet": flashcard.flashcard_set_id,
        }

    def test_create(self, api_client, flashcard_set):
        response = api_client.post(
            reverse("flashcard-list", args=[flashcard_set.id]),
            data={"question": "Test Question", "answer": "Test Answer", "flashcardSet": flashcard_set.id},
        )
        assert response.status_code == 201
        assert response.json()["question"] == "Test Question"
        assert response.json()["answer"] == "Test Answer"

    def test_update(self, api_client, flashcard):
        response = api_client.put(
            reverse("flashcard-detail", args=[flashcard.flashcard_set_id, flashcard.id]),
            data={
                "question": "Updated Question",
                "answer": "Updated Answer",
                "flashcardSet": flashcard.flashcard_set_id,
            },
        )
        assert response.status_code == 200
        assert response.json()["question"] == "Updated Question"
        assert response.json()["answer"] == "Updated Answer"

    def test_partial_update(self, api_client, flashcard):
        response = api_client.patch(
            reverse("flashcard-detail", args=[flashcard.flashcard_set_id, flashcard.id]),
            data={"question": "Updated Question"},
        )
        assert response.status_code == 200
        assert response.json()["question"] == "Updated Question"

    def test_destroy(self, api_client, flashcard):
        response = api_client.delete(reverse("flashcard-detail", args=[flashcard.flashcard_set_id, flashcard.id]))
        assert response.status_code == 204
        assert not response.content
        assert FlashCard.objects.count() == 0

    def test_mark_as_known(self, api_client, flashcard, user):
        response = api_client.post(
            reverse("flashcard-mark_as_known", args=[flashcard.flashcard_set_id, flashcard.id]),
            data={"user": user},
        )
        assert response.status_code == 200
        assert FlashCardResult.objects.filter(flashcard=flashcard, user=user, score=1).exists()

    def test_mark_as_unknown(self, api_client, flashcard, user):
        response = api_client.post(
            reverse("flashcard-mark_as_unknown", args=[flashcard.flashcard_set_id, flashcard.id]),
            data={"user": user},
        )
        assert response.status_code == 200
        assert FlashCardResult.objects.filter(flashcard=flashcard, user=user, score=-1).exists()
