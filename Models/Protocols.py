from sqlalchemy import Column, String, Integer
from Models.Model import Model


class Protocols(Model):
    __tablename__ = 'sv_pcl_details'
    __table_args__ = {"schema": "oncore"}
    protocol_id = Column(Integer, primary_key=True, nullable=False)
    protocol_no = Column(String, nullable=False)
    title = Column(String, nullable=False)