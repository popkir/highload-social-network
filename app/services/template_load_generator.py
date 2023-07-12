from app.services.template_crud import TemplateDBHandler
from app.models.models import TemplateModel
from app.utils.logger import logger
from app.utils.name_generator import get_pseudonym

from random import randint, random


class TemplateLoadGenerator():
    @staticmethod
    def generate_template() -> TemplateModel:
        """Generates a template with random values. The name is generated using the name generator.

        Returns:
            TemplateModel: Template with random values
        """
        name = get_pseudonym()

        template = TemplateModel(
            name=name,
            description=f"Template for {name}",
            count=randint(1, 100),
            price=random() * 1000
        )

        return template

    @staticmethod
    async def insert_templates(number: int) -> int:
        """Generates and inserts a number of templates into the database. Returns the number of successful inserts.

        Args:
            number (int): Number of templates to generate and insert

        Raises:
            e: Any exception raised by the database

        Returns:
            int: Number of successful inserts
        """
        success_counter = 0
        for i in range(number):
            try:
                template = __class__.generate_template()
                await TemplateDBHandler.insert_one(template)
                success_counter += 1
                if success_counter % 1000 == 0:
                    logger.info(f"Inserted {success_counter} templates out of {i}")
            except Exception as e:
                logger.error(f"Error inserting template {i}: {e}")
                raise e
            
        logger.info(f"Successfully inserted {success_counter} templates")

        return success_counter