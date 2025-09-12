#!/usr/bin/env python3
"""Check database schema configuration"""

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def check_schema():
    database_url = "postgresql://ADMIN:Brant01!@34.63.109.196:5432/postgres?sslmode=require"
    
    print("Checking database schema configuration...")
    print("-" * 50)
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check current database
            result = conn.execute(text("SELECT current_database()"))
            current_db = result.scalar()
            print(f"Connected to database: {current_db}")
            
            # Check all schemas
            result = conn.execute(text("""
                SELECT schema_name 
                FROM information_schema.schemata 
                ORDER BY schema_name
            """))
            schemas = result.fetchall()
            print(f"\nAvailable schemas:")
            for schema in schemas:
                print(f"  - {schema[0]}")
            
            # Check current search path
            result = conn.execute(text("SHOW search_path"))
            search_path = result.scalar()
            print(f"\nCurrent search_path: {search_path}")
            
            # Check if public schema exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.schemata 
                    WHERE schema_name = 'public'
                )
            """))
            public_exists = result.scalar()
            print(f"\nPublic schema exists: {public_exists}")
            
            if public_exists:
                # Check tables in public schema
                result = conn.execute(text("""
                    SELECT table_name, table_type
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """))
                tables = result.fetchall()
                
                print(f"\nTables in 'public' schema: {len(tables)}")
                if tables:
                    for table in tables:
                        print(f"  - {table[0]} ({table[1]})")
                else:
                    print("  (No tables found)")
                
                # Check if we need specific tables for the application
                expected_tables = [
                    'uploads', 'documents', 'processing_results', 
                    'users', 'sessions', 'api_keys'
                ]
                
                existing_tables = [t[0] for t in tables]
                missing_tables = [t for t in expected_tables if t not in existing_tables]
                
                if missing_tables:
                    print(f"\nMissing expected tables:")
                    for table in missing_tables:
                        print(f"  - {table}")
            
            # Check permissions for ADMIN user
            print(f"\nChecking permissions for ADMIN user...")
            result = conn.execute(text("""
                SELECT has_schema_privilege('ADMIN', 'public', 'CREATE')
            """))
            can_create = result.scalar()
            print(f"  Can create objects in public schema: {can_create}")
            
            result = conn.execute(text("""
                SELECT has_schema_privilege('ADMIN', 'public', 'USAGE')
            """))
            can_use = result.scalar()
            print(f"  Can use public schema: {can_use}")
            
            # Try to create a test table to verify write permissions
            print(f"\nTesting write permissions...")
            try:
                conn.execute(text("CREATE TABLE IF NOT EXISTS test_permissions (id INT)"))
                conn.execute(text("DROP TABLE IF EXISTS test_permissions"))
                print("  Write permissions: OK")
            except Exception as e:
                print(f"  Write permissions: FAILED - {e}")
                
            print("\n" + "=" * 50)
            print("Schema check completed!")
            
            return True
            
    except OperationalError as e:
        print(f"\nConnection failed: {e}")
        return False
        
    except Exception as e:
        print(f"\nUnexpected error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = check_schema()
    exit(0 if success else 1)