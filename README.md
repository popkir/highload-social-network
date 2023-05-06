# Social network
a project for high load architecture course

## Set Up
- Create `.env.local` file from `.env.sample`
- Run `docker network create social-network-default` in case of your first start (if network wasn't created yet)
- Run: `docker-compose up --build` in your shell.
- Run postgres db migrations: `docker-compose exec backend alembic upgrade head` on first run
- Go to `http://localhost:8085/docs#/` - it should work.

## Generating a new migration revision
- Create the new data models in `app/models`
- Run the project `docker-compose up --build`
- From another terminal session, run alembic inside backend container: `docker-compose exec backend alembic revision --autogenerate -m 'revision description here'`
- Go to `app/db/migrations/alembic/versions` and find the new revision script
- Revise and update the upgrade and downgrade function code
- To apply the migration, run `docker-compose exec backend alembic upgrade head`

### Running Tests
- After launching docker-compose project, and running alembic migrations
- With an EMPTY db, do this:  `docker-compose exec backend pytest -v`

