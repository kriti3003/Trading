"""
Test client for Trading System API
Run the main app.py first, then run this script to test all endpoints
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:5000/api/v1"

def print_response(title, response):
    """Pretty print API response"""
    print("\n" + "=" * 60)
    print(f"TEST: {title}")
    print("=" * 60)
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))

def test_health():
    """Test health check"""
    response = requests.get(f"{BASE_URL}/health")
    print_response("Health Check", response)
    return response.status_code == 200

def test_get_instruments():
    """Test fetching instruments"""
    response = requests.get(f"{BASE_URL}/instruments")
    print_response("Get All Instruments", response)
    return response.status_code == 200

def test_place_buy_order():
    """Test placing a buy order"""
    order_data = {
        "symbol": "AAPL",
        "orderType": "BUY",
        "orderStyle": "MARKET",
        "quantity": 10
    }
    response = requests.post(f"{BASE_URL}/orders", json=order_data)
    print_response("Place BUY Order (MARKET)", response)
    
    if response.status_code == 201:
        return response.json()["data"]["order"]["orderId"]
    return None

def test_place_limit_order():
    """Test placing a limit order"""
    order_data = {
        "symbol": "GOOGL",
        "orderType": "BUY",
        "orderStyle": "LIMIT",
        "quantity": 5,
        "price": 140.00
    }
    response = requests.post(f"{BASE_URL}/orders", json=order_data)
    print_response("Place BUY Order (LIMIT)", response)
    
    if response.status_code == 201:
        return response.json()["data"]["order"]["orderId"]
    return None

def test_place_sell_order():
    """Test placing a sell order"""
    order_data = {
        "symbol": "AAPL",
        "orderType": "SELL",
        "orderStyle": "MARKET",
        "quantity": 5
    }
    response = requests.post(f"{BASE_URL}/orders", json=order_data)
    print_response("Place SELL Order (MARKET)", response)
    
    if response.status_code == 201:
        return response.json()["data"]["order"]["orderId"]
    return None

def test_invalid_order():
    """Test validation - invalid order"""
    order_data = {
        "symbol": "AAPL",
        "orderType": "BUY",
        "orderStyle": "MARKET",
        "quantity": -5  # Invalid: negative quantity
    }
    response = requests.post(f"{BASE_URL}/orders", json=order_data)
    print_response("Invalid Order (Negative Quantity)", response)

def test_limit_order_without_price():
    """Test validation - limit order without price"""
    order_data = {
        "symbol": "AAPL",
        "orderType": "BUY",
        "orderStyle": "LIMIT",
        "quantity": 10
        # Missing price
    }
    response = requests.post(f"{BASE_URL}/orders", json=order_data)
    print_response("Invalid Order (LIMIT without price)", response)

def test_get_order_status(order_id):
    """Test fetching order status"""
    response = requests.get(f"{BASE_URL}/orders/{order_id}")
    print_response(f"Get Order Status (ID: {order_id})", response)

def test_get_all_orders():
    """Test fetching all orders"""
    response = requests.get(f"{BASE_URL}/orders")
    print_response("Get All Orders", response)

def test_get_trades():
    """Test fetching trades"""
    response = requests.get(f"{BASE_URL}/trades")
    print_response("Get All Trades", response)

def test_get_portfolio():
    """Test fetching portfolio"""
    response = requests.get(f"{BASE_URL}/portfolio")
    print_response("Get Portfolio", response)

def run_all_tests():
    """Run all test cases"""
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + " " * 15 + "TRADING SYSTEM API TESTS" + " " * 19 + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)
    
    try:
        # 1. Health check
        if not test_health():
            print("\n❌ Server is not running. Please start app.py first!")
            return
        
        sleep(0.5)
        
        # 2. Get instruments
        test_get_instruments()
        sleep(0.5)
        
        # 3. Place multiple buy orders
        order_id_1 = test_place_buy_order()
        sleep(0.5)
        
        order_id_2 = test_place_limit_order()
        sleep(0.5)
        
        # Buy more stocks for testing
        print("\n--- Buying more stocks for portfolio diversity ---")
        for symbol in ["MSFT", "TSLA"]:
            order_data = {
                "symbol": symbol,
                "orderType": "BUY",
                "orderStyle": "MARKET",
                "quantity": 3
            }
            response = requests.post(f"{BASE_URL}/orders", json=order_data)
            print(f"Bought {symbol}: {response.status_code}")
            sleep(0.3)
        
        # 4. Place sell order
        order_id_3 = test_place_sell_order()
        sleep(0.5)
        
        # 5. Test validation
        test_invalid_order()
        sleep(0.5)
        
        test_limit_order_without_price()
        sleep(0.5)
        
        # 6. Get order status
        if order_id_1:
            test_get_order_status(order_id_1)
            sleep(0.5)
        
        # 7. Get all orders
        test_get_all_orders()
        sleep(0.5)
        
        # 8. Get all trades
        test_get_trades()
        sleep(0.5)
        
        # 9. Get portfolio
        test_get_portfolio()
        
        print("\n" + "#" * 60)
        print("#" + " " * 58 + "#")
        print("#" + " " * 20 + "TESTS COMPLETED" + " " * 23 + "#")
        print("#" + " " * 58 + "#")
        print("#" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to the server!")
        print("Please make sure app.py is running on http://localhost:5000")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    run_all_tests()