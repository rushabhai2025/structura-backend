# Structura.AI Backend

A FastAPI-based backend service for Structura.AI that provides comprehensive PDF data extraction for technical, commercial, and basic machine specifications.

## 🚀 Features

- **Comprehensive PDF Extraction**: Extract technical, commercial, and basic data from PDFs
- **Multi-Stakeholder Output**: Generate specialized data for:
  - **Technical**: Engineering specifications and technical details
  - **Commercial**: Pricing, terms, and commercial information  
  - **Basic**: Machine details and applications
- **AI-Powered Analysis**: Uses OpenAI GPT for intelligent data extraction
- **PDF Processing**: Robust PDF text extraction with PDF.co API
- **RESTful API**: Clean, documented API endpoints
- **Railway Ready**: Optimized for Railway deployment
- **Health Monitoring**: Built-in health check endpoints
- **CORS Support**: Cross-origin resource sharing enabled

## 📋 API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /health` - Detailed health status

### PDF Data Extraction
- `POST /extract-pdf` - Extract comprehensive data from PDF file
- `POST /extract-quotes` - Extract quotes from text (legacy)
- `GET /api/v1/info` - Service information

## 🛠️ Local Development

### Prerequisites
- Python 3.8+
- pip
- OpenAI API key
- PDF.co API key (optional, for enhanced PDF processing)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd structura-backend
```

2. Create a virtual environment:
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
# Edit .env with your API keys
```

5. Run the development server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🚀 Railway Deployment

### Automatic Deployment
1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Python project
3. The service will be deployed using the configuration in `railway.json`

### Manual Deployment
1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login to Railway:
```bash
railway login
```

3. Initialize and deploy:
```bash
railway init
railway up
```

## 📝 Usage Examples

### Extract comprehensive data from PDF
```bash
curl -X POST "http://localhost:8000/extract-pdf" \
  -F "file=@machine_specifications.pdf"
```

### Extract quotes from text (legacy)
```bash
curl -X POST "http://localhost:8000/extract-quotes" \
  -H "Content-Type: application/json" \
  -d '{"text": "Albert Einstein said \"Imagination is more important than knowledge.\""}'
```

### Response Format (PDF Extraction)
```json
{
  "success": true,
  "filename": "machine_specifications.pdf",
  "text_length": 5000,
  "technical_fields": 45,
  "commercial_fields": 30,
  "basic_fields": 25,
  "data": {
    "technical": {
      "machine_model": "PF1-2000",
      "forming_area": "2000x1500mm",
      "heating_power": "50kW"
    },
    "commercial": {
      "base_price": "$150,000",
      "lead_time": "8-12 weeks",
      "warranty_period": "2 years"
    },
    "basic": {
      "machine_description": "Advanced thermoforming machine",
      "applications": "Automotive, packaging, medical"
    }
  }
}
```

## 🔧 Configuration

### Environment Variables
- `PORT`: Server port (default: 8000)
- `CORS_ORIGINS`: Allowed CORS origins (default: "*")
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `PDFCO_API_KEY`: PDF.co API key for enhanced PDF processing (optional)

### Railway Environment Variables
Railway automatically sets:
- `PORT`: Railway-assigned port
- `RAILWAY_STATIC_URL`: Static asset URL

## 📊 Monitoring

### Health Checks
- Railway automatically monitors `/health` endpoint
- Returns service status and version information

### Logging
- Application logs are available in Railway dashboard
- Log level: INFO
- Structured logging for debugging

## 🧪 Testing

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test quote extraction
curl -X POST "http://localhost:8000/extract-quotes" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test quote: \"Hello, world!\""}'
```

### Sample Test Data
```python
test_text = '''
"Be the change you wish to see in the world." - Mahatma Gandhi
Albert Einstein once said, "Imagination is more important than knowledge."
> This is a block quote that should be extracted
"Hello," said John. "How are you today?"
'''
```

## 🔒 Security Considerations

- CORS is configured for development (allow all origins)
- For production, configure specific allowed origins
- File upload size limits are enforced
- Input validation on all endpoints

## 📈 Performance

- Optimized quote extraction algorithms
- Efficient text processing
- Minimal memory footprint
- Fast response times

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the API documentation at `/docs`
- Review the health endpoint at `/health`

---

**Built with ❤️ for Structura.AI** 