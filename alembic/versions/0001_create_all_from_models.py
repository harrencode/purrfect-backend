"""Create all tables from models

Revision ID: 0001_create_all
Revises:
Create Date: 2026-01-14

"""

import importlib
import pkgutil

from alembic import op

from src.database.core import Base


# revision identifiers, used by Alembic.
revision = "0001_create_all"
down_revision = None
branch_labels = None
depends_on = None


def _import_all_entity_models() -> None:
    import src.entities as entities_pkg

    for module_info in pkgutil.iter_modules(entities_pkg.__path__, entities_pkg.__name__ + "."):
        importlib.import_module(module_info.name)


def upgrade() -> None:
    _import_all_entity_models()
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    _import_all_entity_models()
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
