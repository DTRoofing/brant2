#!/usr/bin/env python3
"""Test remote database connection"""

import os
import sys
from urllib.parse import urlparse, parse_qs

def test_connection():
    # Test with the exact DATABASE_URL from environment
    database_url = "postgresql://ADMIN:Brant01!@34.63.109.196:5432/postgres?schema=public"
    
    print(f"🔍 Testing connection to remote PostgreSQL database")
    print(f"📍 Host: 34.63.109.196:5432")
    print(f"📁 Database: postgres")
    print(f"👤 User: ADMIN")
    
    # Parse URL to extract schema if present
    parsed = urlparse(database_url)
    query_params = parse_qs(parsed.query)
    schema = query_params.get('schema', ['public'])[0]
    print(f"📋 Schema: {schema}")
    
    # Remove schema from URL for connection (add it back later if needed)
    base_url = database_url.split('?')[0]
    
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.exc import OperationalError
        
        print("\n🔄 Attempting connection...")
        
        # Try connection without schema parameter first
        engine = create_engine(base_url)
        
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            print("✅ Basic connection successful!")
            
            # Get PostgreSQL version
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"📊 PostgreSQL version: {version}")
            
            # Get current database and user
            result = conn.execute(text("SELECT current_database(), current_user"))
            db, user = result.fetchone()
            print(f"📁 Connected to database: {db}")
            print(f"👤 Connected as user: {user}")
            
            # Check if schema exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.schemata 
                    WHERE schema_name = :schema
                )
            """), {"schema": schema})
            schema_exists = result.scalar()
            
            if schema_exists:
                print(f"✅ Schema '{schema}' exists")
                
                # Set search path to the schema
                conn.execute(text(f"SET search_path TO {schema}"))
                print(f"📋 Set search_path to '{schema}'")
                
                # Count tables in the schema
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = :schema
                """), {"schema": schema})
                table_count = result.scalar()
                print(f"📊 Tables in '{schema}' schema: {table_count}")
                
                if table_count > 0:
                    # List some tables
                    result = conn.execute(text("""
                        SELECT table_name FROM information_schema.tables 
                        WHERE table_schema = :schema 
                        ORDER BY table_name LIMIT 5
                    """), {"schema": schema})
                    tables = result.fetchall()
                    print(f"\n📋 Sample tables:")
                    for table in tables:
                        print(f"   - {table[0]}")
            else:
                print(f"⚠️  Schema '{schema}' does not exist")
                
                # List available schemas
                result = conn.execute(text("""
                    SELECT schema_name FROM information_schema.schemata 
                    WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
                    ORDER BY schema_name
                """))
                schemas = result.fetchall()
                print(f"\n📂 Available schemas:")
                for s in schemas:
                    print(f"   - {s[0]}")
            
            print("\n✅ Connection test completed successfully!")
            return True
            
    except OperationalError as e:
        error_msg = str(e)
        print(f"\n❌ Connection failed: {error_msg}")
        
        if "password authentication failed" in error_msg.lower():
            print("\n⚠️  AUTHENTICATION ERROR DETECTED!")
            print("The credentials appear to be incorrect.")
            print("Please verify and update the following:")
            print(f"  - Username: ADMIN")
            print(f"  - Password: Brant01!")
            print(f"  - Host: 34.63.109.196")
            print(f"  - Port: 5432")
            print(f"  - Database: postgres")
            return "CREDENTIALS_ERROR"
        
        return False
        
    except ImportError:
        print("❌ SQLAlchemy not installed. Running inside Docker container is recommended.")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    result = test_connection()
    
    if result == "CREDENTIALS_ERROR":
        print("\n🔑 Please update the DATABASE_URL in your .env file with the correct credentials.")
        sys.exit(2)
    elif not result:
        print("\n💡 Troubleshooting tips:")
        print("   1. Ensure the database server allows connections from your IP")
        print("   2. Check if there's a firewall blocking the connection")
        print("   3. Verify the database service is running on the server")
        sys.exit(1)
    
    sys.exit(0)