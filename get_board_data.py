import pandas as pd
import requests as rq
import os

# API Contraints
apiKey = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjU2NTk5MTYzMSwiYWFpIjoxMSwidWlkIjo3ODQyMzE3NCwiaWFkIjoiMjAyNS0wOS0yNFQxMToyODoyNy41NTBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTMyMTQyMDAsInJnbiI6ImV1YzEifQ.T9ztwB-EWTKeHjCrO56K99alj6ImHpRu5J3Ltw0nC4E"
apiURL = "https://api.monday.com/v2"
apiVer = "2025-07"
headers = {"Authorization" : apiKey,"API-Version" : apiVer}
path = './Boards data' #this can be changed to any path you like

# Create directory if it doesn't exist
if not os.path.isdir(path):
    os.makedirs(path)

# Query using GraphQL
# Get all data (limit 500) using a cursor as a pointer of where to continue from.

def retrieve_board(board_id):
  all_items = []  # store all item pages here

  # --- Step 1: initial query ---
  query = f'''
  query {{
    boards (ids: {board_id}) {{
      items_page (limit: 500) {{
        cursor
        items {{
          id
          name
          column_values {{
            column {{ title }}
            text
          }}
        }}
      }}
    }}
  }}
  '''
  data = {'query': query}

  try:
      r = rq.post(url=apiURL, json=data, headers=headers)
      jsonData = r.json()
  except rq.exceptions.RequestException as e:
      print(e)
      quit()

  # extract first batch of items + cursor
  items_page = jsonData['data']['boards'][0]['items_page']
  all_items.extend(items_page['items'])
  cursor = items_page.get('cursor')

  # --- Step 2: loop through next pages ---
  while cursor:
      query = f'''
      query {{
        next_items_page (cursor: "{cursor}") {{
          cursor
          items {{
            id
            name
            column_values {{
              column {{ title }}
              text
            }}
          }}
        }}
      }}
      '''
      data = {'query': query}
      r = rq.post(url=apiURL, json=data, headers=headers)
      jsonData = r.json()
      page = jsonData['data']['next_items_page']
      all_items.extend(page['items'])
      cursor = page.get('cursor')  # None if done

  # --- Step 3: build DataFrame ---
  dfData = []
  for item in all_items:
      rowData = {"Store": item["name"]}
      for columnValue in item["column_values"]:
          columnTitle = columnValue["column"]["title"]
          text = columnValue["text"]
          rowData[columnTitle] = text
      dfData.append(rowData)

  df = pd.DataFrame(dfData)

  return df

# Get Board IDs
df_board_ids = pd.read_csv('board_ids.csv')
columns = ["Monday Board of Interest", "Board ID"]

# Filter to only necessary columns
df_board_ids = df_board_ids[columns]

# Change board id dataframe to dictionary
board_id_dict = df_board_ids.set_index('Monday Board of Interest')['Board ID'].to_dict()
# Invoices and Collections
InvoicesAndCollections = retrieve_board(int(board_id_dict["Invoices and Collections"]))
InvoicesAndCollections.to_csv(f'{path}/InvoicesAndCollections.csv', sep=',', encoding='utf-8', index=False)

SMMMSmasterList = retrieve_board(int(board_id_dict["SMMS Masterlist"]))

# Data import and cleaning
SMMMSmasterList = SMMMSmasterList[SMMMSmasterList['Live Status'] == "Live"]
# Drop rows where Official_Link is NaN
SMMMSmasterList = SMMMSmasterList.dropna(subset=["Official Link"])

# Drop any columns where all values are NaN
SMMMSmasterList = SMMMSmasterList.dropna(axis=1, how='all')

SMMMSmasterList.to_csv(f'{path}/SMMSMasterList.csv', sep=',', encoding='utf-8', index=False)

webinarAttendees = retrieve_board(int(board_id_dict["Webinar Attendance Masterlist"]))

webinarAttendees.to_csv(f'{path}/webinarAttendees.csv', sep=',', encoding='utf-8', index=False)

orgMasterList = retrieve_board(int(board_id_dict["Organisation Masterlist"]))

orgMasterList.to_csv(f'{path}/Organisation Masterlist.csv', sep=',', encoding='utf-8', index=False)

#SupportDesk = retrieve_board(int(board_id_dict["Support Desk Dashboard"]))
#SupportDesk.to_csv(f'{path}/Support Desk Dashboard.csv', sep=',', encoding='utf-8', index=False)

IndividualsBoard = retrieve_board(int(board_id_dict["Individuals Board"]))
IndividualsBoard.to_csv(f'{path}/Individuals Board.csv', sep=',', encoding='utf-8', index=False)
#
## Opportunities Board
OpportunitiesBoard = retrieve_board(int(board_id_dict["Opportunities Board"]))
OpportunitiesBoard.to_csv(f'{path}/OpportunitiesBoard.csv', sep=',', encoding='utf-8', index=False)
#
## Follow-up List
FollowUpList = retrieve_board(int(board_id_dict["Follow-up List"]))
FollowUpList.to_csv(f'{path}/FollowUpList.csv', sep=',', encoding='utf-8', index=False)

# Advanced Training
#AdvancedTraining = retrieve_board(int(board_id_dict["Advanced Training"]))
#AdvancedTraining.to_csv(f'{path}/Advanced Training.csv', sep=',', encoding='utf-8', index=False)

# Main Workspace
#MainWorkspace = retrieve_board(int(board_id_dict["Main Workspace"]))
#MainWorkspace.to_csv(f'{path}/MainWorkspace.csv', sep=',', encoding='utf-8', index=False)



'''
def df_to_text(df, name="output"):
  # Convert DataFrame to string
  text = str(df.to_dict(orient='records'))

  # Save string to a text file

  with open(f'Board string/{name}.text', "w", encoding="utf-8") as file:
    # Write the string to the file
    file.write(text)

  print(f"DataFrame saved to Board string/{name}.text")


df_to_text(SMMMSmasterList, "SMMSMasterList")
df_to_text(webinarAttendees, "webinarAttendees")
df_to_text(orgMasterList, "Organisation Masterlist")
'''