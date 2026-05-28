import uuid

from sqlalchemy.orm import Session

from app.models.submission import Submission


def create_submission(db: Session, task_id: uuid.UUID) -> Submission:
    sub = Submission(task_id=task_id)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def get_submission_by_task(db: Session, task_id: uuid.UUID) -> Submission | None:
    return db.query(Submission).filter(Submission.task_id == task_id).first()


def get_submission_by_id(db: Session, submission_id: uuid.UUID) -> Submission | None:
    return db.query(Submission).filter(Submission.id == submission_id).first()


def grade_submission(db: Session, submission: Submission, is_correct: bool, comment: str | None) -> Submission:
    submission.is_correct = is_correct
    submission.comment = comment
    db.commit()
    db.refresh(submission)
    return submission
