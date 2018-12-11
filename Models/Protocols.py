from sqlalchemy import Column, String, Integer
from Model import Model


class Protocols(Model):
    __tablename__ = 'sv_pcl_details'
    __table_args__ = {"schema": "oncore"}
    protocol_id = Column(Integer, primary_key=True, nullable=False)
    protocol_no = Column(String, nullable=False)
