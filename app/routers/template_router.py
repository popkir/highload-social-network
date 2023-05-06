from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from app.utils.logger import logger
from app.db.db import close_session

from app.services.template_crud import TemplateDBHandler
from app.schemas.template_schema import TemplateCreateSchema, TemplateUpdateSchema, TemplateSchema
from app.models.models import TemplateModel

router = APIRouter()

@close_session
@router.post("/create", response_model=dict)
async def create(template: TemplateCreateSchema):
    try: 
        model = TemplateModel(**template.dict())
        TemplateDBHandler.insert_one(model)

        response = JSONResponse(
            status_code=200,
            content={
                "success": "true",
                "message": "Entry created successfully",
                "id": str(model.id),
                "details": str(model)
            }
        )

    except Exception as e:
        logger.error(f"Error in router while creating house: {e}")
        response = JSONResponse(
            status_code=400, 
            content={
                "success": "false", 
                "message": "Error creating entry", 
                "details": str(e)
            }
        )

    return response

@close_session
@router.get("/get-all", response_model=dict)
async def get_all():
    try: 
        entries = TemplateDBHandler.get_active_entries()
        entries_schemas = [TemplateSchema(**entry.__dict__) for entry in entries]
        entry_dicts = [jsonable_encoder(entry.dict()) for entry in entries_schemas]

        response = JSONResponse(
            status_code=200,
            content={
                "success": "true",
                "message": "Entries retrieved successfully",
                "data": entry_dicts
            }
        )

    except Exception as e:
        logger.error(f"Error in router getting all entries: {e}")
        response = JSONResponse(
            status_code=400,
            content={
                "success": "false",
                "message": "Error getting all entries",
                "details": str(e)
            }
        )

    return response

@close_session
@router.get("/get/{id}", response_model=dict)
async def get(id: str):
    try: 
        entry = TemplateDBHandler.get_entry_by_id(id)
        entry_schema = TemplateSchema(**entry.__dict__)
        entry_dict = jsonable_encoder(entry_schema.dict())

        response = JSONResponse(
            status_code=200,
            content={
                "success": "true",
                "message": "Entry retrieved successfully",
                "data": entry_dict
            }
        )

    except Exception as e:
        logger.error(f"Error in router getting entry by id: {e}")
        response = JSONResponse(
            status_code=400,
            content={
                "success": "false",
                "message": "Error getting entry by id",
                "details": str(e)
            }
        )

    return response

@close_session
@router.put("/update/{id}", response_model=dict)
async def update(id: str, template: TemplateUpdateSchema):
    try: 
        update_data = template.dict(exclude_unset=True)
        print(update_data)

        TemplateDBHandler.update_entry(id, update_data)

        response = JSONResponse(
            status_code=200,
            content={
                "success": "true",
                "message": "Entry updated successfully",
                "details": str(update_data)
            }
        )

    except Exception as e:
        logger.error(f"Error in router updating entry: {e}")
        response = JSONResponse(
            status_code=400,
            content={
                "success": "false",
                "message": "Error updating entry",
                "details": str(e)
            }
        )

    return response

@close_session
@router.delete("/delete/{id}", response_model=dict)
async def delete(id: str):
    try: 
        TemplateDBHandler.delete_entry(id)

        response = JSONResponse(
            status_code=200,
            content={
                "success": "true",
                "message": "Entry deleted successfully",
                "id": id
            }
        )
    except Exception as e:
        logger.error(f"Error in router deleting entry: {e}")
        response = JSONResponse(
            status_code=400,
            content={
                "success": "false",
                "message": "Error deleting entry",
                "details": str(e)
            }
        )
    
    return response