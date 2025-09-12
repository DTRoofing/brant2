import psycopg2
from datetime import datetime

# Connect to database
conn = psycopg2.connect('postgresql://ADMIN:Brant01!@34.63.109.196:5432/postgres?sslmode=require')
cur = conn.cursor()

# Get recent documents
cur.execute("""
    SELECT id, filename, processing_status, created_at 
    FROM documents 
    ORDER BY created_at DESC 
    LIMIT 10
""")

print("Recent documents in database:")
print("-" * 80)
for row in cur.fetchall():
    doc_id, filename, status, created = row
    print(f"ID: {doc_id}")
    print(f"File: {filename}")
    print(f"Status: {status}")
    print(f"Created: {created}")
    print("-" * 40)

cur.close()
conn.close()