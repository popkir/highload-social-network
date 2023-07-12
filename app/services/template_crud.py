from typing import Tuple
from app.db.db import SessionManager
from app.utils.logger import logger
from app.models.models import TemplateModel

class TemplateDBHandler():
    @staticmethod
    def insert_one(entry: TemplateModel) -> bool:
        try:
            SessionManager.current.add(entry)
            SessionManager.current.commit()
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error inserting an entry into table {TemplateModel.__tablename__}: {e}")
            raise e
        return True

    @staticmethod
    def get_all_entries() -> Tuple[TemplateModel]:
        try:
            entries = SessionManager.current.query(TemplateModel).all()
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error querying entries in table {TemplateModel.__tablename__}: {e}")
            raise e

        return entries
    
    @staticmethod
    def get_active_entries() -> Tuple[TemplateModel]:
        try:
            entries = SessionManager.current.query(TemplateModel).filter(TemplateModel.deleted == False).all()
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error querying active entries in table {TemplateModel.__tablename__}: {e}")
            raise e

        return entries

    @staticmethod
    def get_entry_by_id(id: str) -> TemplateModel:
        try:
            entry = SessionManager.current.query(TemplateModel).filter(TemplateModel.id == id).first()
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error querying entry by id in table {TemplateModel.__tablename__}: {e}")
            raise e

        return entry
    
    @staticmethod
    def update_entry(id: str, update_data: dict) -> bool:
        try:
            logger.info(f'Updating record {id} in table {TemplateModel.__tablename__} with {update_data}')
            SessionManager.current.query(TemplateModel).filter(TemplateModel.id == id).update(update_data)
            SessionManager.current.commit()
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error updating entry by id in table {TemplateModel.__tablename__}: {e}")
            raise e

        return True
    
    @staticmethod
    def delete_entry(id: str) -> bool:
        try:
            SessionManager.current.query(TemplateModel).filter(TemplateModel.id == id).update({TemplateModel.deleted: True})
            SessionManager.current.commit()
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error deleting entry by id in table {TemplateModel.__tablename__}: {e}")
            raise e

        return True