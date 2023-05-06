import bcrypt
from typing import Tuple
from app.db.db import Session
from app.utils.logger import logger
from app.models.models import UserModel
from app.schemas.user_schema import UserCreateSchema, UserUpdateSchema, UserSchema

class UserDBHandler():
    @staticmethod
    def insert_one(entry: UserModel) -> bool:
        try:
            Session.add(entry)
            Session.commit()
        except Exception as e:
            Session.rollback()
            logger.error(f"Error inserting an entry into table {UserModel.__tablename__}: {e}")
            raise e
        return True

    @staticmethod
    def get_all_entries() -> Tuple[UserModel]:
        try:
            entries = Session.query(UserModel).all()
        except Exception as e:
            Session.rollback()
            logger.error(f"Error querying entries in table {UserModel.__tablename__}: {e}")
            raise e

        return entries
    
    @staticmethod
    def get_active_entries() -> Tuple[UserModel]:
        try:
            entries = Session.query(UserModel).filter(UserModel.deleted == False).all()
        except Exception as e:
            Session.rollback()
            logger.error(f"Error querying active entries in table {UserModel.__tablename__}: {e}")
            raise e

        return entries

    @staticmethod
    def get_entry_by_id(id: str) -> UserModel:
        try:
            entry = Session.query(UserModel).filter(UserModel.id == id).first()
        except Exception as e:
            Session.rollback()
            logger.error(f"Error querying entry by id in table {UserModel.__tablename__}: {e}")
            raise e

        return entry
    
    @staticmethod
    def update_entry(id: str, entry: UserModel) -> bool:
        try:
            print(entry)
            Session.query(UserModel).filter(UserModel.id == id).update(entry)
            Session.commit()
        except Exception as e:
            Session.rollback()
            logger.error(f"Error updating entry by id in table {UserModel.__tablename__}: {e}")
            raise e

        return True
    
    @staticmethod
    def delete_entry(id: str) -> bool:
        try:
            Session.query(UserModel).filter(UserModel.id == id).update({UserModel.deleted: True})
            Session.commit()
        except Exception as e:
            Session.rollback()
            logger.error(f"Error deleting entry by id in table {UserModel.__tablename__}: {e}")
            raise e

        return True
    
class UserManager():
    @staticmethod
    def generate_salt_and_hash(password: str) -> Tuple[str, str]:
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return salt, password_hash

    @staticmethod
    def register_user(user: UserCreateSchema):
        try:
            # Convert password to bytes
            try:
                password = user.password.encode('utf-8')
            except Exception as e:
                logger.error(f"Error encoding password as utf-8: {e}")
                raise e

            # Generate salt and hash
            salt, password_hash = __class__.generate_salt_and_hash(password)

            # Create user model
            user_model = UserModel(
                first_name=user.first_name,
                last_name=user.last_name,
                birthday=user.birthday,
                biography=user.biography,
                city=user.city,
                password_salt=salt,
                password_hash=password_hash
            )

            # Insert user model into database
            UserDBHandler.insert_one(user_model)

            # Return user id
            return user_model
        
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise e




