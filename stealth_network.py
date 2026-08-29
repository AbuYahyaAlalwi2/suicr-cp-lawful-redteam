# app/core/stealth_network.py (محدث)
import requests
import random
import time
import socket
from app.core.tor_manager import TorManager

class StealthNetwork:
    _instance = None
    _tor_manager = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """تهيئة الشبكة المخفية (تشغيل Tor تلقائياً)"""
        self.tor_manager = TorManager()
        self.tor_manager.start()
        self.session = self.create_stealth_session()
    
    def create_stealth_session(self):
        """إنشاء جلسة طلبات مخفية"""
        session = requests.Session()
        
        # تعيين البروكسي عبر Tor
        proxy = self.tor_manager.get_proxy()
        session.proxies.update(proxy)
        
        # تمويه بصمة المتصفح
        session.headers.update({
            'User-Agent': self.get_random_user_agent(),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'DNT': '1',
        })
        
        # إعادة المحاولات في حالة الفشل
        session.max_redirects = 5
        session.timeout = (10, 30)  # connect, read timeout
        
        return session
    
    def get_random_user_agent(self):
        """الحصول على وكيل مستخدم عشوائي"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/124.0',
        ]
        return random.choice(agents)
    
    def stealth_request(self, url, method='GET', data=None, json_data=None, headers=None):
        """
        تنفيذ طلب مخفي بالكامل مع إعادة محاولة تلقائية
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                session = self.create_stealth_session()
                
                if headers:
                    session.headers.update(headers)
                
                # تنفيذ الطلب
                if method.upper() == 'GET':
                    response = session.get(url, timeout=30)
                elif method.upper() == 'POST':
                    response = session.post(url, data=data, json=json_data, timeout=30)
                else:
                    response = session.request(method, url, data=data, json=json_data, timeout=30)
                
                # إذا تم الحظر (كود 403 أو 429)، جدد الهوية
                if response.status_code in [403, 429, 503]:
                    self.tor_manager.renew_identity()
                    time.sleep(2)
                    continue
                
                return response
                
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                # تغيير الهوية وإعادة المحاولة
                self.tor_manager.renew_identity()
                time.sleep(random.uniform(1, 3))
                continue
            
            except Exception as e:
                logger.error(f"خطأ في الطلب المخفي: {str(e)}")
                continue
        
        # إذا فشلت جميع المحاولات
        return None
    
    def renew_identity(self):
        """تجديد هوية النظام بالكامل"""
        self.tor_manager.renew_identity()
        self.session = self.create_stealth_session()
        return True
