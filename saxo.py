from saxo_openapi import API
import saxo_openapi.endpoints.rootservices as rs
import saxo_openapi.endpoints.portfolio as ps

from pprint import pprint


class SaxoPosition:
    """Represents single position in Saxo Bank portfolio. Available fields:
    - name
    - amount
    - open_price
    - current_price
    - profit_loss
    - exposure
    """

    __match_args__ = ('name', 'amount', 'open_price', 'current_price', 'profit_loss', 'exposure')

    def __init__(self, name: str, amount: float, open_price: float, current_price: float,
                 profit_loss: float, exposure: float):
        self.name = name
        self.amount = amount
        self.open_price = open_price
        self.current_price = current_price
        self.profit_loss = profit_loss
        self.exposure = exposure

    @classmethod
    def parse(cls, raw: dict):
        def safe_get(d, key, default=None):
            if key in d:
                return d[key]
            else:
                return default
        name = raw['DisplayAndFormat']['Description']
        base = raw['NetPositionBase']
        view = raw['NetPositionView']
        amount = safe_get(base, 'Amount', 0.0)
        open_price = -safe_get(view, 'MarketValueOpenInBaseCurrency', -0.0)
        current_price = safe_get(view, 'MarketValueInBaseCurrency', 0.0)
        profit_loss = safe_get(view, 'TradeCostsTotalInBaseCurrency', 0.0)
        exposure = safe_get(view, 'ExposureInBaseCurrency', 0.0)
        if current_price == 0.0 and open_price != 0.0:
            current_price = open_price + profit_loss
        return SaxoPosition(name, amount, open_price, current_price, profit_loss, exposure)

class SaxoConnection:
    """Connection to Saxo Bank platform"""

    def __init__(self, environment: str, token: str):
        self._client = API(access_token=token, environment=environment)
        # let's make a diagnostics request, it should return '' with a state 200
        r = rs.diagnostics.Get()
        rv = self._client.request(r)
        assert rv is None and r.status_code == 200

    def get_account_info(self) -> dict[str, object]:
        req = ps.accounts.AccountsMe()
        return self._client.request(req)

    def get_account_balance(self) -> float:
        req = ps.balances.AccountBalancesMe()
        resp = self._client.request(req)
        pprint(resp)
        return resp['TotalValue']

    def get_account_positions(self) -> list[SaxoPosition]:
        req = ps.netpositions.NetPositionsMe({'FieldGroups': 'NetPositionBase,NetPositionView,DisplayAndFormat'})
        print(req)
        resp = self._client.request(req)
        print("PositionsMe: response=")
        pprint(resp)
        _positions = []
        for p in resp['Data']:
            _positions.append(SaxoPosition.parse(p))
        return _positions

if __name__ == "__main__":
    token = "eyJhbGciOiJFUzI1NiIsIng1dCI6IkRFNDc0QUQ1Q0NGRUFFRTlDRThCRDQ3ODlFRTZDOTEyRjVCM0UzOTQifQ.eyJvYWEiOiI3Nzc3NSIsImlzcyI6Im9hIiwiYWlkIjoiMTA5IiwidWlkIjoidXw0R01CQk42amxEbXBCb3kyQ0JMUT09IiwiY2lkIjoidXw0R01CQk42amxEbXBCb3kyQ0JMUT09IiwiaXNhIjoiRmFsc2UiLCJ0aWQiOiIyMDAyIiwic2lkIjoiYTQzYTNmNDg1OWIyNGM5YWIyOTY0MGZkYmU3OTA5NTYiLCJkZ2kiOiI4NCIsImV4cCI6IjE3MDAxMzY0NjEiLCJvYWwiOiIxRiIsImlpZCI6ImViZWNlYmM0NmIxYTRkNzA5NmRlMDhkYjkxYjBhNzUxIn0.ZgISXe3I1HLtp_ki2KO7-GomNe4RXgxmsp8LiHSO-_46yQ0WPqqz7WD2juDHsJh2VsfIcY3VYjn-nuf-uQf8oA"
    connection = SaxoConnection("simulation", token)
    # connection.get_account_info()
    # print(f"Account balance = {connection.get_account_balance()} EUR")
    for p in connection.get_account_positions():
        print(f"{p.name} {p.amount} {p.open_price} {p.current_price} {p.profit_loss} {p.exposure}")