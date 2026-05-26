# Cloud Billing System

A modern, full-featured billing system built with **Python Flask**, **SQLite**, **Bootstrap 5**, and vanilla **JavaScript**.

## Features

- **Dashboard** — Overview with stats cards (products, clients, invoices, revenue)
- **Products** — Full CRUD management with stock tracking
- **Clients** — Full CRUD management with contact details
- **Invoices** — Create, view, and delete invoices with line items
- **Login System** — Secure session-based authentication
- **Responsive Design** — Modern sidebar layout that works on all devices
- **SQLite Database** — Auto-created on first run, no setup required

## Requirements

- Python 3.8+
- pip (Python package manager)

## Quick Start

```bash
# 1. Clone or download the project
cd cloud-billing-system

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python app.py

# 4. Open in your browser
http://localhost:5000
```

## Default Login

| Username | Password  |
|----------|-----------|
| admin    | admin123  |

## Project Structure

```
├── app.py              # Flask application (routes, database, auth)
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── database.db         # SQLite database (auto-created)
├── templates/
│   ├── base.html           # Layout with sidebar & navbar
│   ├── login.html          # Login page
│   ├── dashboard.html      # Admin dashboard
│   ├── products.html       # Product list
│   ├── product_form.html   # Add/Edit product
│   ├── clients.html        # Client list
│   ├── client_form.html    # Add/Edit client
│   ├── invoices.html       # Invoice list
│   ├── invoice_form.html   # Create invoice
│   └── invoice_view.html   # Invoice detail / print view
└── static/
    ├── css/
    │   └── style.css       # Custom styles
    └── js/
        └── main.js          # Frontend functionality
```

## Deploy to Azure App Service

1. Create an Azure App Service (Python stack)
2. Deploy via Git, FTP, or ZIP deploy
3. Ensure `app.py` is the entry point
4. Set `debug=False` in production
5. Azure auto-installs from `requirements.txt`
6. For persistent storage, mount a storage account to replace the local SQLite file

## License

MIT
