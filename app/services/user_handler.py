import bcrypt
from datetime import datetime
from typing import Tuple
from uuid import UUID

from app.db.db import Session
from app.utils.logger import logger
from app.models.models import UserModel
from app.schemas.user_schema import UserCreateSchema, UserPublicSchema


class UserNotFoundException(Exception):
    pass
class UserIdInvalidException(Exception):
    pass
class UserRegistrationDataIncompleteException(Exception):
    pass

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
            # Check if id is uuid
            try:
                uuid_obj = UUID(id, version=4)
            except ValueError:
                raise UserIdInvalidException(f"User id {id} is not a valid uuid")

            # Query entry
            entry = Session.query(UserModel)\
                .filter(
                    UserModel.id == id,
                    UserModel.deleted == False
                ).first()
            if entry is None:
                raise UserNotFoundException(f"User with id {id} not found")
            
        except Exception as e:
            Session.rollback()
            logger.error(f"Error querying entry by id in table {UserModel.__tablename__}: {e}")
            raise e

        return entry

    @staticmethod
    def get_auth_details_by_id(id: str) -> Tuple[str, str]:
        try:
            # Check if id is uuid
            try:
                uuid_obj = UUID(id, version=4)
            except ValueError:
                raise UserIdInvalidException(f"User id {id} is not a valid uuid")
            
            # Query entry
            entry = Session\
                .query(UserModel.password_salt, UserModel.password_hash)\
                .filter(
                    UserModel.id == id, 
                    UserModel.deleted == False
                ).first()
            
            if entry is None:
                raise UserNotFoundException(f"User with id {id} not found")
            
            return entry

        except Exception as e:
            Session.rollback()
            logger.error(f"Error querying entry by id in table {UserModel.__tablename__}: {e}")
            raise e
            
    @staticmethod
    def update_entry(id: str, entry: UserModel) -> bool:
        try:
            logger.debug(entry)
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
    def get_pwd_hash(password: str, salt: str | bytes) -> str:
        try:
            # Convert salt to bytes
            if type(salt) == str:
                salt = salt.encode('utf-8')
            logger.debug(f"using salt: {salt}, type {type(salt)}")
            
            # Convert password to bytes
            try:
                password = password.encode('utf-8')
            except Exception as e:
                logger.error(f"Error encoding password as utf-8: {e}")
                raise e
            logger.debug(f"hashing password: {password}, type {type(password)}")
            
            password_hash = bcrypt.hashpw(password, salt)
            password_hash_str = password_hash.decode('utf-8')

            return password_hash_str
        
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise e
    
    @staticmethod
    def generate_salt_and_hash(password: str) -> Tuple[str, str]:
        salt = bcrypt.gensalt()
        logger.debug(f"creating new salt: {salt}, type {type(salt)}")
        
        password_hash_str = __class__.get_pwd_hash(password, salt)

        salt_str = salt.decode('utf-8')

        return salt_str, password_hash_str

    @staticmethod
    def register_user(user: UserCreateSchema) -> UserModel:
        try:
            # Validate completeness
            required_fields = ['first_name', 'last_name', 'birthday', 'biography', 'city']
            missing_fields = [field for field in required_fields if getattr(user, field) is None]
            if len(missing_fields) > 0:
                raise UserRegistrationDataIncompleteException(f"Missing fields: {missing_fields}")

            # Generate salt and hash
            salt, password_hash = __class__.generate_salt_and_hash(user.password)

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

    @staticmethod
    def get_user_by_id(id: str) -> UserPublicSchema:
        try:
            # Get user model from db
            user_model = UserDBHandler.get_entry_by_id(id)
            
            # Compute age
            age = (datetime.now().date() - user_model.birthday).days // 365

            # Create user public schema
            user = UserPublicSchema(
                id=user_model.id,
                first_name=user_model.first_name,
                last_name=user_model.last_name,
                age=age,
                birthday=user_model.birthday,
                biography=user_model.biography,
                city=user_model.city
            )

            return user
        except Exception as e:
            logger.error(f"Error getting user by id: {e}")
            raise e
        
    @staticmethod
    def get_auth_details_by_id(id: str) -> Tuple[str, str]:
        try:
            return UserDBHandler.get_auth_details_by_id(id)
        except Exception as e:
            logger.error(f"Error getting auth details by id: {e}")
            raise e