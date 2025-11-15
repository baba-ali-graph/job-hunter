# Job Hunter Bot

AI-Powered Job Analysis & CV Optimization Bot with FastAPI, robust error handling, and Discord integration.

## Features

- **Job Analysis**: Parse job postings from URLs or raw text and extract key requirements
- **CV Analysis**: Analyze CV files (PDF, DOCX) and extract skills, experience, and education
- **CV Optimization**: Compare CV against job requirements and provide improvement suggestions
- **Discord Integration**: Send analysis results and recommendations via Discord webhooks
- **RESTful API**: FastAPI-based API with comprehensive error handling
- **Rate Limiting**: Built-in rate limiting and security measures
- **Comprehensive Testing**: Unit and integration tests with 90%+ coverage

## Quick Start

### Prerequisites

- Python 3.9+
- Docker (optional)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd job-hunter
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Docker Installation

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

## API Documentation

Once the application is running, visit:
- **Swagger UI**: `http://localhost:8000/api/v1/docs`
- **ReDoc**: `http://localhost:8000/api/v1/redoc`

## API Endpoints

### Job Analysis

- `POST /api/v1/jobs/analyze` - Analyze a job posting
- `GET /api/v1/jobs/{job_id}` - Get job analysis by ID
- `GET /api/v1/jobs/` - List job analyses

### CV Analysis

- `POST /api/v1/cv/analyze` - Analyze a CV file
- `POST /api/v1/cv/optimize` - Optimize CV for a specific job
- `GET /api/v1/cv/{cv_id}` - Get CV analysis by ID
- `GET /api/v1/cv/` - List CV analyses

### Discord Integration

- `POST /api/v1/discord/webhook` - Send message to Discord webhook
- `POST /api/v1/discord/job-analysis` - Send job analysis to Discord
- `POST /api/v1/discord/cv-optimization` - Send CV optimization to Discord

### Health & Monitoring

- `GET /api/v1/health/` - Health check
- `GET /api/v1/health/ready` - Readiness check
- `GET /api/v1/health/live` - Liveness check
- `GET /api/v1/health/metrics` - Service metrics

## Usage Examples

### Analyze a Job Posting

```bash
curl -X POST "http://localhost:8000/api/v1/jobs/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "job_url": "https://example.com/job/123",
       "job_description": "We are looking for a Senior Python Developer..."
     }'
```

### Analyze a CV

```bash
curl -X POST "http://localhost:8000/api/v1/cv/analyze" \
     -F "file=@cv.pdf"
```

### Send Results to Discord

```bash
curl -X POST "http://localhost:8000/api/v1/discord/webhook" \
     -H "Content-Type: application/json" \
     -d '{
       "webhook_url": "https://discord.com/api/webhooks/123456789/abcdef",
       "message": {
         "content": "Job Analysis Complete! 🎯",
         "username": "Job Hunter Bot"
       }
     }'
```

## Configuration

The application can be configured using environment variables. See `.env.example` for all available options.

### Key Configuration Options

- `DEBUG`: Enable debug mode (default: false)
- `RATE_LIMIT_REQUESTS`: Max requests per window (default: 10)
- `RATE_LIMIT_WINDOW`: Rate limit window in seconds (default: 60)
- `MAX_FILE_SIZE`: Maximum CV file size in bytes (default: 10MB)
- `ALLOWED_FILE_TYPES`: Allowed CV file types (default: pdf,docx,doc)

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/  # Integration tests only
```

## Development

### Code Quality

The project uses several tools for code quality:

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/
```

### Project Structure

```
job-hunter/
├── app/
│   ├── api/           # API endpoints and dependencies
│   ├── core/          # Core configuration and exceptions
│   ├── models/        # Pydantic models
│   ├── services/      # Business logic services
│   ├── utils/         # Utility functions
│   └── main.py        # FastAPI application
├── tests/
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   └── fixtures/      # Test fixtures
├── docs/              # Documentation
├── scripts/           # Utility scripts
├── requirements.txt   # Python dependencies
├── pyproject.toml     # Project configuration
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose setup
└── README.md          # This file
```

## Error Handling

The application includes comprehensive error handling:

- **Validation Errors**: Input validation with detailed error messages
- **Rate Limiting**: Automatic rate limiting with retry-after headers
- **External Service Errors**: Graceful handling of external API failures
- **File Processing Errors**: Robust file parsing with fallback mechanisms
- **Discord Webhook Errors**: Retry logic with exponential backoff

## Security

- Input validation and sanitization
- Rate limiting per IP address
- File upload restrictions
- HTTPS enforcement (in production)
- Secure webhook URL handling

## Monitoring

The application includes built-in monitoring:

- Health check endpoints
- Metrics collection
- Structured logging
- Request/response logging
- Error tracking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/api/v1/docs`
- Review the test cases for usage examples
- 
- 
- 
- 
## Setting up Dependencies
```sh

sudo dnf install -y python3-devel gcc gcc-c++ make
```
