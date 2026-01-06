# AkibaFlow - Budgeting App

**Version:** 0.1.0 | **OpenAPI Spec:** OAS 3.1

AkibaFlow is a comprehensive budgeting application designed to help users plan their finances and track expenses effortlessly. The app is built on a high-performance, API-driven architecture and is planned to leverage SMS integration to automatically capture and categorize spending, making financial management intuitive and accessible.

## Features

- **User Authentication**: Secure login and registration system (Email/password and future OTP-based).
- **User Management**: CRUD operations for user accounts.
- **Expense Tracking via SMS (Planned)**: Automatically parse and record expenses from SMS notifications.
- **Budget Planning (Planned)**: Create and manage personal budgets.
- **Transaction Management (Planned)**: View, categorize, and analyze spending patterns.
- **Real-time Notifications (Planned)**: Get alerts on budget limits and spending trends.
- **API-Driven Architecture**: RESTful API for seamless integration with auto-generated documentation.

## Tech Stack

The architecture is built for performance and scalability, leveraging modern Python tools.

| Component            | Technology                   | Role                                                 |
| :------------------- | :--------------------------- | :--------------------------------------------------- |
| **Backend**          | FastAPI (Python 3.12+)       | High-performance asynchronous API framework.         |
| **Database**         | PostgreSQL with SQLModel ORM | Robust relational database and type-safe ORM.        |
| **Migrations**       | Alembic                      | Database schema management.                          |
| **Authentication**   | JWT tokens                   | Stateless security.                                  |
| **Task Queue**       | Celery with Redis            | Background processing for scheduled and heavy tasks. |
| **Containerization** | Docker & Docker Compose      | Consistent development and deployment environment.   |
| **Documentation**    | Swagger UI / ReDoc           | Auto-generated API documentation.                    |

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+
- Git

### Installation (Recommended)

Use Docker Compose for the fastest setup.

1.  Clone the repository:

    ```bash
    git clone [https://github.com/yourusername/akibaflow.git](https://github.com/yourusername/akibaflow.git)
    cd akibaflow
    ```

2.  Create and configure the environment file:

    ```bash
    cp .env.example .env
    # IMPORTANT: Edit the .env file with your specific configurations (DB credentials, secrets).
    ```

3.  Build and start all services:

    ```bash
    docker-compose up --build
    ```

4.  Access the API documentation:

    - Swagger UI: `http://localhost:8000/api/v1/docs`
    - ReDoc: `http://localhost:8000/api/v1/redoc`

### Local Development (Alternative)

If you prefer to run the application directly on your host machine:

1.  Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

2.  Run database migrations (Ensure PostgreSQL is running locally):

    ```bash
    alembic upgrade head
    ```

3.  Start the server:

    ```bash
    uvicorn app.main:app --reload
    ```

## API Endpoints

The API is versioned under `/api/v1/` and uses standard HTTP status codes.

### Home / Health

| Method | Endpoint                 | Description                               |
| :----- | :----------------------- | :---------------------------------------- |
| `GET`  | `/` or `/api/v1/`        | Home endpoints.                           |
| `GET`  | `/api/v1/liveness-check` | Health check for container orchestration. |

### Authentication

| Method | Endpoint              | Description                                    |
| :----- | :-------------------- | :--------------------------------------------- |
| `POST` | `/api/v1/auth/login`  | Login using email and password.                |
| `GET`  | `/api/v1/auth/whoami` | Get info about the current authenticated user. |

### User Management

| Method | Endpoint                 | Description               | Schema          |
| :----- | :----------------------- | :------------------------ | :-------------- |
| `GET`  | `/api/v1/user`           | Get all users.            | `UserRead`      |
| `POST` | `/api/v1/user`           | Create a new user.        | `UserCreate`    |
| `GET`  | `/api/v1/user/search`    | Search users by criteria. | -               |
| `GET`  | `/api/v1/user/{user_id}` | Get a user by ID.         | `UserRead`      |
| `PUT`  | `/api/v1/user/{user_id}` | Update a user by ID.      | `UserUpdateReq` |

---

### Schemas (Key Models)

| Schema                | Description                                             |
| :-------------------- | :------------------------------------------------------ |
| `Token`               | JWT access token response.                              |
| `UserCreate`          | Request body for creating a new user.                   |
| `UserRead`            | Standard response model for returning user information. |
| `HTTPValidationError` | Standard validation error response.                     |

## Project Structure
