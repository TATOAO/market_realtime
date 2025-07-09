import time
from futu import OrderBookHandlerBase, RET_OK, RET_ERROR, OpenQuoteContext, SubType
from config import settings

class OrderBookTest(OrderBookHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(OrderBookTest,self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("OrderBookTest: error, msg: %s" % data)
            return RET_ERROR, data
        print("OrderBookTest ", data) # OrderBookTest 自己的处理逻辑
        return RET_OK, data

# Use configuration instead of hardcoded values
def main():
    quote_ctx = OpenQuoteContext(
        host=settings.futu_host, 
        port=settings.futu_port
    )
    handler = OrderBookTest()
    quote_ctx.set_handler(handler)  # 设置实时摆盘回调
    # quote_ctx.unsubscribe(['HK.00700'], [SubType.ORDER_BOOK, SubType.RT_DATA, SubType.TICKER])
    quote_ctx.subscribe(['HK.00700'], [SubType.ORDER_BOOK, SubType.RT_DATA, SubType.TICKER])  # 订阅买卖摆盘类型，OpenD 开始持续收到服务器的推送
    time.sleep(200)  #  设置脚本接收 OpenD 的推送持续时间为15秒
    quote_ctx.close()  # 关闭当条连接，OpenD 会在1分钟后自动取消相应股票相应类型的订阅

# python -m core.api_client.futu_client
if __name__ == "__main__":
    main()