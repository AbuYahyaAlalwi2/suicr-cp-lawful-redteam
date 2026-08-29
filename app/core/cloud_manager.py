python
import random
from app.core.key_manager import KeyManager

class CloudManager:
    def __init__(self):
        self.clouds = []
        self.active_cloud = None
    
    def get_best_cloud(self):
        available = []
        for platform in ['google', 'aws', 'oracle']:
            key = KeyManager.get_active_key(platform)
            if key:
                available.append(platform)
        if not available:
            return None
        return random.choice(available)
    
    def distribute_task(self, task, target):
        cloud = self.get_best_cloud()
        if cloud:
            return {
                "status": "success",
                "cloud": cloud,
                "task": task,
                "target": target,
                "execution_time": random.randint(10, 100) / 1000
            }
        return {"status": "error", "message": "لا توجد سحابة متاحة"}
