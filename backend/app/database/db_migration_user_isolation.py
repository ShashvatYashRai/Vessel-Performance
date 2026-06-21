import os
import sys
from sqlalchemy import create_engine, text

# Add backend directory to Python path
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.database.connection import DATABASE_URL

def run_migration():
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        print("Starting migration...")
        
        # 1. Drop old constraint and index
        print("Dropping old constraint uq_vessel_report_date...")
        conn.execute(text("ALTER TABLE daily_reports DROP CONSTRAINT IF EXISTS uq_vessel_report_date;"))
        
        print("Dropping old index ix_vessel_report_date...")
        conn.execute(text("DROP INDEX IF EXISTS ix_vessel_report_date;"))
        
        # 2. Add new user-scoped constraint and index
        print("Adding new unique constraint uq_vessel_report_date_user...")
        conn.execute(text("ALTER TABLE daily_reports ADD CONSTRAINT uq_vessel_report_date_user UNIQUE (vessel_id, report_date, user_id);"))
        
        print("Adding new index ix_vessel_report_date_user...")
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_vessel_report_date_user ON daily_reports (vessel_id, report_date, user_id);"))
        
        print("Database migration completed successfully.")

if __name__ == "__main__":
    run_migration()
