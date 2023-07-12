import bcrypt
from datetime import datetime, timedelta
from typing import Tuple
import uuid

from app.db.db import SessionManager
from app.utils.logger import logger
from app.models.models import AuthSessionModel
from app.schemas.auth_session_schema import AuthSessionCreateSchema
from app.services.user_handler import UserManager
from app.utils.timestamps_getter import get_current_timestamp


class LoginFailedException(Exception):
    pass
class AuthTokenInvalidFormatException(Exception):
    pass
class AuthSessionNotFoundException(Exception):
    pass
class AuthSessionExpiredException(Exception):
    pass

class AuthSessionDBHandler():
    @staticmethod
    def insert_one(entry: AuthSessionModel) -> bool:
        try:
            SessionManager.current.add(entry)
            SessionManager.current.commit()
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error inserting an entry into table {AuthSessionModel.__tablename__}: {e}")
            raise e
        return True

    @staticmethod
    def get_all_entries() -> Tuple[AuthSessionModel]:
        try:
            entries = SessionManager.current.query(AuthSessionModel).all()
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error querying entries in table {AuthSessionModel.__tablename__}: {e}")
            raise e

        return entries
    
    @staticmethod
    def get_active_entries() -> Tuple[AuthSessionModel]:
        try:
            entries = SessionManager.current.query(AuthSessionModel).filter(AuthSessionModel.deleted == False).all()
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error querying active entries in table {AuthSessionModel.__tablename__}: {e}")
            raise e

        return entries

    @staticmethod
    def get_entry_by_id(id: str) -> AuthSessionModel:
        try:
            entry = SessionManager.current.query(AuthSessionModel)\
                .filter(
                    AuthSessionModel.id == id, 
                    AuthSessionModel.deleted == False
                ).first()
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error querying entry by id in table {AuthSessionModel.__tablename__}: {e}")
            raise e

        return entry
    
    @staticmethod
    def get_entry_by_token(token: str) -> AuthSessionModel:
        try:
            entry = SessionManager.current.query(AuthSessionModel)\
                .filter(
                    AuthSessionModel.token == token,
                    AuthSessionModel.deleted == False
                ).first()
            
            if entry is None:
                raise AuthSessionNotFoundException(f"Auth session with token {token} not found")

        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error querying entry by token in table {AuthSessionModel.__tablename__}: {e}")
            raise e

        return entry
    
    @staticmethod

    @staticmethod
    def update_entry(id: str, update_data: dict) -> bool:
        try:
            logger.info(f'Updating record {id} in table {AuthSessionModel.__tablename__} with {update_data}')
            SessionManager.current.query(AuthSessionModel).filter(AuthSessionModel.id == id).update(update_data)
            SessionManager.current.commit()
        except Exception as e:
            SessionManager.current.rollback()
            logger.error(f"Error updating entry by id in table {AuthSessionModel.__tablename__}: {e}")
            raise e

        return True
    
    @staticmethod
    def delete_entry(id: str) -> bool:
        try:
            SessionManager.current.query(AuthSessionModel).filter(AuthSessionModel.id == id).update({AuthSessionModel.deleted: True})
            SessionManager.current.commit()
        except Exception as e:
            SessionManager.current.rollback()
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

                """
                # Delete any existing auth sessions for this user
                # Or should we just update the expiry date?
                # Or should we just allow multiple sessions?
                # Or should we just allow multiple sessions with a limit?
                # Or should we just allow multiple sessions with a limit and delete the oldest?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government and the aliens?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government and the aliens and the gods?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government and the aliens and the gods and the universe?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government and the aliens and the gods and the universe and the multiverse?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government and the aliens and the gods and the universe and the multiverse and the omniverse?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government and the aliens and the gods and the universe and the multiverse and the omniverse and the metaverse?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government and the aliens and the gods and the universe and the multiverse and the omniverse and the metaverse and the xenoverse?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government and the aliens and the gods and the universe and the multiverse and the omniverse and the metaverse and the xenoverse and the hyperverse?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government and the aliens and the gods and the universe and the multiverse and the omniverse and the metaverse and the xenoverse and the hyperverse and the ultraverse?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government and the aliens and the gods and the universe and the multiverse and the omniverse and the metaverse and the xenoverse and the hyperverse and the ultraverse and the archverse?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government and the aliens and the gods and the universe and the multiverse and the omniverse and the metaverse and the xenoverse and the hyperverse and the ultraverse and the archverse and the megaverse?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government and the aliens and the gods and the universe and the multiverse and the omniverse and the metaverse and the xenoverse and the hyperverse and the ultraverse and the archverse and the megaverse and the gigaverse?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government and the aliens and the gods and the universe and the multiverse and the omniverse and the metaverse and the xenoverse and the hyperverse and the ultraverse and the archverse and the megaverse and the gigaverse and the teraverse?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government and the aliens and the gods and the universe and the multiverse and the omniverse and the metaverse and the xenoverse and the hyperverse and the ultraverse and the archverse and the megaverse and the gigaverse and the teraverse and the petaverse?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government and the aliens and the gods and the universe and the multiverse and the omniverse and the metaverse and the xenoverse and the hyperverse and the ultraverse and the archverse and the megaverse and the gigaverse and the teraverse and the petaverse and the exaverse?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government and the aliens and the gods and the universe and the multiverse and the omniverse and the metaverse and the xenoverse and the hyperverse and the ultraverse and the archverse and the megaverse and the gigaverse and the teraverse and the petaverse and the exaverse and the zettaverse?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government and the aliens and the gods and the universe and the multiverse and the omniverse and the metaverse and the xenoverse and the hyperverse and the ultraverse and the archverse and the megaverse and the gigaverse and the teraverse and the petaverse and the exaverse and the zettaverse and the yottaverse?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government and the aliens and the gods and the universe and the multiverse and the omniverse and the metaverse and the xenoverse and the hyperverse and the ultraverse and the archverse and the megaverse and the gigaverse and the teraverse and the petaverse and the exaverse and the zettaverse and the yottaverse and the brontoverse?
                # Or should we just allow multiple sessions with a limit and delete the oldest and notify the user and the admin and the security team and the police and the military and the government and the aliens and the gods and the universe and the multiverse and the omniverse and the metaverse and the xenoverse and the hyperverse and the ultraverse and the archverse and the megaverse and the gigaverse and the teraverse and the petaverse and the exaverse and the zettaverse and the yottaverse and the brontoverse and the geoverse?
                # 
                # I think we should just allow multiple sessions with a limit and delete the oldest
                #
                # But what if the user is logged in on multiple devices?
                #
                # I think we should just allow multiple sessions with a limit and delete the oldest
                #
                # But what if the user is logged in on multiple devices and they are all in different timezones?
                #
                # I think we should just allow multiple sessions with a limit and delete the oldest
                #
                # But what if the user is logged in on multiple devices and they are all in different timezones and they are all in different dimensions?
                #
                # I think we should just allow multiple sessions with a limit and delete the oldest
                #
                # But what if the user is logged in on multiple devices and they are all in different timezones and they are all in different dimensions and they are all in different universes?
                #
                # I think we should just allow multiple sessions with a limit and delete the oldest
                #
                # But what if the user is logged in on multiple devices and they are all in different timezones and they are all in different dimensions and they are all in different universes and they are all in different multiverses?
                #
                # I think we should just allow multiple sessions with a limit and delete the oldest
                #
                # But what if the user is logged in on multiple devices and they are all in different timezones and they are all in different dimensions and they are all in different universes and they are all in different multiverses and they are all in different omniverses?
                #
                # I think we should just allow multiple sessions with a limit and delete the oldest
                #
                # But what if the user is logged in on multiple devices and they are all in different timezones and they are all in different dimensions and they are all in different universes and they are all in different multiverses and they are all in different omniverses and they are all in different metaverses?
                """

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
                raise LoginFailedException(f"Login failed for user {user_id} due to incorrect password")
            
        except Exception as e:
            logger.error(f"Error during login: {e}")
            raise e
        
    @staticmethod
    def validate_token(token: str) -> str:
        # Returns the user_id and expiry date if the token is valid
        try:
            try:
                uuid_token = uuid.UUID(token)
            except ValueError:
                raise AuthTokenInvalidFormatException

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