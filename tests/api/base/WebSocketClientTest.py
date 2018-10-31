# encoding: UTF-8
import unittest

from Promise import Promise
from vnpy.api.websocket import WebsocketClient


class TestWebsocketClient(WebsocketClient):
    
    def __init__(self):
        host = 'wss://echo.websocket.org'
        super(TestWebsocketClient, self).__init__()
        self.init(host)
        self.p = Promise()
        self.cp = Promise()
    
    def onPacket(self, packet):
        self.p.set_result(packet)
        pass
    
    def onConnected(self):
        self.cp.set_result(True)
        pass
    
    def onError(self, exceptionType, exceptionValue, tb):
        self.p.set_exception(exceptionValue)
        pass


class WebsocketClientTest(unittest.TestCase):
    
    def setUp(self):
        self.c = TestWebsocketClient()
        self.c.start()
        self.c.cp.get(3) # wait for connected
    
    def tearDown(self):
        self.c.stop()
    
    def test_sendReq(self):
        req = {
            'name': 'val'
        }
        self.c.sendPacket(req)
        res = self.c.p.get(3)
        
        self.assertEqual(res, req)

    def test_parseError(self):
        class CustomException(Exception): pass
    
        def onPacket(packet):
            raise CustomException("Just a exception")
    
        self.c.onPacket = onPacket
        req = {
            'name': 'val'
        }
        self.c.sendPacket(req)
    
        with self.assertRaises(CustomException):
            self.c.p.get(3)


if __name__ == '__main__':
    unittest.main()
