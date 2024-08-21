## Dev Stack

* [Python 3.12](https://www.python.org/downloads/)
* [FastAPI](https://fastapi.tiangolo.com/)
* [SQLAlchemy](https://www.sqlalchemy.org/)
* [pytest](https://docs.pytest.org/en/8.1.x/)
* [Docker](https://www.docker.com/)

## Local Install

    python3.12 -m venv venv
    . venv/bin/activate
    pip install -U pip
    pip install -r requirements.txt
    pytest app -v
    uvicorn app.main:app --port 8080

## Docker Install

    docker-compose up web

## Documentation

* [Swagger UI](http://localhost:8080/docs)
* [ReDoc](http://localhost:8080/redoc)

## Personal Notes

* I chose `FastAPI` over `TornadoWeb` because of the integrated API documentation. The framework is simple, production-ready, and well-documented. The development experience was great.
* The first challenge was using the `SQLAlchemy` in async mode. So, I had to improvise with both documentation (`FastAPI` & `SQLAlchemy`) to bake my solution.
* The second challenge was the testing environment. `FastAPI` uses `Dependency Injection` at each endpoint. But that looks unnecessarily repetitive to me. I tried to move the `DI` to the application lifespan function without success. Finally, I implemented an environment variable to switch the database for testing.
* The final challenge was the `alert job` (watchdog). Python can be very tricky with module import issues. I considered a practical solution to create an async task inside the main script for the watchdog. AFAIK the job script should be independent, and the usage of the system cron service should be more scalable. But, honestly, I need to go more in-depth with this.
