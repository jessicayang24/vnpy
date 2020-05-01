# VNPY 1Token 文档

## 更新SDK

把  `https://raw.githubusercontent.com/1token-trade/vnpy/dev-1token/vnpy/gateway/onetoken/onetoken_gateway.py` 复制到 `c:\vnstudio\lib\site-packages\vnpy\gateway\onetoken` 下面

## 行情

我们提供了一个供测试的

* 输入测试 OT Key: `vglTLYcq-Unx1gO3S-VCHQaMs5-HvVRQkcX`  

* 输入测试 OT Secret: `NNXveWWx-TqbNNtMZ-xB6sska0-CVDQBP40`
* 交易所选择 OKEX
* 账号填写 mock-vnpyplay
* 代理地址留空
* 代理端口填0

在左上角选择交易所, 填入交易对, 按回车键, 一切正常的话, 行情会添加在右侧图表里面

* 由于1Token和VNPY的架构有所不同 所以选择有一定的区别
  * 比如okef的期货交易所 在左上角只需要选择OKEX, 下面代码填写 eth.usd.q 即可
  * 比如okex的现货交易所 在左上角只需要选择OKEX, 下面代码填写 eth.usdt 即可

<a href="https://1token.trade/docs#/instruction/naming-rules?id=%e5%b8%81%e5%b8%81%e4%ba%a4%e6%98%93%e4%bb%a3%e7%a0%81" target="_blank">
https://1token.trade/docs#/instruction/naming-rules?id=币币交易代码 </a>

![image](https://raw.githubusercontent.com/1token-trade/vnpy/dev-1token/vnpy/gateway/onetoken/quote.png)


## 交易

* 模拟账号 填入 代码, 价格, 数量之后 可以正常下单
![image](https://raw.githubusercontent.com/1token-trade/vnpy/dev-1token/vnpy/gateway/onetoken/trade.png)
