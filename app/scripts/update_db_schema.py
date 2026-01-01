import os
import sys
from sqlalchemy import create_engine, text

# Add parent dir to path to import app modules if needed, 
# but here we just need the DB URL.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings

def update_schema():
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        conn.begin()
        try:
            # Add installation_id
            print("Adding installation_id column...")
            conn.execute(text("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS installation_id BIGINT;"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_organizations_installation_id ON organizations (installation_id);"))
            
            # Add slack_webhook_url
            print("Adding slack_webhook_url column...")
            conn.execute(text("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS slack_webhook_url VARCHAR;"))
            
            # Add teams_webhook_url
            print("Adding teams_webhook_url column...")
            conn.execute(text("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS teams_webhook_url VARCHAR;"))
            
            # Add alert_threshold_minutes
            print("Adding alert_threshold_minutes column...")
            conn.execute(text("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS alert_threshold_minutes INTEGER DEFAULT 10;"))
            
            # Add advanced alert type settings
            print("Adding advanced alert type columns...")
            conn.execute(text("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS alert_on_delayed BOOLEAN DEFAULT TRUE;"))
            conn.execute(text("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS alert_on_stuck BOOLEAN DEFAULT TRUE;"))
            conn.execute(text("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS alert_on_anomaly BOOLEAN DEFAULT TRUE;"))
            conn.execute(text("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS stuck_threshold_multiplier FLOAT DEFAULT 2.0;"))
            conn.execute(text("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS anomaly_threshold_stddev FLOAT DEFAULT 2.0;"))
            
            conn.commit()
            print("Schema updated successfully!")
        except Exception as e:
            print(f"Error updating schema: {e}")
            conn.rollback()

if __name__ == "__main__":
    update_schema()
