# Pull base image
FROM python:3.10

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONFAULTHANDLER 1
ENV POETRY_VERSION=1.2.2

# Set work directory
WORKDIR /code/

# Install dependencies
## the poetry way
RUN pip install --upgrade pip
RUN pip install poetry==1.2.2
COPY ./pyproject.toml .
COPY ./poetry.lock .
RUN poetry config virtualenvs.create false
RUN poetry install -v

# Copy app
COPY . .

EXPOSE 8085
EXPOSE 5432

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8085", "--reload"]