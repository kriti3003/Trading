# Trading System Wrapper SDK

A simplified stock trading platform backend that simulates core trading workflows including order placement, portfolio management, and trade execution.

## 🎯 Overview

This project implements a wrapper SDK around REST APIs for a trading platform. It allows users to view instruments, place orders, check order status, view trades, and manage their portfolio - all without real market connectivity.

The system simulates:
- Real-time order execution
- Portfolio management with profit/loss tracking
- Complete trade history
- Comprehensive validation and error handling

---

## ✨ Features

### 1. Instrument Management
- View all tradable instruments (stocks)
- Each instrument includes: symbol, exchange, type, and last traded price

### 2. Order Management
- **Order Types**: BUY / SELL
- **Order Styles**: MARKET / LIMIT
- Place orders with validation
- Track order lifecycle: NEW → PLACED → EXECUTED
- Fetch order status by ID
- View all orders

### 3. Trade History
- View all executed trades
- Track price, quantity, and timestamp
- Link trades to original orders

### 4. Portfolio Management
- Real-time portfolio holdings
- Average price calculation
- Current value and profit/loss tracking
- Percentage-based returns

### 5. Validation & Error Handling
- Quantity validation (must be > 0)
- Price validation for LIMIT orders
- Instrument existence checks
- Proper HTTP status codes
- Detailed error messages

---

## 🛠️ Technology Stack

- **Language**: Python 3.8+
- **Framework**: Flask 3.0.0
- **Data Storage**: In-memory (Python dictionaries)
- **API Format**: JSON
- **HTTP Client**: requests (for testing)

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone or download the project files**
   ```bash
   # Ensure you have these files:
   # - app.py
   # - requirements.txt
   # - test_trading_system.py
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**
   ```bash
   python app.py
   ```

   The server will start on `http://localhost:5000`

5. **Verify the server is running**
   ```bash
   curl http://localhost:5000/api/v1/health
   ```

---

## 📚 API Documentation

### Base URL
```
http://localhost:5000/api/v1
```

### Endpoints

#### 1. Health Check
**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "Trading System API",
  "timestamp": "2026-01-08T10:30:00.000000"
}
```

---

#### 2. Get All Instruments
**GET** `/instruments`

Fetch list of all tradable instruments.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "AAPL",
      "exchange": "NASDAQ",
      "instrumentType": "STOCK",
      "lastTradedPrice": 175.50
    }
  ],
  "count": 5
}
```
---

#### 3. Place Order
**POST** `/orders`

Place a new buy or sell order.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "orderType": "BUY",
  "orderStyle": "MARKET",
  "quantity": 10,
  "price": 175.00  // Required only for LIMIT orders
}
```

**Parameters:**
- `symbol` (string, required): Stock symbol
- `orderType` (string, required): "BUY" or "SELL"
- `orderStyle` (string, required): "MARKET" or "LIMIT"
- `quantity` (integer, required): Number of shares (must be > 0)
- `price` (float, optional): Required for LIMIT orders

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Order placed and executed successfully",
  "data": {
    "order": {
      "orderId": "550e8400-e29b-41d4-a716-446655440000",
      "symbol": "AAPL",
      "orderType": "BUY",
      "orderStyle": "MARKET",
      "quantity": 10,
      "status": "EXECUTED",
      "createdAt": "2026-01-08T10:30:00.000000",
      "executedAt": "2026-01-08T10:30:00.100000",
      "executionPrice": 175.50
    },
    "trade": {
      "tradeId": "660e8400-e29b-41d4-a716-446655440001",
      "orderId": "550e8400-e29b-41d4-a716-446655440000",
      "symbol": "AAPL",
      "orderType": "BUY",
      "quantity": 10,
      "price": 175.50,
      "totalValue": 1755.00,
      "executedAt": "2026-01-08T10:30:00.100000"
    }
  }
}
```

---

#### 4. Get Order Status
**GET** `/orders/{orderId}`

Fetch status of a specific order.

**Response:**
```json
{
  "success": true,
  "data": {
    "orderId": "550e8400-e29b-41d4-a716-446655440000",
    "symbol": "AAPL",
    "orderType": "BUY",
    "orderStyle": "MARKET",
    "quantity": 10,
    "status": "EXECUTED",
    "createdAt": "2026-01-08T10:30:00.000000",
    "executedAt": "2026-01-08T10:30:00.100000",
    "executionPrice": 175.50
  }
}
```

---

#### 5. Get All Orders
**GET** `/orders`

Fetch list of all orders.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "orderId": "550e8400-e29b-41d4-a716-446655440000",
      "symbol": "AAPL",
      "status": "EXECUTED",
      ...
    }
  ],
  "count": 10
}
```

---

#### 6. Get All Trades
**GET** `/trades`

Fetch list of all executed trades.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "tradeId": "660e8400-e29b-41d4-a716-446655440001",
      "orderId": "550e8400-e29b-41d4-a716-446655440000",
      "symbol": "AAPL",
      "orderType": "BUY",
      "quantity": 10,
      "price": 175.50,
      "totalValue": 1755.00,
      "executedAt": "2026-01-08T10:30:00.100000"
    }
  ],
  "count": 5
}
```

---

#### 7. Get Portfolio
**GET** `/portfolio`

Fetch current portfolio holdings with profit/loss.

**Response:**
```json
{
  "success": true,
  "data": {
    "holdings": [
      {
        "symbol": "AAPL",
        "quantity": 10,
        "averagePrice": 175.50,
        "currentPrice": 175.50,
        "currentValue": 1755.00,
        "profitLoss": 0.00,
        "profitLossPercent": 0.00
      }
    ],
    "summary": {
      "totalValue": 1755.00,
      "totalInvested": 1755.00,
      "totalProfitLoss": 0.00,
      "totalProfitLossPercent": 0.00
    }
  },
  "count": 1
}
```

---

## 📖 Sample API Usage

### Using curl

#### 1. View All Instruments
```bash
curl -X GET http://localhost:5000/api/v1/instruments
```

#### 2. Place a Market Buy Order
```bash
curl -X POST http://localhost:5000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "orderType": "BUY",
    "orderStyle": "MARKET",
    "quantity": 10
  }'
```

#### 3. Place a Limit Buy Order
```bash
curl -X POST http://localhost:5000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "GOOGL",
    "orderType": "BUY",
    "orderStyle": "LIMIT",
    "quantity": 5,
    "price": 140.00
  }'
```

#### 4. Place a Sell Order
```bash
curl -X POST http://localhost:5000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "orderType": "SELL",
    "orderStyle": "MARKET",
    "quantity": 5
  }'
```

#### 5. Get Order Status
```bash
# Replace {orderId} with actual order ID from previous response
curl -X GET http://localhost:5000/api/v1/orders/{orderId}
```

#### 6. View All Trades
```bash
curl -X GET http://localhost:5000/api/v1/trades
```

#### 7. View Portfolio
```bash
curl -X GET http://localhost:5000/api/v1/portfolio
```

### Using the Test Script

Run the automated test script to test all endpoints:

```bash
python test_trading_system.py
```

This will:
1. Check server health
2. Fetch all instruments
3. Place multiple orders (buy and sell)
4. Test validation with invalid data
5. Fetch order status
6. View all trades
7. Display final portfolio

---

## 🔍 Assumptions

### 1. **Single User System**
   - The system is designed for a single user
   - No authentication or user management required
   - All data belongs to one default user

### 2. **Instant Order Execution**
   - All orders are executed immediately upon placement
   - No order queue or pending state
   - Orders move from NEW → PLACED → EXECUTED instantly

### 3. **Market Simulation**
   - Stock prices are static (no real-time price updates)
   - MARKET orders execute at the last traded price
   - LIMIT orders execute at the specified limit price (always successful)

### 4. **In-Memory Storage**
   - All data is stored in memory
   - Data is lost when the server restarts
   - Suitable for development/testing purposes

### 5. **Portfolio Management**
   - Average price is calculated using weighted average method
   - Selling shares reduces portfolio quantity
   - Portfolio entries are removed when quantity reaches zero

### 6. **Order Validation**
   - Quantity must be a positive integer
   - Price is mandatory for LIMIT orders
   - Symbol must exist in the instruments list
   - No check for sufficient balance or portfolio quantity for sells

### 7. **Trading Hours**
   - No restriction on trading hours
   - Orders can be placed 24/7

### 8. **Data Constraints**
   - Order IDs and Trade IDs are UUID v4
   - Timestamps use ISO 8601 format
   - Prices are stored as floats with 2 decimal precision for display

---

## 📁 Project Structure

```
trading-system/
│
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── test_trading_system.py      # Automated test suite
├── README.md                   # This file
│
└── (Runtime data - in memory)
    ├── instruments[]           # List of tradable stocks
    ├── orders{}                # Dictionary of all orders
    ├── trades[]                # List of executed trades
    └── portfolio{}             # User's current holdings
```

### Code Structure in app.py

```
app.py
├── Enums (OrderType, OrderStyle, OrderStatus)
├── Data Storage (instruments, orders, trades, portfolio)
├── Helper Functions
│   ├── get_instrument_by_symbol()
│   ├── validate_order()
│   ├── execute_order()
│   └── update_portfolio()
├── API Routes
│   ├── GET  /api/v1/health
│   ├── GET  /api/v1/instruments
│   ├── POST /api/v1/orders
│   ├── GET  /api/v1/orders/{orderId}
│   ├── GET  /api/v1/orders
│   ├── GET  /api/v1/trades
│   └── GET  /api/v1/portfolio
└── Error Handlers (404, 500)
```

---

## 🛡️ Error Handling

### HTTP Status Codes

- **200 OK**: Successful GET request
- **201 Created**: Successful POST request (order placed)
- **400 Bad Request**: Validation error
- **404 Not Found**: Resource not found (order, endpoint)
- **500 Internal Server Error**: Server error

### Error Response Format

All errors follow a consistent format:

```json
{
  "success": false,
  "error": "Error message here",
  "errors": ["List of validation errors"]  // For validation failures
}
```

### Validation Examples

#### Invalid Quantity
```json
{
  "success": false,
  "errors": ["Quantity must be greater than 0"]
}
```

#### Missing Price for LIMIT Order
```json
{
  "success": false,
  "errors": ["Price is mandatory for LIMIT orders"]
}
```

#### Invalid Symbol
```json
{
  "success": false,
  "errors": ["Instrument XYZ not found"]
}
```

#### Order Not Found
```json
{
  "success": false,
  "error": "Order not found"
}
```

---

## 🧪 Testing

### Manual Testing with curl

Test each endpoint individually using the curl commands provided in the [Sample API Usage](#sample-api-usage) section.

### Automated Testing

Run the complete test suite:

```bash
python test_trading_system.py
```

The test script covers:
- ✅ Health check
- ✅ Fetching instruments
- ✅ Placing MARKET orders
- ✅ Placing LIMIT orders
- ✅ Placing SELL orders
- ✅ Input validation (negative quantity, missing price)
- ✅ Order status retrieval
- ✅ Trade history
- ✅ Portfolio management

### Expected Test Flow

1. Server health verification
2. Fetch available instruments (5 stocks)
3. Place BUY orders for AAPL (10 shares)
4. Place LIMIT order for GOOGL (5 shares)
5. Place additional orders for MSFT and TSLA
6. Place SELL order for AAPL (5 shares)
7. Test validation failures
8. Verify order status
9. Check trade history
10. View final portfolio with P&L

---

## 🚀 Running in Production

For production deployment, consider:

1. **Database**: Replace in-memory storage with PostgreSQL/MySQL
2. **Authentication**: Add JWT-based authentication
3. **Rate Limiting**: Implement API rate limiting
4. **Logging**: Add comprehensive logging
5. **Configuration**: Use environment variables
6. **WSGI Server**: Use Gunicorn or uWSGI instead of Flask dev server
7. **Reverse Proxy**: Deploy behind Nginx
8. **Docker**: Containerize the application

---