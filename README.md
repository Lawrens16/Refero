# Refero

Refero is a web-based Thesis Reference Management System designed specifically for 3rd and 4th-year college students. Similar to tools like Zotero, it allows users to collect, organize, cite, and share research materials to streamline the thesis writing process.

## Key Features

*   **Reference Management:** Organize thesis sources, journals, and articles in a centralized dashboard.
*   **User Accounts:** Secure signup and login functionality.
*   **Social Authentication:** Sign in easily using Google or Facebook accounts (powered by `django-allauth`).
*   **Citation Generation:** Automatically generate citations for stored references.
*   **Progressive Web App (PWA):** Installable on mobile and desktop devices for offline access.
*   **REST API:** Backend API support for potential mobile or external integrations.
*   **Email Notifications:** Integrated email services via SendGrid for account verification and updates.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

*   **Python** (3.8 or higher)
*   **pip** (Python package manager)
*   **Git**

## Installation & Setup

Follow these steps to set up the project locally.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Refero
```

### 2. Create and Activate a Virtual Environment

It is recommended to run this project in a virtual environment to manage dependencies.

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the `refero` directory (where `settings.py` is located) to store sensitive keys.

**File:** `refero/refero/.env`

```env
SECRET_KEY=your_secret_key_here
DEBUG=True
SENDGRID_API_KEY=your_sendgrid_api_key
```

### 5. Apply Database Migrations

Initialize the SQLite database and apply the models.

```bash
cd refero
python manage.py migrate
```

### 6. Create a Superuser (Optional)

To access the Django admin panel, create a superuser account.

```bash
python manage.py createsuperuser
```

### 7. Run the Development Server

Start the local server.

```bash
python manage.py runserver
```

## Usage

1.  **Access the App:** Open your browser and navigate to `http://127.0.0.1:8000/`.
2.  **Login/Signup:** Use the login page to create an account or sign in via Google/Facebook.
3.  **Admin Panel:** Access the administrative dashboard at `http://127.0.0.1:8000/admin/` using your superuser credentials.

## Tech Stack

*   **Backend:** Django 5.2.7
*   **API:** Django REST Framework
*   **Database:** SQLite (Development)
*   **Authentication:** Django Allauth
*   **Email:** Anymail (SendGrid)
*   **Frontend:** Django Templates + Bootstrap 5 (Crispy Forms)
