from sqlalchemy import Column, String, Integer, TIMESTAMP
from models.Model import Model

class LogDetail(Model):
    __tablename__ = 'log_details'
    __table_args__ = {"schema": "ufapi"}
    log_details_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_name = Column(String(511))
    call_time = Column(TIMESTAMP)
    ip_address = Column(String(39))
    validated = Column(Integer)
    op_type = Column(Integer)
