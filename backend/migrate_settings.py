import sqlite3
import os

DB_FILE = "data/sagarr.db"

def migrate():
    if not os.path.exists(DB_FILE):
        print(f"Database file {DB_FILE} not found. Skipping migration (will be created on startup).")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "settings" not in columns:
            print("Adding 'settings' column to 'users' table...")
            cursor.execute("ALTER TABLE users ADD COLUMN settings TEXT DEFAULT '{}'")
            conn.commit()
            print("Migration successful.")
        else:
            print("'settings' column already exists.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
