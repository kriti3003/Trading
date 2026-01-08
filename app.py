"""
Trading System Backend - Simplified Stock Trading Platform
Run with: python app.py
"""

from flask import Flask, request, jsonify
from datetime import datetime
from enum import Enum
import uuid

app = Flask(__name__)

# ENUMS

class OrderType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStyle(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"

class OrderStatus(str, Enum):
    NEW = "NEW"
    PLACED = "PLACED"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"


# IN-MEMORY DATA

INSTRUMENTS = [
    {"symbol": "RELIANCE", "exchange": "NSE", "instrumentType": "STOCK", "lastTradedPrice": 175.50},
    {"symbol": "TCS", "exchange": "NSE", "instrumentType": "STOCK", "lastTradedPrice": 140.25},
    {"symbol": "LT", "exchange": "NSE", "instrumentType": "STOCK", "lastTradedPrice": 380.00},
    {"symbol": "BAJFINANCE", "exchange": "NSE", "instrumentType": "STOCK", "lastTradedPrice": 245.75},
    {"symbol": "HINDUNILVR", "exchange": "NSE", "instrumentType": "STOCK", "lastTradedPrice": 155.30},
]

ORDERS = {}
TRADES = []
PORTFOLIO = {}


# ======================================================
# HELPERS
# ======================================================

def now():
    return datetime.now().isoformat()

def get_instrument(symbol):
    return next((i for i in INSTRUMENTS if i["symbol"] == symbol), None)

def error_response(errors, status=400):
    return jsonify({"success": False, "errors": errors}), status

def success_response(data, status=200, message=None):
    payload = {"success": True, "data": data}
    if message:
        payload["message"] = message
    return jsonify(payload), status


# ======================================================
# VALIDATION
# ======================================================

def validate_order(data):
    errors = []

    required = ["symbol", "orderType", "orderStyle", "quantity"]
    for field in required:
        if field not in data:
            errors.append(f"Missing field: {field}")

    if errors:
        return errors

    if data["quantity"] <= 0:
        errors.append("Quantity must be greater than zero")

    if data["orderType"] not in OrderType.__members__:
        errors.append("Invalid orderType")

    if data["orderStyle"] not in OrderStyle.__members__:
        errors.append("Invalid orderStyle")

    if data["orderStyle"] == OrderStyle.LIMIT and "price" not in data:
        errors.append("Price required for LIMIT order")

    instrument = get_instrument(data["symbol"])
    if not instrument:
        errors.append("Instrument not found")

    if data["orderType"] == OrderType.SELL:
        holding = PORTFOLIO.get(data["symbol"])
        if not holding or holding["quantity"] < data["quantity"]:
            errors.append("Insufficient holdings to sell")

    return errors


# ======================================================
# CORE LOGIC
# ======================================================

def execute_order(order):
    instrument = get_instrument(order["symbol"])

    execution_price = (
        instrument["lastTradedPrice"]
        if order["orderStyle"] == OrderStyle.MARKET
        else order["price"]
    )

    order.update({
        "status": OrderStatus.EXECUTED,
        "executedAt": now(),
        "executionPrice": execution_price
    })

    trade = {
        "tradeId": str(uuid.uuid4()),
        "orderId": order["orderId"],
        "symbol": order["symbol"],
        "orderType": order["orderType"],
        "quantity": order["quantity"],
        "price": execution_price,
        "totalValue": execution_price * order["quantity"],
        "executedAt": order["executedAt"]
    }

    TRADES.append(trade)
    update_portfolio(order, execution_price)

    return trade


def update_portfolio(order, price):
    symbol = order["symbol"]
    qty = order["quantity"]

    if symbol not in PORTFOLIO:
        PORTFOLIO[symbol] = {
            "symbol": symbol,
            "quantity": 0,
            "averagePrice": 0,
            "totalInvested": 0
        }

    holding = PORTFOLIO[symbol]

    if order["orderType"] == OrderType.BUY:
        total_cost = holding["totalInvested"] + qty * price
        total_qty = holding["quantity"] + qty

        holding["quantity"] = total_qty
        holding["totalInvested"] = total_cost
        holding["averagePrice"] = total_cost / total_qty

    else:  # SELL
        holding["quantity"] -= qty
        if holding["quantity"] == 0:
            del PORTFOLIO[symbol]
        else:
            holding["totalInvested"] = holding["quantity"] * holding["averagePrice"]


# ======================================================
# ROUTES
# ======================================================

@app.route("/api/v1/instruments", methods=["GET"])
def instruments():
    return success_response(INSTRUMENTS)

@app.route("/api/v1/orders", methods=["POST"])
def place_order():
    data = request.get_json()
    errors = validate_order(data)

    if errors:
        return error_response(errors)

    order_id = str(uuid.uuid4())
    order = {
        "orderId": order_id,
        "symbol": data["symbol"],
        "orderType": OrderType[data["orderType"]],
        "orderStyle": OrderStyle[data["orderStyle"]],
        "quantity": data["quantity"],
        "price": data.get("price"),
        "status": OrderStatus.PLACED,
        "createdAt": now(),
        "executedAt": None,
        "executionPrice": None
    }

    ORDERS[order_id] = order
    trade = execute_order(order)

    return success_response(
        {"order": order, "trade": trade},
        status=201,
        message="Order placed and executed"
    )

@app.route("/api/v1/orders", methods=["GET"])
def all_orders():
    return success_response(list(ORDERS.values()))

@app.route("/api/v1/orders/<order_id>", methods=["GET"])
def order_status(order_id):
    order = ORDERS.get(order_id)
    if not order:
        return error_response(["Order not found"], 404)
    return success_response(order)

@app.route("/api/v1/trades", methods=["GET"])
def trades():
    return success_response(TRADES)

@app.route("/api/v1/portfolio", methods=["GET"])
def portfolio():
    holdings = []

    for symbol, h in PORTFOLIO.items():
        price = get_instrument(symbol)["lastTradedPrice"]
        value = h["quantity"] * price

        holdings.append({
            "symbol": symbol,
            "quantity": h["quantity"],
            "averagePrice": round(h["averagePrice"], 2),
            "currentPrice": price,
            "currentValue": round(value, 2),
            "profitLoss": round(value - h["totalInvested"], 2),
        })

    total_value = sum(h["currentValue"] for h in holdings)
    total_invested = sum(h["quantity"] * h["averagePrice"] for h in holdings)

    return success_response({
        "holdings": holdings,
        "summary": {
            "totalValue": round(total_value, 2),
            "totalInvested": round(total_invested, 2),
            "totalProfitLoss": round(total_value - total_invested, 2)
        }
    })

@app.route("/api/v1/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "timestamp": now()})


# ======================================================
# START SERVER
# ======================================================

if __name__ == "__main__":
    print("Trading System API running at http://localhost:5000")
    app.run(debug=True)
