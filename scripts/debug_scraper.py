"""
Debug script to inspect HTML structure from IBM docs
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def debug_fetch(url):
    """Fetch and inspect HTML structure"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            html = await response.text()
            
            print(f"Status: {response.status}")
            print(f"Content length: {len(html)}")
            print("\n" + "="*60)
            print("HTML Preview (first 2000 chars):")
            print("="*60)
            print(html[:2000])
            print("\n" + "="*60)
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Check for main content areas
            print("\nLooking for content containers:")
            print("="*60)
            
            selectors = [
                ('main', {}),
                ('article', {}),
                ('div', {'class': 'content'}),
                ('div', {'id': 'content'}),
                ('div', {'class': 'main-content'}),
                ('div', {'role': 'main'}),
                ('div', {'class': 'body'}),
                ('div', {'class': 'section'})
            ]
            
            for tag, attrs in selectors:
                elements = soup.find_all(tag, attrs)
                if elements:
                    print(f"\nFound {len(elements)} <{tag}> with {attrs}")
                    for i, elem in enumerate(elements[:2]):  # Show first 2
                        text = elem.get_text(strip=True)[:200]
                        print(f"  [{i}] Text preview: {text}...")
            
            # Check all divs with class
            print("\n" + "="*60)
            print("All div classes found:")
            print("="*60)
            div_classes = set()
            for div in soup.find_all('div', class_=True):
                classes = div.get('class', [])
                div_classes.update(classes)
            
            for cls in sorted(div_classes)[:30]:  # Show first 30
                print(f"  - {cls}")

if __name__ == "__main__":
    # Test URLs
    urls = [
        "https://cloud.ibm.com/docs/overview?topic=overview-whatis-platform",
        "https://www.ibm.com/docs/en/masv-and-l/cd?topic=overview"
    ]
    
    for url in urls:
        print(f"\n{'#'*60}")
        print(f"Testing: {url}")
        print(f"{'#'*60}\n")
        asyncio.run(debug_fetch(url))
        print("\n")
