from akshare import stock_zh_a_spot_em

"""
 "stock_zh_a_spot"  # 新浪 A 股实时行情数据
 "stock_zh_a_spot_em"  # 东财 A 股实时行情数据
 "stock_sh_a_spot_em"  # 东财沪 A 股实时行情数据
 "stock_sz_a_spot_em"  # 东财深 A 股实时行情数据
 "stock_bj_a_spot_em"  # 东财京 A 股实时行情数据
 "stock_new_a_spot_em"  # 东财新股实时行情数据
 "stock_kc_a_spot_em"  # 东财科创板实时行情数据

"""


def main():
    result = stock_zh_a_spot_em()
    # save result into pickle file
    import pickle
    import os
    with open(os.path.join(os.path.dirname(__file__), 'realtime_stock_zh_a_em.pkl'), 'wb') as f:
        pickle.dump(result, f)
    

    import ipdb 
    ipdb.set_trace()

# python -m core.api_client.akshare.realtime_stock
if __name__ == "__main__":
    main()