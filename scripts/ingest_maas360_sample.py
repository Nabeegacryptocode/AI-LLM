"""
Script to ingest sample IBM MaaS360 data for testing
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

# Sample IBM MaaS360 documentation content
SAMPLE_MAAS360_DOCS = [
    {
        "content": """IBM MaaS360 with Watson is a unified endpoint management (UEM) solution that helps organizations secure and manage mobile devices, applications, and content. It provides comprehensive mobile device management (MDM), mobile application management (MAM), and mobile content management (MCM) capabilities. MaaS360 uses AI-powered analytics to provide insights into device security and compliance.""",
        "metadata": {
            "title": "IBM MaaS360 Overview",
            "url": "https://www.ibm.com/products/maas360",
            "source_type": "IBM MaaS360",
            "product": "IBM MaaS360",
            "category": "Overview"
        }
    },
    {
        "content": """MaaS360 Mobile Device Management (MDM) enables IT administrators to enroll, configure, and secure mobile devices across iOS, Android, Windows, and macOS platforms. It provides over-the-air device enrollment, policy-based configuration, remote wipe capabilities, and real-time device monitoring. Administrators can enforce security policies, manage device settings, and ensure compliance with corporate standards.""",
        "metadata": {
            "title": "MaaS360 Mobile Device Management",
            "url": "https://www.ibm.com/products/maas360/mobile-device-management",
            "source_type": "IBM MaaS360",
            "product": "IBM MaaS360",
            "category": "Features"
        }
    },
    {
        "content": """MaaS360 Mobile Application Management (MAM) allows organizations to distribute, manage, and secure mobile applications. It supports both public app store apps and enterprise custom apps. Features include app catalog management, app configuration policies, app-level VPN, and containerization for data protection. MAM enables secure access to corporate apps while maintaining user privacy.""",
        "metadata": {
            "title": "MaaS360 Mobile Application Management",
            "url": "https://www.ibm.com/products/maas360/mobile-application-management",
            "source_type": "IBM MaaS360",
            "product": "IBM MaaS360",
            "category": "Features"
        }
    },
    {
        "content": """MaaS360 Security and Threat Management uses AI-powered analytics to detect and respond to security threats. It provides real-time threat detection, vulnerability assessment, and automated remediation. The platform monitors device behavior, identifies anomalies, and alerts administrators to potential security risks. Integration with IBM Watson provides advanced threat intelligence and predictive analytics.""",
        "metadata": {
            "title": "MaaS360 Security and Threat Management",
            "url": "https://www.ibm.com/products/maas360/security",
            "source_type": "IBM MaaS360",
            "product": "IBM MaaS360",
            "category": "Security"
        }
    },
    {
        "content": """MaaS360 Compliance Management helps organizations meet regulatory requirements and industry standards. It provides compliance reporting, audit trails, and policy enforcement capabilities. The platform supports compliance frameworks including GDPR, HIPAA, PCI-DSS, and SOX. Automated compliance checks ensure devices meet security standards, and detailed reports provide evidence for audits.""",
        "metadata": {
            "title": "MaaS360 Compliance Management",
            "url": "https://www.ibm.com/products/maas360/compliance",
            "source_type": "IBM MaaS360",
            "product": "IBM MaaS360",
            "category": "Compliance"
        }
    },
    {
        "content": """MaaS360 provides comprehensive endpoint visibility and analytics through an intuitive dashboard. Administrators can view device inventory, monitor security status, track compliance metrics, and analyze usage patterns. Real-time alerts notify administrators of security incidents, policy violations, and device issues. Customizable reports provide insights for decision-making and strategic planning.""",
        "metadata": {
            "title": "MaaS360 Analytics and Reporting",
            "url": "https://www.ibm.com/products/maas360/analytics",
            "source_type": "IBM MaaS360",
            "product": "IBM MaaS360",
            "category": "Analytics"
        }
    },
    {
        "content": """MaaS360 integrates with enterprise systems including Active Directory, LDAP, SIEM platforms, and identity management solutions. It supports single sign-on (SSO), multi-factor authentication (MFA), and conditional access policies. API access enables custom integrations and automation. The platform works seamlessly with Microsoft 365, Google Workspace, and other productivity suites.""",
        "metadata": {
            "title": "MaaS360 Integration Capabilities",
            "url": "https://www.ibm.com/products/maas360/integrations",
            "source_type": "IBM MaaS360",
            "product": "IBM MaaS360",
            "category": "Integration"
        }
    }
]


async def ingest_maas360_sample():
    """Ingest sample MaaS360 documentation data"""
    try:
        logger.info("Adding IBM MaaS360 sample documents...")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Total documents to ingest: {len(SAMPLE_MAAS360_DOCS)}")
        logger.info(f"{'='*60}\n")
        
        # Ingest into vector database
        logger.info("Ingesting documents into vector database...")
        
        result = await embedding_service.ingest_documents(
            documents=SAMPLE_MAAS360_DOCS,
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
        
        test_query = "What is MaaS360?"
        logger.info(f"Query: '{test_query}'")
        results = await embedding_service.search_similar(
            query=test_query,
            top_k=3,
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
    asyncio.run(ingest_maas360_sample())
    logger.info("\n✅ Script completed successfully!")


if __name__ == "__main__":
    main()

# Made with Bob
