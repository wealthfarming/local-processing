from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import class_mapper, relationship
from sqlalchemy import Column, Integer, Text, JSON, TIMESTAMP, Numeric, func, create_engine
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
load_dotenv()

db_engine = os.getenv("DB_LOCAL_URL")
engine = create_engine(db_engine)
Base = declarative_base()

class TrackingDaily(Base):
    __tablename__ = "tracking_daily"  # Tên bảng

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_logs = Column(JSON, nullable=True)  # JSONB column
    account_id = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=False), server_default=func.now(), onupdate=func.now(), nullable=False)
    broker_name = Column(Text, nullable=False)
    platform_name = Column(Text, nullable=False)

    def to_dict(self):
        """
        Convert the SQLAlchemy object to a dictionary.
        """
        return {column.key: getattr(self, column.key) for column in class_mapper(self.__class__).columns}

    def __repr__(self):
        return f"<TrackingDailyAccount(id={self.id}, broker_name={self.broker_name}, platform_name={self.platform_name})>"
    
class HistoryDealsSeries(Base):
    __tablename__ = "history_deals_series"  # Tên bảng

    id = Column(Integer, primary_key=True, autoincrement=True)
    time_iso = Column(Text, nullable=True) 
    tracking_account_id = Column(Text, nullable=True) #
    balance_amount = Column(Numeric(precision=18, scale=2), nullable=True, default=0)
    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=False), server_default=func.now(), onupdate=func.now(), nullable=False)
    tracking_daily_id = Column(Integer, nullable=False) # ref ID to TrackingDaily
    

    def to_dict(self):
        """
        Convert the SQLAlchemy object to a dictionary.
        """
        return {column.key: getattr(self, column.key) for column in class_mapper(self.__class__).columns}

# db_engine = "<dialect>+<driver>://<username>:<password>@<host>:<port>/<db_name>"
Base.metadata.create_all(engine)
