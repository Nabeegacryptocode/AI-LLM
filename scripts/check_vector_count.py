"""Quick script to check Pinecone vector count"""
import asyncio
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from services.vector_service import vector_service

async def main():
    stats = await vector_service.get_index_stats()
    print(f"\n{'='*60}")
    print(f"Pinecone Database Statistics")
    print(f"{'='*60}")
    print(f"Total Vectors: {stats['total_vector_count']}")
    print(f"Dimension: {stats['dimension']}")
    print(f"Index Fullness: {stats['index_fullness']}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    asyncio.run(main())
