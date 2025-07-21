# FASTAPI_DATA_UNIFIER_KOOL


Kool Data Hub API
Project Description

The Kool Data Hub API is a robust RESTful web service built with FastAPI, designed to manage and centralize various data aspects for Koolboks operations. It provides comprehensive CRUD (Create, Read, Update, Delete) functionalities for different entities such as in different departments.

The application leverages SQLModel for efficient asynchronous database interactions with PostgreSQL, ensuring high performance and data integrity. It also incorporates APSScheduler for managing recurring background data synchronization tasks, and is structured for scalable deployment using Gunicorn and Uvicorn.
Features

    RESTful API: Standard HTTP methods (GET, POST, PATCH, DELETE) for all resources.

    Asynchronous Operations: Built with async/await for non-blocking I/O, enhancing concurrency.

    Database Management:

        SQLModel: Type-hinted ORM for seamless interaction with PostgreSQL.

        PostgreSQL: Robust and reliable relational database.

        Alembic (Implicit): Assumed for database migrations (though not explicitly in provided code, standard for SQLModel projects).

    

    Background Tasks:

        APSScheduler: For recurring, periodic data synchronization jobs (e.g., Zoho data syncs).

        FastAPI BackgroundTasks: For short, non-blocking tasks that run after an HTTP response.

    Authentication: Includes an auth_router (details depend on its implementation, e.g., JWT).

    Middleware: Custom middleware for logging.

    Scalability Ready: Designed to be deployed with Gunicorn/Uvicorn for production-grade performance and concurrency.

    Automatic API Documentation: Swagger UI (/docs) and ReDoc (/redoc) provided by FastAPI.

Technologies Used

    Backend Framework: FastAPI

    ORM: SQLModel

    Database: PostgreSQL

    Asynchronous Database Driver: AsyncPG (via SQLAlchemy/SQLModel)

    Data Validation/Serialization: Pydantic

    Background Scheduler: APSScheduler

    ASGI Server: Uvicorn

    WSGI HTTP Server (for production): Gunicorn

    Database Migrations: Alembic (implied, typical for SQLModel)

    Authentication: Custom AccessTokenBearer (details depend on implementation)


Running the Application
Development (Uvicorn direct)

For local development, you can run Uvicorn directly:

uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

    --reload: Automatically reloads the application on code changes.

    --host 0.0.0.0: Makes the server accessible from your network.

    --port 8000: Specifies the port.

Production-like (Gunicorn + Uvicorn - Linux/WSL only)

Important Note for Windows Users: Gunicorn does not run natively on Windows due to its reliance on Unix-specific features (fcntl). If you are developing on Windows and want to test a production-like setup, you should use WSL (Windows Subsystem for Linux) or Docker.

If using WSL/Linux:

gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

    --workers 4: Adjust the number of workers based on your CPU cores (e.g., (2 * CPU_CORES) + 1).

Once running, the API documentation will be available at http://localhost:8000/docs (Swagger UI) and http://localhost:8000/redoc (ReDoc).
API Endpoints

The API is structured with versioning /api/v1/ and separate routers for each entity.