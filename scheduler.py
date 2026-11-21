from datetime import datetime, timezone
from fsrs import Scheduler, Card, Rating

scheduler = Scheduler()

def create_new_card() -> dict:
    card = Card()
    return {
        "due_date": card.due.isoformat(),
        "fsrs_data": card.to_json()
    }

def process_review(fsrs_data_json: str, rating_number: int) -> dict:
    card = Card.from_json(fsrs_data_json)
    rating = Rating(rating_number)

    updated_card, _ = scheduler.review_card(card, rating)

    return {
        "due_date": updated_card.due.isoformat(),
        "fsrs_data": updated_card.to_json()
    }

if __name__ == "__main__":
    new_card_info = create_new_card()
    print("Новая карточка создана. Показать:", new_card_info["due_date"])

    reviewed = process_review(new_card_info["fsrs_data"], 3)
    print("После оценки 'Хорошо' следующий показ:", reviewed["due_date"])