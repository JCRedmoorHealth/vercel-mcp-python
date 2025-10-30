# api/index.py
import json
import datetime
from http.server import BaseHTTPRequestHandler
import pandas as pd
import os
from docx import Document
import PyPDF2

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

def _read_board(board_name: str):
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

def _read_document(document_name: str):
    path = './document data'  # Ensure this matches the path used in get_board.py
    file_path = os.path.join(path, f"{document_name}.docx")
    try:
        doc = Document(file_path)
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        return '\n'.join(fullText)

    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None

def _read_pdf(pdf_name: str):
    text = ""
    path = './document data'  # Ensure this matches the path used in get_board.py
    file_path = os.path.join(path, f"{pdf_name}.pdf")
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text

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
            {
                "name": "get_organisationMasterlist",
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
            {
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
            {
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
            {
                "name": "get_webinarAttendees",
                "description":  "Filter, sort, and limit data from the Webinar attendees Board. Allows selecting specific columns, applying filters, sorting by a column, and limiting rows returned.",
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
