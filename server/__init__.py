from futu import OpenSecTradeContext, TrdMarket, SecurityFirm, TrdEnv, Currency, RET_OK

class FutuAPIHandler:
    """

    A class to handle all interactions with the Futu API for trading purposes.
    This class provides methods to query account funds and position lists.

    1. `__init__`: The constructor method for the `FutuAPIHandler` class. It initializes the class by creating a trading context using the Futu API.

    2. `close`: A method that closes the trading context, which is important to release resources and ensure that the connection to the Futu API server is properly terminated.

    3. `get_account_funds`: A method that queries the account funds from the Futu API. It returns a pandas DataFrame with the account funds data if successful, or `None` if there is an error.

    4. `get_position_list`: A method that queries the list of positions (such as stocks, bonds, etc.) from the Futu API. It returns a pandas DataFrame with the position list data if successful, or `None` if there is an error.

    """
    def __init__(self, filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES):
        self.trd_ctx = OpenSecTradeContext(
            filter_trdmarket=filter_trdmarket,
            host=host,
            port=port,
            security_firm=security_firm
        )

    def close(self):
        """
     `close`: A method that closes the trading context, which is important to release resources and ensure that the connection to the Futu API server is properly terminated.
        """
        self.trd_ctx.close()

    def get_account_funds(self, trd_env=TrdEnv.REAL, acc_id=0, acc_index=0, refresh_cache=False, currency=Currency.HKD):
        """
        Queries the account funds from the Futu API.

        :param trd_env: The trading environment (e.g., TrdEnv.REAL for real trading).
        :param acc_id: The account ID to query.
        :param acc_index: The account index to query.
        :param refresh_cache: Whether to refresh the cache.
        :param currency: The currency to query.
        :return: A pandas DataFrame with the account funds data if successful, otherwise None.
        """
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

    def get_position_list(self, trd_env=TrdEnv.REAL, acc_id=0):
        """
        Queries the list of positions (stocks, bonds, etc.) from the Futu API.

        :param trd_env: The trading environment (e.g., TrdEnv.REAL for real trading).
        :param acc_id: The account ID to query.
        :return: A pandas DataFrame with the position list data if successful, otherwise None.
        """
        ret, data = self.trd_ctx.position_list_query(trd_env=trd_env, acc_id=acc_id)
        if ret == RET_OK:
            return data
        else:
            print("Error querying position list:", data)
            return None

# Example usage:
if __name__ == '__main__':
    futu_handler = FutuAPIHandler()
    try:
        funds_data = futu_handler.get_account_funds()
        if funds_data is not None:
            print("Account Funds:")
            print(funds_data)

        positions_data = futu_handler.get_position_list()
        if positions_data is not None:
            print("\nList of owned entities (fund details):")
            for index, row in positions_data.iterrows():
                print(row.to_dict())

    finally:
        futu_handler.close()
