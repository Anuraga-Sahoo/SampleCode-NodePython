# Node.js API Connector and Python Client

This project consists of two components:
1. A Node.js server that connects to third-party APIs
2. A Python client that retrieves data from the Node.js server

## Setup Instructions

### Prerequisites
- Node.js (v14 or higher)
- npm (v6 or higher)
- Python (v3.6 or higher)
- pip (for Python package installation)

### Node.js Server Setup

1. Create a new directory for the Node.js server:
```bash
mkdir nodejs-api-server
cd nodejs-api-server
```

2. Initialize a new Node.js project:
```bash
npm init -y
```

3. Install the required dependencies:
```bash
npm install express axios cors
```

4. Create a file named `server.js` and paste the Node.js code provided earlier.

5. Start the server:
```bash
node server.js
```

The server should now be running on port 3000.

### Python Client Setup

1. Create a new directory for the Python client:
```bash
mkdir python-api-client
cd python-api-client
```

2. Install the required Python packages:
```bash
pip install requests
```

3. Create a file named `client.py` and paste the Python code provided earlier.

## Usage

### Using the Python Client

The Python client provides a command-line interface with the following commands:

1. Check server health:
```bash
python client.py server
```

2. Get stock data for a symbol:
```bash
python client.py stock AAPL
```

4. Make a custom API request:
```bash
python client.py custom "https://api.example.com/data" --method GET --headers '{"Authorization": "Bearer token123"}' --data '{"param1": "value1"}'
```

### Example Output

When fetching stock data:
```
===== STOCK INFORMATION =====
Symbol: AAPL
Price: $178.72
Change: +2.14 (+1.21%)
Volume: 32458901
Updated At: 2025-03-07T15:30:00.000Z
=============================

## Notes

- The Node.js server includes caching to reduce the number of requests to third-party APIs.
- The Python client includes error handling to provide meaningful error messages.
- For production use, you should secure the server with authentication and rate limiting.
- API keys should be stored in environment variables, not hardcoded in the source code.
