from django.contrib import admin

from flashcard_workshop.flashcards.models import FlashCard, FlashCardResult, FlashCardSet


class FlashCardInline(admin.TabularInline):
    model = FlashCard
    extra = 1


@admin.register(FlashCardSet)
class FlashCardAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)
    inlines = (FlashCardInline,)


@admin.register(FlashCardResult)
class FlashCardResultAdmin(admin.ModelAdmin):
    list_display = ("flashcard", "user", "score")
    search_fields = ("user",)
