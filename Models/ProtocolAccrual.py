from sqlalchemy import Column, String, Integer
from Models.Model import Model

class ProtocolAccrual(Model):
    __tablename__ = 'sv_pcl_accrual'
    __table_args__ = {"schema": "oncore"}
    protocol_id = Column(Integer, primary_key=True, nullable=False)
    consented_count = Column(Integer, nullable=True)
    on_study_count= Column(Integer, nullable=True)
    on_treatment_count = Column(Integer, nullable=True)
    off_treatment_count = Column(Integer, nullable=True)
    on_follow_up_count = Column(Integer, nullable=True)
    off_study_count = Column(Integer, nullable=True)
    expired_count = Column(Integer, nullable=True)
    on_ltfu_count = Column(Integer, nullable=True)
    not_eligible_count = Column(Integer, nullable=True)

