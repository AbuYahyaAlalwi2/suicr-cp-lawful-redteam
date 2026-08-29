# app/core/tor_manager.py
import os
import subprocess
import time
import tempfile
import signal
import shutil
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TorManager:
    """
    مدير Tor مدمج داخل النظام
    يقوم بإنشاء ملفات الإعدادات وتشغيل العمليات دون الاعتماد على خدمة النظام
    """
    
    def __init__(self, bridges=None, data_dir=None):
        self.bridges = bridges or []
        self.base_dir = data_dir or tempfile.mkdtemp(prefix="tor_cyber_")
        self.torrc_path = os.path.join(self.base_dir, "torrc")
        self.data_dir = os.path.join(self.base_dir, "data")
        self.tor_process = None
        self.obfs4_process = None
        
        # تهيئة المجلدات
        os.makedirs(self.data_dir, exist_ok=True)
        
        # الجسور الافتراضية (التي قدمها المستخدم)
        if not self.bridges:
            self.bridges = [
                "obfs4 51.68.237.125:10125 A123C73825513B929A30C612D7B80DDD41CBDF50 cert=AObLLfVUZv81ARLp73IwKrN1naKBNsm9zirTKWj0jtMz+7iSDZs1Aw8D4z/bYlhU3mzgUw iat-mode=0",
                "obfs4 15.235.46.121:7669 407E4A0A1A4BCE79138EE90C3FF0FFD5102D2BE2 cert=SGywEjZ/zSzT9PqZjTujyfAHE2GHipSDWxvEO8XMNhvlSw/enjdcsUuEsCeQO8hGSazcaA iat-mode=0"
            ]
    
    def generate_torrc(self):
        """إنشاء ملف تكوين Tor مع الجسور المحددة"""
        config_lines = [
            "# ملف إعدادات Tor تم إنشاؤه تلقائياً بواسطة النظام السيبراني",
            f"DataDirectory {self.data_dir}",
            "SocksPort 0.0.0.0:9050",  # استماع على جميع الواجهات (للاستخدام الداخلي)
            "ControlPort 0.0.0.0:9051",
            "CookieAuthentication 1",
            "CookieAuthFileGroupReadable 1",
            "",
            "# تشغيل obfs4proxy كملحق نقل",
            "ClientTransportPlugin obfs4 exec /usr/bin/obfs4proxy",
            "",
            "# تفعيل استخدام الجسور (لاختراق الحظر)",
            "UseBridges 1",
        ]
        
        # إضافة الجسور
        for bridge in self.bridges:
            config_lines.append(f"Bridge {bridge}")
        
        # خيارات إضافية لتحسين التخفي
        config_lines.extend([
            "",
            "# إعدادات التخفي الإضافية",
            "SafeLogging 1",
            "AvoidDiskWrites 1",
            "LearnCircuitBuildTimeout 0",  # لمنع حفظ أنماط التوقيت
            "CircuitBuildTimeout 30",
        ])
        
        # كتابة الملف
        with open(self.torrc_path, 'w') as f:
            f.write("\n".join(config_lines))
        
        logger.info(f"✅ تم إنشاء ملف الإعدادات: {self.torrc_path}")
        return self.torrc_path
    
    def start(self):
        """بدء تشغيل Tor مع الجسور"""
        # 1. التأكد من تثبيت Tor و obfs4proxy
        if not shutil.which("tor"):
            logger.error("❌ Tor غير مثبت على النظام. قم بتشغيل: apt-get install tor")
            return False
        
        if not shutil.which("obfs4proxy"):
            logger.warning("⚠️ obfs4proxy غير مثبت. سيتم استخدام الإعدادات الافتراضية (قد يعمل بشكل محدود).")
        
        # 2. إنشاء ملف الإعدادات
        self.generate_torrc()
        
        # 3. إيقاف أي عملية Tor قديمة (لتجنب تعارض المنافذ)
        self.stop()
        
        # 4. تشغيل Tor
        try:
            logger.info("🚀 جاري تشغيل Tor مع الجسور...")
            self.tor_process = subprocess.Popen(
                ["tor", "--torrc-file", self.torrc_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 5. انتظار اكتمال بدء التشغيل (التحقق من سجلات البداية)
            time.sleep(3)
            
            # 6. التحقق من أن العملية لا تزال حية
            if self.tor_process.poll() is None:
                logger.info("✅ Tor يعمل بنجاح على المنفذ 9050")
                return True
            else:
                # قراءة الأخطاء
                stdout, stderr = self.tor_process.communicate()
                logger.error(f"❌ فشل تشغيل Tor: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ خطأ في تشغيل Tor: {str(e)}")
            return False
    
    def stop(self):
        """إيقاف Tor و obfs4proxy"""
        try:
            if self.tor_process:
                self.tor_process.terminate()
                self.tor_process.wait(timeout=5)
                logger.info("🛑 تم إيقاف Tor")
        except:
            pass
        
        # تنظيف العمليات المتبقية
        subprocess.run(["pkill", "-f", "tor"], stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-f", "obfs4proxy"], stderr=subprocess.DEVNULL)
    
    def restart(self):
        """إعادة تشغيل Tor (لتجديد الهوية)"""
        self.stop()
        time.sleep(2)
        return self.start()
    
    def get_proxy(self):
        """إرجاع إعدادات البروكسي للاستخدام في الطلبات"""
        return {
            "http": "socks5h://127.0.0.1:9050",
            "https": "socks5h://127.0.0.1:9050"
        }
    
    def renew_identity(self):
        """تغيير مسار Tor (هوية جديدة)"""
        try:
            # استخدام stem للتحكم في Tor عبر ControlPort
            from stem import Signal
            from stem.control import Controller
            
            with Controller.from_port(port=9051) as controller:
                controller.authenticate()  # قراءة كلمة المرور من ملف Cookie
                controller.signal(Signal.NEWNYM)
                logger.info("🔄 تم تجديد هوية Tor")
                return True
        except Exception as e:
            logger.warning(f"⚠️ فشل تجديد الهوية: {str(e)}. سيتم إعادة التشغيل.")
            return self.restart()
