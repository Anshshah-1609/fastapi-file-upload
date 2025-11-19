""" Database connection setup. """

from urllib.parse import quote_plus
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import Depends

from app.configs import app_config
from app.logger import get_logger


logger = get_logger(__name__)


encoded_password = quote_plus(app_config.DB_PASSWORD)
SQLALCHEMY_DATABASE_URL = f"postgresql://{app_config.DB_USER}:{encoded_password}@{app_config.DB_HOST}:{app_config.DB_PORT}/{app_config.DB_NAME}"


# Create database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=app_config.DEBUG
)

# Create Base - this will be imported by models
Base = declarative_base()
# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """ Initialize database by creating all tables. """
    # Import models to ensure they're registered with Base.metadata
    from app.models import FileModel  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """ Dependency for getting database session. """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def sync_database():
    """Synchronize database schema with models.

    - Creates tables if they don't exist
    - Adds new columns from models
    - Removes columns that no longer exist in models
    - Preserves existing data
    """
    # Import models to ensure they're registered with Base.metadata
    from app.models import FileModel  # noqa: F401

    try:
        inspector = inspect(engine)

        # Process each table in the metadata
        for table_name, table in Base.metadata.tables.items():
            table_exists = inspector.has_table(table_name)

            if not table_exists:
                # Create table if it doesn't exist
                logger.info(f"Creating table '{table_name}'...")
                table.create(bind=engine, checkfirst=True)
                logger.info(f"Table '{table_name}' created successfully")
            else:
                # Table exists, check for schema differences
                logger.info(
                    f"Table '{table_name}' exists, checking for schema changes...")
                sync_table_schema(table_name, table, inspector)

        logger.info("Database synchronized successfully")
    except SQLAlchemyError as e:
        logger.exception("Error synchronizing database: %s", str(e))
        raise
    except Exception as e:
        logger.exception("Unexpected error synchronizing database: %s", str(e))
        raise


def sync_table_schema(table_name: str, table, inspector):
    """Synchronize a single table's schema with the model definition.

    Args:
        table_name: Name of the table
        table: SQLAlchemy Table object from metadata
        inspector: SQLAlchemy Inspector instance
    """
    # Get existing columns from database
    existing_columns = {col['name']: col for col in inspector.get_columns(table_name)}
    # Get columns from model
    model_columns = {col.name: col for col in table.columns}

    # Find columns to add (in model but not in database)
    columns_to_add = set(model_columns.keys()) - set(existing_columns.keys())
    # Find columns to remove (in database but not in model)
    columns_to_remove = set(existing_columns.keys()) - \
        set(model_columns.keys())

    # Add new columns
    if columns_to_add:
        logger.info(
            f"Adding {len(columns_to_add)} new column(s) to '{table_name}': {', '.join(columns_to_add)}")
        with engine.begin() as conn:
            for col_name in columns_to_add:
                model_col = model_columns[col_name]
                # Build ALTER TABLE ADD COLUMN statement
                alter_stmt = build_add_column_statement(table_name, model_col)
                # Safe: table_name and column come from SQLAlchemy models, not user input
                conn.execute(text(alter_stmt))  # noqa: S608
                logger.info(
                    f"Added column '{col_name}' to table '{table_name}'")

    # Remove obsolete columns
    if columns_to_remove:
        logger.info(
            f"Removing {len(columns_to_remove)} obsolete column(s) from '{table_name}': {', '.join(columns_to_remove)}")
        with engine.begin() as conn:
            for col_name in columns_to_remove:
                # Skip primary key columns - don't remove them automatically
                if existing_columns[col_name].get('primary_key'):
                    logger.warning(
                        f"Skipping removal of primary key column '{col_name}' from '{table_name}'")
                    continue
                # Quote identifiers for PostgreSQL (table and column names come from models, not user input)
                quoted_table = f'"{table_name}"'
                quoted_col = f'"{col_name}"'
                # Safe: table_name and col_name come from SQLAlchemy models, not user input
                alter_stmt = text(
                    f"ALTER TABLE {quoted_table} DROP COLUMN IF EXISTS {quoted_col}")  # noqa: S608
                conn.execute(alter_stmt)
                logger.info(
                    f"Removed column '{col_name}' from table '{table_name}'")

    if not columns_to_add and not columns_to_remove:
        logger.info(f"Table '{table_name}' schema is up to date")


def build_add_column_statement(table_name: str, column) -> str:
    """Build ALTER TABLE ADD COLUMN SQL statement.

    Args:
        table_name: Name of the table
        column: SQLAlchemy Column object

    Returns:
        SQL ALTER TABLE statement
    """
    # Quote identifiers for PostgreSQL (table and column names come from models, not user input)
    quoted_table = f'"{table_name}"'
    quoted_col = f'"{column.name}"'

    # Get column type
    col_type = column.type.compile(dialect=engine.dialect)

    # Build column definition
    col_def = f"{quoted_col} {col_type}"

    # Add nullable constraint
    # For new columns, we allow NULL initially if there's existing data
    # unless it's explicitly NOT NULL and has a default
    if not column.nullable and column.default is not None:
        col_def += " NOT NULL"
    elif not column.nullable and column.default is None:
        # If NOT NULL without default, allow NULL initially to avoid errors
        # This should be handled by application logic or manual migration
        logger.warning(
            f"Column '{column.name}' is NOT NULL without default. "
            f"Allowing NULL initially - ensure existing rows have values."
        )

    # Add default value if present
    if column.default is not None:
        default = column.default
        # Handle callable defaults (like datetime.utcnow)
        if callable(default.arg):
            # For callable defaults, use the function name or a suitable default
            # For datetime functions, use CURRENT_TIMESTAMP
            if 'utcnow' in str(default.arg).lower() or 'now' in str(default.arg).lower():
                col_def += " DEFAULT CURRENT_TIMESTAMP"
            else:
                # For other callables, we can't easily convert to SQL
                # Log a warning and skip the default
                logger.warning(
                    f"Column '{column.name}' has a callable default that cannot be "
                    f"automatically converted to SQL. Default will be handled by application."
                )
        else:
            # Handle literal defaults
            default_value = default.arg
            if isinstance(default_value, str):
                # Escape single quotes in string defaults
                escaped_value = default_value.replace("'", "''")
                col_def += f" DEFAULT '{escaped_value}'"
            else:
                col_def += f" DEFAULT {default_value}"

    return f"ALTER TABLE {quoted_table} ADD COLUMN IF NOT EXISTS {col_def}"


# Type hint for dependency injection
GetDb = Depends(get_db)
