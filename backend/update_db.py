#!/usr/bin/env python3
"""
Script to update the database schema to add the favorited column
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def update_database():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("No DATABASE_URL found. Using SQLite for development.")
        DATABASE_URL = "sqlite:///./litflix.db"
    
    try:
        engine = create_engine(DATABASE_URL, echo=True)
        
        with engine.connect() as conn:
            # Check if favorited column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'saved_items' 
                AND column_name = 'favorited'
            """))
            
            if not result.fetchone():
                print("Adding favorited column to saved_items table...")
                conn.execute(text("ALTER TABLE saved_items ADD COLUMN favorited BOOLEAN DEFAULT FALSE"))
                conn.commit()
                print("✅ favorited column added successfully!")
            else:
                print("✅ favorited column already exists!")
                
    except Exception as e:
        print(f"❌ Error updating database: {e}")
        # For SQLite, try a different approach
        if "sqlite" in DATABASE_URL.lower():
            try:
                engine = create_engine(DATABASE_URL, echo=True)
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE saved_items ADD COLUMN favorited BOOLEAN DEFAULT 0"))
                    conn.commit()
                    print("✅ favorited column added to SQLite database!")
            except Exception as sqlite_error:
                print(f"❌ SQLite update failed: {sqlite_error}")

if __name__ == "__main__":
    update_database() 