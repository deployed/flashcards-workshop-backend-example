from collections.abc import Sequence
from random import shuffle

from django.conf import settings
from django.db import models
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _


class FlashCardSetManager(models.Manager):
    def annotate_flashcard_count(self):
        return self.annotate(_flashcard_count=models.Count("flashcards"))


class FlashCardSet(models.Model):
    title = models.CharField(max_length=100)

    objects = FlashCardSetManager()

    class Meta:
        verbose_name = _("Flashcard Set")
        verbose_name_plural = _("Flashcard Sets")
        ordering = ["title"]

    def __str__(self):
        return self.title

    @property
    def flashcard_count(self):
        if hasattr(self, "_flashcard_count"):
            return self._flashcard_count
        return self.flashcards.count()

    def get_cards_to_learn(self, user: str) -> Sequence["FlashCard"]:
        """
        Get flashcards to learn based on results of the user.
        First for every flashcard from set, annotate score for the user. By default it is 0.
        Then order flashcards by score and take first FLASHCARD_MAX_COUNT * 2 flashcards.
        Shuffle them and return only FLASHCARD_MAX_COUNT flashcards.

        Docs:
            https://docs.djangoproject.com/en/5.1/ref/models/querysets/#django.db.models.query.QuerySet.annotate
            https://docs.djangoproject.com/en/5.1/ref/models/database-functions/#django.db.models.functions.Coalesce
            https://docs.djangoproject.com/en/5.1/ref/models/expressions/#subquery-expressions

        """
        flashcards = list(
            self.flashcards.annotate(
                result_score=Coalesce(
                    models.Subquery(
                        FlashCardResult.objects.filter(flashcard=models.OuterRef("pk"), user=user).values("score")[:1]
                    ),
                    0,
                )
            ).order_by("result_score")[: (settings.FLASHCARD_MAX_COUNT * 2)]
        )
        shuffle(flashcards)
        return flashcards[: settings.FLASHCARD_MAX_COUNT]


class FlashCard(models.Model):
    question = models.TextField()
    answer = models.TextField()
    flashcard_set = models.ForeignKey(FlashCardSet, on_delete=models.CASCADE, related_name="flashcards")

    class Meta:
        verbose_name = _("Flashcard")
        verbose_name_plural = _("Flashcards")

    def __str__(self):
        return f"Flashcard #{self.id}"

    def mark_as_known(self, user) -> None:
        flashcard_result, created = FlashCardResult.objects.get_or_create(user=user, flashcard=self)
        flashcard_result.score += 1
        flashcard_result.save()

    def mark_as_unknown(self, user) -> None:
        flashcard_result, created = FlashCardResult.objects.get_or_create(user=user, flashcard=self)
        flashcard_result.score -= 1
        flashcard_result.save()


class FlashCardResult(models.Model):
    flashcard = models.ForeignKey(FlashCard, on_delete=models.CASCADE, related_name="results")
    user = models.CharField(max_length=100)
    score = models.IntegerField(default=0)

    class Meta:
        verbose_name = _("Flashcard Result")
        verbose_name_plural = _("Flashcard Results")

    def __str__(self):
        return f"{self.user} - {self.flashcard} - {self.score}"
