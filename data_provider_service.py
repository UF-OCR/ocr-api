from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from models import Protocols, LogDetail, DiseaseDiagnosis, ProtocolStatus, ProtocolAccrual
import logging
import os

logging.basicConfig(filename=os.environ.get('log_file', None), level=logging.DEBUG)

class DataProviderService:
    def __init__(self, wallet_engine, op_engine):
        """
        :param wallet_engine: The wallet_engine route and login details
        :return: a new instance of DAL class
        :type wallet_engine: string
        """
        if not wallet_engine:
            raise ValueError('The values specified in wallet_engine parameter has to be supported by SQLAlchemy')
        self.wallet_engine = wallet_engine
        wallet_db_engine = create_engine(wallet_engine,poolclass=NullPool)

        wallet_db_session = sessionmaker(bind=wallet_db_engine)
        self.wallet_session = wallet_db_session()
        logging.info("Opening connection to Advarra Database")

        if not op_engine:
            raise ValueError('The values specified in op_engine parameter has to be supported by SQLAlchemy')
        self.op_engine = op_engine
        op_db_engine = create_engine(op_engine,poolclass=NullPool)

        op_db_session = sessionmaker(bind=op_db_engine)
        self.op_session = op_db_session()
        logging.info("Opening connection to On Premise Database")

    def get_protocols(self):
        """
                            Loads all the protocols

                            :return: The protocol_no.
                            """
        try:
            all_protocols = self.wallet_session.query(Protocols.protocol_no, Protocols.title).all()
            return all_protocols
        except:
            self.wallet_session.rollback()
            raise


    def log_details(self, user_name, ip_address, call_time, validated,op_type):
        """

               Creates and saves logFiles to the on premise database.

               :param user_name: user name recorded from the request
               :param ip_address: ip address of the user
               :param call_time: request call time
               :param validated: record if user was validated

               """
        try:
            new_log_detail = LogDetail(
                user_name=user_name,
                call_time=call_time,
                ip_address=ip_address,
                validated=validated,
                op_type=op_type
            )
            self.op_session.add(new_log_detail)
            self.op_session.commit()
            return new_log_detail.log_details_id
        except:
            self.op_session.rollback()
            raise

    def get_covid_protocols(self):
        """
        Loads all the protocols

        :return: The protocol_no.
        """
        try:
            covid_protocols = self.wallet_session.query(DiseaseDiagnosis.protocol_id).filter("U07.1" == DiseaseDiagnosis.code).all()
            covid_protocols_result = {}
            for x in covid_protocols:
                if x[0] not in covid_protocols_result:
                    covid_protocols_result[x[0]] = {}
                protocol = self.wallet_session.query(Protocols).filter(x[0]  == Protocols.protocol_id).first()
                if protocol:
                    covid_protocols_result[x[0]]["protocol_no"] = protocol.protocol_no
                    covid_protocols_result[x[0]]["phase"] = protocol.phase
                    covid_protocols_result[x[0]]["nct_number"] = protocol.nct_number
                    covid_protocols_result[x[0]]["title"] = protocol.title
                protocol_status = self.wallet_session.query(ProtocolStatus).filter(x[0]  == ProtocolStatus.protocol_id).first()
                if protocol_status:
                    covid_protocols_result[x[0]]["status"] = protocol_status.status
                    covid_protocols_result[x[0]]["irb_no"] = protocol_status.irb_no
                accrual_summary = self.wallet_session.query(ProtocolAccrual).filter(x[0] == ProtocolAccrual.protocol_id).first()
                if accrual_summary:
                    covid_protocols_result[x[0]]["accruals"] = {}
                    covid_protocols_result[x[0]]["accruals"]["consented_count"] = accrual_summary.consented_count
                    covid_protocols_result[x[0]]["accruals"]["on_study_count"] = accrual_summary.on_study_count
                    covid_protocols_result[x[0]]["accruals"]["on_treatment_count"] = accrual_summary.on_treatment_count
                    covid_protocols_result[x[0]]["accruals"]["off_treatment_count"] = accrual_summary.off_treatment_count
                    covid_protocols_result[x[0]]["accruals"]["on_follow_up_count"] = accrual_summary.on_follow_up_count
                    covid_protocols_result[x[0]]["accruals"]["off_study_count"] = accrual_summary.off_study_count
                    covid_protocols_result[x[0]]["accruals"]["expired_count"] = accrual_summary.expired_count
                    covid_protocols_result[x[0]]["accruals"]["on_ltfu_count"] = accrual_summary.on_ltfu_count
                    covid_protocols_result[x[0]]["accruals"]["not_eligible_count"] = accrual_summary.not_eligible_count
            return covid_protocols_result
        except:
            self.wallet_session.rollback()
            raise

    def close_connection(self):
        if self.wallet_session is not None:
            self.wallet_session.close()
            logging.info("Closing connection to Advarra database")

        if self.op_session is not None:
            self.op_session.close()
            logging.info("Closing connection to On-Premise database")
