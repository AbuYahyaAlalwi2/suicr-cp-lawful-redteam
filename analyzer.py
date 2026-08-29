# تحديث core/analyzer.py
from app.core.stealth_network import StealthNetwork

stealth = StealthNetwork()

def analyze_website_stealth(url):
    """
    تحليل موقع باستخدام اتصال مخفي
    لا يمكن تتبع الطلب أو معرفة مصدره
    """
    try:
        # استخدام الاتصال المخفي
        response = stealth.stealth_request(url)
        if not response:
            return {"error": "فشل الاتصال المخفي"}
        
        # تحليل النتيجة
        return {
            "status": "تم التحليل بنجاح",
            "headers": dict(response.headers),
            "content_length": len(response.content),
            "server": response.headers.get('Server', 'غير معروف'),
            "note": "تم الاتصال عبر شبكة الظل (Shadow Network)"
        }
    except Exception as e:
        return {"error": str(e)}
