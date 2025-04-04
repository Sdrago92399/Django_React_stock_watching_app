# Django React Stock Watching App

This repository contains a full-stack stock watching application built with Django (backend) and React/Next.js (frontend). The application includes features such as JWT authentication, real-time stock updates via WebSockets, stock search using a real stock API, user watchlists, and price alerts.

## Features

- **JWT Authentication:** Secure user registration and login with JSON Web Tokens.
- **Real-time Stock Updates:** Live stock price updates using Django Channels and WebSockets.
- **Stock Search:** Search for stocks using a real API (e.g., Alpha Vantage).
- **User Watchlist:** Add or remove stocks from your personal watchlist.
- **Price Alerts:** Set price alerts and receive notifications when a stock reaches your target price.
- **Modern Frontend:** Built with React/Next.js, Tailwind CSS, and Framer Motion for smooth animations.

## Getting Started

### Backend Setup (Django)

1. **Navigate to the backend directory:**

   ```bash
   cd stockwatch
   ```

2. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your environment variables:**  
   Create a `.env` file (or set environment variables) for settings such as your Django secret key, database connection, API keys (e.g., Alpha Vantage), email settings, etc.

4. **Run the Django development server on port 8000:**

   ```bash
   python manage.py runserver 8000
   ```

5. **Run the Daphne server for WebSocket connections on port 80001:**

   ```bash
   daphne -p 80001 stockwatch.asgi:application
   ```

### Frontend Setup (Next.js)

1. **Navigate to the frontend directory:**

   ```bash
   cd ../frontend
   ```

2. **Install Node.js dependencies:**

   ```bash
   npm install
   ```

3. **Start the Next.js development server:**

   ```bash
   npm run dev
   ```

   The frontend will start in development mode (typically on port 3000).

## Additional Information

- **Authentication:** The app uses Django REST Framework's Simple JWT for token-based authentication. After login, tokens are stored on the client (e.g., in localStorage) and attached to API requests.
- **WebSocket Connection:** The frontend connects to the Django Channels WebSocket endpoint (configured to run on port 80001) for live stock price updates.
- **Stock API Integration:** Stock search and price information are retrieved using a real stock API (e.g., Alpha Vantage). Make sure to set your API key in the environment variables.
- **Frontend Technologies:**  
  The frontend is built with React/Next.js, Tailwind CSS for styling, and Framer Motion for animations. It provides a modern, responsive UI for managing your watchlist and alerts.

## Repository Structure

```
├── stockwatch/               # Django backend
│   ├── manage.py
│   ├── requirements.txt
│   ├── stockwatch/           # Project settings, asgi, urls, etc.
│   └── ...                   # Apps (stocks, alerts, accounts, etc.)
└── frontend/                 # Next.js frontend
    ├── package.json
    ├── pages/
    ├── components/
    ├── hooks/
    └── ...                   # Other configuration files
```

## Contributing

Contributions are welcome! Please open issues or pull requests for improvements or bug fixes.

## License

This project is licensed under the MIT License.
