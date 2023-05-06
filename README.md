# Social network
a project for high load architecture course

## Set Up
- Create `.env.local` file from `.env.sample`
- Run `docker network create social-network-default` in case of your first start (if network wasn't created yet)
- Run: `docker-compose up --build` in your shell.
- Run postgres db migrations: `docker-compose exec backend alembic upgrade head` on first run
- Go to `http://localhost:8085/docs#/` - it should work.

### Running Tests
- After launching docker-compose project, and running alembic migrations
- With an EMPTY db, do this:  `docker-compose exec backend pytest -v`

