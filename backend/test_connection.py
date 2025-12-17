from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

print("🔌 Testing MongoDB Atlas connection...")
print(f"📍 Connection string: {os.getenv('MONGODB_URL')[:50]}...")

try:
    # Connect
    client = MongoClient(os.getenv("MONGODB_URL"))
    
    # Test connection by listing databases
    db = client.smartops
    
    # Try to insert a test document
    test_collection = db.test
    result = test_collection.insert_one({
        "test": "Hello from Smart OPS!",
        "status": "connected"
    })
    
    print("✅ SUCCESS! Connected to MongoDB Atlas")
    print(f"✅ Inserted test document with ID: {result.inserted_id}")
    
    # Read it back
    doc = test_collection.find_one({"_id": result.inserted_id})
    print(f"✅ Retrieved document: {doc}")
    
    # Clean up
    test_collection.delete_one({"_id": result.inserted_id})
    print("✅ Cleaned up test data")
    
    print("\n🎉 Your MongoDB Atlas is ready to use!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\n🔍 Common fixes:")
    print("1. Check your password in .env (no < > symbols)")
    print("2. Make sure IP is whitelisted (0.0.0.0/0)")
    print("3. Wait 1-2 minutes after changing network settings")