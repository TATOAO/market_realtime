import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
from futu import OpenSecTradeContext, TrdMarket, SecurityFirm, TrdEnv, Currency, RET_OK, OpenQuoteContext

class FutuAPIHandler:
    """
    A class to handle all interactions with the Futu API for trading purposes.
    This class provides methods to query account funds and position lists.

    1. `__init__`: The constructor method for the `FutuAPIHandler` class. It initializes the class by creating a trading context using the Futu API.

    2. `close`: A method that closes the trading context, which is important to release resources and ensure that the connection to the Futu API server is properly terminated.

    3. `get_account_funds`: A method that queries the account funds from the Futu API. It returns a pandas DataFrame with the account funds data if successful, or `None` if there is an error.

    4. `get_position_list`: A method that queries the list of positions (such as stocks, bonds, etc.) from the Futu API. It returns a pandas DataFrame with the position list data if successful, or `None` if there is an error.

    5. Queries the historical price data for a given stock symbol.
    """

    def __init__(self, filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES):
        self.executor = ThreadPoolExecutor()
        self.trd_ctx = OpenSecTradeContext(
            filter_trdmarket=filter_trdmarket,
            host=host,
            port=port,
            security_firm=security_firm
        )
        self.quote_ctx = OpenQuoteContext(host=host, port=port)

    async def close(self):
        """
        `close`: A method that closes the trading context, which is important to release resources and ensure that the connection to the Futu API server is properly terminated.
        """
        # self.trd_ctx.close()
        # self.quote_ctx.close()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.trd_ctx.close)
        await loop.run_in_executor(None, self.quote_ctx.close)
        self.executor.shutdown(wait=True)

    async def get_account_funds(self, trd_env=TrdEnv.REAL, acc_id=0, acc_index=0, refresh_cache=False, currency=Currency.HKD):
        """
        Queries the account funds from the Futu API.

        :param trd_env: The trading environment (e.g., TrdEnv.REAL for real trading).
        :param acc_id: The account ID to query.
        :param acc_index: The account index to query.
        :param refresh_cache: Whether to refresh the cache.
        :param currency: The currency to query.
        :return: A pandas DataFrame with the account funds data if successful, otherwise None.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._query_account_funds, trd_env, acc_id, acc_index, refresh_cache, currency)

    def _query_account_funds(self, trd_env, acc_id, acc_index, refresh_cache, currency):
        ret, data = self.trd_ctx.accinfo_query(
            trd_env=trd_env,
            acc_id=acc_id,
            acc_index=acc_index,
            refresh_cache=refresh_cache,
            currency=currency
        )
        if ret == RET_OK:
            return data
        else:
            print("Error querying account funds:", data)
            return None

    async def get_position_list(self, trd_env=TrdEnv.REAL, acc_id=0):
        """
        Queries the list of positions (stocks, bonds, etc.) from the Futu API.

        :param trd_env: The trading environment (e.g., TrdEnv.REAL for real trading).
        :param acc_id: The account ID to query.
        :return: A pandas DataFrame with the position list data if successful, otherwise None.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._query_position_list, trd_env, acc_id)

    def _query_position_list(self, trd_env, acc_id):
        ret, data = self.trd_ctx.position_list_query(trd_env=trd_env, acc_id=acc_id)
        if ret == RET_OK:
            return data
        else:
            print("Error querying position list:", data)
            return None

    async def get_stock_price_history(self, symbol, start_date, duration_days=30):
        """
        Queries the historical price data for a given stock symbol.

        :param symbol: The stock symbol for which to query the price history.
        :param start_date: The start date for the price history query in 'YYYY-MM-DD' format.
        :param duration_days: The number of days for which to query the price history (default is 30 days).
        :return: A pandas DataFrame with the historical price data if successful, otherwise None.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._query_stock_price_history, symbol, start_date, duration_days)

    def _query_stock_price_history(self, symbol, start_date, duration_days):
        # Calculate the end date based on the current date and duration_days
        now = datetime.datetime.now()
        end_date = now - datetime.timedelta(days=now.day - 1)  # Go to the start of the current month
        end_date += datetime.timedelta(days=duration_days - 1)  # Add duration_days to get the end date

        # Format start_date and end_date as strings in 'YYYY-MM-DD' format
        start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y-%m-%d')
        end_time = end_date.strftime('%Y-%m-%d')

        ret, data = self.quote_ctx.request_history_kline(symbol, start=start_time, end=end_time)
        if ret == RET_OK:
            return data
        else:
            print("Error querying stock price history:", data)
            return None


def main():
    asyncio.run(async_main())

async def async_main():
    
    futu_handler = FutuAPIHandler()
    try:
        funds_data = await futu_handler.get_account_funds()
        if funds_data is not None:
            print("Account Funds:")
            print(funds_data)

        positions_data = await futu_handler.get_position_list()
        if positions_data is not None:
            print("\nList of owned entities (fund details):")
            for index, row in positions_data.iterrows():
                print(row.to_dict())
    finally:
        await futu_handler.close()
        print('xxx')

if __name__ == "__main__":
    main()

