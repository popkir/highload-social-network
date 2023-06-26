from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from app.utils.logger import logger
from app.db.db import close_session

from app.services.user_handler import UserManager, UserRegistrationDataIncompleteException, \
    UserNotFoundException, UserIdInvalidException, UserSearchEmptyResult, UserSearchNeedsAtLeastOneNameField
from app.schemas.user_schema import UserCreateSchema

from asgi_correlation_id import correlation_id

router = APIRouter()

@close_session
@router.post("/register", response_model=dict)
async def register_user(user: UserCreateSchema):
    try: 
        model = UserManager.register_user(user)

        response = JSONResponse(
            status_code=200,
            content={
                "message": "User created successfully",
                "user_id": str(model.id)
            }
        )
    except UserRegistrationDataIncompleteException as e:
        logger.error(f"Error in router while creating user: {e}")
        response = JSONResponse(
            status_code=400, 
            content={
                "message": "User registration data incomplete", 
                "details": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Error in router while creating user: {e}")
        response = JSONResponse(
            status_code=500, 
            content={
                "request_id": correlation_id.get(),
                "message": "Error creating user", 
                "details": str(e)
            }
        )

    return response

@close_session
@router.get("/get/{id}", response_model=dict)
async def get_user_by_id(id: str):
    try: 
        user_schema = UserManager.get_user_by_id(id)
        user_dict = jsonable_encoder(user_schema.dict())

        response = JSONResponse(
            status_code=200,
            content=user_dict
        )
    except UserIdInvalidException as e:
        logger.error(f"Error in router getting user by id: {e}")
        response = JSONResponse(
            status_code=400,
            content={
                "message": "User id invalid",
                "details": str(e)
            }
        )
    except UserNotFoundException as e:
        logger.error(f"Error in router getting user by id: {e}")
        response = JSONResponse(
            status_code=404,
            content={
                "message": "User not found",
                "details": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Error in router getting user by id: {e}")
        response = JSONResponse(
            status_code=500,
            content={
                "request_id": correlation_id.get(),
                "message": "Error getting user", 
                "details": str(e)
            }
        )

    return response

@close_session
@router.get("/search", response_model=dict)
async def search_user(first_name: str = None, last_name: str = None):    
    try: 
        users = UserManager.search_user_by_name(first_name, last_name)
        users = jsonable_encoder([u.dict() for u in users])

        response = JSONResponse(
            status_code=200,
            content=users
        )
    except UserSearchNeedsAtLeastOneNameField as e:
        logger.error(f"Error in router searching user: {e}")
        response = JSONResponse(
            status_code=400,
            content={
                "message": "User search needs at least first name or last name",
                "details": str(e)
            }
        )
    except UserSearchEmptyResult as e:
        logger.error(f"Error in router searching user: {e}")
        response = JSONResponse(
            status_code=404,
            content={
                "message": "Users not found",
                "details": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Error in router searching user: {e}")
        response = JSONResponse(
            status_code=500,
            content={
                "request_id": correlation_id.get(),
                "message": "Error getting user", 
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