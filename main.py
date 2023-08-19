import logging

import gspread
from gspread import Client, Spreadsheet
from positions_table import PositionsTable
from saxo import SaxoConnection, SaxoPosition
from saxo_login import SaxoLogin

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # set up Saxo connection
    connection: SaxoConnection = SaxoLogin("sim.json").login()

    # set up Google Sheets connection
    serviceAccount: Client = gspread.service_account()
    sheet: Spreadsheet = serviceAccount.open("FinBridge")
    positionsTable: PositionsTable = PositionsTable(sheet.worksheet("Positions"), "Saxo")

    # update positions
    positions: list[SaxoPosition] = connection.get_account_positions()
    positions.append(SaxoPosition("Cash", 0.0, 0.0, 0.0, connection.get_account_balance(), 0.0))
    for p in positions:
        logging.info(f"Adding/updating position {p.name}")
        positionsTable.add_or_update_position(p.name, p.open_price, p.current_price, p.profit_loss, p.exposure)
    known_positions: list[str] = list(map(lambda y: y.name, positions))
    removed_positions: list[str] = list(filter(lambda x: x not in known_positions, positionsTable.positions()))
    for p in removed_positions:
        logging.info(f"Removing position {p}")
        positionsTable.remove_position(p)
