# AkibaFlow - Budgeting App

AkibaFlow is a comprehensive budgeting application designed to help users plan their finances and track expenses effortlessly. The app leverages SMS integration to automatically capture and categorize spending, making financial management intuitive and accessible.

## Features

- **User Authentication**: Secure login and registration system
- **Expense Tracking via SMS**: Automatically parse and record expenses from SMS notifications
- **Budget Planning**: Create and manage personal budgets
- **Transaction Management**: View, categorize, and analyze spending patterns
- **Real-time Notifications**: Get alerts on budget limits and spending trends
- **API-Driven Architecture**: RESTful API for seamless integration

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Authentication**: JWT tokens
- **Task Queue**: Celery with Redis
- **Containerization**: Docker & Docker Compose
- **Documentation**: Auto-generated API docs with Swagger/ReDoc

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/akibaflow.git
   cd akibaflow
   ```

2. Create environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start the application:
   ```bash
   docker-compose up --build
   ```

4. Access the API documentation at `http://localhost:8000/api/v1/docs`

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run database migrations:
   ```bash
   alembic upgrade head
   ```

3. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration

### User Management
- `GET /api/v1/user/me` - Get current user info
- `PUT /api/v1/user/me` - Update user profile

### Transactions (Planned)
- `GET /api/v1/transactions` - List transactions
- `POST /api/v1/transactions` - Create transaction
- `PUT /api/v1/transactions/{id}` - Update transaction

### Budgets (Planned)
- `GET /api/v1/budgets` - List budgets
- `POST /api/v1/budgets` - Create budget
- `PUT /api/v1/budgets/{id}` - Update budget

## Project Structure

```
akibaflow/
├── app/
│   ├── api/v1/          # API version 1 routes
│   ├── core/            # Configuration and core functionality
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   └── celery/          # Background tasks
├── tests/               # Test suites
├── scripts/             # Utility scripts
├── alembic/             # Database migrations
└── docker-compose.yml   # Container orchestration
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

- [ ] SMS parsing and integration
- [ ] Budget creation and monitoring
- [ ] Transaction categorization
- [ ] Financial reports and analytics
- [ ] Mobile app companion
- [ ] Multi-currency support</content>
<parameter name="filePath">/home/andrew-ambuka/AkibaFlow/README.md
