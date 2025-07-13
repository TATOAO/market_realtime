from akshare import stock_us_spot, stock_us_daily

def get_us_stock_list():
    return stock_us_spot()


# python -m app.core.api_client.akshare.us_stock
if __name__ == "__main__":
    result = get_us_stock_list()
    import ipdb; ipdb.set_trace()

    print('end')