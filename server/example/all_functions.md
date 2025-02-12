class SubRecord:
    def __init__(self):
    def sub(self, code_list, subtype_list, is_orderbook_detail, extended_time):
    def unsub(self, code_list, subtype_list):
    def unsub_all(self):
    def get_sub_list(self):
    def _merge_sub_list(self, orig_sub_list):
    def _conv_sub_list(self, orig_sub_list):



class OpenQuoteContext(OpenContextBase):
    def __init__(self, host='127.0.0.1', port=11111, is_encrypt=None, is_async_connect=False):
    def close(self):
    def on_api_socket_reconnected(self):
    def request_trading_days(self, market=None, start=None, end=None, code=None):
    def get_stock_basicinfo(self, market, stock_type=SecurityType.STOCK, code_list=None):
    def request_history_kline(self,
    def get_market_snapshot(self, code_list):
    def get_rt_data(self, code):
    def get_plate_list(self, market, plate_class):
    def get_plate_stock(self, plate_code, sort_field=SortField.CODE, ascend=True):
    def get_broker_queue(self, code):
    def _check_subscribe_param(self, code_list, subtype_list):
    def subscribe(self, code_list, subtype_list, is_first_push=True, subscribe_push=True, is_detailed_orderbook=False, extended_time=False):
    def _subscribe_impl(self, code_list, subtype_list, is_first_push, subscribe_push=True, is_detailed_orderbook=False, extended_time=False):
    def _reconnect_subscribe(self, code_list, subtype_list, is_detailed_orderbook, extended_time):
    def unsubscribe(self, code_list, subtype_list, unsubscribe_all=False):
    def unsubscribe_all(self):
    def query_subscription(self, is_all_conn=True):
    def get_stock_quote(self, code_list):
    def get_rt_ticker(self, code, num=500):
    def get_cur_kline(self, code, num, ktype=SubType.K_DAY, autype=AuType.QFQ):
    def get_order_book(self, code, num = 10):
    def get_referencestock_list(self, code, reference_type):
    def get_owner_plate(self, code_list):
    def get_holding_change_list(self, code, holder_type, start=None, end=None):
    def get_option_chain(self, code, index_option_type=IndexOptionType.NORMAL, start=None, end=None, option_type=OptionType.ALL, option_cond_type=OptionCondType.ALL, data_filter = None):
            start, end, delta_days=29, default_time_end='00:00:00', prefer_end_now=False)
    def get_warrant(self, stock_owner='', req=None):
    def get_history_kl_quota(self, get_detail=False):
    def get_rehab(self, code):
    def get_user_info(self, info_field=[]):
    def get_capital_distribution(self, stock_code):
    def get_capital_flow(self, stock_code, period_type = PeriodType.INTRADAY, start=None, end=None):
    def verification(self, verification_type=VerificationType.NONE, verification_op=VerificationOp.NONE, code=""):
    def get_delay_statistics(self, type_list, qot_push_stage, segment_list):
    def modify_user_security(self, group_name, op, code_list):
    def get_user_security(self, group_name):
    def get_stock_filter(self, market, filter_list=None, plate_code=None, begin=0, num=200):
    def get_code_change(self, code_list=[], time_filter_list=[], type_list=[]):
    def get_ipo_list(self, market):
    def get_future_info(self, code_list):
    def set_price_reminder(self, code, op, key=None, reminder_type=None, reminder_freq=None, value=None, note=None):
    def get_price_reminder(self, code=None, market=None):
    def get_user_security_group(self, group_type = UserSecurityGroupType.ALL):
    def get_market_state(self, code_list):
    def get_option_expiration_date(self, code, index_option_type=IndexOptionType.NORMAL):

class OpenTradeContextBase(OpenContextBase):
    def __init__(self, trd_mkt, host="127.0.0.1", port=11111, is_encrypt=None, security_firm=SecurityFirm.FUTUSECURITIES, trd_category=TrdCategory.NONE, need_general_sec_acc=False):
    def close(self):
    def on_api_socket_reconnected(self):
    def is_futures_market_sim(self, trdMkt_list):
    def get_acc_list(self):
    def unlock_trade(self, password=None, password_md5=None, is_unlock=True):
    def _async_sub_acc_push(self, acc_id_list):
    def on_async_sub_acc_push(self, ret_code, msg):
    def _check_trd_env(self, trd_env):
    def __check_acc_sub_push(self):
    def _check_acc_id(self, trd_env, acc_id):
            acc_id = self._get_default_acc_id(trd_env)
    def _check_order_status(self, status_filter_list):
    def _get_default_acc_id(self, trd_env):
    def _get_default_acc_id(self, trd_env):
    def _get_acc_id_by_acc_index(self, trd_env, acc_index=0):
                msg = "No available real accounts with {0} market authority in {1}, please check the input parameters 'security_firm' and 'filter_trdmarket' of {2}.".format(self.__trd_mkt, get_string_by_securityFirm(self.__security_firm), self.__class__.__name__)
                msg = "No available paper accounts with {0} market authority in {1}, please check the input parameters 'security_firm' and 'filter_trdmarket' of {2}.".format(self.__trd_mkt, get_string_by_securityFirm(self.__security_firm), self.__class__.__name__)
    def _check_acc_id_exist(self, trd_env, acc_id):
    def _check_acc_id_and_acc_index(self, trd_env, acc_id, acc_index):
    def accinfo_query(self, trd_env=TrdEnv.REAL, acc_id=0, acc_index=0, refresh_cache=False, currency=Currency.HKD):
    def _get_trd_market_from_market(self, qot_market, trd_env, trd_category):
    def _check_stock_code(self, code):
    def _split_stock_code(self, code):
    def position_list_query(self, code='', pl_ratio_min=None,
    def order_list_query(self, order_id="", status_filter_list=[], code='', start='', end='',
    def _order_list_query_impl(self, order_id, status_filter_list, code, start, end, trd_env, acc_id, refresh_cache, trd_mkt, order_market):
    def place_order(self, price, qty, code, trd_side, order_type=OrderType.NORMAL,
    def modify_order(self, modify_order_op, order_id, qty, price,
    def cancel_all_order(self, trd_env=TrdEnv.REAL, acc_id=0, acc_index=0, trdmarket=TrdMarket.NONE):
    def change_order(self, order_id, price, qty, adjust_limit=0, trd_env=TrdEnv.REAL, acc_id=0):
    def deal_list_query(self, code="", trd_env=TrdEnv.REAL, acc_id=0, acc_index=0, refresh_cache=False, deal_market= TrdMarket.NONE):
    def history_order_list_query(self, status_filter_list=[], code='', start='', end='',
    def order_fee_query(self, order_id_list=[], trd_env=TrdEnv.REAL, acc_id=0, acc_index=0):
    def history_deal_list_query(self, code='', start='', end='', trd_env=TrdEnv.REAL, acc_id=0, acc_index=0, deal_market= TrdMarket.NONE):
    def acctradinginfo_query(self, order_type, code, price, order_id=None, adjust_limit=0, trd_env=TrdEnv.REAL, acc_id=0, acc_index=0):
    def get_margin_ratio(self, code_list):

class OpenHKTradeContext(OpenTradeContextBase):
    def __init__(self, host="127.0.0.1", port=11111, is_encrypt=None, security_firm=SecurityFirm.FUTUSECURITIES):
class OpenUSTradeContext(OpenTradeContextBase):
    def __init__(self, host="127.0.0.1", port=11111, is_encrypt=None, security_firm=SecurityFirm.FUTUSECURITIES):
class OpenHKCCTradeContext(OpenTradeContextBase):
    def __init__(self, host="127.0.0.1", port=11111, is_encrypt=None, security_firm=SecurityFirm.FUTUSECURITIES):
class OpenCNTradeContext(OpenTradeContextBase):
    def __init__(self, host="127.0.0.1", port=11111, is_encrypt=None, security_firm=SecurityFirm.FUTUSECURITIES):
class OpenFutureTradeContext(OpenTradeContextBase):
    def __init__(self, host="127.0.0.1", port=11111, is_encrypt=None, security_firm=SecurityFirm.FUTUSECURITIES):
class OpenSecTradeContext(OpenTradeContextBase):
    def __init__(self, filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, is_encrypt=None, security_firm=SecurityFirm.FUTUSECURITIES):
