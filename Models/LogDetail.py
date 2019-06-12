from sqlalchemy import Column, String, Integer, TIMESTAMP
from Models.Model import Model


class LogDetail(Model):
    __tablename__ = 'log_details'
    log_details_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_name = Column(String(511))
    call_time = Column(TIMESTAMP)
    ip_address = Column(String(39))
    validated = Column(Integer)
