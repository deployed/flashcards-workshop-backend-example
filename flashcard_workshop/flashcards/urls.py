from rest_framework_nested import routers

from flashcard_workshop.flashcards.views import FlashCardSetViewSet, FlashCardViewSet

flash_card_sets_router = routers.SimpleRouter()
flash_card_sets_router.register("flash-card-sets", FlashCardSetViewSet)

flash_cards_router = routers.NestedSimpleRouter(flash_card_sets_router, r"flash-card-sets", lookup="flash_card_set")
flash_cards_router.register(r"flash-cards", FlashCardViewSet, basename="flashcard")
