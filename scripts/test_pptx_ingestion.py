"""
Test script for PPTX ingestion and query testing
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from scraper.pptx_scraper import pptx_scraper
from services.embedding_service import embedding_service
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def create_sample_pptx_data(namespace: str = ""):
    """
    Create sample PPTX data directly in Pinecone for testing
    """
    print("\n" + "="*80)
    print("Creating Sample PPTX Data for Testing")
    print("="*80)
    
    from services.embedding_service import embedding_service
    
    # Sample PPTX content
    sample_chunks = [
        {
            'content': """Slide 1: Introduction to IBM Cloud
IBM Cloud is a comprehensive cloud computing platform that provides infrastructure as a service (IaaS), 
platform as a service (PaaS), and software as a service (SaaS) offerings. It enables businesses to 
build, deploy, and manage applications with enterprise-grade security and reliability.""",
            'metadata': {
                'filename': 'ibm_cloud_overview.pptx',
                'source_type': 'PowerPoint Presentation',
                'slide_number': 1,
                'total_slides': 5,
                'title': 'IBM Cloud Overview',
                'author': 'IBM',
                'category': 'Cloud Computing'
            }
        },
        {
            'content': """Slide 2: Key Features of IBM Cloud
- Hybrid Cloud Capabilities: Seamlessly integrate on-premises and cloud resources
- AI and Machine Learning: Built-in Watson AI services
- Security: Enterprise-grade security with compliance certifications
- Global Infrastructure: Data centers across multiple regions
- DevOps Tools: Integrated CI/CD pipelines and automation""",
            'metadata': {
                'filename': 'ibm_cloud_overview.pptx',
                'source_type': 'PowerPoint Presentation',
                'slide_number': 2,
                'total_slides': 5,
                'title': 'IBM Cloud Overview',
                'author': 'IBM',
                'category': 'Cloud Computing'
            }
        },
        {
            'content': """Slide 3: IBM Watson Services
IBM Watson provides AI-powered services including:
- Natural Language Processing (NLP)
- Computer Vision and Image Recognition
- Speech to Text and Text to Speech
- Machine Learning Model Training
- Chatbots and Virtual Assistants
Watson can be integrated into applications to add cognitive capabilities.""",
            'metadata': {
                'filename': 'ibm_watson_services.pptx',
                'source_type': 'PowerPoint Presentation',
                'slide_number': 1,
                'total_slides': 3,
                'title': 'IBM Watson Services',
                'author': 'IBM',
                'category': 'Artificial Intelligence'
            }
        },
        {
            'content': """Slide 4: IBM Cloud Security
IBM Cloud provides comprehensive security features:
- Data Encryption: At rest and in transit
- Identity and Access Management (IAM)
- Network Security: Firewalls, VPNs, and DDoS protection
- Compliance: GDPR, HIPAA, SOC 2, ISO 27001
- Security Monitoring: 24/7 threat detection and response""",
            'metadata': {
                'filename': 'ibm_cloud_security.pptx',
                'source_type': 'PowerPoint Presentation',
                'slide_number': 1,
                'total_slides': 4,
                'title': 'IBM Cloud Security',
                'author': 'IBM',
                'category': 'Security'
            }
        },
        {
            'content': """Slide 5: Getting Started with IBM Cloud
Steps to get started:
1. Create an IBM Cloud account
2. Choose your service (IaaS, PaaS, or SaaS)
3. Configure your resources
4. Deploy your application
5. Monitor and scale as needed
Free tier available for testing and development.""",
            'metadata': {
                'filename': 'ibm_cloud_getting_started.pptx',
                'source_type': 'PowerPoint Presentation',
                'slide_number': 1,
                'total_slides': 2,
                'title': 'Getting Started with IBM Cloud',
                'author': 'IBM',
                'category': 'Tutorial'
            }
        }
    ]
    
    print(f"\nIngesting {len(sample_chunks)} sample PPTX chunks...")
    
    results = await embedding_service.ingest_documents(
        sample_chunks,
        namespace=namespace
    )
    
    print(f"✅ Successfully ingested {results.get('stored', 0)} vectors")
    print(f"   Namespace: {namespace or '(default)'}")
    
    return results


async def test_queries(namespace: str = ""):
    """
    Test queries against ingested PPTX data
    """
    print("\n" + "="*80)
    print("Testing Queries")
    print("="*80)
    
    test_queries = [
        "What is IBM Cloud?",
        "Tell me about IBM Watson services",
        "What security features does IBM Cloud provide?",
        "How do I get started with IBM Cloud?",
        "What are the key features of IBM Cloud?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[Query {i}] {query}")
        print("-" * 80)
        
        try:
            # Search for similar documents
            results = await embedding_service.search_similar(
                query=query,
                namespace=namespace,
                top_k=3
            )
            
            if results:
                print(f"Found {len(results)} results:\n")
                for j, result in enumerate(results, 1):
                    metadata = result.get('metadata', {})
                    score = result.get('score', 0)
                    content = result.get('content', '')[:200]
                    
                    print(f"  Result {j} (Score: {score:.4f})")
                    print(f"  File: {metadata.get('filename', 'Unknown')}")
                    print(f"  Slide: {metadata.get('slide_number', 'N/A')}")
                    print(f"  Content: {content}...")
                    print()
            else:
                print("  No results found")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
    
    print("="*80)


async def main():
    """Main function"""
    print("\n" + "="*80)
    print("PPTX Ingestion and Query Test")
    print("="*80)
    
    # Check if a local PPTX file path was provided
    if len(sys.argv) > 1 and sys.argv[1].endswith(('.pptx', '.ppt')):
        pptx_path = sys.argv[1]
        namespace = sys.argv[2] if len(sys.argv) > 2 else ""
        
        print(f"\nProcessing local PPTX file: {pptx_path}")
        
        if not Path(pptx_path).exists():
            print(f"❌ File not found: {pptx_path}")
            sys.exit(1)
        
        result = await pptx_scraper.process_pptx(
            pptx_path,
            namespace=namespace,
            chunk_by_slide=True
        )
        
        if result['success']:
            print(f"✅ Successfully processed PPTX")
            print(f"   Slides: {result['slides_processed']}/{result['total_slides']}")
            print(f"   Chunks: {result['chunks_created']}")
            print(f"   Vectors: {result['vectors_stored']}")
        else:
            print(f"❌ Failed to process PPTX: {result.get('error')}")
            sys.exit(1)
    else:
        # Create sample data
        namespace = sys.argv[1] if len(sys.argv) > 1 else ""
        await create_sample_pptx_data(namespace)
    
    # Test queries
    namespace = sys.argv[2] if len(sys.argv) > 2 else (sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].endswith(('.pptx', '.ppt')) else "")
    await test_queries(namespace)
    
    print("\n✅ Test complete!\n")


if __name__ == "__main__":
    print("\nUsage:")
    print("  python test_pptx_ingestion.py [pptx_file] [namespace]")
    print("  python test_pptx_ingestion.py [namespace]  # Use sample data")
    print("\nExamples:")
    print("  python test_pptx_ingestion.py  # Sample data, default namespace")
    print("  python test_pptx_ingestion.py my-namespace  # Sample data, custom namespace")
    print("  python test_pptx_ingestion.py presentation.pptx  # Local file, default namespace")
    print("  python test_pptx_ingestion.py presentation.pptx my-namespace  # Local file, custom namespace")
    print()
    
    asyncio.run(main())

# Made with Bob
