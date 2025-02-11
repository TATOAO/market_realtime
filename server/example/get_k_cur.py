
from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret_sub, err_message = quote_ctx.subscribe(['HK.00700'], [SubType.RT_DATA], subscribe_push=False)
# Subscribe to the Time Frame data type first. After the subscription is successful, OpenD will continue to receive pushes from the server, False means that there is no need to push to the script temporarily


if ret_sub == RET_OK:   # Successfully subscribed
    ret, data = quote_ctx.get_cur_kline('HK.00700', 10)   # Get Time Frame data once
    if ret == RET_OK:
        print(data)
    else:
        print('error:', data)
else:
    print('subscription failed', err_message)
quote_ctx.close()   # Close the current link, OpenD will automatically cancel the corresponding type of subscription for the corresponding stock after 1 minute
 

