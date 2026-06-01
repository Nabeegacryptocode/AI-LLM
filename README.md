# Fahm Faris

An AI-powered question-answering system that integrates with WordPress and uses IBM documentation as its knowledge base. Built with Retrieval Augmented Generation (RAG) to provide accurate, context-aware responses.

## 🌟 Features

- **RAG-Powered Q&A**: Accurate answers grounded in IBM documentation
- **WordPress Integration**: Easy-to-use chat widget for your WordPress site
- **Multi-Source Support**: Scrapes multiple IBM documentation sources
- **Scalable Architecture**: Grows from MVP to enterprise scale
- **Real-time Responses**: Fast query processing with caching
- **Source Citations**: Every answer includes source references
- **Admin Dashboard**: Monitor usage, costs, and performance
- **Customizable UI**: Themeable chat widget to match your brand

## 🏗️ Architecture

The system consists of three main components:

1. **Documentation Ingestion Pipeline**: Scrapes and processes IBM documentation
2. **Backend API**: FastAPI service with RAG implementation
3. **WordPress Plugin**: User-facing chat interface

```mermaid
graph LR
    A[User] --> B[WordPress Plugin]
    B --> C[Backend API]
    C --> D[Vector Database]
    C --> E[LLM Service]
    F[IBM Docs] --> G[Scraper]
    G --> D
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for development tools)
- WordPress 6.0+
- OpenAI API key
- Pinecone account (free tier available)

### Backend Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd fahm-faris
```

2. **Set up Python environment**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

4. **Initialize vector database**:
```bash
python scripts/setup_pinecone.py
```

5. **Ingest IBM documentation**:
```bash
python scripts/ingest_docs.py --source ibm-cloud --limit 100
```

6. **Start the API server**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### WordPress Plugin Setup

1. **Install the plugin**:
```bash
cd wordpress-plugin
zip -r fahm-faris.zip FAHMLLM3/
```

2. **Upload to WordPress**:
   - Go to WordPress Admin → Plugins → Add New
   - Click "Upload Plugin"
   - Select `fahm-faris.zip`
   - Click "Install Now" and then "Activate"

3. **Configure the plugin**:
   - Go to Settings → Fahm Faris
   - Enter your Backend API URL (e.g., `https://your-api.railway.app`)
   - Enter your API Key
   - Save settings

4. **Add chat widget to your site**:
   - Use shortcode: `[fahm_faris_chat]`
   - Or enable the floating widget in plugin settings

## 📚 Documentation

- [Architecture Design](ARCHITECTURE.md) - System architecture and design decisions
- [Implementation Guide](IMPLEMENTATION_GUIDE.md) - Detailed implementation instructions
- [API Documentation](docs/API.md) - API endpoints and usage
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment instructions
- [User Guide](docs/USER_GUIDE.md) - End-user documentation

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **LLM**: OpenAI GPT-4 Turbo
- **Vector DB**: Pinecone
- **Embeddings**: OpenAI text-embedding-3-small
- **Cache**: Redis
- **Database**: PostgreSQL

### WordPress Plugin
- **Language**: PHP 8.0+
- **Frontend**: Vanilla JavaScript
- **Styling**: CSS3
- **API**: WordPress REST API

### Infrastructure
- **Hosting**: Railway / Render / AWS
- **CI/CD**: GitHub Actions
- **Monitoring**: Application logs + Sentry

## 💰 Cost Estimation

### Monthly Costs (1000 queries/month)

| Service | Cost |
|---------|------|
| OpenAI API (GPT-4 Turbo) | $20-40 |
| OpenAI Embeddings | $1-2 |
| Backend Hosting (Railway) | $5-20 |
| Pinecone (Free Tier) | $0 |
| Redis (Free Tier) | $0 |
| **Total** | **$26-62** |

Costs scale linearly with usage. See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed cost analysis.

## 🔧 Configuration

### Backend Configuration (.env)

```env
# API Settings
API_KEY=your_secure_api_key_here
ALLOWED_ORIGINS=["https://your-wordpress-site.com"]

# LLM Settings
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.7
MAX_TOKENS=1000

# Vector DB Settings
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=fahm-faris

# Redis Settings
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600

# RAG Settings
TOP_K_RESULTS=5
CHUNK_SIZE=800
CHUNK_OVERLAP=200

# Database
DATABASE_URL=postgresql://user:pass@localhost/fahm_faris
```

### WordPress Plugin Settings

Configure in WordPress Admin → Settings → Fahm Faris:

- **API URL**: Your backend API endpoint
- **API Key**: Secure API key for authentication
- **Widget Title**: Customize chat widget title
- **Theme**: Light or dark theme
- **Position**: Floating widget position (bottom-right, bottom-left, etc.)

## 📊 Usage Examples

### Using the Chat Widget

1. **Shortcode in posts/pages**:
```
[fahm_faris_chat title="Ask Fahm Faris" theme="light"]
```

2. **PHP template**:
```php
<?php echo do_shortcode('[fahm_faris_chat]'); ?>
```

3. **Floating widget**: Enable in plugin settings

### API Usage

```bash
# Send a chat request
curl -X POST https://your-api.railway.app/api/chat \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I deploy a container on IBM Cloud?",
    "conversation_id": null
  }'
```

Response:
```json
{
  "answer": "To deploy a container on IBM Cloud...",
  "sources": [
    {
      "title": "IBM Cloud Container Registry",
      "url": "https://cloud.ibm.com/docs/...",
      "content": "...",
      "relevance_score": 0.92
    }
  ],
  "conversation_id": "conv_123",
  "tokens_used": 450
}
```

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Test WordPress Plugin
```bash
cd wordpress-plugin
# Install WordPress test suite
bash bin/install-wp-tests.sh wordpress_test root '' localhost latest
# Run tests
phpunit
```

### Manual Testing
1. Start backend: `uvicorn app.main:app --reload`
2. Test API: `curl http://localhost:8000/api/health`
3. Test WordPress plugin in local WordPress installation

## 🚢 Deployment

### Backend Deployment (Railway)

1. **Install Railway CLI**:
```bash
npm install -g @railway/cli
```

2. **Deploy**:
```bash
cd backend
railway login
railway init
railway up
```

3. **Set environment variables** in Railway dashboard

### WordPress Plugin Deployment

1. **Create release**:
```bash
cd wordpress-plugin
zip -r fahm-faris-v1.0.0.zip FAHMLLM3/
```

2. **Upload to WordPress** or distribute via WordPress.org

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

## 🔒 Security

- API key authentication for all requests
- Rate limiting to prevent abuse
- Input sanitization and validation
- CORS configuration for WordPress origins
- Secure storage of API keys in WordPress
- No PII stored in vector database

## 📈 Monitoring

### Key Metrics
- Query volume and response times
- Token usage and costs
- Cache hit rates
- Error rates and types
- User satisfaction scores

### Logging
- Structured JSON logs
- Error tracking with Sentry
- Performance monitoring
- Usage analytics in WordPress admin

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: See [docs/](docs/) folder
- **Issues**: Open an issue on GitHub
- **Email**: support@example.com

## 🗺️ Roadmap

### Phase 1 (Current)
- [x] Architecture design
- [x] Implementation guide
- [ ] Backend API development
- [ ] WordPress plugin development
- [ ] MVP deployment

### Phase 2 (Q3 2026)
- [ ] Multi-language support
- [ ] Advanced analytics
- [ ] Custom model fine-tuning
- [ ] Mobile app

### Phase 3 (Q4 2026)
- [ ] Voice interface
- [ ] IBM Cloud API integration
- [ ] Enterprise features
- [ ] White-label solution

## 🙏 Acknowledgments

- OpenAI for GPT-4 and embeddings API
- Pinecone for vector database
- IBM for comprehensive documentation
- WordPress community for plugin ecosystem

## 📞 Contact

- **Project Lead**: Your Name
- **Email**: your.email@example.com
- **Website**: https://your-website.com
- **GitHub**: https://github.com/yourusername/fahm-faris

---

Built with ❤️ for the IBM community
