"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TYPE company_type AS ENUM (
            'customer','general_contractor','subcontractor',
            'designer','supervisor','operator','other'
        );
        CREATE TYPE user_role AS ENUM ('admin','manager','editor','viewer');
        CREATE TYPE project_status AS ENUM ('planned','active','frozen','closed');
        CREATE TYPE project_company_role AS ENUM (
            'customer','general_contractor','subcontractor',
            'designer','supervisor','operator','other'
        );
        CREATE TYPE chain_direction AS ENUM ('incoming','outgoing','mixed');
        CREATE TYPE letter_type AS ENUM ('incoming','outgoing','internal');
        CREATE TYPE letter_status AS ENUM ('received','in_work','done','sent','archived');
        CREATE TYPE doc_type AS ENUM (
            'project_doc','working_doc','as_built','contract','order','report','other'
        );
        CREATE TYPE doc_status AS ENUM ('draft','on_approval','approved','archived');
        CREATE TYPE approval_status AS ENUM (
            'pending','in_progress','approved','rejected','cancelled'
        );

        CREATE TABLE companies (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name        VARCHAR(500) NOT NULL,
            short_name  VARCHAR(200) NOT NULL,
            inn         VARCHAR(12),
            kpp         VARCHAR(9),
            company_type company_type NOT NULL DEFAULT 'other',
            is_internal BOOLEAN NOT NULL DEFAULT FALSE,
            is_active   BOOLEAN NOT NULL DEFAULT TRUE,
            created_at  TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE users (
            id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email               VARCHAR(255) NOT NULL UNIQUE,
            username            VARCHAR(100) NOT NULL UNIQUE,
            full_name           VARCHAR(300) NOT NULL,
            hashed_password     VARCHAR(255) NOT NULL,
            is_active           BOOLEAN NOT NULL DEFAULT TRUE,
            is_superuser        BOOLEAN NOT NULL DEFAULT FALSE,
            current_company_id  UUID REFERENCES companies(id) ON DELETE SET NULL,
            created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
            last_login          TIMESTAMP
        );
        CREATE INDEX ix_users_email    ON users(email);
        CREATE INDEX ix_users_username ON users(username);

        CREATE TABLE user_company_roles (
            id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id    UUID NOT NULL REFERENCES users(id)    ON DELETE CASCADE,
            company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
            role       user_role NOT NULL DEFAULT 'viewer',
            is_active  BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
        CREATE INDEX ix_ucr_user    ON user_company_roles(user_id);
        CREATE INDEX ix_ucr_company ON user_company_roles(company_id);

        CREATE TABLE projects (
            id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            code             VARCHAR(100) NOT NULL UNIQUE,
            name             VARCHAR(500) NOT NULL,
            description      TEXT,
            status           project_status NOT NULL DEFAULT 'planned',
            start_date       DATE,
            end_date         DATE,
            owner_company_id UUID NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
            created_at       TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at       TIMESTAMP NOT NULL DEFAULT NOW()
        );
        CREATE INDEX ix_projects_code   ON projects(code);
        CREATE INDEX ix_projects_status ON projects(status);
        CREATE INDEX ix_projects_owner  ON projects(owner_company_id);

        CREATE TABLE project_companies (
            id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            project_id UUID NOT NULL REFERENCES projects(id)  ON DELETE CASCADE,
            company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
            role       project_company_role NOT NULL DEFAULT 'other',
            joined_at  TIMESTAMP NOT NULL DEFAULT NOW()
        );
        CREATE INDEX ix_pc_project ON project_companies(project_id);
        CREATE INDEX ix_pc_company ON project_companies(company_id);

        CREATE TABLE chains (
            id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            project_id      UUID NOT NULL REFERENCES projects(id)  ON DELETE CASCADE,
            subject         VARCHAR(500) NOT NULL,
            direction       chain_direction NOT NULL DEFAULT 'mixed',
            main_company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
            created_at      TIMESTAMP NOT NULL DEFAULT NOW()
        );
        CREATE INDEX ix_chains_project      ON chains(project_id);
        CREATE INDEX ix_chains_main_company ON chains(main_company_id);

        CREATE TABLE letters (
            id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            chain_id         UUID NOT NULL REFERENCES chains(id)   ON DELETE CASCADE,
            project_id       UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            owner_company_id UUID NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
            letter_type      letter_type NOT NULL,
            letter_date      DATE,
            number           VARCHAR(100),
            org_number       VARCHAR(100),
            from_company_id  UUID REFERENCES companies(id) ON DELETE SET NULL,
            to_company_id    UUID REFERENCES companies(id) ON DELETE SET NULL,
            subject          VARCHAR(500),
            body             TEXT,
            status           letter_status NOT NULL DEFAULT 'received',
            reply_to_id      UUID REFERENCES letters(id) ON DELETE SET NULL,
            resolution       TEXT,
            note             TEXT,
            created_at       TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at       TIMESTAMP NOT NULL DEFAULT NOW()
        );
        CREATE INDEX ix_letters_project  ON letters(project_id);
        CREATE INDEX ix_letters_chain    ON letters(chain_id);
        CREATE INDEX ix_letters_owner    ON letters(owner_company_id);
        CREATE INDEX ix_letters_type     ON letters(letter_type);
        CREATE INDEX ix_letters_status   ON letters(status);
        CREATE INDEX ix_letters_date     ON letters(letter_date);
        CREATE INDEX ix_letters_number   ON letters(number);
        CREATE INDEX ix_letters_reply_to ON letters(reply_to_id);
        CREATE INDEX ix_letters_from     ON letters(from_company_id);
        CREATE INDEX ix_letters_to       ON letters(to_company_id);

        CREATE TABLE letter_files (
            id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            letter_id     UUID NOT NULL REFERENCES letters(id) ON DELETE CASCADE,
            filename      VARCHAR(500) NOT NULL,
            original_name VARCHAR(500) NOT NULL,
            content_type  VARCHAR(200) NOT NULL,
            size          BIGINT NOT NULL,
            storage_path  VARCHAR(1000) NOT NULL,
            uploaded_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
            uploaded_at   TIMESTAMP NOT NULL DEFAULT NOW()
        );
        CREATE INDEX ix_letter_files_letter ON letter_files(letter_id);

        CREATE TABLE project_documents (
            id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            project_id       UUID NOT NULL REFERENCES projects(id)  ON DELETE CASCADE,
            owner_company_id UUID NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
            doc_type         doc_type NOT NULL DEFAULT 'other',
            code             VARCHAR(200),
            name             VARCHAR(500) NOT NULL,
            description      TEXT,
            status           doc_status NOT NULL DEFAULT 'draft',
            version          VARCHAR(50) NOT NULL DEFAULT '1.0',
            linked_letter_id UUID REFERENCES letters(id) ON DELETE SET NULL,
            created_at       TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at       TIMESTAMP NOT NULL DEFAULT NOW()
        );
        CREATE INDEX ix_docs_project ON project_documents(project_id);
        CREATE INDEX ix_docs_owner   ON project_documents(owner_company_id);
        CREATE INDEX ix_docs_type    ON project_documents(doc_type);
        CREATE INDEX ix_docs_status  ON project_documents(status);
        CREATE INDEX ix_docs_code    ON project_documents(code);

        CREATE TABLE project_document_files (
            id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            document_id   UUID NOT NULL REFERENCES project_documents(id) ON DELETE CASCADE,
            filename      VARCHAR(500) NOT NULL,
            original_name VARCHAR(500) NOT NULL,
            content_type  VARCHAR(200) NOT NULL,
            size          BIGINT NOT NULL,
            storage_path  VARCHAR(1000) NOT NULL,
            version       VARCHAR(50) NOT NULL DEFAULT '1.0',
            uploaded_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
            uploaded_at   TIMESTAMP NOT NULL DEFAULT NOW()
        );
        CREATE INDEX ix_doc_files_document ON project_document_files(document_id);

        CREATE TABLE approval_routes (
            id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            project_id  UUID REFERENCES projects(id) ON DELETE CASCADE,
            name        VARCHAR(300) NOT NULL,
            description TEXT,
            is_active   BOOLEAN NOT NULL DEFAULT TRUE,
            created_at  TIMESTAMP NOT NULL DEFAULT NOW()
        );

        CREATE TABLE approval_steps (
            id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            route_id      UUID NOT NULL REFERENCES approval_routes(id) ON DELETE CASCADE,
            order_num     INTEGER NOT NULL,
            name          VARCHAR(300) NOT NULL,
            assignee_id   UUID REFERENCES users(id) ON DELETE SET NULL,
            company_id    UUID REFERENCES companies(id) ON DELETE SET NULL,
            deadline_days INTEGER
        );

        CREATE TABLE approval_tasks (
            id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            project_id     UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            route_id       UUID REFERENCES approval_routes(id) ON DELETE SET NULL,
            letter_id      UUID REFERENCES letters(id) ON DELETE CASCADE,
            document_id    UUID REFERENCES project_documents(id) ON DELETE CASCADE,
            title          VARCHAR(500) NOT NULL,
            status         approval_status NOT NULL DEFAULT 'pending',
            current_step   INTEGER NOT NULL DEFAULT 1,
            assignee_id    UUID REFERENCES users(id) ON DELETE SET NULL,
            created_by_id  UUID REFERENCES users(id) ON DELETE SET NULL,
            comment        TEXT,
            deadline       TIMESTAMP,
            created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at     TIMESTAMP NOT NULL DEFAULT NOW()
        );
        CREATE INDEX ix_tasks_project  ON approval_tasks(project_id);
        CREATE INDEX ix_tasks_assignee ON approval_tasks(assignee_id);
        CREATE INDEX ix_tasks_status   ON approval_tasks(status);
        CREATE INDEX ix_tasks_letter   ON approval_tasks(letter_id);
        CREATE INDEX ix_tasks_document ON approval_tasks(document_id);
    """)


def downgrade() -> None:
    op.execute("""
        DROP TABLE IF EXISTS approval_tasks, approval_steps, approval_routes,
            project_document_files, project_documents, letter_files, letters,
            chains, project_companies, projects, user_company_roles, users,
            companies CASCADE;
        DROP TYPE IF EXISTS approval_status, doc_status, doc_type, letter_status,
            letter_type, chain_direction, project_company_role, project_status,
            user_role, company_type CASCADE;
    """)
