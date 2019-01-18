import vnctptd
from vnctptd import *

print(vnctptd)
print(dir(vnctptd))

for i in dir(vnctptd):
    print(f"{i} : {vnctptd.__dict__[i]}")

print("creating ctp api")
api = CThostFtdcTraderApi.CreateFtdcTraderApi("flow2")

print("creating ctp spi")


class Spi(CThostFtdcTraderSpi):
    
    def OnFrontConnected(self) -> None:
        print("OnFrontConnected!")
    
    def OnFrontDisconnected(self, nReason: int) -> None:
        print("OnFrontDisconnected!")
    
    def OnRspAuthenticate(self, pRspAuthenticateField: CThostFtdcRspAuthenticateField,
                          pRspInfo: CThostFtdcRspInfoField, nRequestID: int, bIsLast: bool) -> None:
        print("OnRspAuthenticate!")
    
    def OnRspUserLogin(self, pRspUserLogin: CThostFtdcRspUserLoginField,
                       pRspInfo: CThostFtdcRspInfoField, nRequestID: int, bIsLast: bool) -> None:
        print("OnRspUserLogin!")
    
    def OnRspUserLogout(self, pUserLogout: CThostFtdcUserLogoutField,
                        pRspInfo: CThostFtdcRspInfoField, nRequestID: int, bIsLast: bool) -> None:
        print("OnRspUserLogout!")
    
    def OnRspError(self, pRspInfo: CThostFtdcRspInfoField, nRequestID: int, bIsLast: bool) -> None:
        print("OnRspError!")


spi = Spi()

print("registering spi")
api.RegisterSpi(spi)
print("registering front")
api.RegisterFront("tcp://180.168.146.187:10030")
print("Init() ...")
api.Init()

print("Join() ...")
while True:
    pass


input()
