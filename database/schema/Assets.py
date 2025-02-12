from .meta import Base
from sqlalchemy import Boolean, Column, Text, Integer, String, Float, DateTime, ForeignKey


class DataSchema():
    pass


class PlateList(Base, DataSchema):
    """
    __tablename__ = 'PlateList'
    code                    str            股票代码
    plate_name              str            板块名字
    plate_id                str            板块id
    """
    __tablename__ = 'PlateList'

    plate_id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False)
    plate_name = Column(String, nullable=False)


class RTData(Base, DataSchema):
    """
    __tablename__ = 'RTData'

        code  name                 time  is_blank  opened_mins  cur_price  last_close   avg_price  volume     turnover
    0  HK.00700  腾讯控股  2025-02-11 09:30:00     False          570      440.0       437.0  440.000000  905000  39820000
    0.0
    1  HK.00700  腾讯控股  2025-02-11 09:31:00     False          571      440.6       437.0  440.053874  714700  31455526
    0.0
    2  HK.00700  腾讯控股  2025-02-11 09:32:00     False          572      439.0       437.0  440.042516  281100  12367755
    5.0
    3  HK.00700  腾讯控股  2025-02-11 09:33:00     False          573      438.0       437.0  439.884347  212800   9330674
    0.0
    4  HK.00700  腾讯控股  2025-02-11 09:34:00     False          574      437.0       437.0  439.644709  261000  11424077
    0.0

    """
    __tablename__ = 'RTData'

    code = Column(String, primary_key=True)
    name = Column(String)
    time = Column(DateTime)
    is_blank = Column(Boolean)
    opened_mins = Column(Integer)
    cur_price = Column(Float)
    last_close = Column(Float)
    avg_price = Column(Float)
    volume = Column(Integer)
    turnover = Column(Float)


class BasicInfo(Base, DataSchema):
    """
    =================   ===========   ==================================================================
    参数                  类型                        说明
    =================   ===========   ==================================================================
    code                str            股票代码
    name                str            名字
    lot_size            int            每手数量
    stock_type          str            股票类型，参见SecurityType
    stock_child_type    str            窝轮子类型，参见WrtType
    stock_owner         str            所属正股的代码
    option_type         str            期权类型，Qot_Common.OptionType
    strike_time         str            行权日
    strike_price        float          行权价
    suspension          bool           是否停牌(True表示停牌)
    listing_date        str            上市时间
    stock_id            int            股票id
    delisting           bool           是否退市
    index_option_type   str            指数期权类型（期权特有字段）
    main_contract       bool           是否主连合约（期货特有字段）
    last_trade_time     string         最后交易时间（期货特有字段，非主连期货合约才有值）
    exchange_type       str            所属交易所，Qot_Common.ExchType
    """

    __tablename__ = 'BasicInfo'

    code = Column(String, primary_key=True, nullable=False)
    name = Column(String)
    lot_size = Column(Integer)
    stock_type = Column(String)
    stock_child_type = Column(String)
    stock_owner = Column(String)
    stock_id = Column(Integer)
    option_type = Column(String)
    strike_time = Column(String)
    strike_price = Column(Float)
    suspension = Column(Boolean)
    listing_date = Column(String)
    delisting = Column(Boolean)
    index_option_type = Column(String)
    main_contract = Column(Boolean)
    last_trade_time = Column(String)
    exchange_type = Column(String)



