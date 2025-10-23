# src/mcp_server.py
import datetime
import json
from typing import Dict, Any, List
import os
import pandas as pd

class MCPServer:
    """Simple MCP server implementation for Vercel deployment"""
    
    def __init__(self):
        self.tools = {
            "echo": {
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
            "get_time": {
                "name": "get_time", 
                "description": "Get the current server time",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "get_boards_info": {
                "name": "get_boards_info",
                "description": "Get all monday board data",
                "inputSchema": {
                    "type": "object", 
                    "properties": {}
                }
            }
        }
        
        self.resources = {
            "config://server": {
                "uri": "config://server",
                "name": "Server Configuration",
                "description": "Server configuration information",
                "mimeType": "application/json"
            }
        }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests"""
        try:
            method = request.get("method")
            
            if method == "initialize":
                return self._handle_initialize(request)
            elif method == "tools/list":
                return self._handle_tools_list(request)
            elif method == "tools/call":
                return self._handle_tools_call(request)
            elif method == "resources/list":
                return self._handle_resources_list(request)
            elif method == "resources/read":
                return self._handle_resources_read(request)
            else:
                return self._create_error_response(-32601, f"Method not found: {method}")
                
        except Exception as e:
            return self._create_error_response(-32603, f"Internal error: {str(e)}")
    
    def _handle_initialize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {"name": "Vercel MCP Server", "version": "1.0.0"}
            }
        }
    
    def _handle_tools_list(self, request: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0", 
            "id": request.get("id"),
            "result": {"tools": list(self.tools.values())}
        }
    
    def _handle_tools_call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        params = request.get("params", {})
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
            try:
                for file in os.listdir(path):
                    if file.endswith('.csv'):
                        board_name = file[:-4]  # Remove .csv extension
                        board_data = self._read_board(board_name)
                        if board_data is not None:
                            all_boards[board_name] = board_data
                if not all_boards:
                    return None
                result = all_boards
            except FileNotFoundError:
                print(f"Directory {path} not found.")
                return None
        else:
            return self._create_error_response(-32601, f"Tool not found: {tool_name}")
        
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "content": [{"type": "text", "text": str(result)}]
            }
        }
    
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

    
    def _handle_resources_list(self, request: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"), 
            "result": {"resources": list(self.resources.values())}
        }
    
    def _handle_resources_read(self, request: Dict[str, Any]) -> Dict[str, Any]:
        params = request.get("params", {})
        uri = params.get("uri")
        
        if uri == "config://server":
            config = {
                "version": "1.0.0",
                "environment": "vercel", 
                "features": ["tools", "resources"]
            }
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "contents": [{
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(config, indent=2)
                    }]
                }
            }
        else:
            return self._create_error_response(-32601, f"Resource not found: {uri}")
    
    def _create_error_response(self, code: int, message: str) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "error": {"code": code, "message": message}
        }

# Create global instance
mcp = MCPServer()
