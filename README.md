Simple tool to import current positions from Saxo Bank into Google Sheets

## Operation

- Open positions are represented in Google Sheet with specific name ("FinBridge" / "Positions")
- There are multiple positions from different providers
  - Each section starts with a row containing just provider name
  - Each section ends with an empty row
  - There may be many empty rows between sections
  - Last row of the section may be "Cash" row
- This script is going to update only section of "Saxo" provider
- Columns:
  - A: Investment type - single letter (manual)
  - B: Instrument name as it appears in Saxo Platform (manual)
  - C: Investment Country (manual)
  - D: Instrument Sector (manual)
  - E: Amount (manual)
  - F: Open price (manual)
  - G: Current price (manual)
  - H: Currency (manual)
  - I: Open position, euros
  - J: Current position, euros
  - K: P/L, euros
  - L: Exposure (if available), euros
- Script goes over all Saxo accounts, for each tries to find row by matching instrument name 
  - If found: Updates existing columns 3-7
  - If not found: inserts and fills new row before section end (or "Cash" row)
- For all rows where matching position is not found, deletes rows
- Updates "Cash" row with sum of cash in all accounts in euros


## Running

```shell
python3 main.py <config_file>
```

Where `<config_file>` is JSON file with following fields:
- `saxo_app`: Saxo app configuration, as downloaded from app registration page on developer portal. `RedirectUrl` 
should be configured to `http://localhost:5050/webhook`.
- `google_sheets`: Google Sheets configuration
  - `sheet_name`: Name of the sheet
  - `worksheet_name`: Name of the worksheet
  - `section_name`: Name of the section
  - `throttle_delay`: Delay between requests to Google Sheets API, in seconds
- `debug`: If true, prints debug messages

Example config file:
```json
{
  "saxo_app": {
    "AppName": "FinBridge",
    "AppKey": "...",
    "AuthorizationEndpoint": "https://live.logonvalidation.net/authorize",
    "TokenEndpoint": "https://live.logonvalidation.net/token",
    "GrantType": "Code",
    "OpenApiBaseUrl": "https://gateway.saxobank.com/openapi/",
    "RedirectUrls": [
      "http://localhost:5050/webhook"
    ],
    "AppSecret": "..."
  },
  "google_sheets": {
    "sheet_name": "FinBridge",
    "worksheet_name": "Positions",
    "section_name": "Saxo",
    "throttle_delay": 1.0
  },
  "debug": true
}
```
