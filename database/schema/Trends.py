from .meta import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey

class Trends(Base):
    """

    
    """
    __tablename__ = 'NewsAssets'

    trends_id = Column(Integer, primary_key=True, autoincrement=True)
    news_hash = Column(Integer, ForeignKey('news.news_hash'))
    asset_id = Column(Integer, ForeignKey('Assets.asset_id'))
    relevance = Column(Float)
    relation = Column(String)
