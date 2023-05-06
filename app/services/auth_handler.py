import bcrypt
from datetime import datetime, timedelta
from typing import Tuple
import uuid

from app.db.db import Session
from app.utils.logger import logger
from app.models.models import UserModel, AuthSessionModel
from app.schemas.user_schema import UserCreateSchema, UserPublicSchema
from app.schemas.auth_session_schema import AuthSessionCreateSchema, AuthSessionPublicSchema
from app.services.user_handler import UserManager
from app.utils.timestamps_getter import get_current_timestamp


class LoginFailedException(Exception):
    pass

class AuthSessionNotFoundException(Exception):
    pass

class AuthSessionExpiredException(Exception):
    pass

class AuthSessionDBHandler():
    @staticmethod
    def insert_one(entry: AuthSessionModel) -> bool:
        try:
            Session.add(entry)
            Session.commit()
        except Exception as e:
            Session.rollback()
            logger.error(f"Error inserting an entry into table {AuthSessionModel.__tablename__}: {e}")
            raise e
        return True

    @staticmethod
    def get_all_entries() -> Tuple[AuthSessionModel]:
        try:
            entries = Session.query(AuthSessionModel).all()
        except Exception as e:
            Session.rollback()
            logger.error(f"Error querying entries in table {AuthSessionModel.__tablename__}: {e}")
            raise e

        return entries
    
    @staticmethod
    def get_active_entries() -> Tuple[AuthSessionModel]:
        try:
            entries = Session.query(AuthSessionModel).filter(AuthSessionModel.deleted == False).all()
        except Exception as e:
            Session.rollback()
            logger.error(f"Error querying active entries in table {AuthSessionModel.__tablename__}: {e}")
            raise e

        return entries

    @staticmethod
    def get_entry_by_id(id: str) -> AuthSessionModel:
        try:
            entry = Session.query(AuthSessionModel).filter(AuthSessionModel.id == id).first()
        except Exception as e:
            Session.rollback()
            logger.error(f"Error querying entry by id in table {AuthSessionModel.__tablename__}: {e}")
            raise e

        return entry
    
    @staticmethod
    def get_entry_by_token(token: str) -> AuthSessionModel:
        try:
            entry = Session.query(AuthSessionModel).filter(AuthSessionModel.token == token).first()
            
            if entry is None:
                raise AuthSessionNotFoundException(f"Auth session with token {token} not found")

        except Exception as e:
            Session.rollback()
            logger.error(f"Error querying entry by token in table {AuthSessionModel.__tablename__}: {e}")
            raise e

        return entry
    
    @staticmethod
    def update_entry(id: str, entry: AuthSessionModel) -> bool:
        try:
            print(entry)
            Session.query(AuthSessionModel).filter(AuthSessionModel.id == id).update(entry)
            Session.commit()
        except Exception as e:
            Session.rollback()
            logger.error(f"Error updating entry by id in table {AuthSessionModel.__tablename__}: {e}")
            raise e

        return True
    
    @staticmethod
    def delete_entry(id: str) -> bool:
        try:
            Session.query(AuthSessionModel).filter(AuthSessionModel.id == id).update({AuthSessionModel.deleted: True})
            Session.commit()
        except Exception as e:
            Session.rollback()
            logger.error(f"Error deleting entry by id in table {AuthSessionModel.__tablename__}: {e}")
            raise e

        return True
    

class AuthSessionManager():
    @staticmethod
    def login(user_id: str, password: str) -> str:
        # Returns a session token if the login is successful
        try:
            # Get the user auth details
            salt, pwd_hash = UserManager.get_auth_details_by_id(user_id)

            # Hash the entered password with the salt
            login_pwd_hash = UserManager.get_pwd_hash(password, salt)

            # Compare the hashes
            if login_pwd_hash == pwd_hash:
                logger.info(f"User {user_id} logged in")

                # Create a new token
                token = str(uuid.uuid4())

                # Create a new auth session
                auth_session_create_schema = AuthSessionCreateSchema(
                    user_id = user_id,
                    token = token,
                    expires_at = get_current_timestamp() + timedelta(hours=1)
                )
                auth_session_model = AuthSessionModel(**auth_session_create_schema.dict())

                # Insert the new auth session into the database
                AuthSessionDBHandler.insert_one(auth_session_model)
                return token
            else:
                raise LoginFailedException(f"Login failed for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error during login: {e}")
            raise e
        
    @staticmethod
    def validate_token(token: str) -> str:
        # Returns the user_id and expiry date if the token is valid
        try:
            auth_session = AuthSessionDBHandler.get_entry_by_token(token)

            expires_at = auth_session.expires_at

            if expires_at > get_current_timestamp():
                user_id = auth_session.user_id
                return user_id, expires_at
            else:
                raise AuthSessionExpiredException(f"Auth session with token {token} has expired")
            
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            raise e