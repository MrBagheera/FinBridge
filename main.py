from typing import List, Any

import gspread
from gspread import Client, Spreadsheet
from positions_table import PositionsTable
from saxo import SaxoConnection, SaxoPosition

serviceAccount: Client = gspread.service_account()
sheet: Spreadsheet = serviceAccount.open("FinBridge")
positionsTable: PositionsTable = PositionsTable(sheet.worksheet("Positions"), "Saxo")

token = "eyJhbGciOiJFUzI1NiIsIng1dCI6IkRFNDc0QUQ1Q0NGRUFFRTlDRThCRDQ3ODlFRTZDOTEyRjVCM0UzOTQifQ.eyJvYWEiOiI3Nzc3NSIsImlzcyI6Im9hIiwiYWlkIjoiMTA5IiwidWlkIjoidXw0R01CQk42amxEbXBCb3kyQ0JMUT09IiwiY2lkIjoidXw0R01CQk42amxEbXBCb3kyQ0JMUT09IiwiaXNhIjoiRmFsc2UiLCJ0aWQiOiIyMDAyIiwic2lkIjoiYTQzYTNmNDg1OWIyNGM5YWIyOTY0MGZkYmU3OTA5NTYiLCJkZ2kiOiI4NCIsImV4cCI6IjE3MDAxMzY0NjEiLCJvYWwiOiIxRiIsImlpZCI6ImViZWNlYmM0NmIxYTRkNzA5NmRlMDhkYjkxYjBhNzUxIn0.ZgISXe3I1HLtp_ki2KO7-GomNe4RXgxmsp8LiHSO-_46yQ0WPqqz7WD2juDHsJh2VsfIcY3VYjn-nuf-uQf8oA"
connection: SaxoConnection = SaxoConnection(token)
positions: list[SaxoPosition] = connection.get_account_positions()
positions.append(SaxoPosition("Cash", 0.0, 0.0, 0.0, connection.get_account_balance(), 0.0))
for p in positions:
    print(f"Adding/updating position {p.name}")
    positionsTable.add_or_update_position(p.name, p.open_price, p.current_price, p.profit_loss, p.exposure)
known_positions: list[str] = list(map(lambda y: y.name, positions))
removed_positions: list[str] = list(filter(lambda x: x not in known_positions, positionsTable.positions()))
for p in removed_positions:
    print(f"Removing position {p}")
    positionsTable.remove_position(p)
