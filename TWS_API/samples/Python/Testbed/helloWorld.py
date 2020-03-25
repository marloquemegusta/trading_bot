from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import datetime

import pandas as pd

class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, reqId, errorCode: int, errorString: str):
        print("Error: ", reqId, " ", errorString)

    def historicalData(self, reqId, bar):
        print(type(bar))

def main():
    app = TestApp()

    app.connect("13.84.231.198", 9999, 0)
    contract = Contract()
    contract.symbol = "IBEX"
    contract.secType = "CONTFUT"
    contract.exchange = "MEFFRV"

    app.reqHistoricalData(0, contract, "", "4 D", "1 day", "MIDPOINT", 0, 1, False, [])
    app.run()


if __name__ == "__main__":
    main()
