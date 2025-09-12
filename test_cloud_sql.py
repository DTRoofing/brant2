#!/usr/bin/env python3
"""Test Google Cloud SQL connection with SSL"""

import os
import sys

def test_connection():
    # Test with SSL required
    database_url = "postgresql://ADMIN:Brant01!@34.63.109.196:5432/postgres?sslmode=require"
    
    print(f"🔍 Testing Google Cloud SQL connection")
    print(f"📍 Host: 34.63.109.196:5432")
    print(f"📁 Database: postgres")
    print(f"👤 User: ADMIN")
    print(f"🔒 SSL Mode: require")
    
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.exc import OperationalError
        
        print("\n🔄 Attempting connection with SSL...")
        
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            print("✅ Connection successful!")
            
            # Get PostgreSQL version
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"📊 PostgreSQL version: {version}")
            
            # Check current IP
            result = conn.execute(text("SELECT inet_client_addr()"))
            client_ip = result.scalar()
            print(f"🌐 Your IP as seen by database: {client_ip}")
            
            # List databases
            result = conn.execute(text("""
                SELECT datname FROM pg_database 
                WHERE datistemplate = false 
                ORDER BY datname
            """))
            databases = result.fetchall()
            print(f"\n📁 Available databases:")
            for db in databases:
                print(f"   - {db[0]}")
            
            print("\n✅ Connection test completed successfully!")
            return True
            
    except OperationalError as e:
        error_msg = str(e)
        print(f"\n❌ Connection failed: {error_msg}")
        
        if "no pg_hba.conf entry" in error_msg.lower():
            print("\n⚠️  AUTHORIZATION ERROR!")
            print("Your IP address is not authorized to connect to this Cloud SQL instance.")
            print("You need to add your IP to the authorized networks in Google Cloud Console.")
            return "NEEDS_IP_WHITELIST"
        
        elif "password authentication failed" in error_msg.lower():
            print("\n⚠️  AUTHENTICATION ERROR!")
            print("The credentials appear to be incorrect.")
            return "CREDENTIALS_ERROR"
        
        elif "SSL connection is required" in error_msg.lower():
            print("\n⚠️  SSL REQUIRED!")
            print("The server requires SSL connections.")
            return "SSL_REQUIRED"
        
        return False
        
    except ImportError:
        print("❌ SQLAlchemy not installed")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    result = test_connection()
    
    if result == "NEEDS_IP_WHITELIST":
        print("\n🔧 To fix this:")
        print("1. Get your current IP address")
        print("2. Go to Google Cloud Console > SQL > Your instance")
        print("3. Click 'Edit' > 'Connections' > 'Authorized networks'")
        print("4. Add your IP address")
        print("\nTo get your current IP, run: curl -s ifconfig.me")
        sys.exit(3)
    elif result == "CREDENTIALS_ERROR":
        print("\n🔑 Please verify the credentials are correct.")
        sys.exit(2)
    elif not result:
        sys.exit(1)
    
    sys.exit(0)