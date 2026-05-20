# IBM Documentation LLM - Implementation Guide

## Project Structure

```
ibm-docs-llm/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application
│   │   ├── config.py               # Configuration management
│   │   ├── models.py               # Pydantic models
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── chat.py             # Chat endpoints
│   │       ├── ingest.py           # Ingestion endpoints
│   │       └── health.py           # Health check endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py          # LLM interaction
│   │   ├── vector_service.py       # Vector DB operations
│   │   ├── embedding_service.py    # Embedding generation
│   │   └── cache_service.py        # Redis caching
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── base_scraper.py         # Base scraper class
│   │   ├── ibm_cloud_scraper.py    # IBM Cloud docs
│   │   ├── ibm_watson_scraper.py   # Watson docs
│   │   └── document_processor.py   # Text processing
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py               # Logging setup
│   │   └── auth.py                 # Authentication
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   ├── test_scraper.py
│   │   └── test_rag.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── wordpress-plugin/
│   ├── ibm-docs-llm/
│   │   ├── ibm-docs-llm.php        # Main plugin file
│   │   ├── includes/
│   │   │   ├── class-api-client.php
│   │   │   ├── class-settings.php
│   │   │   └── class-widget.php
│   │   ├── admin/
│   │   │   ├── admin-page.php
│   │   │   ├── settings-page.php
│   │   │   └── analytics-page.php
│   │   ├── public/
│   │   │   ├── css/
│   │   │   │   └── chat-widget.css
│   │   │   └── js/
│   │   │       └── chat-widget.js
│   │   ├── assets/
│   │   │   └── icon.png
│   │   └── readme.txt
├── docs/
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── USER_GUIDE.md
├── scripts/
│   ├── setup.sh
│   ├── deploy.sh
│   └── ingest_docs.py
├── ARCHITECTURE.md
├── IMPLEMENTATION_GUIDE.md
└── README.md
```

## Component Implementation Details

### 1. Backend API (FastAPI)

#### Main Application (backend/app/main.py)

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, ingest, health
from app.config import settings
from app.utils.logger import setup_logger

app = FastAPI(
    title="IBM Docs LLM API",
    version="1.0.0",
    description="RAG-powered Q&A system for IBM documentation"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(ingest.router, prefix="/api", tags=["ingest"])
app.include_router(health.router, prefix="/api", tags=["health"])

logger = setup_logger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting IBM Docs LLM API")
    # Initialize services
    
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down IBM Docs LLM API")
```

#### Configuration (backend/app/config.py)

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Settings
    API_KEY: str
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # LLM Settings
    OPENAI_API_KEY: str
    LLM_MODEL: str = "gpt-4-turbo-preview"
    LLM_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 1000
    
    # Embedding Settings
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536
    
    # Vector DB Settings
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str
    PINECONE_INDEX_NAME: str = "ibm-docs"
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600
    
    # RAG Settings
    TOP_K_RESULTS: int = 5
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 200
    
    # Database Settings
    DATABASE_URL: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

#### Chat Endpoint (backend/app/api/chat.py)

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.services.llm_service import LLMService
from app.services.vector_service import VectorService
from app.services.cache_service import CacheService
from app.utils.auth import verify_api_key

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None
    max_tokens: Optional[int] = 1000

class Source(BaseModel):
    title: str
    url: str
    content: str
    relevance_score: float

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    conversation_id: str
    tokens_used: int

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Process a chat request using RAG pipeline
    """
    try:
        # Check cache first
        cache_key = f"chat:{request.question}"
        cached_response = await CacheService.get(cache_key)
        if cached_response:
            return cached_response
        
        # Generate embedding for question
        question_embedding = await LLMService.generate_embedding(request.question)
        
        # Retrieve relevant documents
        relevant_docs = await VectorService.search(
            embedding=question_embedding,
            top_k=5
        )
        
        # Build context from retrieved documents
        context = "\n\n".join([doc.content for doc in relevant_docs])
        
        # Generate response using LLM
        response = await LLMService.generate_response(
            question=request.question,
            context=context,
            conversation_id=request.conversation_id,
            max_tokens=request.max_tokens
        )
        
        # Format sources
        sources = [
            Source(
                title=doc.metadata.get("title", ""),
                url=doc.metadata.get("url", ""),
                content=doc.content[:200] + "...",
                relevance_score=doc.score
            )
            for doc in relevant_docs
        ]
        
        chat_response = ChatResponse(
            answer=response.answer,
            sources=sources,
            conversation_id=response.conversation_id,
            tokens_used=response.tokens_used
        )
        
        # Cache the response
        await CacheService.set(cache_key, chat_response, ttl=3600)
        
        return chat_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. LLM Service (backend/services/llm_service.py)

```python
import openai
from typing import Optional
from app.config import settings

class LLMService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
    
    @staticmethod
    async def generate_embedding(text: str) -> list:
        """Generate embedding for text"""
        response = await openai.Embedding.acreate(
            model=settings.EMBEDDING_MODEL,
            input=text
        )
        return response['data'][0]['embedding']
    
    @staticmethod
    async def generate_response(
        question: str,
        context: str,
        conversation_id: Optional[str] = None,
        max_tokens: int = 1000
    ):
        """Generate response using RAG"""
        
        system_prompt = """You are an expert assistant for IBM documentation. 
        Answer questions based on the provided context from IBM documentation.
        If the answer is not in the context, say so clearly.
        Provide accurate, technical answers with examples when appropriate.
        Always cite the source documentation."""
        
        user_prompt = f"""Context from IBM Documentation:
{context}

Question: {question}

Please provide a detailed answer based on the context above."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await openai.ChatCompletion.acreate(
            model=settings.LLM_MODEL,
            messages=messages,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=max_tokens
        )
        
        return {
            "answer": response.choices[0].message.content,
            "conversation_id": conversation_id or response.id,
            "tokens_used": response.usage.total_tokens
        }
```

### 3. Documentation Scraper (backend/scraper/ibm_cloud_scraper.py)

```python
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
from app.scraper.base_scraper import BaseScraper
from app.scraper.document_processor import DocumentProcessor

class IBMCloudScraper(BaseScraper):
    """Scraper for IBM Cloud documentation"""
    
    BASE_URL = "https://cloud.ibm.com/docs"
    
    async def scrape_documentation(self, start_urls: List[str]) -> List[Dict]:
        """Scrape IBM Cloud documentation"""
        documents = []
        
        async with aiohttp.ClientSession() as session:
            for url in start_urls:
                try:
                    doc = await self._scrape_page(session, url)
                    if doc:
                        documents.append(doc)
                except Exception as e:
                    self.logger.error(f"Error scraping {url}: {e}")
        
        return documents
    
    async def _scrape_page(self, session: aiohttp.ClientSession, url: str) -> Dict:
        """Scrape a single page"""
        async with session.get(url) as response:
            if response.status != 200:
                return None
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract content
            title = soup.find('h1').text.strip() if soup.find('h1') else ""
            
            # Remove navigation, scripts, styles
            for tag in soup(['nav', 'script', 'style', 'header', 'footer']):
                tag.decompose()
            
            # Extract main content
            content_div = soup.find('main') or soup.find('article')
            content = content_div.get_text(separator='\n', strip=True) if content_div else ""
            
            # Process and chunk the document
            chunks = DocumentProcessor.chunk_document(
                content=content,
                chunk_size=800,
                chunk_overlap=200
            )
            
            return {
                "title": title,
                "url": url,
                "content": content,
                "chunks": chunks,
                "metadata": {
                    "source": "IBM Cloud Docs",
                    "scraped_at": datetime.now().isoformat()
                }
            }
```

### 4. WordPress Plugin (wordpress-plugin/ibm-docs-llm/ibm-docs-llm.php)

```php
<?php
/**
 * Plugin Name: IBM Docs LLM
 * Plugin URI: https://example.com/ibm-docs-llm
 * Description: AI-powered Q&A system using IBM documentation
 * Version: 1.0.0
 * Author: Your Name
 * License: GPL v2 or later
 */

if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('IBM_DOCS_LLM_VERSION', '1.0.0');
define('IBM_DOCS_LLM_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('IBM_DOCS_LLM_PLUGIN_URL', plugin_dir_url(__FILE__));

// Include required files
require_once IBM_DOCS_LLM_PLUGIN_DIR . 'includes/class-api-client.php';
require_once IBM_DOCS_LLM_PLUGIN_DIR . 'includes/class-settings.php';
require_once IBM_DOCS_LLM_PLUGIN_DIR . 'includes/class-widget.php';

// Initialize plugin
function ibm_docs_llm_init() {
    // Register settings
    IBM_Docs_LLM_Settings::init();
    
    // Register widget
    IBM_Docs_LLM_Widget::init();
    
    // Enqueue scripts and styles
    add_action('wp_enqueue_scripts', 'ibm_docs_llm_enqueue_scripts');
    add_action('admin_enqueue_scripts', 'ibm_docs_llm_admin_enqueue_scripts');
}
add_action('plugins_loaded', 'ibm_docs_llm_init');

// Enqueue frontend scripts
function ibm_docs_llm_enqueue_scripts() {
    wp_enqueue_style(
        'ibm-docs-llm-chat',
        IBM_DOCS_LLM_PLUGIN_URL . 'public/css/chat-widget.css',
        array(),
        IBM_DOCS_LLM_VERSION
    );
    
    wp_enqueue_script(
        'ibm-docs-llm-chat',
        IBM_DOCS_LLM_PLUGIN_URL . 'public/js/chat-widget.js',
        array('jquery'),
        IBM_DOCS_LLM_VERSION,
        true
    );
    
    // Pass settings to JavaScript
    wp_localize_script('ibm-docs-llm-chat', 'ibmDocsLLM', array(
        'apiUrl' => get_option('ibm_docs_llm_api_url'),
        'apiKey' => get_option('ibm_docs_llm_api_key'),
        'nonce' => wp_create_nonce('ibm_docs_llm_nonce')
    ));
}

// Register REST API endpoints
add_action('rest_api_init', function() {
    register_rest_route('ibm-llm/v1', '/chat', array(
        'methods' => 'POST',
        'callback' => 'ibm_docs_llm_handle_chat',
        'permission_callback' => '__return_true'
    ));
});

function ibm_docs_llm_handle_chat($request) {
    $question = sanitize_text_field($request->get_param('question'));
    
    // Call backend API
    $api_client = new IBM_Docs_LLM_API_Client();
    $response = $api_client->send_chat_request($question);
    
    return rest_ensure_response($response);
}

// Add shortcode for chat widget
function ibm_docs_llm_chat_shortcode($atts) {
    $atts = shortcode_atts(array(
        'title' => 'Ask IBM Docs',
        'placeholder' => 'Ask a question about IBM...',
        'theme' => 'light'
    ), $atts);
    
    ob_start();
    include IBM_DOCS_LLM_PLUGIN_DIR . 'public/chat-widget-template.php';
    return ob_get_clean();
}
add_shortcode('ibm_docs_chat', 'ibm_docs_llm_chat_shortcode');
```

### 5. Chat Widget JavaScript (wordpress-plugin/ibm-docs-llm/public/js/chat-widget.js)

```javascript
(function($) {
    'use strict';
    
    class IBMDocsChat {
        constructor() {
            this.conversationId = null;
            this.isLoading = false;
            this.init();
        }
        
        init() {
            this.bindEvents();
        }
        
        bindEvents() {
            $('#ibm-docs-chat-form').on('submit', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
            
            $('#ibm-docs-chat-toggle').on('click', () => {
                this.toggleChat();
            });
        }
        
        async sendMessage() {
            if (this.isLoading) return;
            
            const question = $('#ibm-docs-chat-input').val().trim();
            if (!question) return;
            
            this.isLoading = true;
            this.showLoading();
            
            try {
                const response = await $.ajax({
                    url: ibmDocsLLM.apiUrl + '/api/chat',
                    method: 'POST',
                    headers: {
                        'Authorization': 'Bearer ' + ibmDocsLLM.apiKey,
                        'Content-Type': 'application/json'
                    },
                    data: JSON.stringify({
                        question: question,
                        conversation_id: this.conversationId
                    })
                });
                
                this.conversationId = response.conversation_id;
                this.displayMessage(question, 'user');
                this.displayMessage(response.answer, 'assistant', response.sources);
                
                $('#ibm-docs-chat-input').val('');
                
            } catch (error) {
                console.error('Chat error:', error);
                this.displayError('Sorry, there was an error processing your request.');
            } finally {
                this.isLoading = false;
                this.hideLoading();
            }
        }
        
        displayMessage(text, role, sources = null) {
            const messageHtml = `
                <div class="chat-message chat-message-${role}">
                    <div class="message-content">${this.escapeHtml(text)}</div>
                    ${sources ? this.renderSources(sources) : ''}
                </div>
            `;
            
            $('#ibm-docs-chat-messages').append(messageHtml);
            this.scrollToBottom();
        }
        
        renderSources(sources) {
            if (!sources || sources.length === 0) return '';
            
            let html = '<div class="message-sources"><strong>Sources:</strong><ul>';
            sources.forEach(source => {
                html += `<li><a href="${source.url}" target="_blank">${source.title}</a></li>`;
            });
            html += '</ul></div>';
            
            return html;
        }
        
        showLoading() {
            $('#ibm-docs-chat-loading').show();
        }
        
        hideLoading() {
            $('#ibm-docs-chat-loading').hide();
        }
        
        toggleChat() {
            $('#ibm-docs-chat-widget').toggleClass('open');
        }
        
        scrollToBottom() {
            const messages = $('#ibm-docs-chat-messages');
            messages.scrollTop(messages[0].scrollHeight);
        }
        
        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        displayError(message) {
            this.displayMessage(message, 'error');
        }
    }
    
    // Initialize when document is ready
    $(document).ready(function() {
        new IBMDocsChat();
    });
    
})(jQuery);
```

## Deployment Instructions

### Backend Deployment (Railway/Render)

1. **Prepare Environment Variables**:
```bash
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_environment
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
API_KEY=your_secure_api_key
```

2. **Deploy to Railway**:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

3. **Set up Pinecone**:
```python
import pinecone

pinecone.init(
    api_key="your_api_key",
    environment="your_environment"
)

# Create index
pinecone.create_index(
    name="ibm-docs",
    dimension=1536,
    metric="cosine"
)
```

### WordPress Plugin Installation

1. Upload plugin folder to `/wp-content/plugins/`
2. Activate plugin in WordPress admin
3. Configure settings:
   - API URL: Your backend URL
   - API Key: Your secure API key
4. Add chat widget using shortcode: `[ibm_docs_chat]`

## Testing Strategy

### Unit Tests
- Test individual components (scraper, embeddings, LLM service)
- Mock external API calls
- Validate data processing

### Integration Tests
- Test RAG pipeline end-to-end
- Verify WordPress plugin API calls
- Test authentication and rate limiting

### Performance Tests
- Load testing with concurrent requests
- Measure response times
- Monitor token usage

## Monitoring Setup

### Application Logging
```python
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
```

### Metrics to Track
- Request count and latency
- Token usage and costs
- Cache hit rate
- Error rates
- User satisfaction (feedback)

## Next Steps

1. Review this implementation guide
2. Set up development environment
3. Implement backend API
4. Build WordPress plugin
5. Test integration
6. Deploy to production
7. Monitor and iterate

## Resources

- FastAPI Documentation: https://fastapi.tiangolo.com
- OpenAI API: https://platform.openai.com/docs
- Pinecone Documentation: https://docs.pinecone.io
- WordPress Plugin Development: https://developer.wordpress.org