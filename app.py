"""
Trading System Backend - A simplified stock trading platform
Run with: python app.py
"""

from flask import Flask, request, jsonify
from datetime import datetime
from enum import Enum
import uuid

app = Flask(__name__)

# Enums for order types
class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStyle(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"

class OrderStatus(Enum):
    NEW = "NEW"
    PLACED = "PLACED"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"

# In-memory storage
instruments = [
    {
        "symbol": "AAPL",
        "exchange": "NASDAQ",
        "instrumentType": "STOCK",
        "lastTradedPrice": 175.50
    },
    {
        "symbol": "GOOGL",
        "exchange": "NASDAQ",
        "instrumentType": "STOCK",
        "lastTradedPrice": 140.25
    },
    {
        "symbol": "MSFT",
        "exchange": "NASDAQ",
        "instrumentType": "STOCK",
        "lastTradedPrice": 380.00
    },
    {
        "symbol": "TSLA",
        "exchange": "NASDAQ",
        "instrumentType": "STOCK",
        "lastTradedPrice": 245.75
    },
    {
        "symbol": "AMZN",
        "exchange": "NASDAQ",
        "instrumentType": "STOCK",
        "lastTradedPrice": 155.30
    }
]

orders = {}  # orderId -> order_object
trades = []  # list of executed trades
portfolio = {}  # symbol -> holding_object

# Helper functions
def get_instrument_by_symbol(symbol):
    """Find an instrument by its symbol"""
    for instrument in instruments:
        if instrument["symbol"] == symbol:
            return instrument
    return None

def validate_order(order_data):
    """Validate order data"""
    errors = []
    
    # Check required fields
    required_fields = ["symbol", "orderType", "orderStyle", "quantity"]
    for field in required_fields:
        if field not in order_data:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return False, errors
    
    # Validate quantity
    if order_data["quantity"] <= 0:
        errors.append("Quantity must be greater than 0")
    
    # Validate order type
    if order_data["orderType"] not in [e.value for e in OrderType]:
        errors.append(f"Invalid orderType. Must be one of: {[e.value for e in OrderType]}")
    
    # Validate order style
    if order_data["orderStyle"] not in [e.value for e in OrderStyle]:
        errors.append(f"Invalid orderStyle. Must be one of: {[e.value for e in OrderStyle]}")
    
    # Validate LIMIT order has price
    if order_data["orderStyle"] == "LIMIT" and "price" not in order_data:
        errors.append("Price is mandatory for LIMIT orders")
    
    # Validate instrument exists
    instrument = get_instrument_by_symbol(order_data["symbol"])
    if not instrument:
        errors.append(f"Instrument {order_data['symbol']} not found")
    
    if errors:
        return False, errors
    
    return True, []

def execute_order(order_id):
    """Simulate order execution"""
    order = orders[order_id]
    instrument = get_instrument_by_symbol(order["symbol"])
    
    # Determine execution price
    if order["orderStyle"] == "MARKET":
        execution_price = instrument["lastTradedPrice"]
    else:  # LIMIT
        execution_price = order["price"]
    
    # Update order status
    order["status"] = OrderStatus.EXECUTED.value
    order["executedAt"] = datetime.now().isoformat()
    order["executionPrice"] = execution_price
    
    # Create trade record
    trade = {
        "tradeId": str(uuid.uuid4()),
        "orderId": order_id,
        "symbol": order["symbol"],
        "orderType": order["orderType"],
        "quantity": order["quantity"],
        "price": execution_price,
        "totalValue": execution_price * order["quantity"],
        "executedAt": order["executedAt"]
    }
    trades.append(trade)
    
    # Update portfolio
    update_portfolio(order["symbol"], order["orderType"], order["quantity"], execution_price)
    
    return trade

def update_portfolio(symbol, order_type, quantity, price):
    """Update portfolio holdings"""
    if symbol not in portfolio:
        portfolio[symbol] = {
            "symbol": symbol,
            "quantity": 0,
            "averagePrice": 0,
            "totalInvested": 0
        }
    
    holding = portfolio[symbol]
    
    if order_type == "BUY":
        # Calculate new average price
        total_cost = (holding["quantity"] * holding["averagePrice"]) + (quantity * price)
        new_quantity = holding["quantity"] + quantity
        holding["quantity"] = new_quantity
        holding["averagePrice"] = total_cost / new_quantity if new_quantity > 0 else 0
        holding["totalInvested"] = total_cost
    
    elif order_type == "SELL":
        holding["quantity"] -= quantity
        if holding["quantity"] <= 0:
            # Remove from portfolio if quantity becomes 0 or negative
            del portfolio[symbol]
        else:
            holding["totalInvested"] = holding["quantity"] * holding["averagePrice"]

# API Routes

@app.route('/api/v1/instruments', methods=['GET'])
def get_instruments():
    """Fetch list of tradable instruments"""
    return jsonify({
        "success": True,
        "data": instruments,
        "count": len(instruments)
    }), 200

@app.route('/api/v1/orders', methods=['POST'])
def place_order():
    """Place a new order"""
    try:
        order_data = request.get_json()
        
        # Validate order
        is_valid, errors = validate_order(order_data)
        if not is_valid:
            return jsonify({
                "success": False,
                "errors": errors
            }), 400
        
        # Create order
        order_id = str(uuid.uuid4())
        order = {
            "orderId": order_id,
            "symbol": order_data["symbol"],
            "orderType": order_data["orderType"],
            "orderStyle": order_data["orderStyle"],
            "quantity": order_data["quantity"],
            "price": order_data.get("price"),
            "status": OrderStatus.NEW.value,
            "createdAt": datetime.now().isoformat(),
            "executedAt": None,
            "executionPrice": None
        }
        
        # Store order
        orders[order_id] = order
        
        # Update status to PLACED
        order["status"] = OrderStatus.PLACED.value
        
        # Auto-execute (simulating instant execution)
        trade = execute_order(order_id)
        
        return jsonify({
            "success": True,
            "message": "Order placed and executed successfully",
            "data": {
                "order": order,
                "trade": trade
            }
        }), 201
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/v1/orders/<order_id>', methods=['GET'])
def get_order_status(order_id):
    """Fetch order status by ID"""
    if order_id not in orders:
        return jsonify({
            "success": False,
            "error": "Order not found"
        }), 404
    
    return jsonify({
        "success": True,
        "data": orders[order_id]
    }), 200

@app.route('/api/v1/orders', methods=['GET'])
def get_all_orders():
    """Fetch all orders"""
    return jsonify({
        "success": True,
        "data": list(orders.values()),
        "count": len(orders)
    }), 200

@app.route('/api/v1/trades', methods=['GET'])
def get_trades():
    """Fetch list of executed trades"""
    return jsonify({
        "success": True,
        "data": trades,
        "count": len(trades)
    }), 200

@app.route('/api/v1/portfolio', methods=['GET'])
def get_portfolio():
    """Fetch current portfolio holdings"""
    # Calculate current values
    portfolio_with_current_value = []
    
    for symbol, holding in portfolio.items():
        instrument = get_instrument_by_symbol(symbol)
        current_price = instrument["lastTradedPrice"]
        current_value = holding["quantity"] * current_price
        
        portfolio_with_current_value.append({
            "symbol": holding["symbol"],
            "quantity": holding["quantity"],
            "averagePrice": round(holding["averagePrice"], 2),
            "currentPrice": current_price,
            "currentValue": round(current_value, 2),
            "profitLoss": round(current_value - holding["totalInvested"], 2),
            "profitLossPercent": round(((current_value - holding["totalInvested"]) / holding["totalInvested"] * 100), 2) if holding["totalInvested"] > 0 else 0
        })
    
    # Calculate total portfolio value
    total_value = sum(item["currentValue"] for item in portfolio_with_current_value)
    total_invested = sum(portfolio[symbol]["totalInvested"] for symbol in portfolio)
    
    return jsonify({
        "success": True,
        "data": {
            "holdings": portfolio_with_current_value,
            "summary": {
                "totalValue": round(total_value, 2),
                "totalInvested": round(total_invested, 2),
                "totalProfitLoss": round(total_value - total_invested, 2),
                "totalProfitLossPercent": round(((total_value - total_invested) / total_invested * 100), 2) if total_invested > 0 else 0
            }
        },
        "count": len(portfolio_with_current_value)
    }), 200

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Trading System API",
        "timestamp": datetime.now().isoformat()
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

if __name__ == '__main__':
    print("=" * 50)
    print("Trading System API Starting...")
    print("=" * 50)
    print("\nAvailable Endpoints:")
    print("  GET  /api/v1/instruments      - List all instruments")
    print("  POST /api/v1/orders           - Place a new order")
    print("  GET  /api/v1/orders/<id>      - Get order status")
    print("  GET  /api/v1/orders           - Get all orders")
    print("  GET  /api/v1/trades           - List all trades")
    print("  GET  /api/v1/portfolio        - View portfolio")
    print("  GET  /api/v1/health           - Health check")
    print("\nServer running on: http://localhost:5000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)