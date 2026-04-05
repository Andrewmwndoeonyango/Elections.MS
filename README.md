# Kenya Elections Management System

A comprehensive web-based system for managing elections in Kenya, built with Django.

## Features

- Voter registration with ID/Passport verification
- Role-based access control (Voters and Admins)
- Support for six election positions:
  - President
  - Governor
  - Senator
  - Women Representative
  - Member of Parliament
  - Member of County Assembly
- Nested dependent dropdowns for location selection
- Real-time election statistics and results
- Admin dashboard with detailed analytics
- Secure voting system with vote verification
- Mobile-responsive design

## Requirements

- Python 3.8+
- SQLite 3 (configured by default)
- Other dependencies listed in requirements.txt

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd elections
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure database:

- SQLite is configured by default (db.sqlite3 file will be created)
- Optionally update database settings in elections/settings.py for PostgreSQL

5. Apply migrations:

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

6. Create a superuser:

```bash
python3 manage.py createsuperuser
```

7. Run the development server:

```bash
python3 manage.py runserver
```

## Initial Setup

1. Log in to the admin interface at http://localhost:8000/admin
2. Add the following data:
   - Counties
   - Constituencies
   - Wards
   - Polling Centers
   - Polling Stations
   - Political Parties
   - Election Positions
   - Candidates

## Usage

1. Voters can:
   - Register with their details
   - Log in to their account
   - View their profile
   - Cast votes for different positions
   - View their voting history

2. Admins can:
   - Manage all system data through the admin interface
   - View real-time election statistics
   - Monitor voter registration and voting trends
   - Generate reports and analytics

## Security Features

- Password hashing and validation
- CSRF protection
- Session management
- One vote per position per voter
- Audit trail for all votes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
