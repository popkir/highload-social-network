import bcrypt
from datetime import datetime
from typing import Tuple
from uuid import UUID

from app.db.db import SessionManager, with_slave
from app.utils.logger import logger
from app.models.models import UserModel
from app.schemas.user_schema import UserCreateSchema, UserPublicSchema

from  sqlalchemy.sql.expression import func, select


class UserNotFoundException(Exception):
    pass
class UserIdInvalidException(Exception):
    pass
class UserRegistrationDataIncompleteException(Exception):
    pass
class UserSearchNeedsAtLeastOneNameField(Exception):
    pass
class UserSearchEmptyResult(Exception):
    pass


class UserDBHandler():
    @staticmethod
    async def insert_one(entry: UserModel) -> bool:
        try:
            SessionManager.current.add(entry)
            SessionManager.current.commit()
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error inserting an entry into table {UserModel.__tablename__}: {e}")
            raise e
        return True

    @staticmethod
    def get_all_entries() -> Tuple[UserModel]:
        try:
            entries = SessionManager.current.query(UserModel).all()
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error querying entries in table {UserModel.__tablename__}: {e}")
            raise e

        return entries
    
    @staticmethod
    def get_active_entries() -> Tuple[UserModel]:
        try:
            entries = SessionManager.current.query(UserModel).filter(UserModel.deleted == False).all()
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error querying active entries in table {UserModel.__tablename__}: {e}")
            raise e

        return entries

    @staticmethod
    async def get_active_entry_ids(limit: int = 10, random: bool = True) -> Tuple[str]:
        try:
            if random:
                id_rows = SessionManager.current\
                    .query(UserModel.id)\
                    .filter(UserModel.deleted == False)\
                    .order_by(func.random())\
                    .limit(limit)\
                    .all()
            else:
                id_rows = SessionManager.current\
                    .query(UserModel.id)\
                    .filter(UserModel.deleted == False)\
                    .order_by(UserModel.id)\
                    .limit(limit)\
                    .all()
            if id_rows is None:
                raise ValueError("got None from db instead of user ids")
            if len(id_rows) == 0:
                raise ValueError("got empty list from db instead of user ids")
            
            ids = tuple(str(x[0]) for x in id_rows)
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error querying active entries in table {UserModel.__tablename__}: {e}")
            raise e
        return ids

    @staticmethod
    async def get_entry_by_id(id: str) -> UserModel:
        try:
            # Check if id is uuid
            try:
                uuid_obj = UUID(id, version=4)
            except ValueError:
                raise UserIdInvalidException(f"User id {id} is not a valid uuid")

            # Query entry
            entry = SessionManager.current.query(UserModel)\
                .filter(
                    UserModel.id == id,
                    UserModel.deleted == False
                ).first()
            if entry is None:
                raise UserNotFoundException(f"User with id {id} not found")
            
        except Exception as e:
            SessionManager.current.rollback()
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
            entry = SessionManager.current\
                .query(UserModel.password_salt, UserModel.password_hash)\
                .filter(
                    UserModel.id == id, 
                    UserModel.deleted == False
                ).first()
            
            if entry is None:
                raise UserNotFoundException(f"User with id {id} not found")
            
            return entry

        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error querying entry by id in table {UserModel.__tablename__}: {e}")
            raise e
            
    @staticmethod
    def update_entry(id: str, update_data: dict) -> bool:
        try:
            logger.info(f'Updating record {id} in table {UserModel.__tablename__} with {update_data}')
            SessionManager.current.query(UserModel).filter(UserModel.id == id).update(update_data)
            SessionManager.current.commit()
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error updating entry by id in table {UserModel.__tablename__}: {e}")
            raise e

        return True
    
    @staticmethod
    def delete_entry(id: str) -> bool:
        try:
            SessionManager.current.query(UserModel).filter(UserModel.id == id).update({UserModel.deleted: True})
            SessionManager.current.commit()
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error deleting entry by id in table {UserModel.__tablename__}: {e}")
            raise e

        return True

    @staticmethod
    async def search_by_first_name(first_name: str) -> Tuple[UserModel]:
        try:
            entries = SessionManager.current\
                .query(UserModel)\
                .filter(
                    UserModel.first_name.like(first_name + '%'),
                    UserModel.deleted == False
                )\
                .order_by(UserModel.id)\
                .all()
            if entries is None or entries == []:
                raise UserSearchEmptyResult(f"Users with first name starting with {first_name} not found")
            
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error querying entry by first_name in table {UserModel.__tablename__}: {e}")
            raise e

        return entries

    @staticmethod
    async def search_by_last_name(last_name: str) -> Tuple[UserModel]:
        try:
            entries = SessionManager.current\
                .query(UserModel)\
                .filter(
                    UserModel.last_name.like(last_name + '%'),
                    UserModel.deleted == False
                )\
                .order_by(UserModel.id)\
                .all()
            if entries is None or entries == []:
                raise UserSearchEmptyResult(f"Users with last name starting with {last_name} not found")
            
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error querying entry by last_name in table {UserModel.__tablename__}: {e}")
            raise e

        return entries

    @staticmethod
    async def search_by_first_and_last_name(first_name: str, last_name: str) -> Tuple[UserModel]:
        try:
            entries = SessionManager.current\
                .query(UserModel)\
                .filter(
                    UserModel.first_name.like(first_name + '%'),
                    UserModel.last_name.like(last_name + '%'),
                    UserModel.deleted == False
                )\
                .order_by(UserModel.id)\
                .all()
            if entries is None or entries == []:
                raise UserSearchEmptyResult(f"Users with first name starting with {first_name} and last name starting with {last_name} not found")
            
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error querying entry by first_name and last_name in table {UserModel.__tablename__}: {e}")
            raise e

        return entries

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
    async def register_user(user: UserCreateSchema) -> UserModel:
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
            await UserDBHandler.insert_one(user_model)

            # Return user id
            return user_model
        
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise e

    @staticmethod
    def compute_age(user_model: UserModel) -> int:
        age = (datetime.now().date() - user_model.birthday).days // 365
        return age
    
    @staticmethod
    async def get_user_by_id(id: str) -> UserPublicSchema:
        try:
            # Get user model from db
            user_model = await UserDBHandler.get_entry_by_id(id)
            
            # Compute age
            age = __class__.compute_age(user_model)

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
        
    @staticmethod
    async def search_user_by_name(first_name: str | None, last_name: str | None) -> Tuple[UserPublicSchema]:
        try:
            if first_name is None:
                if last_name is None:
                    raise UserSearchNeedsAtLeastOneNameField(f"User search with no first name and no last name is not well defined, aborting")
                else:
                    user_models = await UserDBHandler.search_by_last_name(last_name)
            else:
                if last_name is None:
                    user_models = await UserDBHandler.search_by_first_name(first_name)
                else:
                    user_models = await UserDBHandler.search_by_first_and_last_name(first_name, last_name)
            
            user_schemas = []
            for user_model in user_models:
                age = __class__.compute_age(user_model)
                user = UserPublicSchema(
                    id=user_model.id,
                    first_name=user_model.first_name,
                    last_name=user_model.last_name,
                    age=age,
                    birthday=user_model.birthday,
                    biography=user_model.biography,
                    city=user_model.city
                )
                user_schemas.append(user)
            
            return tuple(user_schemas)

        except Exception as e:
            logger.error(f"Error searching user by name: {e}")
            raise e
        
    @staticmethod
    async def get_user_ids(limit: int = 10, random: bool = True) -> Tuple[str]:
        try:
            ids = await UserDBHandler.get_active_entry_ids(limit, random)
            return ids
    
        except Exception as e:
            logger.error(f"Error getting user ids: {e}")
            raise e