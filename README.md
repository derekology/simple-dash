# Simple Dash

**Privacy-first email campaign analytics tool** that helps you visualize and compare your email marketing performance across multiple campaigns.

[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128.0-green.svg)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.5-brightgreen.svg)](https://vuejs.org/)

## ✨ Features

- 📊 **Instant Insights** - Upload CSV reports and instantly see trends and performance comparisons
- 🔒 **Privacy First** - Files are parsed on the server and immediately discarded with no persistent storage
- 🚀 **No Setup Required** - No accounts, no tracking, no cookies
- 📈 **Multi-Platform Support** - MailChimp and MailerLite Classic formats
- 📉 **Interactive Charts** - Visualize campaign performance with Chart.js
- 🎯 **Trend Analysis** - Compare metrics across campaigns and time
- 🔄 **Automatic Deduplication** - Smart handling of duplicate campaigns

## 🚀 Quick Start

### Using Docker (Recommended)

**Linux/Mac:**

```bash
./start.sh
```

**Windows:**

```cmd
start.bat
```

**Or manually:**

```bash
docker compose up -d
```

Access the application at `http://localhost:8000`

### Manual Installation

**Backend:**

```bash
# Install Python dependencies
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**

```bash
# Install Node dependencies
cd frontend
npm install

# Development mode
npm run dev

# Production build
npm run build
```

## 📖 Documentation

- [Docker Setup Guide](DOCKER_SETUP.md) - Comprehensive Docker documentation
- [Deployment Guide](DEPLOYMENT.md) - Production deployment instructions

## 🏗️ Architecture

### Tech Stack

**Backend:**

- FastAPI (Python 3.11)
- Pandas for CSV parsing
- Uvicorn ASGI server

**Frontend:**

- Vue.js 3 with TypeScript
- Vue Router
- Chart.js / Vue-ChartJS
- Vite build tool

### Project Structure

```
simpledash/
├── app/                    # FastAPI backend
│   ├── main.py            # API endpoints
│   ├── models.py          # Data models
│   └── parsers/           # CSV parsers
│       ├── detector.py    # Platform detection
│       ├── mailchimp.py   # MailChimp parser
│       └── mailerlite_classic.py
├── frontend/              # Vue.js frontend
│   ├── src/
│   │   ├── components/    # Vue components
│   │   ├── views/         # Page views
│   │   ├── resources/     # Constants and maps
│   │   └── router/        # Vue Router config
│   └── dist/              # Built static files
├── Dockerfile             # Multi-stage Docker build
├── docker-compose.yml     # Docker Compose config
├── requirements.txt       # Python dependencies
└── Makefile              # Helper commands
```

## 🔧 Configuration

### Environment Variables

| Variable        | Default    | Description          |
| --------------- | ---------- | -------------------- |
| `PORT`          | `8000`     | Server port          |
| `MAX_FILE_SIZE` | `10485760` | Max file size (10MB) |
| `MAX_FILES`     | `12`       | Max files per upload |

Create a `.env` file:

```env
PORT=8000
MAX_FILE_SIZE=10485760
MAX_FILES=12
```

## 📊 Supported Platforms

### MailChimp

- Export campaign reports as CSV
- Multiple campaigns per file supported
- Automatic deduplication by unique ID

### MailerLite Classic

- Export campaign reports as CSV
- Single or multiple campaigns

**More platforms coming soon!**

## 🔒 Privacy & Security

- **No persistent storage** - CSV files are parsed and immediately discarded
- **Session-only data** - Parsed data stored in browser session storage
- **No tracking** - No cookies, no accounts, no analytics
- **Non-root container** - Docker security best practices
- **CORS configured** - Secure cross-origin requests

## 🐳 Docker

### Quick Commands

```bash
# Build image
docker compose build

# Start container
docker compose up -d

# View logs
docker compose logs -f

# Stop container
docker compose down

# Restart
docker compose restart

# Shell access
docker compose exec simpledash sh
```

### Using Makefile

```bash
make build    # Build image
make up       # Start container
make down     # Stop container
make logs     # View logs
make restart  # Restart container
make clean    # Clean everything
make shell    # Open shell
make health   # Check health
```

## 🚀 Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed production deployment instructions including:

- Reverse proxy setup (nginx)
- SSL/TLS with Let's Encrypt
- Security hardening
- Monitoring and logging
- Scaling strategies

### Quick Production Setup

```bash
# 1. Clone and configure
git clone https://github.com/derekology/simpledash
cd simpledash
cp .env.example .env

# 2. Build and start
docker compose up -d
```

## 🛠️ Development

### Run in Development Mode

**Backend:**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend
npm run dev
```

Access frontend dev server at `http://localhost:5173`

### Build for Production

```bash
# Build frontend
cd frontend
npm run build

# Frontend dist will be served by FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📝 API Endpoints

### POST /parse

Upload and parse CSV files

**Request:**

- Content-Type: `multipart/form-data`
- Body: Multiple CSV files (max 12)

**Response:**

```json
{
  "results": [...],
  "errors": [...]
}
```

### GET /health

Health check endpoint

**Response:**

```json
{
  "status": "healthy",
  "max_file_size": 10485760,
  "max_files": 12
}
```

### GET /

Serve frontend application

## 🧪 Testing

```bash
# Backend tests (if implemented)
pytest

# Frontend tests
cd frontend
npm run test

# Linting
cd frontend
npm run lint
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

ISC

## ⚠️ Disclaimer

Simple Dash is provided "as-is" without warranties. Files are sent to the server for parsing and immediately discarded with no persistent storage. Users are responsible for compliance with data privacy laws and regulations.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Frontend powered by [Vue.js](https://vuejs.org/)
- Charts by [Chart.js](https://www.chartjs.org/)

## 📧 Support

For issues or questions:

- Open an issue on GitHub
