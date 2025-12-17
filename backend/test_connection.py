from database import db, supabase
from auth import hash_password
import uuid

print("🔌 Testing Supabase connection...")
print()

try:
    # Test 1: Create test user
    print("⏳ Creating test user...")
    test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    user = db.create_user(test_email, hash_password("test123"))
    print(f"✅ Created user: {user['email']}")
    user_id = user['id']
    
    # Test 2: Find user
    print("⏳ Finding user...")
    found = db.get_user_by_email(test_email)
    print(f"✅ Found user: {found['email']}")
    
    # Test 3: Create server
    print("⏳ Creating server...")
    server = db.create_server(user_id, "Test Server", "192.168.1.1", "test_key")
    print(f"✅ Created server: {server['name']}")
    server_id = server['id']
    
    # Test 4: Insert metrics
    print("⏳ Inserting metrics...")
    metrics = db.insert_metrics(server_id, {
        "cpu_percent": 45.5,
        "ram_percent": 67.8,
        "disk_read": 1000000,
        "disk_write": 500000,
        "net_sent": 2000000,
        "net_recv": 3000000
    })
    print(f"✅ Inserted metrics")
    
    # Test 5: Get metrics
    print("⏳ Retrieving metrics...")
    retrieved = db.get_metrics(server_id)
    print(f"✅ Retrieved {len(retrieved)} metric(s)")
    
    # Test 6: Clean up
    print("⏳ Cleaning up...")
    db.delete_server(server_id)
    supabase.table("users").delete().eq("id", user_id).execute()
    print("✅ Cleaned up test data")
    
    print("\n🎉 SUCCESS! Supabase is working perfectly!")
    print("✅ All database operations tested")
    print("✅ No firewall issues!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\n🔍 Check:")
    print("1. SUPABASE_URL and SUPABASE_KEY in .env")
    print("2. Tables created in SQL Editor")
    print("3. Internet connection active")