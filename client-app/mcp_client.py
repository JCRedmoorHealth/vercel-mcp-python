#!/usr/bin/env python3
"""
MCP Client for testing the Vercel MCP Python Server
"""

import requests
import json
import time
import os
from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from colorama import init, Fore, Style
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class MCPClient:
    """Client for connecting to MCP servers"""
    
    def __init__(self, server_url: str, timeout: int = 10):
        self.server_url = server_url
        self.timeout = timeout
        self.console = Console()
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'MCP-Client/1.0'
        })
    
    def send_request(self, method: str, params: Dict[str, Any] = None, request_id: int = 1) -> Dict[str, Any]:
        """Send a request to the MCP server"""
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method
        }
        
        if params:
            payload["params"] = params
        
        try:
            response = self.session.post(self.server_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON response: {str(e)}"}
    
    def test_connection(self) -> bool:
        """Test basic connection to the server"""
        try:
            response = self.session.get(self.server_url, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                self.console.print(f"✅ Server Status: {data.get('status', 'unknown')}")
                self.console.print(f"📊 Available Tools: {data.get('tools', 0)}")
                self.console.print(f"📚 Available Resources: {data.get('resources', 0)}")
                return True
            else:
                self.console.print(f"❌ Server returned status: {response.status_code}")
                return False
        except Exception as e:
            self.console.print(f"❌ Connection failed: {str(e)}")
            return False
    
    def initialize(self) -> bool:
        """Initialize the MCP connection"""
        self.console.print("🔌 Initializing MCP connection...")
        
        response = self.send_request("initialize", {})
        
        if "error" in response:
            self.console.print(f"❌ Initialization failed: {response['error']}")
            return False
        
        result = response.get("result", {})
        server_info = result.get("serverInfo", {})
        
        self.console.print(f"✅ Connected to: {server_info.get('name', 'Unknown')}")
        self.console.print(f"📋 Version: {server_info.get('version', 'Unknown')}")
        self.console.print(f"🔧 Protocol: {result.get('protocolVersion', 'Unknown')}")
        
        return True
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        self.console.print("🔧 Fetching available tools...")
        
        response = self.send_request("tools/list", {})
        
        if "error" in response:
            self.console.print(f"❌ Failed to get tools: {response['error']}")
            return []
        
        tools = response.get("result", {}).get("tools", [])
        
        # Display tools in a nice table
        table = Table(title="Available MCP Tools")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Parameters", style="yellow")
        
        for tool in tools:
            params = []
            properties = tool.get("inputSchema", {}).get("properties", {})
            required = tool.get("inputSchema", {}).get("required", [])
            
            for param_name, param_info in properties.items():
                param_type = param_info.get("type", "unknown")
                is_required = param_name in required
                param_str = f"{param_name} ({param_type})"
                if is_required:
                    param_str += " *"
                params.append(param_str)
            
            table.add_row(
                tool.get("name", "unknown"),
                tool.get("description", "No description"),
                ", ".join(params) if params else "None"
            )
        
        self.console.print(table)
        return tools
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific tool with arguments"""
        self.console.print(f"🔨 Calling tool: {tool_name}")
        
        response = self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
        if "error" in response:
            self.console.print(f"❌ Tool call failed: {response['error']}")
            return None
        
        result = response.get("result", {})
        content = result.get("content", [])
        
        if content:
            for item in content:
                if item.get("type") == "text":
                    return item.get("text", "")
        
        return result
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """Get list of available resources"""
        self.console.print("📚 Fetching available resources...")
        
        response = self.send_request("resources/list", {})
        
        if "error" in response:
            self.console.print(f"❌ Failed to get resources: {response['error']}")
            return []
        
        resources = response.get("result", {}).get("resources", [])
        
        # Display resources in a nice table
        table = Table(title="Available MCP Resources")
        table.add_column("URI", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Description", style="yellow")
        table.add_column("Type", style="green")
        
        for resource in resources:
            table.add_row(
                resource.get("uri", "unknown"),
                resource.get("name", "unknown"),
                resource.get("description", "No description"),
                resource.get("mimeType", "unknown")
            )
        
        self.console.print(table)
        return resources
    
    def read_resource(self, uri: str) -> str:
        """Read a specific resource"""
        self.console.print(f"📖 Reading resource: {uri}")
        
        response = self.send_request("resources/read", {"uri": uri})
        
        if "error" in response:
            self.console.print(f"❌ Resource read failed: {response['error']}")
            return ""
        
        contents = response.get("result", {}).get("contents", [])
        
        if contents:
            for content in contents:
                if content.get("mimeType") == "application/json":
                    return content.get("text", "")
        
        return ""

def main():
    """Main client application"""
    console = Console()
    
    # Load server URL from environment variables
    server_url = os.getenv('MCP_SERVER_URL', 'https://your-deployed-server.vercel.app')
    timeout = int(os.getenv('MCP_TIMEOUT', '10'))
    debug = os.getenv('MCP_DEBUG', 'false').lower() == 'true'
    
    if debug:
        console.print(f"[dim]Debug mode enabled[/dim]")
        console.print(f"[dim]Server URL: {server_url}[/dim]")
        console.print(f"[dim]Timeout: {timeout}s[/dim]")
    
    console.print(Panel.fit(
        "[bold blue]MCP Client for Vercel MCP Python Server[/bold blue]\n"
        f"[dim]Connecting to: {server_url}[/dim]",
        title="🤖 MCP Client",
        border_style="blue"
    ))
    
    # Create client
    client = MCPClient(server_url, timeout)
    
    # Test connection
    if not client.test_connection():
        console.print("❌ Failed to connect to server. Exiting.")
        return
    
    console.print()
    
    # Initialize MCP
    if not client.initialize():
        console.print("❌ Failed to initialize MCP connection. Exiting.")
        return
    
    console.print()
    
    # Interactive menu
    while True:
        console.print("\n" + "="*50)
        console.print("[bold cyan]MCP Client Menu[/bold cyan]")
        console.print("1. List Tools")
        console.print("2. Call Tool")
        console.print("3. List Resources")
        console.print("4. Read Resource")
        console.print("5. Test All Tools")
        console.print("6. Exit")
        
        choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6"])
        
        if choice == "1":
            client.list_tools()
        
        elif choice == "2":
            tools = client.list_tools()
            if not tools:
                continue
            
            tool_names = [tool["name"] for tool in tools]
            tool_name = Prompt.ask("Enter tool name", choices=tool_names)
            
            # Get tool details
            tool = next((t for t in tools if t["name"] == tool_name), None)
            if not tool:
                console.print("❌ Tool not found")
                continue
            
            # Get arguments
            arguments = {}
            properties = tool.get("inputSchema", {}).get("properties", {})
            required = tool.get("inputSchema", {}).get("required", [])
            
            for param_name, param_info in properties.items():
                param_type = param_info.get("type", "string")
                param_desc = param_info.get("description", "")
                is_required = param_name in required
                
                if param_type == "integer":
                    value = Prompt.ask(f"Enter {param_name} (integer)" + (" *" if is_required else ""))
                    try:
                        arguments[param_name] = int(value)
                    except ValueError:
                        console.print(f"❌ Invalid integer for {param_name}")
                        continue
                else:
                    value = Prompt.ask(f"Enter {param_name} (string)" + (" *" if is_required else ""))
                    arguments[param_name] = value
            
            # Call tool
            result = client.call_tool(tool_name, arguments)
            if result is not None:
                console.print(f"✅ Result: {result}")
        
        elif choice == "3":
            client.list_resources()
        
        elif choice == "4":
            resources = client.list_resources()
            if not resources:
                continue
            
            uris = [resource["uri"] for resource in resources]
            uri = Prompt.ask("Enter resource URI", choices=uris)
            
            content = client.read_resource(uri)
            if content:
                console.print(f"✅ Resource content:\n{content}")
        
        elif choice == "5":
            console.print("🧪 Testing all tools...")
            
            # Test echo
            result = client.call_tool("echo", {"message": "Hello from MCP Client!"})
            console.print(f"Echo: {result}")
            
            # Test get_time
            result = client.call_tool("get_time", {})
            console.print(f"Time: {result}")
            
            # Test get_board_info
            result = client.call_tool("get_boards_info", {})
            console.print(f"Board Info: {result}")
            
            console.print("✅ All tools tested successfully!")
        
        elif choice == "6":
            console.print("👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
