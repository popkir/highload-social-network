from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from app.utils.logger import logger
from app.db.db import close_session

from app.schemas.login_schema import LoginSchema
from app.services.auth_handler import AuthSessionManager, AuthSessionNotFoundException, AuthSessionExpiredException, LoginFailedException

router = APIRouter()

@close_session
@router.post("/login", response_model=dict)
async def login(credentials: LoginSchema):
    try: 
        user_id = credentials.user_id
        password = credentials.password

        auth_session_token = AuthSessionManager.login(user_id, password)

        response = JSONResponse(
            status_code=200,
            content={
                "success": "true",
                "message": "User logged in successfully",
                "token": auth_session_token
            }
        )

    except Exception as e:
        logger.error(f"Error in router while logging in: {e}")
        response = JSONResponse(
            status_code=400, 
            content={
                "success": "false", 
                "message": "Error logging in", 
                "details": str(e)
            }
        )

    return response

@close_session
@router.post("/auth", response_model=dict)
async def authenticate(token: str):
    try: 
        user_id, expires_at = AuthSessionManager.validate_token(token)

        response = JSONResponse(
            status_code=200,
            content={
                "success": "true",
                "message": f"User authenticated successfully with token {token}",
                "user_id": str(user_id),
                "expires_at": str(expires_at)
            }
        )

    except Exception as e:
        logger.error(f"Error in router getting user by id: {e}")
        response = JSONResponse(
            status_code=400,
            content={
                "success": "false",
                "message": f"Error authenticating user by token {token}",
                "details": str(e)
            }
        )

    return response

# @close_session
# @router.put("/update/{id}", response_model=dict)
# async def update(id: str, template: TemplateUpdateSchema):
#     try: 
#         update_data = template.dict(exclude_unset=True)
#         print(update_data)

#         TemplateDBHandler.update_entry(id, update_data)

#         response = JSONResponse(
#             status_code=200,
#             content={
#                 "success": "true",
#                 "message": "Entry updated successfully",
#                 "details": str(update_data)
#             }
#         )

#     except Exception as e:
#         logger.error(f"Error in router updating entry: {e}")
#         response = JSONResponse(
#             status_code=400,
#             content={
#                 "success": "false",
#                 "message": "Error updating entry",
#                 "details": str(e)
#             }
#         )

#     return response

# @close_session
# @router.delete("/delete/{id}", response_model=dict)
# async def delete(id: str):
#     try: 
#         TemplateDBHandler.delete_entry(id)

#         response = JSONResponse(
#             status_code=200,
#             content={
#                 "success": "true",
#                 "message": "Entry deleted successfully",
#                 "id": id
#             }
#         )
#     except Exception as e:
#         logger.error(f"Error in router deleting entry: {e}")
#         response = JSONResponse(
#             status_code=400,
#             content={
#                 "success": "false",
#                 "message": "Error deleting entry",
#                 "details": str(e)
#             }
#         )
    
#     return response