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
            "get_SMMSMasterlist": {
                "name": "get_SMMSMasterlist",
                "description": "Get the Monday SMMS Masterlist board data. These are the columns: Store, Display Name, Live Status, Live Date, Update Date, License type, Locality, Comms Plan, Admin Access, Added to New Admin, 2nd Admin, 3rd admin, Comments, Status, Official Link, Rejected Posting, Unofficial Link, Unofficial checked, Removal request date (unofficial page), First license, Type of social media, LIVE Social Type, On Hootsuite?, Email 1, Email 2, Email 3, Email 4, GMB email, Email Login, Username Login, Password, GMB, Renewal",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "columns": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": "List of columns to include in the result."
                        },
                         "filters": {
                            "type": "object",
                            "description": "Optional filters to apply to the data. Each key is a column name, and the value can be a string, number, or an array of acceptable values.",
                            "additionalProperties": {
                            "oneOf": [
                                { "type": "string" },
                                { "type": "number" },
                                {
                                "type": "array",
                                "items": { "type": ["string", "number"] }
                                }
                            ]
                            }
                        },
                        "order_by": {
                            "type": "string",
                            "description": "Column name to order by."
                        },
                        "ascending": {
                            "type": "boolean",
                            "description": "Whether to sort in ascending order. Defaults to true."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of rows to return."
                        }
                    }
                }
            },
            "get_organisationMasterlist": {
                "name": "get_SMMSMasterlist",
                "description":  "Filter, sort, and limit data from the Organisation Masterlist Board. Allows selecting specific columns, applying filters, sorting by a column, and limiting rows returned.",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "filters": {
                            "type": "object",
                            "description": "Optional filters to apply to the data. Each key is a column name, and the value can be a string, number, or an array of acceptable values.",
                            "additionalProperties": {
                            "oneOf": [
                                { "type": "string" },
                                { "type": "number" },
                                {
                                "type": "array",
                                "items": { "type": ["string", "number"] }
                                }
                            ]
                            }
                        },
                        "columns": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": "List of columns to include in the result. Available columns include: Store, Subitems, Code, Email, Job Title, First name, Surname, Email 1, First name 1, Surname 1, Job Title 1, Email 2, First name 2, Surname 2, Job Title 2, SMMS Contacted, SMMS Customer, Facebook Page Official, Facebook Page Unofficial, Official Checked, Unofficial Checked, ICB, PCN Name, Practice Contact, Duplicate ODS, Practice Email, PCN Code, ICB Code, Region, Region Code, Sales Lead, DJP, D&T Invite Sent, D&T Hub Progress, Mirror 1, DMS, Strategic, DT Network, link to Helpdesk Dashboard, link to SMMS Tasks, link to 👩🏻‍💼 Leads, link to Website Master Sheet, link to 💵 Opportunities, link to 👩🏻‍💼 Individuals, link to 🏢 Organisations, link to Cohort Log, link to Salford PCN Webinar x3 - Delivery Plan, link to North Central London Action Log, link to DMS Overview, link to Feedback Received, link to Delivery Plan, Email Count, link to End Of Project Feedback, link to Staffordshire Tracker 04Y, 05D, 05G, 05V, 05W, Master List, Mirror, link to South West London Tracker 36L, link to Pathfinder Customers, link to stacey test, Webinar Attendance Master Sheet, Mirror 2, link to CPD Purchased/Delivered."
                        },
                        "order_by": {
                            "type": "string",
                            "description": "Column name to order by."
                        },
                        "ascending": {
                            "type": "boolean",
                            "description": "Whether to sort in ascending order. Defaults to true."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of rows to return."
                        }
                    }
                }
            },
            "get_supportDeskDashboard": {
                "name": "get_supportDeskDashboard",
                "description": "Filter, sort, and limit data from the Support Desk Dashboard CSV. Allows selecting specific columns, applying filters, sorting by a column, and limiting rows returned.",
                "parameters": {
                    "type": "object",
                    "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Optional filters to apply to the data. Each key is a column name, and the value can be a string, number, or an array of acceptable values.",
                        "additionalProperties": {
                        "oneOf": [
                            { "type": "string" },
                            { "type": "number" },
                            {
                            "type": "array",
                            "items": { "type": ["string", "number"] }
                            }
                        ]
                        }
                    },
                    "columns": {
                        "type": "array",
                        "items": { "type": "string" },
                        "description": "List of columns to include in the result. Available columns include: Store, Subitems, Created at, Task Status, Category, Assignee, Customer Type, Enquiry Type, ODS Code, Practices affected, AI Video, Organisation Master List, Email Address, Text/Information to be posted, Image to be posted (if applicable), Date to be posted, What is your name?, Mirror, PCN, ICB, ICB Code, Region, Job Role, Please select the CPD courses you are interested in., Resolution, Feedback Form Sent, Resolution Date, How long it's opened, Requestor phone, Formula, Hootsuite, Delete, Social Media Type, Social Media ID."
                    },
                    "order_by": {
                        "type": "string",
                        "description": "Column name to order by."
                    },
                    "ascending": {
                        "type": "boolean",
                        "description": "Whether to sort in ascending order. Defaults to true."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of rows to return."
                    }
                    }
                }
            },
            "get_individualsBoard": {
                "name": "get_individualsBoard",
                "description": "Filter, sort, and limit data from the Individuals Board CSV. Allows selecting specific columns, applying filters, sorting by a column, and limiting rows returned.",
                "parameters": {
                    "type": "object",
                    "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Optional filters to apply to the data. Each key is a column name, and the value can be a string, number, or an array of acceptable values.",
                        "additionalProperties": {
                        "oneOf": [
                            { "type": "string" },
                            { "type": "number" },
                            {
                            "type": "array",
                            "items": { "type": ["string", "number"] }
                            }
                        ]
                        }
                    },
                    "columns": {
                        "type": "array",
                        "items": { "type": "string" },
                        "description": "List of columns to include in the result. Available columns include: Store, Subitems, Job Type, Friend, Can we contact?, D&T Network, D&T Hub Invite Sent, DJP, SMMS, DMS, Item ID, *Company, 💵 *Opportunities, Job Title, Phone, Email, Organisation, PCN, ODS, ICB, Region, Mirror, Comments, Location, *New/Exiting, *Create a new account & connect, *Connect to existing account, *Crate an Opportunity, *👩🏻‍💼 Leads, link to Helpdesk Dashboard, Duplication, Duplicate Indicator, link to Cohort Log, link to Salford PCN Webinar x3 - Delivery Plan, link to 👩🏻‍💼 Leads, link to BSOL Appointment Redesign, link to Stakeholder Database, link to Webinar Attendance Master Sheet, link to Staffordshire Tracker 04Y, 05D, 05G, 05V, 05W, link to South West London Tracker 36L, link to Cambridgeshire & Peterborough Tracker 06H, D and T Network Email, monday Doc v2."
                    },
                    "order_by": {
                        "type": "string",
                        "description": "Column name to order by."
                    },
                    "ascending": {
                        "type": "boolean",
                        "description": "Whether to sort in ascending order. Defaults to true."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of rows to return."
                    }
                    }
                }
            },
            "get_webinarAttendees": {
                "name": "get_webinarAttendees",
                "description":  "Filter, sort, and limit data from the Organisation Masterlist Board. Allows selecting specific columns, applying filters, sorting by a column, and limiting rows returned.",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "filters": {
                            "type": "object",
                            "description": "Optional filters to apply to the data. Each key is a column name, and the value can be a string, number, or an array of acceptable values.",
                            "additionalProperties": {
                            "oneOf": [
                                { "type": "string" },
                                { "type": "number" },
                                {
                                "type": "array",
                                "items": { "type": ["string", "number"] }
                                }
                            ]
                            }
                        },
                        "columns": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description":  "List of columns to include in the result. Available columns include: Store, Subitems, Session Date, Programme, Webinar Type, Please tick the box if you would like to subscribe to a newsletter from Redmoor Health, assigned to pick up, Followed up Network, Which product or service are you most interested in?, Can Redmoor contact?, Added to stakeholder/org master list, Added to Individuals Board, First Name, Last Name, Job Title, Email address, Formula, Webinar Attendance Master Sheet, Duplicate Trigger, Organisation, ODS Code (if known), PCN, ICB/ICS, Organisation Master List, ODS Code, ICB, ICB Code, Region, Connect boards, Name of session, Registration First Name, Registration Last Name, Registration Email, Webinar, Organization, ODS code if known, Job title."
                        },
                        "order_by": {
                            "type": "string",
                            "description": "Column name to order by."
                        },
                        "ascending": {
                            "type": "boolean",
                            "description": "Whether to sort in ascending order. Defaults to true."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of rows to return."
                        }
                    }
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
            
        elif tool_name == "get_supportDeskDashboard":
            path = './Boards data'  # Ensure this matches the path used in get_board.py
            file_path = os.path.join(path, f"Support Desk Dashboard.csv")
            try:
                df = pd.read_csv(file_path)
                # Convert df to a dictionary or string representation as needed
                # Extract optional transformation parameters
                columns = arguments.get("columns")               # list of columns
                order_by = arguments.get("order_by")             # column name
                ascending = arguments.get("ascending", True)     # bool
                limit = arguments.get("limit")                   # int
                filters = arguments.get("filters", {})          # dict of filters

                # 1. Filter columns
                if filters:
                    for col, val in filters.items():
                        if col not in df.columns:
                            result = f"Invalid filter column: {col}. Available: {list(df.columns)}"
                            break
                        # handle lists or single values
                        if isinstance(val, list):
                            df = df[df[col].isin(val)]
                        else:
                            df = df[df[col] == val]

                if columns:
                    missing = [col for col in columns if col not in df.columns]
                    if missing:
                        result = f"Invalid columns: {missing}. Available: {list(df.columns)}"
                    else:
                        df = df[columns]

                # 2. Sort
                if order_by:
                    if order_by not in df.columns:
                        result = f"Invalid order_by column: {order_by}. Available: {list(df.columns)}"
                    else:
                        df = df.sort_values(by=order_by, ascending=ascending)

                # 3. Limit rows
                if limit is not None:
                    try:
                        limit = int(limit)
                        df = df.head(limit)
                    except ValueError:
                        result = "Invalid limit value. Must be an integer."

                #print(f"Successfully read board data from {file_path}")
                result = str(df.to_dict(orient='records'))

            except FileNotFoundError:
                result = f"File {file_path} not found."
        
        elif tool_name == "get_individualsBoard":
            path = './Boards data'  # Ensure this matches the path used in get_board.py
            file_path = os.path.join(path, f"Individuals Board.csv")
            try:
                df = pd.read_csv(file_path)
                # Convert df to a dictionary or string representation as needed
                # Extract optional transformation parameters
                columns = arguments.get("columns")               # list of columns
                order_by = arguments.get("order_by")             # column name
                ascending = arguments.get("ascending", True)     # bool
                limit = arguments.get("limit")                   # int
                filters = arguments.get("filters", {})          # dict of filters

                # 1. Filter columns
                if filters:
                    for col, val in filters.items():
                        if col not in df.columns:
                            result = f"Invalid filter column: {col}. Available: {list(df.columns)}"
                            break
                        # handle lists or single values
                        if isinstance(val, list):
                            df = df[df[col].isin(val)]
                        else:
                            df = df[df[col] == val]

                if columns:
                    missing = [col for col in columns if col not in df.columns]
                    if missing:
                        result = f"Invalid columns: {missing}. Available: {list(df.columns)}"
                    else:
                        df = df[columns]

                # 2. Sort
                if order_by:
                    if order_by not in df.columns:
                        result = f"Invalid order_by column: {order_by}. Available: {list(df.columns)}"
                    else:
                        df = df.sort_values(by=order_by, ascending=ascending)

                # 3. Limit rows
                if limit is not None:
                    try:
                        limit = int(limit)
                        df = df.head(limit)
                    except ValueError:
                        result = "Invalid limit value. Must be an integer."

                #print(f"Successfully read board data from {file_path}")
                result = str(df.to_dict(orient='records'))

            except FileNotFoundError:
                result = f"File {file_path} not found."

        elif tool_name == "get_SMMSMasterlist":
            path = './Boards data'  # Ensure this matches the path used in get_board.py
            file_path = os.path.join(path, f"SMMSMasterList.csv")
            try:
                df = pd.read_csv(file_path)
                # Convert df to a dictionary or string representation as needed
                # Extract optional transformation parameters
                columns = arguments.get("columns")               # list of columns
                order_by = arguments.get("order_by")             # column name
                ascending = arguments.get("ascending", True)     # bool
                limit = arguments.get("limit")                   # int
                filters = arguments.get("filters", {})

                # 1. Filter columns
                if filters:
                    for col, val in filters.items():
                        if col not in df.columns:
                            result = f"Invalid filter column: {col}. Available: {list(df.columns)}"
                            break
                        # handle lists or single values
                        if isinstance(val, list):
                            df = df[df[col].isin(val)]
                        else:
                            df = df[df[col] == val]

                if columns:
                    missing = [col for col in columns if col not in df.columns]
                    if missing:
                        result = f"Invalid columns: {missing}. Available: {list(df.columns)}"
                    else:
                        df = df[columns]

                # 2. Sort
                if order_by:
                    if order_by not in df.columns:
                        result = f"Invalid order_by column: {order_by}. Available: {list(df.columns)}"
                    else:
                        df = df.sort_values(by=order_by, ascending=ascending)

                # 3. Limit rows
                if limit is not None:
                    try:
                        limit = int(limit)
                        df = df.head(limit)
                    except ValueError:
                        result = "Invalid limit value. Must be an integer."

                #print(f"Successfully read board data from {file_path}")
                result = str(df.to_dict(orient='records'))

            except FileNotFoundError:
                result = f"File {file_path} not found."

        elif tool_name == "get_webinarAttendees":
            path = './Boards data'  # Ensure this matches the path used in get_board.py
            file_path = os.path.join(path, f"webinarAttendees.csv")
            try:
                df = pd.read_csv(file_path)
                # Convert df to a dictionary or string representation as needed
                # Extract optional transformation parameters
                columns = arguments.get("columns")               # list of columns
                order_by = arguments.get("order_by")             # column name
                ascending = arguments.get("ascending", True)     # bool
                limit = arguments.get("limit")                   # int
                filters = arguments.get("filters", {})

                # 1. Filter columns
                if filters:
                    for col, val in filters.items():
                        if col not in df.columns:
                            result = f"Invalid filter column: {col}. Available: {list(df.columns)}"
                            break
                        # handle lists or single values
                        if isinstance(val, list):
                            df = df[df[col].isin(val)]
                        else:
                            df = df[df[col] == val]

                if columns:
                    missing = [col for col in columns if col not in df.columns]
                    if missing:
                        result = f"Invalid columns: {missing}. Available: {list(df.columns)}"
                    else:
                        df = df[columns]

                # 2. Sort
                if order_by:
                    if order_by not in df.columns:
                        result = f"Invalid order_by column: {order_by}. Available: {list(df.columns)}"
                    else:
                        df = df.sort_values(by=order_by, ascending=ascending)

                # 3. Limit rows
                if limit is not None:
                    try:
                        limit = int(limit)
                        df = df.head(limit)
                    except ValueError:
                        result = "Invalid limit value. Must be an integer."

                #print(f"Successfully read board data from {file_path}")
                result = str(df.to_dict(orient='records'))

            except FileNotFoundError:
                result = f"File {file_path} not found."

        elif tool_name == "get_organisationMasterlist":
            path = './Boards data'  # Ensure this matches the path used in get_board.py
            file_path = os.path.join(path, f"Organisation Masterlist.csv")
            try:
                df = pd.read_csv(file_path)
                # Convert df to a dictionary or string representation as needed
                # Extract optional transformation parameters
                columns = arguments.get("columns")               # list of columns
                order_by = arguments.get("order_by")             # column name
                ascending = arguments.get("ascending", True)     # bool
                limit = arguments.get("limit")                   # int
                filters = arguments.get("filters", {})

                # 1. Filter columns
                if filters:
                    for col, val in filters.items():
                        if col not in df.columns:
                            result = f"Invalid filter column: {col}. Available: {list(df.columns)}"
                            break
                        # handle lists or single values
                        if isinstance(val, list):
                            df = df[df[col].isin(val)]
                        else:
                            df = df[df[col] == val]

                if columns:
                    missing = [col for col in columns if col not in df.columns]
                    if missing:
                        result = f"Invalid columns: {missing}. Available: {list(df.columns)}"
                    else:
                        df = df[columns]

                # 2. Sort
                if order_by:
                    if order_by not in df.columns:
                        result = f"Invalid order_by column: {order_by}. Available: {list(df.columns)}"
                    else:
                        df = df.sort_values(by=order_by, ascending=ascending)

                # 3. Limit rows
                if limit is not None:
                    try:
                        limit = int(limit)
                        df = df.head(limit)
                    except ValueError:
                        result = "Invalid limit value. Must be an integer."

                #print(f"Successfully read board data from {file_path}")
                result = str(df.to_dict(orient='records'))

            except FileNotFoundError:
                result = f"File {file_path} not found."
        else:
            return self._create_error_response(-32601, f"Tool not found: {tool_name}")
        
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "content": [{"type": "text", "text": str(result)}]
            }
        }
    
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
