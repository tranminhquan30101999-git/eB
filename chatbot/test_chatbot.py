import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8080/api/v1"

def test_chat():
    """Test the chatbot with various scenarios"""
    
    # Conversation ID to maintain context
    conversation_id = None
    
    # Test scenarios
    test_messages = [
        "Xin chào, tôi muốn biết các dịch vụ của tiệm",
        "Tôi muốn đặt lịch làm móng gel",
        "Ngày mai có lịch trống không?",
        "Tôi muốn đặt vào 10 giờ sáng",
        "Tên tôi là Nguyễn Văn A, số điện thoại 0901234567"
    ]
    
    print("=== Testing Nail Salon Chatbot ===\n")
    
    for message in test_messages:
        print(f"User: {message}")
        
        # Prepare request
        payload = {
            "message": message,
            "conversation_id": conversation_id
        }
        
        try:
            # Send request
            response = requests.post(f"{BASE_URL}/chat", json=payload)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            conversation_id = data["conversation_id"]
            
            print(f"Bot: {data['response']}")
            print("-" * 50)
            
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            break
        
        # Wait for user input to continue (optional)
        input("Press Enter to continue...")

def test_admin_endpoints():
    """Test admin endpoints"""
    print("\n=== Testing Admin Endpoints ===\n")
    
    # Test getting services
    try:
        response = requests.get(f"{BASE_URL}/admin/services")
        response.raise_for_status()
        services = response.json()
        
        print("Available Services:")
        for service in services:
            print(f"- {service['name']}: {service['price']:,.0f} VND ({service['duration_minutes']} phút)")
        
    except requests.exceptions.RequestException as e:
        print(f"Error getting services: {e}")
    
    print("\n")
    
    # Test getting time slots
    from datetime import date, timedelta
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    try:
        response = requests.get(f"{BASE_URL}/admin/timeslots/{tomorrow}")
        response.raise_for_status()
        slots = response.json()
        
        print(f"Available slots for {tomorrow}:")
        for slot in slots[:5]:  # Show first 5 slots
            print(f"- {slot['start_time']} - {slot['end_time']}")
        
        if len(slots) > 5:
            print(f"... and {len(slots) - 5} more slots")
            
    except requests.exceptions.RequestException as e:
        print(f"Error getting time slots: {e}")

if __name__ == "__main__":
    print("Make sure the API is running at http://localhost:8080")
    print("You can start it with: python run.py\n")
    
    choice = input("Test chat (1) or admin endpoints (2)? Enter 1 or 2: ")
    
    if choice == "1":
        test_chat()
    elif choice == "2":
        test_admin_endpoints()
    else:
        print("Invalid choice. Running both tests...")
        test_chat()
        test_admin_endpoints()