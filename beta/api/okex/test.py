# encoding: UTF-8

from __future__ import absolute_import
from .vnokex import *

# 在OkCoin网站申请这两个Key，分别对应用户名和密码
apiKey = ''
secretKey = ''

# 创建API对象
api = OKEX_Sub_Spot_Api()

api.connect_Subpot(apiKey, secretKey, True)

sleep(3)

#api.login()
#api.subscribeSpotTicker("bch_btc")
#api.subscribeSpotDepth("bch_btc")
#api.subscribeSpotDepth5("bch_btc")
#api.subscribeSpotDeals("bch_btc")
#api.subscribeSpotKlines("bch_btc","30min")

api.spotTrade("tnb_btc","buy", 0.00000220, 600 )
#api.spotCancelOrder("etc_btc","44274138")
#api.spotUserInfo()
#api.spotOrderInfo("etc_btc", 44284731)

# api = OKEX_Contract_Api()
# api.connect_Contract(apiKey, secretKey, True)

# sleep(3)
#api.subsribeFutureTicker("btc","this_week")
#api.subscribeFutureKline("btc","this_week","30min")
#api.subscribeFutureDepth("btc","this_week")
#api.subscribeFutureDepth20("btc","this_week")
#api.subscribeFutureTrades("btc","this_week")
#api.subscribeFutureIndex("btc")
#api.subscribeFutureForecast_price("btc")

#api.login()
#api.futureTrade( "etc_usd", "this_week" ,"1" , 20 , 1 , _match_price = '0' , _lever_rate = '10')  # 14245727693
#api.futureCancelOrder("etc_usd","14245727693" , "this_week")
#api.futureUserInfo()
#api.futureOrderInfo("etc_usd" , "14245727693" , "this_week" , '1', '1'  , '10')
# api.subscribeFutureTrades()

'''
合约账户信息、 持仓信息等，在登录后都会自动推送。。。官方文档这样写的，还没实际验证过
'''