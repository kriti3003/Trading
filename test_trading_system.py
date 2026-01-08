"""
Test Client for Trading System API
Start app.py first, then run:
python test_client.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api/v1"
TIMEOUT = 5

# UTILITIES

def divider(title=""):
    print("\n" + "=" * 70)
    if title:
        print(f"TEST: {title}")
        print("=" * 70)

def pretty_print(response):
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except ValueError:
        print("Invalid JSON response")

def api_request(method, endpoint, payload=None):
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.request(
            method=method,
            url=url,
            json=payload,
            timeout=TIMEOUT
        )
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


# ======================================================
# TEST CASES
# ======================================================

def test_health():
    divider("Health Check")
    response = api_request("GET", "/health")
    if response:
        pretty_print(response)
        return response.status_code == 200
    return False


def test_get_instruments():
    divider("Fetch Instruments")
    response = api_request("GET", "/instruments")
    if response:
        pretty_print(response)


def test_place_order(symbol, order_type, style, quantity, price=None):
    payload = {
        "symbol": symbol,
        "orderType": order_type,
        "orderStyle": style,
        "quantity": quantity
    }
    if price is not None:
        payload["price"] = price

    divider(f"Place {order_type} Order ({style}) - {symbol}")
    response = api_request("POST", "/orders", payload)
    if response:
        pretty_print(response)
        if response.status_code == 201:
            return response.json()["data"]["order"]["orderId"]
    return None


def test_invalid_order():
    divider("Invalid Order - Negative Quantity")
    payload = {
        "symbol": "AAPL",
        "orderType": "BUY",
        "orderStyle": "MARKET",
        "quantity": -10
    }
    response = api_request("POST", "/orders", payload)
    if response:
        pretty_print(response)


def test_limit_without_price():
    divider("Invalid Order - LIMIT without Price")
    payload = {
        "symbol": "AAPL",
        "orderType": "BUY",
        "orderStyle": "LIMIT",
        "quantity": 5
    }
    response = api_request("POST", "/orders", payload)
    if response:
        pretty_print(response)


def test_order_status(order_id):
    divider(f"Order Status (ID: {order_id})")
    response = api_request("GET", f"/orders/{order_id}")
    if response:
        pretty_print(response)


def test_all_orders():
    divider("Fetch All Orders")
    response = api_request("GET", "/orders")
    if response:
        pretty_print(response)


def test_trades():
    divider("Fetch Trades")
    response = api_request("GET", "/trades")
    if response:
        pretty_print(response)


def test_portfolio():
    divider("Fetch Portfolio")
    response = api_request("GET", "/portfolio")
    if response:
        pretty_print(response)


# ======================================================
# TEST RUNNER
# ======================================================

def run_tests():
    print("\n" + "#" * 70)
    print("#" + " " * 22 + "TRADING SYSTEM API TEST SUITE" + " " * 21 + "#")
    print("#" * 70)

    if not test_health():
        print("\n❌ Server is not running. Start app.py first.")
        return

    time.sleep(0.4)

    test_get_instruments()
    time.sleep(0.4)

    # BUY Orders
    buy_order_id = test_place_order("AAPL", "BUY", "MARKET", 10)
    time.sleep(0.4)

    limit_order_id = test_place_order("GOOGL", "BUY", "LIMIT", 5, price=140.00)
    time.sleep(0.4)

    # Additional buys
    print("\n--- Adding Portfolio Diversity ---")
    for symbol in ["MSFT", "TSLA"]:
        test_place_order(symbol, "BUY", "MARKET", 3)
        time.sleep(0.3)

    # SELL Order
    sell_order_id = test_place_order("AAPL", "SELL", "MARKET", 5)
    time.sleep(0.4)

    # Validation tests
    test_invalid_order()
    time.sleep(0.4)

    test_limit_without_price()
    time.sleep(0.4)

    # Fetch data
    if buy_order_id:
        test_order_status(buy_order_id)

    test_all_orders()
    test_trades()
    test_portfolio()

    print("\n" + "#" * 70)
    print("#" + " " * 27 + "ALL TESTS COMPLETED" + " " * 27 + "#")
    print("#" * 70)


if __name__ == "__main__":
    run_tests()
