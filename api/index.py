# api/index.py
import json
import datetime
from http.server import BaseHTTPRequestHandler
import pandas as pd
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "name": "Vercel MCP Server",
                "version": "1.0.0",
                "status": "running",
                "tools": 4,
                "resources": 1
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def do_POST(self):
        """Handle POST requests"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if post_data:
                request_data = json.loads(post_data.decode('utf-8'))
                response = handle_mcp_request(request_data)
            else:
                response = {"error": "No data received"}
                
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-API-Key')
        self.end_headers()

def _read_board(self, board_name: str) -> Any:
    path = './Boards data'  # Ensure this matches the path used in get_board.py
    file_path = os.path.join(path, f"{board_name}.csv")
    try:
        df = pd.read_csv(file_path)
        # Convert df to a dictionary or string representation as needed
        print(f"Successfully read board data from {file_path}")
        return df.to_dict(orient='records')

    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None

def handle_mcp_request(request_data):
    """Handle MCP protocol requests"""
    method = request_data.get("method")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {"name": "Vercel MCP Server", "version": "1.0.0"}
            }
        }
    
    elif method == "tools/list":
        tools = [
            {
                "name": "echo",
                "description": "Echo the provided message back to the user",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "The message to echo back"}
                    },
                    "required": ["message"]
                }
            },
            {
                "name": "get_time", 
                "description": "Get the current server time",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_boards_info",
                "description": "Get all Monday Board data",
                "inputSchema": {
                    "type": "object", 
                    "properties": {}
                }
            }
        ]
        return {
            "jsonrpc": "2.0", 
            "id": request_data.get("id"),
            "result": {"tools": tools}
        }
    
    elif method == "tools/call":
        params = request_data.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "echo":
            message = arguments.get("message", "")
            result = f"Tool echo: {message}"
        elif tool_name == "get_time":
            current_time = datetime.datetime.now().isoformat()
            result = f"Current Vercel server time: {current_time}"
        elif tool_name == "get_boards_info":
            path = './Boards data'  # Ensure this matches the path used in get_board.py
            all_boards = {}
            for file in os.listdir(path):
                if file.endswith('.csv'):
                    board_name = file[:-4]  # Remove .csv extension
                    board_data = _read_board(board_name)
                    if board_data is not None:
                        all_boards[board_name] = board_data
            if not all_boards:
                result = "No boards found."
            else:
                result = all_boards
        else:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}
            }
        
        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id"),
            "result": {
                "content": [{"type": "text", "text": str(result)}]
            }
        }
    
    elif method == "resources/list":
        resources = [
            {
                "uri": "config://server",
                "name": "Server Configuration",
                "description": "Server configuration information",
                "mimeType": "application/json"
            }
        ]
        return {
            "jsonrpc": "2.0",
            "id": request_data.get("id"), 
            "result": {"resources": resources}
        }
    
    elif method == "resources/read":
        params = request_data.get("params", {})
        uri = params.get("uri")
        
        if uri == "config://server":
            config = {
                "version": "1.0.0",
                "environment": "vercel", 
                "features": ["tools", "resources"]
            }
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "result": {
                    "contents": [{
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(config, indent=2)
                    }]
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Resource not found: {uri}"}
            }
    
    else:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }
