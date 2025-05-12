# PharmaHub - Medical Store Management System

PharmaHub is a comprehensive medical store management system that enables efficient management of multiple medical stores, their inventory, and operations.

## Features

- Multi-store management system
- Real-time inventory tracking
- Customer management
- Purchase tracking
- Data analytics and reporting
- QR code-based remote access

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- SQLite3

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pharmahub.git
cd pharmahub
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

The application can be run in two modes:

### Local Mode
For development and local access:
```bash
python main.py local
```
This will start the server at `http://localhost:8000`

### Remote Mode
For remote access across your network:
```bash
python main.py remote
```
This will:
- Start the server on your local network
- Generate a QR code for easy mobile access
- Display the server URL for browser access

## Project Structure

```
pharmahub/
├── api/                    # API routes and endpoints
├── src/                    # Source code
│   ├── database/          # Database models and operations
│   ├── utils/             # Utility functions
│   └── init_db.py         # Database initialization
├── templates/             # HTML templates
├── static/               # Static files (CSS, JS, images)
├── results/              # Database and logs
│   ├── logs/            # Application logs
│   └── medical_store.db # SQLite database
└── docs/                # Documentation
```

## Database

The system uses SQLite as its database. The database is automatically initialized when you first run the application. It includes tables for:

- Stores
- Medicines
- Customers
- Operators
- Purchases
- Storage Locations
- Batches

## Logging

Logs are stored in the `results/logs` directory with timestamps. Each component has its own log file:
- Main application logs: `main_*.log`
- Database logs: `database_*.log`
- Initialization logs: `init_db_*.log`

## Security

- The system uses FastAPI's built-in security features
- All database operations are parameterized to prevent SQL injection
- Sensitive data is properly handled and not exposed in logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the development team.

## Documentation

For detailed documentation about individual store management and other features, please refer to the `docs` directory.
