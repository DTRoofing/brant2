#!/usr/bin/env python3
"""Quick database connection test"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def test_connection():
    database_url = "postgresql://ADMIN:Brant01!@34.63.109.196:5432/postgres?sslmode=require"
    
    print("Testing Google Cloud SQL connection")
    print(f"Host: 34.63.109.196:5432")
    print(f"Database: postgres")
    print(f"User: ADMIN")
    print(f"SSL Mode: require")
    
    try:
        print("\nAttempting connection with SSL...")
        
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            print("Connection successful!")
            
            # Get PostgreSQL version
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"PostgreSQL version: {version}")
            
            # Check current IP
            result = conn.execute(text("SELECT inet_client_addr()"))
            client_ip = result.scalar()
            print(f"Your IP as seen by database: {client_ip}")
            
            # List databases
            result = conn.execute(text("""
                SELECT datname FROM pg_database 
                WHERE datistemplate = false 
                ORDER BY datname
            """))
            databases = result.fetchall()
            print(f"\nAvailable databases:")
            for db in databases:
                print(f"   - {db[0]}")
            
            # Check tables in public schema
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = result.fetchall()
            print(f"\nTables in public schema:")
            if tables:
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("   (no tables found)")
            
            print("\nConnection test completed successfully!")
            return True
            
    except OperationalError as e:
        error_msg = str(e)
        print(f"\nConnection failed: {error_msg}")
        
        if "no pg_hba.conf entry" in error_msg.lower():
            print("\nAUTHORIZATION ERROR!")
            print("Your IP address is not authorized to connect to this Cloud SQL instance.")
            print("You need to add your IP to the authorized networks in Google Cloud Console.")
            print("\nTo get your current IP, run: curl -s ifconfig.me")
            return False
        
        elif "password authentication failed" in error_msg.lower():
            print("\nAUTHENTICATION ERROR!")
            print("The credentials appear to be incorrect.")
            return False
        
        elif "SSL connection is required" in error_msg.lower():
            print("\nSSL REQUIRED!")
            print("The server requires SSL connections.")
            return False
        
        return False
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure SQLAlchemy is installed: pip install sqlalchemy psycopg2-binary")
        return False
        
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1)