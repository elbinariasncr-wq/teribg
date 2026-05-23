import aiohttp
import asyncio
import random
from typing import List

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.working_proxies = []
        self.last_update = 0
        
    async def fetch_free_proxies(self):
        """Ambil proxy dari berbagai sumber gratis"""
        sources = [
            'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
            'https://api.proxyscrape.com/v2/?request=get&protocol=socks5&timeout=10000&country=all',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
            'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
            'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt',
            'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
            'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/http.txt',
            'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
            'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt'
        ]
        
        all_proxies = []
        
        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_from_source(session, url) for url in sources]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_proxies.extend(result)
        
        self.proxies = list(set(all_proxies))
        print(f"[PROXY] Fetched {len(self.proxies)} proxies from {len(sources)} sources")
        
        return self.proxies
    
    async def _fetch_from_source(self, session, url):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    text = await response.text()
                    proxies = []
                    
                    for line in text.split('\n'):
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        
                        if ':' in line:
                            if 'socks5' in url.lower():
                                proxies.append(f'socks5://{line}')
                            elif 'socks4' in url.lower():
                                proxies.append(f'socks4://{line}')
                            else:
                                proxies.append(f'http://{line}')
                    
                    return proxies
        except Exception as e:
            print(f"[PROXY] Failed to fetch from {url}: {e}")
            return []
    
    async def test_proxy(self, proxy, test_url='http://httpbin.org/ip'):
        """Test apakah proxy working"""
        try:
            if proxy.startswith('socks'):
                from aiohttp_socks import ProxyConnector
                connector = ProxyConnector.from_url(proxy)
            else:
                connector = None
            
            async with aiohttp.ClientSession(connector=connector) as session:
                if not connector:
                    proxy_dict = {'http': proxy, 'https': proxy}
                else:
                    proxy_dict = None
                
                async with session.get(
                    test_url, 
                    proxy=proxy if not connector else None,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        return True
        except:
            pass
        
        return False
    
    async def get_working_proxies(self, max_test=100):
        """Filter proxy yang bener-bener working"""
        if not self.proxies:
            await self.fetch_free_proxies()
        
        test_batch = random.sample(self.proxies, min(max_test, len(self.proxies)))
        
        tasks = [self.test_proxy(proxy) for proxy in test_batch]
        results = await asyncio.gather(*tasks)
        
        self.working_proxies = [
            proxy for proxy, working in zip(test_batch, results) if working
        ]
        
        print(f"[PROXY] Tested {len(test_batch)} proxies, {len(self.working_proxies)} working")
        
        return self.working_proxies
    
    def get_random_proxy(self):
        """Ambil random working proxy"""
        if self.working_proxies:
            return random.choice(self.working_proxies)
        elif self.proxies:
            return random.choice(self.proxies)
        return None
    
    async def auto_refresh(self, interval=300):
        """Auto refresh proxy list setiap X detik"""
        while True:
            await self.fetch_free_proxies()
            await self.get_working_proxies(max_test=50)
            await asyncio.sleep(interval)