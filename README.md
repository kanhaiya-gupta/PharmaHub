# PharmaHub - Medical Store Management System

PharmaHub is a comprehensive medical store management system that enables efficient management of multiple medical stores, their inventory, and operations. The system supports both centralized and distributed deployments, allowing stores to operate independently while maintaining data synchronization.

## Features

- Multi-store management system
- Real-time inventory tracking
- Customer management
- Purchase tracking
- Data analytics and reporting
- Offline operation support
- Automatic data synchronization
- Secure cloud-based deployment

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- SQLite3
- Internet connection for remote stores

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

The application can be run in three modes:

### Development Mode
For local development and testing:
```bash
python main.py dev
```
This will start the server at `http://localhost:8000`

### Store Mode
For individual store deployment:
```bash
python main.py store --store-id <store_id> --server-url <main_server_url>
```
This will:
- Start the store's local server
- Connect to the main PharmaHub server
- Enable offline operation with data synchronization
- Store data is cached locally and synced when online

### Server Mode
For main server deployment:
```bash
python main.py server --host <host> --port <port>
```
This will:
- Start the main PharmaHub server
- Handle connections from multiple stores
- Manage data synchronization
- Provide centralized analytics and reporting

## Deployment Architecture

### Main Server
- Hosted on a cloud platform (AWS, Azure, GCP)
- Handles central database and analytics
- Manages store connections and data sync
- Provides web interface for data management

### Store Deployment
Each store runs its own instance:
- Local server for offline operation
- Local database for caching
- Automatic data synchronization
- Secure connection to main server

### Data Synchronization
- Real-time sync when online
- Queue-based sync when offline
- Conflict resolution
- Data integrity checks

## Accessing the System

### Main Dashboard
- URL: `https://your-domain.com/` (production)
- URL: `http://localhost:8000/` (development)
- Shows overview of all stores
- Access to data manager features
- System-wide statistics

### Individual Stores
Each store has its own dedicated dashboard:
- Local access: `http://localhost:8000/stores/{store_id}` (development)
- Remote access: `https://your-domain.com/stores/{store_id}` (production)
- Example: `https://your-domain.com/stores/1` for the first store

### Store Management
- List all stores: `/stores`
- Add new store: `/stores/add`
- Store dashboard: `/stores/{store_id}/dashboard`

### Data Manager Access
- Data manager dashboard: `/data-manager`
- Analytics: `/data-manager/analytics`
- Reports: `/data-manager/reports`

## Project Structure

```
pharmahub/
├── api/                    # API routes and endpoints
│   ├── routes/            # API route modules
│   │   ├── sync.py       # Sync endpoints
│   │   ├── stores.py     # Store endpoints
│   │   └── data_manager.py # Data manager endpoints
├── src/                    # Source code
│   ├── database/          # Database models and operations
│   ├── utils/             # Utility functions
│   ├── sync/             # Data synchronization
│   └── init_db.py         # Database initialization
├── templates/             # HTML templates
├── static/               # Static files (CSS, JS, images)
├── results/              # Database and logs
│   ├── logs/            # Application logs
│   └── medical_store.db # SQLite database
└── docs/                # Documentation
```

## Database

The system uses SQLite as its database. Each store has its own local database that syncs with the main server:
- Main server: Central database for all stores
- Store instances: Local database for offline operation
- Automatic synchronization when online

## Logging

Logs are stored in the `results/logs` directory with timestamps. Each component has its own log file:
- Main application logs: `main_*.log`
- Database logs: `database_*.log`
- Initialization logs: `init_db_*.log`
- Sync logs: `sync_*.log`

## Security

- The system uses FastAPI's built-in security features
- All database operations are parameterized to prevent SQL injection
- Sensitive data is properly handled and not exposed in logs
- Secure HTTPS connections for remote access
- Token-based authentication for store connections
- Data encryption during synchronization

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
