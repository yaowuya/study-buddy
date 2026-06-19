import uuid

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from app.db_types import GUID


class _Base(DeclarativeBase):
    pass


class Widget(_Base):
    __tablename__ = "widgets"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True)


def test_guid_round_trips_uuid_and_stores_hyphenated_string():
    engine = create_engine("sqlite:///:memory:")
    _Base.metadata.create_all(engine)

    widget_id = uuid.uuid4()
    with Session(engine) as session:
        session.add(Widget(id=widget_id))
        session.commit()

    with Session(engine) as session:
        found = session.get(Widget, widget_id)
        raw_id = session.execute(text("SELECT id FROM widgets")).scalar_one()

    assert found is not None
    assert found.id == widget_id
    assert isinstance(found.id, uuid.UUID)
    assert raw_id == str(widget_id)
