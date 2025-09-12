#!/usr/bin/env python3
"""Simple database connection test using SQLAlchemy from the existing project"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Load environment variables
load_dotenv()

def test_connection():
    """Test PostgreSQL database connection using SQLAlchemy"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    # Mask password in output
    display_url = database_url.split('@')[1] if '@' in database_url else 'Unknown'
    print(f"📍 Testing connection to: {display_url}")
    
    try:
        # Create engine
        print("🔄 Creating database engine...")
        engine = create_engine(database_url)
        
        # Test connection
        print("🔄 Testing connection...")
        with engine.connect() as conn:
            # Get PostgreSQL version
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Successfully connected to PostgreSQL!")
            print(f"📊 Database version: {version}")
            
            # Get current database info
            result = conn.execute(text("""
                SELECT current_database() as db, 
                       current_user as user,
                       inet_server_addr() as host,
                       inet_server_port() as port
            """))
            info = result.fetchone()
            print(f"📁 Database: {info.db}")
            print(f"👤 User: {info.user}")
            print(f"🌐 Server: {info.host}:{info.port}")
            
            # List schemas
            result = conn.execute(text("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
                ORDER BY schema_name
            """))
            schemas = result.fetchall()
            print(f"\n📂 Available schemas:")
            for schema in schemas:
                print(f"   - {schema[0]}")
            
            # Count tables in public schema
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            table_count = result.scalar()
            print(f"\n📊 Tables in 'public' schema: {table_count}")
            
            # List tables if any exist
            if table_count > 0:
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name
                    LIMIT 10
                """))
                tables = result.fetchall()
                print(f"\n📋 First 10 tables in 'public' schema:")
                for table in tables:
                    print(f"   - {table[0]}")
        
        print("\n✅ Database connection test completed successfully!")
        return True
        
    except OperationalError as e:
        print(f"❌ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 PostgreSQL Database Connection Test")
    print("=" * 50)
    
    success = test_connection()
    
    if not success:
        print("\n💡 Troubleshooting tips:")
        print("   1. Check if the DATABASE_URL is correct in .env file")
        print("   2. Ensure the database server is accessible from your network")
        print("   3. Verify the username and password are correct")
        print("   4. Check if the database exists and user has proper permissions")
        print("   5. Ensure PostgreSQL is configured to accept connections from your IP")
        sys.exit(1)
    
    sys.exit(0)