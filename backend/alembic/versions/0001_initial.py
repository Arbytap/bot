"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enums
    company_type = postgresql.ENUM(
        "customer", "general_contractor", "subcontractor", "designer",
        "supervisor", "operator", "other",
        name="company_type", create_type=True
    )
    user_role = postgresql.ENUM(
        "admin", "manager", "editor", "viewer",
        name="user_role", create_type=True
    )
    project_status = postgresql.ENUM(
        "planned", "active", "frozen", "closed",
        name="project_status", create_type=True
    )
    project_company_role = postgresql.ENUM(
        "customer", "general_contractor", "subcontractor", "designer",
        "supervisor", "operator", "other",
        name="project_company_role", create_type=True
    )
    chain_direction = postgresql.ENUM(
        "incoming", "outgoing", "mixed",
        name="chain_direction", create_type=True
    )
    letter_type = postgresql.ENUM(
        "incoming", "outgoing", "internal",
        name="letter_type", create_type=True
    )
    letter_status = postgresql.ENUM(
        "received", "in_work", "done", "sent", "archived",
        name="letter_status", create_type=True
    )
    doc_type = postgresql.ENUM(
        "project_doc", "working_doc", "as_built", "contract", "order", "report", "other",
        name="doc_type", create_type=True
    )
    doc_status = postgresql.ENUM(
        "draft", "on_approval", "approved", "archived",
        name="doc_status", create_type=True
    )
    approval_status = postgresql.ENUM(
        "pending", "in_progress", "approved", "rejected", "cancelled",
        name="approval_status", create_type=True
    )

    company_type.create(op.get_bind(), checkfirst=True)
    user_role.create(op.get_bind(), checkfirst=True)
    project_status.create(op.get_bind(), checkfirst=True)
    project_company_role.create(op.get_bind(), checkfirst=True)
    chain_direction.create(op.get_bind(), checkfirst=True)
    letter_type.create(op.get_bind(), checkfirst=True)
    letter_status.create(op.get_bind(), checkfirst=True)
    doc_type.create(op.get_bind(), checkfirst=True)
    doc_status.create(op.get_bind(), checkfirst=True)
    approval_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("short_name", sa.String(200), nullable=False),
        sa.Column("inn", sa.String(12), nullable=True),
        sa.Column("kpp", sa.String(9), nullable=True),
        sa.Column("company_type", sa.Enum("customer", "general_contractor", "subcontractor", "designer", "supervisor", "operator", "other", name="company_type", create_type=False), nullable=False),
        sa.Column("is_internal", sa.Boolean(), default=False, nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("username", sa.String(100), nullable=False, unique=True),
        sa.Column("full_name", sa.String(300), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("is_superuser", sa.Boolean(), default=False, nullable=False),
        sa.Column("current_company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_login", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_username", "users", ["username"])

    op.create_table(
        "user_company_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.Enum("admin", "manager", "editor", "viewer", name="user_role", create_type=False), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_ucr_user", "user_company_roles", ["user_id"])
    op.create_index("ix_ucr_company", "user_company_roles", ["company_id"])

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(100), nullable=False, unique=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.Enum("planned", "active", "frozen", "closed", name="project_status", create_type=False), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("owner_company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_projects_code", "projects", ["code"])
    op.create_index("ix_projects_status", "projects", ["status"])
    op.create_index("ix_projects_owner", "projects", ["owner_company_id"])

    op.create_table(
        "project_companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.Enum("customer", "general_contractor", "subcontractor", "designer", "supervisor", "operator", "other", name="project_company_role", create_type=False), nullable=False),
        sa.Column("joined_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_pc_project", "project_companies", ["project_id"])
    op.create_index("ix_pc_company", "project_companies", ["company_id"])

    op.create_table(
        "chains",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("direction", sa.Enum("incoming", "outgoing", "mixed", name="chain_direction", create_type=False), nullable=False),
        sa.Column("main_company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_chains_project", "chains", ["project_id"])
    op.create_index("ix_chains_main_company", "chains", ["main_company_id"])

    op.create_table(
        "letters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("chain_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chains.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("owner_company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("letter_type", sa.Enum("incoming", "outgoing", "internal", name="letter_type", create_type=False), nullable=False),
        sa.Column("letter_date", sa.Date(), nullable=True),
        sa.Column("number", sa.String(100), nullable=True),
        sa.Column("org_number", sa.String(100), nullable=True),
        sa.Column("from_company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="SET NULL"), nullable=True),
        sa.Column("to_company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="SET NULL"), nullable=True),
        sa.Column("subject", sa.String(500), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("status", sa.Enum("received", "in_work", "done", "sent", "archived", name="letter_status", create_type=False), nullable=False),
        sa.Column("reply_to_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("letters.id", ondelete="SET NULL"), nullable=True),
        sa.Column("resolution", sa.Text(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_letters_project", "letters", ["project_id"])
    op.create_index("ix_letters_chain", "letters", ["chain_id"])
    op.create_index("ix_letters_owner", "letters", ["owner_company_id"])
    op.create_index("ix_letters_type", "letters", ["letter_type"])
    op.create_index("ix_letters_status", "letters", ["status"])
    op.create_index("ix_letters_date", "letters", ["letter_date"])
    op.create_index("ix_letters_number", "letters", ["number"])
    op.create_index("ix_letters_reply_to", "letters", ["reply_to_id"])
    op.create_index("ix_letters_from", "letters", ["from_company_id"])
    op.create_index("ix_letters_to", "letters", ["to_company_id"])

    op.create_table(
        "letter_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("letter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("letters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("original_name", sa.String(500), nullable=False),
        sa.Column("content_type", sa.String(200), nullable=False),
        sa.Column("size", sa.BigInteger(), nullable=False),
        sa.Column("storage_path", sa.String(1000), nullable=False),
        sa.Column("uploaded_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_letter_files_letter", "letter_files", ["letter_id"])

    op.create_table(
        "project_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("owner_company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("doc_type", sa.Enum("project_doc", "working_doc", "as_built", "contract", "order", "report", "other", name="doc_type", create_type=False), nullable=False),
        sa.Column("code", sa.String(200), nullable=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.Enum("draft", "on_approval", "approved", "archived", name="doc_status", create_type=False), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("linked_letter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("letters.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_docs_project", "project_documents", ["project_id"])
    op.create_index("ix_docs_owner", "project_documents", ["owner_company_id"])
    op.create_index("ix_docs_type", "project_documents", ["doc_type"])
    op.create_index("ix_docs_status", "project_documents", ["status"])
    op.create_index("ix_docs_code", "project_documents", ["code"])

    op.create_table(
        "project_document_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("project_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("original_name", sa.String(500), nullable=False),
        sa.Column("content_type", sa.String(200), nullable=False),
        sa.Column("size", sa.BigInteger(), nullable=False),
        sa.Column("storage_path", sa.String(1000), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("uploaded_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_doc_files_document", "project_document_files", ["document_id"])

    op.create_table(
        "approval_routes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "approval_steps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("route_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("approval_routes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order_num", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("assignee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="SET NULL"), nullable=True),
        sa.Column("deadline_days", sa.Integer(), nullable=True),
    )

    op.create_table(
        "approval_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("route_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("approval_routes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("letter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("letters.id", ondelete="CASCADE"), nullable=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("project_documents.id", ondelete="CASCADE"), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("status", sa.Enum("pending", "in_progress", "approved", "rejected", "cancelled", name="approval_status", create_type=False), nullable=False),
        sa.Column("current_step", sa.Integer(), nullable=False),
        sa.Column("assignee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("deadline", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_tasks_project", "approval_tasks", ["project_id"])
    op.create_index("ix_tasks_assignee", "approval_tasks", ["assignee_id"])
    op.create_index("ix_tasks_status", "approval_tasks", ["status"])
    op.create_index("ix_tasks_letter", "approval_tasks", ["letter_id"])
    op.create_index("ix_tasks_document", "approval_tasks", ["document_id"])


def downgrade() -> None:
    op.drop_table("approval_tasks")
    op.drop_table("approval_steps")
    op.drop_table("approval_routes")
    op.drop_table("project_document_files")
    op.drop_table("project_documents")
    op.drop_table("letter_files")
    op.drop_table("letters")
    op.drop_table("chains")
    op.drop_table("project_companies")
    op.drop_table("projects")
    op.drop_table("user_company_roles")
    op.drop_table("users")
    op.drop_table("companies")

    for enum_name in [
        "approval_status", "doc_status", "doc_type", "letter_status",
        "letter_type", "chain_direction", "project_company_role",
        "project_status", "user_role", "company_type",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
