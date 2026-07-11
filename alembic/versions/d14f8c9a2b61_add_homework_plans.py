"""add homework plans

Revision ID: d14f8c9a2b61
Revises: c7919be721dd
Create Date: 2026-07-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.db_types import GUID


revision: str = "d14f8c9a2b61"
down_revision: Union[str, None] = "c7919be721dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "homework_plans",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("family_id", GUID(), nullable=False),
        sa.Column("created_by", GUID(), nullable=False),
        sa.Column("type", sa.String(length=10), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("desc", sa.Text(), nullable=True),
        sa.Column("duration", sa.Integer(), nullable=True),
        sa.Column("subject", sa.String(length=20), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], name="fk_homework_plans_created_by"),
        sa.ForeignKeyConstraint(["family_id"], ["families.id"], name="fk_homework_plans_family_id"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_homework_plans_family_id", "homework_plans", ["family_id"])
    op.create_index(
        "ix_homework_plans_activity",
        "homework_plans",
        ["family_id", "is_deleted", "start_date", "end_date"],
    )
    op.create_table(
        "homework_plan_dictation_items",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("plan_id", GUID(), nullable=False),
        sa.Column("content", sa.String(length=200), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["plan_id"], ["homework_plans.id"], name="fk_homework_plan_items_plan_id"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_homework_plan_dictation_items_plan_id",
        "homework_plan_dictation_items",
        ["plan_id"],
    )
    op.add_column("tasks", sa.Column("source_plan_id", GUID(), nullable=True))
    op.create_index("ix_tasks_source_plan_id", "tasks", ["source_plan_id"])
    op.create_foreign_key(
        "fk_tasks_source_plan_id",
        "tasks",
        "homework_plans",
        ["source_plan_id"],
        ["id"],
    )
    op.create_unique_constraint(
        "uq_tasks_source_plan_date", "tasks", ["source_plan_id", "date"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_tasks_source_plan_date", "tasks", type_="unique")
    op.drop_constraint("fk_tasks_source_plan_id", "tasks", type_="foreignkey")
    op.drop_index("ix_tasks_source_plan_id", table_name="tasks")
    op.drop_column("tasks", "source_plan_id")
    op.drop_index("ix_homework_plan_dictation_items_plan_id", table_name="homework_plan_dictation_items")
    op.drop_table("homework_plan_dictation_items")
    op.drop_index("ix_homework_plans_activity", table_name="homework_plans")
    op.drop_index("ix_homework_plans_family_id", table_name="homework_plans")
    op.drop_table("homework_plans")
