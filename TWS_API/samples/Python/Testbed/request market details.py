from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract


class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, reqId, errorCode: int, errorString: str):
        print("Error: ", reqId, " ", errorString)

    def contractDetails(self, reqId, contractDetails):
        print("contractDetails:",reqId," ",contractDetails)

def main():
    app = TestApp()

    app.connect("13.84.231.198", 9999, 0)
    contract = Contract()
    contract.symbol = "IBEX"
    contract.secType = "FUT"
    contract.exchange = "MEFFRV"

    app.reqContractDetails(1,contract)

    app.run()


if __name__ == "__main__":
    main()
