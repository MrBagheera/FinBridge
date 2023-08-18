Simple tool to import current positions from Saxo Bank into Google Sheeta

Operation
- Open positions are represented in Google Sheet with specific name ("FinBridge" / "Positions")
- There are multiple positions from different providers
  - Each section starts with a row containing just provider name
  - Each section ends with an empty row
  - There may be many empty rows between sections
  - Last row of the section may be "Cash" row
- This script is going to update only section of "Saxo" provider
- Columns:
  - A: Investment type - single letter (manual)
  - B: Instrument name as it appears in Saxo Platform
  - C: Amount (manual)
  - D: Open price (manual)
  - E: Current price (manual)
  - F: Currency (manual)
  - G: Open position, euros
  - H: Current position, euros
  - I: P/L, euros
  - J: Exposure (if available), euros
  - A few extra columns (manual)
- Script goes over all Saxo accounts, for each tries to find row by matching instrument name 
  - If found: Updates existing columns 3-7
  - If not found: inserts and fills new row before section end (or "Cash" row)
- For all rows where matching position is not found, deletes rows
- Updates "Cash" row with sum of cash in all accounts in euros