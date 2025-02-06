

# Make sure you have installed the futu API package:
#   pip install futu-api

from futu import OpenSecTradeContext, TrdMarket, SecurityFirm, TrdEnv, Currency, RET_OK

def get_account_funds():
    # Create a trading context.
    # You can adjust the filter_trdmarket (e.g. TrdMarket.HK for Hong Kong) and other parameters as needed.
    trd_ctx = OpenSecTradeContext(
        filter_trdmarket=TrdMarket.HK,
        host='127.0.0.1',
        port=11111,
        security_firm=SecurityFirm.FUTUSECURITIES
    )

    # Call the API to query account funds.
    # The function accinfo_query queries the account’s funds details such as total assets, cash,
    # securities assets, buying power, etc. The parameters below use the default trading environment (REAL),
    # account id (0 means use the acc_index), acc_index (0 means the first account) and the currency (HKD).
    ret, data = trd_ctx.accinfo_query(
        trd_env=TrdEnv.REAL,
        acc_id=0,           # Use 0 to indicate using the account index below
        acc_index=0,        # The first trading account
        refresh_cache=False,  # Use cached data; set True to force refresh from the server.
        currency=Currency.HKD  # Currency in which funds are denominated (only applicable for some account types)
    )

    if ret == RET_OK:
        # 'data' is a pandas DataFrame containing your funds information.
        print("Account Funds:")
        print(data)

        # If you want to access the funds details as a list (for example, each row as a dictionary):
        print("\nList of owned entities (fund details):")
        for index, row in data.iterrows():
            # Each 'row' represents a set of funds-related data
            print(row.to_dict())
    else:
        # Handle error: data contains an error description.
        print("Error querying account funds:", data)



    # Call the API to query the list of positions (stocks, bonds, etc.) in the account.
    ret, data = trd_ctx.position_list_query(trd_env=TrdEnv.REAL, acc_id=0)  # Use the account index if needed.
    if ret == RET_OK:
        # 'data' is a pandas DataFrame containing your funds information.

        # If you want to access the funds details as a list (for example, each row as a dictionary):
        print("\nList of owned entities (fund details):")
        for index, row in data.iterrows():
            # Each 'row' represents a set of funds-related data
            print(row.to_dict())



    # Always close the connection after finishing.
    trd_ctx.close()

if __name__ == '__main__':
    get_account_funds()

