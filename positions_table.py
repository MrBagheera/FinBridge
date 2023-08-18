from typing import Any, List

import gspread
from gspread import Client, Spreadsheet, Worksheet


class PositionsTable:
    """Table of positions in a portfolio backed by range of rows in Google Sheets Worksheet."""

    def __init__(self, backend: Worksheet, name: str):
        self._backend = backend
        self._sectionName = name
        # find our rows range
        col_a: List[Any] = backend.col_values(1)
        col_b: List[Any] = backend.col_values(2)
        try:
            section_name_index: int = col_a.index(name)
        except ValueError:
            raise Exception(f"Section name {name} not found in column A")
        try:
            first_empty_cell_index: int = col_b.index('', section_name_index + 1)
        except ValueError:
            first_empty_cell_index = len(col_b)
        self._sectionStartIndex = section_name_index + 1
        self._sectionEndIndex = first_empty_cell_index
        # build a dictionary of positions to row indices
        self._positions: dict[str, int] = {}
        for i in range(self._sectionStartIndex, self._sectionEndIndex):
            self._positions[col_b[i]] = i

    @property
    def name(self) -> str:
        return self._sectionName

    def length(self) -> int:
        return self._sectionEndIndex - self._sectionStartIndex

    def positions(self) -> set[str]:
        return set(self._positions.keys())

    def remove_position(self, name: str):
        """Remove a position from the table."""
        if name not in self._positions:
            raise Exception(f"Position {name} not found in section {self._sectionName}")
        # remove the row
        index: int = self._positions[name]
        self._backend.delete_rows(index + 1)  # Google Sheets is 1-indexed
        del self._positions[name]
        # update indices of remaining positions
        for i in self._positions.keys():
            if self._positions[i] > index:
                self._positions[i] -= 1

    def add_or_update_position(self, name: str, open_price: float, current_price: float,
                               profit_loss: float, exposure: float):
        """Add or update a position in the table."""
        def optional(x: float | int) -> str:
            return '' if x == 0 else str(x)
        values = [
            optional(open_price),
            optional(current_price),
            optional(profit_loss),
            optional(exposure)
        ]
        if name in self._positions:
            # update the row
            index: int = self._positions[name]
            self._backend.update(
                f"G{index+1}:J{index+1}",  # Google Sheets is 1-indexed
                [values],
                value_input_option='USER_ENTERED')
        else:
            # add a new row at the end of the section
            index: int = self._sectionEndIndex
            self._backend.insert_row(
                values=['', name, '', '', '', ''] + values,
                index=index + 1,  # Google Sheets is 1-indexed
                value_input_option='USER_ENTERED')
            self._positions[name] = index
            self._sectionEndIndex += 1


if __name__ == "__main__":
    serviceAccount: Client = gspread.service_account()
    sheet: Spreadsheet = serviceAccount.open("FinBridge")
    positions = PositionsTable(sheet.worksheet("Positions"), "Saxo")
    print(positions.name, positions.length(), positions.positions())
    positions.add_or_update_position("Test", 1.0, 1.1, 0.1, 0)
    # positions.remove_position("Test")
    positions.add_or_update_position("Coca-Cola", 1.0, 1.1, 0.1, 110.0)
    positions.add_or_update_position("Exxon Mobil Corporation", 1.0, 1.1, 0.1, 110.0)
    positions.add_or_update_position("Apple Inc.", 1.0, 1.1, 0.1, 110.0)
    positions.add_or_update_position("Cash", 0, 100000.25, 0, 0)