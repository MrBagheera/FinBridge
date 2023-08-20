import json
import logging
import sys
import time

import gspread
from gspread import Client, Spreadsheet
from positions_table import PositionsTable
from saxo import SaxoConnection, SaxoPosition
from saxo_login import SaxoLogin

class Config:
    """Configuration for FinBridge"""

    def __init__(self, app_config_filename: str):
        # read app config as json
        with open(app_config_filename, 'r') as f:
            app_config = json.load(f)
        self.saxo_app = app_config['saxo_app']
        google_sheets = app_config['google_sheets']
        self.sheet_name = google_sheets['sheet_name']
        self.worksheet_name = google_sheets['worksheet_name']
        self.section_name = google_sheets['section_name']
        self.throttle_delay = google_sheets['throttle_delay']
        if 'debug' in app_config:
            self.debug = app_config['debug']
        else:
            self.debug = False


if __name__ == "__main__":
    # check if config file specified as first parameter
    if len(sys.argv) == 2:
        config_filename = sys.argv[1]
    else:
        print("Usage: python3 main.py <config_file>")
        sys.exit(1)

    config = Config(config_filename)
    logging.basicConfig(level=logging.DEBUG if config.debug else logging.INFO)

    # set up Saxo connection
    connection: SaxoConnection = SaxoLogin(config.saxo_app).login()

    # set up Google Sheets connection
    serviceAccount: Client = gspread.service_account()
    sheet: Spreadsheet = serviceAccount.open(config.sheet_name)
    positionsTable: PositionsTable = PositionsTable(sheet.worksheet(config.worksheet_name), config.section_name)

    # update positions
    positions: list[SaxoPosition] = connection.get_account_positions()
    positions.append(SaxoPosition("Cash", 0, 0.0, connection.get_account_balance(), 0.0, 0.0))
    for p in positions:
        logging.info(f"Adding/updating position {p.name}")
        positionsTable.add_or_update_position(p.name, p.amount, p.open_price, p.current_price, p.profit_loss, p.exposure)
        if config.throttle_delay > 0:
            time.sleep(config.throttle_delay)
    known_positions: list[str] = list(map(lambda y: y.name, positions))
    removed_positions: list[str] = list(filter(lambda x: x not in known_positions, positionsTable.positions()))
    for p in removed_positions:
        logging.info(f"Removing position {p}")
        positionsTable.remove_position(p)
        if config.throttle_delay > 0:
            time.sleep(config.throttle_delay)
