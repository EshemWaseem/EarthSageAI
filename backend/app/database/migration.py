import logging
from sqlalchemy import text
from app.database.connection import engine, Base
from app.database.models import UserModel, RefreshTokenModel, InvestigationModel, ReportModel

logger = logging.getLogger(__name__)

def run_db_migrations():
    """
    Executes idempotent database schema migrations.
    Safely creates authentication tables and adds user_id foreign key to investigations
    without modifying or deleting pre-existing investigations or reports.
    """
    try:
        # First ensure Base metadata tables exist
        Base.metadata.create_all(bind=engine)

        with engine.connect() as conn:
            # Check if sqlite or postgresql
            dialect = engine.dialect.name
            logger.info(f"Running database schema verification for dialect: {dialect}")

            if dialect == "postgresql":
                # Ensure user_id column exists on investigations table
                conn.execute(text("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 
                            FROM information_schema.columns 
                            WHERE table_name = 'investigations' 
                            AND column_name = 'user_id'
                        ) THEN
                            ALTER TABLE investigations 
                            ADD COLUMN user_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL;
                        END IF;
                    END $$;
                """))
                
                # Ensure index exists
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_investigations_user_id ON investigations (user_id);
                """))
                conn.commit()
                logger.info("PostgreSQL migration: verified investigations.user_id column and index.")
            elif dialect == "sqlite":
                # SQLite fallback
                result = conn.execute(text("PRAGMA table_info(investigations)")).fetchall()
                cols = [row[1] for row in result]
                if "user_id" not in cols:
                    conn.execute(text("ALTER TABLE investigations ADD COLUMN user_id VARCHAR(36) REFERENCES users(id)"))
                    conn.commit()
                    logger.info("SQLite migration: added user_id column to investigations.")

    except Exception as e:
        logger.error(f"Error during schema migration: {e}")
        # Re-raise to ensure startup fails loudly rather than running in an invalid state
        raise

