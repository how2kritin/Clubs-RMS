from sqlalchemy.orm import Session
from models.habits.habits_model import UserHabits
from schemas.habits.habits import UserHabitsData


def get_or_create(uid: str, db: Session) -> UserHabits:
    habits = db.query(UserHabits).filter(UserHabits.uid == uid).first()
    if habits is None:
        habits = UserHabits(uid=uid)
        db.add(habits)
        db.commit()
        db.refresh(habits)

    return habits


def update_habits(user_habits: UserHabitsData, db: Session) -> UserHabits:
    uid = user_habits.uid
    habits = get_or_create(uid, db)

    habits.hobbies = user_habits.hobbies  # type: ignore
    habits.skills = user_habits.skills  # type: ignore

    db.commit()
    db.refresh(habits)

    return habits
