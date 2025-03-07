import requests
import json
import time
import argparse
import os
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

class NodeAPIClient:
    """Client for interacting with the Node.js API connector server"""
    
    def __init__(self, base_url: str = None, timeout: int = 10):

        self.base_url = base_url or os.environ.get("API_SERVER_URL", "http://localhost:3000")
        self.timeout = timeout
        self.session = requests.Session()
    
    def check_health(self) -> Dict[str, Any]:
        """Check if the Node.js server is running properly"""
        response = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def get_stock(self, symbol: str) -> Dict[str, Any]:

        if not symbol or not isinstance(symbol, str):
            raise ValueError("Stock symbol must be a non-empty string")
            
        response = self.session.get(
            f"{self.base_url}/api/stocks", 
            params={"symbol": symbol.upper()},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def fetch_api(self, 
                 url: str, 
                 method: str = "GET", 
                 headers: Dict[str, str] = None, 
                 data: Dict[str, Any] = None) -> Dict[str, Any]:

        payload = {
            "url": url,
            "method": method.upper(),
            "headers": headers or {},
            "data": data or {}
        }
        
        response = self.session.post(
            f"{self.base_url}/api/fetch",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()


def display_stock(stock_data: Dict[str, Any]) -> None:
    """Display stock data in a readable format"""
    print("\n===== STOCK INFORMATION =====")
    print(f"Symbol: {stock_data.get('symbol')}")
    print(f"Price: ${stock_data.get('price', 'N/A')}")
    
    change = stock_data.get('change')
    pct_change = stock_data.get('change_percent')
    
    if change is not None and pct_change is not None:
        change_symbol = "▲" if change >= 0 else "▼"
        change_color = "\033[92m" if change >= 0 else "\033[91m"  # Green for positive, red for negative
        reset_color = "\033[0m"
        print(f"Change: {change_color}{change_symbol} ${abs(change):.2f} ({abs(pct_change):.2f}%){reset_color}")
    
    print(f"Volume: {stock_data.get('volume', 'N/A'):,}")
    print(f"Updated At: {stock_data.get('updated_at')}")
    print("=============================\n")


def display_server_health(health_data: Dict[str, Any]) -> None:
    """Display server health information"""
    print("\n===== SERVER HEALTH =====")
    print(f"Status: {health_data.get('status', 'unknown')}")
    print(f"Timestamp: {health_data.get('timestamp', 'N/A')}")
    
    if 'uptime' in health_data:
        print(f"Uptime: {health_data['uptime']}")
    
    if 'environment' in health_data:
        print(f"Environment: {health_data['environment']}")
        
    if 'cache_items' in health_data:
        print(f"Cached Items: {health_data['cache_items']}")
        
    print("=========================\n")


def main():
    """Main function to run the command-line interface"""
    parser = argparse.ArgumentParser(description="Fetch data from Node.js API connector")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Stock command
    stock_parser = subparsers.add_parser("stock", help="Get stock data")
    stock_parser.add_argument("symbol", help="Stock symbol")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Check server health")
    
    # Generic API fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch data from any API")
    fetch_parser.add_argument("url", help="API URL to fetch data from")
    fetch_parser.add_argument("--method", "-m", default="GET", help="HTTP method (default: GET)")
    fetch_parser.add_argument("--header", "-H", action="append", help="HTTP headers in format 'key:value'")
    fetch_parser.add_argument("--data", "-d", help="JSON data for POST/PUT requests")
    
    # Global options
    parser.add_argument("--server", help="API server URL (default: http://localhost:3000)")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds (default: 10)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if a command was specified
    if not args.command:
        parser.print_help()
        return
    
    # Create API client
    client = NodeAPIClient(base_url=args.server, timeout=args.timeout)
    
    try:
        if args.command == "stock":
            start_time = time.time()
            stock_data = client.get_stock(args.symbol)
            elapsed = time.time() - start_time
            display_stock(stock_data)
            print(f"Request completed in {elapsed:.2f} seconds")
        
        elif args.command == "server":
            health = client.check_health()
            display_server_health(health)
        
        elif args.command == "fetch":
            # Process headers
            headers = {}
            if args.header:
                for header in args.header:
                    key, value = header.split(":", 1)
                    headers[key.strip()] = value.strip()
            
            # Process data
            data = None
            if args.data:
                try:
                    data = json.loads(args.data)
                except json.JSONDecodeError:
                    print("Error: Invalid JSON format in data argument")
                    return
            
            # Make the request
            start_time = time.time()
            result = client.fetch_api(args.url, args.method, headers, data)
            elapsed = time.time() - start_time
            
            # Display the result
            print(f"\n===== API RESPONSE =====")
            print(f"Status: {result.get('status')} {result.get('statusText', '')}")
            print(f"Response Data:")
            print(json.dumps(result.get('data'), indent=2))
            print(f"Request completed in {elapsed:.2f} seconds")
            print("========================\n")
    
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server. Make sure it's running.")
    
    except requests.exceptions.Timeout:
        print(f"Error: Request timed out after {args.timeout} seconds")
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            try:
                error_data = e.response.json()
                print(f"API Error: {error_data.get('error', 'Unknown error')}")
                if 'details' in error_data:
                    print(f"Details: {error_data['details']}")
            except ValueError:
                print(f"Status Code: {e.response.status_code}")
                print(f"Response Text: {e.response.text}")
    
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in response")
    
    except ValueError as e:
        print(f"Error: {e}")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")


if __name__ == "__main__":
    main()