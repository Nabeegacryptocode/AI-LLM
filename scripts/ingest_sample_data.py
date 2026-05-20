"""
Script to ingest sample IBM documentation data for testing
This bypasses web scraping and uses pre-defined sample content
"""
import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.embedding_service import embedding_service
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample IBM Cloud documentation content
SAMPLE_IBM_CLOUD_DOCS = [
    {
        "content": """IBM Cloud is a suite of cloud computing services from IBM that offers both platform as a service (PaaS) and infrastructure as a service (IaaS). IBM Cloud supports numerous programming languages and services as well as integrated DevOps to build, run, deploy and manage applications on the cloud. IBM Cloud is built on open-source technology and runs on a global network of data centers.""",
        "metadata": {
            "title": "What is IBM Cloud?",
            "url": "https://cloud.ibm.com/docs/overview?topic=overview-whatis-platform",
            "source_type": "IBM Cloud Docs",
            "product": "IBM Cloud Platform"
        }
    },
    {
        "content": """IBM Cloud Virtual Private Cloud (VPC) is a public cloud offering that lets an enterprise establish its own private cloud-like computing environment on shared public cloud infrastructure. A VPC gives an enterprise the ability to define and control a virtual network that is logically isolated from all other public cloud tenants, creating a private, secure place on the public cloud.""",
        "metadata": {
            "title": "IBM Cloud VPC Overview",
            "url": "https://cloud.ibm.com/docs/vpc?topic=vpc-about-vpc",
            "source_type": "IBM Cloud Docs",
            "product": "IBM Cloud VPC"
        }
    },
    {
        "content": """IBM Cloud Kubernetes Service is a managed container service to deploy, manage, and scale containerized apps on IBM Cloud. It provides intelligent scheduling, self-healing, horizontal scaling, service discovery and load balancing, automated rollouts and rollbacks, and secret and configuration management for your apps.""",
        "metadata": {
            "title": "IBM Cloud Kubernetes Service",
            "url": "https://cloud.ibm.com/docs/containers?topic=containers-getting-started",
            "source_type": "IBM Cloud Docs",
            "product": "IBM Cloud Kubernetes"
        }
    },
    {
        "content": """IBM Cloud Object Storage is a highly scalable cloud storage service, designed for high durability, resiliency and security. Store, manage and access your data via a self-service portal and RESTful APIs. Connect applications directly to Cloud Object Storage use other IBM Cloud Services with your data.""",
        "metadata": {
            "title": "IBM Cloud Object Storage",
            "url": "https://cloud.ibm.com/docs/cloud-object-storage?topic=cloud-object-storage-getting-started",
            "source_type": "IBM Cloud Docs",
            "product": "IBM Cloud Storage"
        }
    },
    {
        "content": """IBM Cloud Identity and Access Management (IAM) enables you to securely authenticate users and control access to all cloud resources consistently in the IBM Cloud. IAM provides a unified approach to managing user identities, services, and access control by using a common set of access policies.""",
        "metadata": {
            "title": "IBM Cloud IAM Overview",
            "url": "https://cloud.ibm.com/docs/account?topic=account-iamoverview",
            "source_type": "IBM Cloud Docs",
            "product": "IBM Cloud IAM"
        }
    }
]

# Sample IBM GDP documentation content
SAMPLE_IBM_GDP_DOCS = [
    {
        "content": """IBM Guardium Data Protection (GDP) is a comprehensive data security platform that provides data activity monitoring, vulnerability assessment, and compliance automation. Guardium helps organizations protect sensitive data across databases, data warehouses, big data platforms, and cloud environments. It provides real-time monitoring, alerting, and blocking of unauthorized data access.""",
        "metadata": {
            "title": "IBM Guardium Data Protection Overview",
            "url": "https://www.ibm.com/docs/en/gdp/11.5.0?topic=guardium-overview",
            "source_type": "IBM GDP Docs",
            "product": "IBM Guardium Data Protection",
            "version": "11.5.0"
        }
    },
    {
        "content": """Guardium installation involves deploying collectors, aggregators, and the central manager. Collectors monitor data sources and send audit data to aggregators. Aggregators process and store the data, while the central manager provides the user interface and reporting capabilities. Installation can be done on physical appliances, virtual machines, or cloud environments.""",
        "metadata": {
            "title": "Guardium Installation Guide",
            "url": "https://www.ibm.com/docs/en/gdp/11.5.0?topic=guardium-installing",
            "source_type": "IBM GDP Docs",
            "product": "IBM Guardium Data Protection",
            "version": "11.5.0"
        }
    },
    {
        "content": """Guardium configuration includes setting up data sources, defining security policies, configuring audit rules, and establishing user access controls. You can configure S-TAP (Software Tap) agents for database monitoring, set up vulnerability assessment scans, and define compliance workflows. Configuration is done through the Guardium Administration Console.""",
        "metadata": {
            "title": "Guardium Configuration",
            "url": "https://www.ibm.com/docs/en/gdp/11.5.0?topic=guardium-configuring",
            "source_type": "IBM GDP Docs",
            "product": "IBM Guardium Data Protection",
            "version": "11.5.0"
        }
    },
    {
        "content": """Guardium monitoring provides real-time visibility into data access patterns, user activities, and potential security threats. It monitors database queries, data modifications, privilege changes, and configuration changes. Guardium can detect anomalous behavior, policy violations, and suspicious activities, generating alerts and reports for security teams.""",
        "metadata": {
            "title": "Guardium Monitoring Capabilities",
            "url": "https://www.ibm.com/docs/en/gdp/11.5.0?topic=guardium-monitoring",
            "source_type": "IBM GDP Docs",
            "product": "IBM Guardium Data Protection",
            "version": "11.5.0"
        }
    },
    {
        "content": """Guardium security policies define rules for data access, user behavior, and compliance requirements. Policies can include access controls, separation of duties, data masking rules, and audit requirements. Guardium supports pre-built compliance templates for regulations like GDPR, HIPAA, PCI-DSS, and SOX, making it easier to achieve and maintain compliance.""",
        "metadata": {
            "title": "Guardium Security Policies",
            "url": "https://www.ibm.com/docs/en/gdp/11.5.0?topic=guardium-policies",
            "source_type": "IBM GDP Docs",
            "product": "IBM Guardium Data Protection",
            "version": "11.5.0"
        }
    },
    {
        "content": """Guardium reports provide detailed insights into data access patterns, compliance status, and security incidents. Built-in reports cover audit trails, user activities, policy violations, vulnerability assessments, and compliance metrics. Custom reports can be created using the report builder, and reports can be scheduled for automatic generation and distribution.""",
        "metadata": {
            "title": "Guardium Reporting",
            "url": "https://www.ibm.com/docs/en/gdp/11.5.0?topic=guardium-reports",
            "source_type": "IBM GDP Docs",
            "product": "IBM Guardium Data Protection",
            "version": "11.5.0"
        }
    },
    {
        "content": """Guardium API provides programmatic access to Guardium functionality, enabling integration with SIEM systems, ticketing systems, and custom applications. The REST API supports operations like querying audit data, managing policies, retrieving reports, and configuring data sources. API authentication uses API keys or OAuth tokens.""",
        "metadata": {
            "title": "Guardium API Reference",
            "url": "https://www.ibm.com/docs/en/gdp/11.5.0?topic=guardium-api",
            "source_type": "IBM GDP Docs",
            "product": "IBM Guardium Data Protection",
            "version": "11.5.0"
        }
    }
]

# Sample IBM MAS documentation content
SAMPLE_IBM_MAS_DOCS = [
    {
        "content": """IBM Maximo Application Suite is a set of applications for asset monitoring, management, predictive maintenance and reliability planning. Maximo Application Suite includes Maximo Manage, Maximo Monitor, Maximo Health, Maximo Predict, Maximo Visual Inspection, Maximo Assist, and Maximo Safety.""",
        "metadata": {
            "title": "IBM Maximo Application Suite Overview",
            "url": "https://www.ibm.com/docs/en/masv-and-l/cd?topic=overview",
            "source_type": "IBM MAS Docs",
            "product": "IBM Maximo Application Suite"
        }
    },
    {
        "content": """Maximo Manage is an enterprise asset management (EAM) solution that helps you manage your physical assets throughout their lifecycle. It provides comprehensive asset lifecycle and maintenance management capabilities including work order management, preventive maintenance, inventory management, and procurement.""",
        "metadata": {
            "title": "Maximo Manage Overview",
            "url": "https://www.ibm.com/docs/en/masv-and-l/cd?topic=manage",
            "source_type": "IBM MAS Docs",
            "product": "Maximo Manage"
        }
    },
    {
        "content": """Maximo Monitor uses AI-powered remote monitoring to provide visibility into asset performance and health. It ingests data from sensors and devices, applies analytics, and provides dashboards and alerts to help you understand asset conditions and take proactive action.""",
        "metadata": {
            "title": "Maximo Monitor Overview",
            "url": "https://www.ibm.com/docs/en/masv-and-l/cd?topic=monitor",
            "source_type": "IBM MAS Docs",
            "product": "Maximo Monitor"
        }
    },
    {
        "content": """Maximo Health provides asset health scoring and risk assessment capabilities. It analyzes asset data to calculate health scores, identify risks, and recommend actions. Health scores help you prioritize maintenance activities and optimize asset performance.""",
        "metadata": {
            "title": "Maximo Health Overview",
            "url": "https://www.ibm.com/docs/en/masv-and-l/cd?topic=health",
            "source_type": "IBM MAS Docs",
            "product": "Maximo Health"
        }
    },
    {
        "content": """Maximo Predict uses AI and machine learning to predict asset failures before they occur. It analyzes historical and real-time data to identify patterns and anomalies, enabling predictive maintenance strategies that reduce downtime and maintenance costs.""",
        "metadata": {
            "title": "Maximo Predict Overview",
            "url": "https://www.ibm.com/docs/en/masv-and-l/cd?topic=predict",
            "source_type": "IBM MAS Docs",
            "product": "Maximo Predict"
        }
    }
]


async def ingest_sample_data(source="both"):
    """
    Ingest sample documentation data
    
    Args:
        source: Which docs to ingest ('cloud', 'mas', or 'both')
    """
    try:
        all_documents = []
        
        if source in ["cloud", "both"]:
            logger.info("Adding IBM Cloud sample documents...")
            all_documents.extend(SAMPLE_IBM_CLOUD_DOCS)
        
        if source in ["mas", "both"]:
            logger.info("Adding IBM MAS sample documents...")
            all_documents.extend(SAMPLE_IBM_MAS_DOCS)
        
        if source in ["gdp", "both"]:
            logger.info("Adding IBM GDP sample documents...")
            all_documents.extend(SAMPLE_IBM_GDP_DOCS)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Total documents to ingest: {len(all_documents)}")
        logger.info(f"{'='*60}\n")
        
        # Ingest into vector database
        logger.info("Ingesting documents into vector database...")
        
        result = await embedding_service.ingest_documents(
            documents=all_documents,
            namespace="ibm-docs"
        )
        
        logger.info(f"\n{'='*60}")
        logger.info("✅ Ingestion complete!")
        logger.info(f"Documents processed: {result['documents_processed']}")
        logger.info(f"Vectors upserted: {result['vectors_upserted']}")
        logger.info(f"Namespace: {result['namespace']}")
        logger.info(f"{'='*60}\n")
        
        # Get statistics
        stats = await embedding_service.get_statistics()
        logger.info("Vector database statistics:")
        logger.info(f"Total documents: {stats['total_documents']}")
        logger.info(f"Index fullness: {stats['index_fullness']:.2%}")
        
        # Test search
        logger.info(f"\n{'='*60}")
        logger.info("Testing search functionality...")
        logger.info(f"{'='*60}\n")
        
        test_queries = [
            "What is IBM Cloud?",
            "Tell me about Maximo",
            "How does Kubernetes work on IBM Cloud?"
        ]
        
        for query in test_queries:
            logger.info(f"\nQuery: '{query}'")
            results = await embedding_service.search_similar(
                query=query,
                top_k=2,
                namespace="ibm-docs"
            )
            
            for i, result in enumerate(results, 1):
                logger.info(f"  Result {i}: {result['metadata'].get('title', 'N/A')} (Score: {result['score']:.4f})")
        
        return result
        
    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest sample IBM documentation')
    parser.add_argument(
        '--source',
        choices=['cloud', 'mas', 'gdp', 'both'],
        default='gdp',
        help='Which documentation to ingest (default: gdp)'
    )
    
    args = parser.parse_args()
    
    # Run ingestion
    asyncio.run(ingest_sample_data(source=args.source))
    
    logger.info("\n✅ Script completed successfully!")
    logger.info("\n📝 Note: This used sample data. For production, implement:")
    logger.info("   - Headless browser scraping (Selenium/Playwright)")
    logger.info("   - IBM API integration if available")
    logger.info("   - Regular content updates")


if __name__ == "__main__":
    main()

# Made with Bob
