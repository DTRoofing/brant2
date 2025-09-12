#!/usr/bin/env python3
"""Test database connection using credentials from .env file"""

import os
import sys
from urllib.parse import urlparse
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test PostgreSQL database connection"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print(f"📍 Testing connection to: {database_url.split('@')[1] if '@' in database_url else 'Unknown'}")
    
    try:
        # Parse the connection string
        parsed = urlparse(database_url)
        
        # Extract connection parameters
        connection_params = {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path[1:].split('?')[0] if parsed.path else 'postgres',
            'user': parsed.username,
            'password': parsed.password
        }
        
        # Handle schema parameter if present
        if '?' in database_url and 'schema=' in database_url:
            schema = database_url.split('schema=')[1].split('&')[0]
            print(f"📋 Using schema: {schema}")
        
        # Connect to the database
        print("🔄 Connecting to PostgreSQL...")
        conn = psycopg2.connect(**connection_params)
        conn.set_session(autocommit=True)
        cursor = conn.cursor()
        
        # Test the connection
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]
        print(f"✅ Successfully connected to PostgreSQL!")
        print(f"📊 Database version: {db_version}")
        
        # Get current database info
        cursor.execute("SELECT current_database(), current_user, inet_server_addr(), inet_server_port();")
        db_info = cursor.fetchone()
        print(f"📁 Database: {db_info[0]}")
        print(f"👤 User: {db_info[1]}")
        print(f"🌐 Server: {db_info[2]}:{db_info[3]}")
        
        # List available schemas
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            ORDER BY schema_name;
        """)
        schemas = cursor.fetchall()
        print(f"\n📂 Available schemas:")
        for schema in schemas:
            print(f"   - {schema[0]}")
        
        # Check if we can access the public schema
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        table_count = cursor.fetchone()[0]
        print(f"\n📊 Tables in 'public' schema: {table_count}")
        
        # Close the connection
        cursor.close()
        conn.close()
        print("\n✅ Database connection test completed successfully!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
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
        sys.exit(1)
    
    sys.exit(0)