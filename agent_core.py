import os
import subprocess
import json
import requests
import re
import time
from typing import List, Dict, Any
from datetime import datetime

class AutonomousAgent:
    """
    وكيل سيبراني ذاتي التطور
    قادر على تنفيذ أوامر، ربط نماذج متعددة، وتحسين نفسه
    """
    
    def __init__(self, email: str = None, github_token: str = None, model_keys: Dict = None):
        self.email = email
        self.github_token = github_token
        self.model_keys = model_keys or {}
        self.models = self.load_models()
        self.commands = self.load_commands()
        self.evolution_log = []
        self.workspace = "/tmp/agent_workspace"
        os.makedirs(self.workspace, exist_ok=True)
    
    # ===== 1. إدارة النماذج =====
    def load_models(self):
        """تحميل جميع النماذج المتاحة"""
        return {
            "openrouter": {
                "url": "https://openrouter.ai/api/v1/chat/completions",
                "key": self.model_keys.get("openrouter"),
                "models": ["mistralai/mistral-7b-instruct", "google/gemini-1.5-flash"]
            },
            "gemini": {
                "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
                "key": self.model_keys.get("gemini")
            },
            "claude": {
                "url": "https://api.anthropic.com/v1/messages",
                "key": self.model_keys.get("claude")
            }
        }
    
    def ask_model(self, model_name: str, prompt: str) -> str:
        """إرسال طلب إلى نموذج محدد"""
        if model_name == "openrouter":
            return self.ask_openrouter(prompt)
        elif model_name == "gemini":
            return self.ask_gemini(prompt)
        elif model_name == "claude":
            return self.ask_claude(prompt)
        else:
            return "⚠️ نموذج غير معروف"
    
    def ask_openrouter(self, prompt: str) -> str:
        """استخدام OpenRouter مع نماذج متعددة"""
        model = self.models["openrouter"]["models"][0]  # اختيار النموذج الأول
        try:
            response = requests.post(
                self.models["openrouter"]["url"],
                headers={"Authorization": f"Bearer {self.models['openrouter']['key']}"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=30
            )
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"❌ خطأ: {str(e)}"
    
    def ask_gemini(self, prompt: str) -> str:
        """استخدام Gemini API"""
        try:
            url = f"{self.models['gemini']['url']}?key={self.models['gemini']['key']}"
            response = requests.post(
                url,
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"❌ خطأ: {str(e)}"
    
    def ask_claude(self, prompt: str) -> str:
        """استخدام Claude API"""
        try:
            response = requests.post(
                self.models["claude"]["url"],
                headers={
                    "x-api-key": self.models["claude"]["key"],
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000
                },
                timeout=30
            )
            return response.json()["content"][0]["text"]
        except Exception as e:
            return f"❌ خطأ: {str(e)}"
    
    def multi_model_query(self, prompt: str) -> Dict[str, str]:
        """سؤال جميع النماذج وجمع الإجابات"""
        results = {}
        for model_name in self.models.keys():
            results[model_name] = self.ask_model(model_name, prompt)
        return results
    
    # ===== 2. محرك التنفيذ =====
    def load_commands(self):
        """تحميل الأوامر المتاحة للوكيل"""
        return {
            "clone": self.execute_clone,
            "search": self.execute_search,
            "modify": self.execute_modify,
            "analyze": self.execute_analyze,
            "push": self.execute_push,
            "deploy": self.execute_deploy
        }
    
    def execute_command(self, command: str, args: Dict) -> str:
        """تنفيذ أمر معين"""
        if command in self.commands:
            return self.commands[command](args)
        return f"❌ أمر غير معروف: {command}"
    
    def execute_clone(self, args: Dict) -> str:
        """استنساخ مستودع"""
        repo_url = args.get("repo_url")
        if not repo_url:
            return "❌ تحتاج إلى رابط المستودع"
        if self.github_token:
            repo_url = repo_url.replace("https://", f"https://{self.github_token}@")
        os.system(f"cd {self.workspace} && git clone {repo_url}")
        return f"✅ تم استنساخ {repo_url} في {self.workspace}"
    
    def execute_search(self, args: Dict) -> str:
        """البحث عن نص في الملفات"""
        pattern = args.get("pattern")
        path = args.get("path", self.workspace)
        if not pattern:
            return "❌ تحتاج إلى نمط بحث"
        result = subprocess.run(
            ["grep", "-r", pattern, path],
            capture_output=True, text=True
        )
        return result.stdout or "🔍 لم يتم العثور على شيء"
    
    def execute_modify(self, args: Dict) -> str:
        """تعديل ملف (باستخدام الذكاء الاصطناعي)"""
        file_path = args.get("file_path")
        changes = args.get("changes")
        if not file_path or not changes:
            return "❌ تحتاج إلى مسار ملف وتغييرات"
        # قراءة الملف
        with open(file_path, 'r') as f:
            content = f.read()
        # طلب الذكاء الاصطناعي لإجراء التعديلات
        prompt = f"قم بتعديل الكود التالي:\n\n{content}\n\nالتغييرات المطلوبة:\n{changes}\n\nأرسل الكود النهائي فقط."
        new_content = self.ask_model("openrouter", prompt)
        # حفظ الملف
        with open(file_path, 'w') as f:
            f.write(new_content)
        return f"✅ تم تعديل {file_path} بنجاح"
    
    def execute_analyze(self, args: Dict) -> str:
        """تحليل الكود أو الملفات"""
        path = args.get("path", self.workspace)
        analysis = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith((".py", ".js", ".html")):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        content = f.read()
                        lines = len(content.split('\n'))
                        analysis.append(f"{file}: {lines} سطر")
        return "\n".join(analysis[:10])  # عرض أول 10 ملفات
    
    def execute_push(self, args: Dict) -> str:
        """رفع التغييرات إلى GitHub"""
        message = args.get("message", "تحديث تلقائي")
        os.system(f"cd {self.workspace} && git add . && git commit -m '{message}' && git push")
        return f"✅ تم رفع التغييرات مع الرسالة: {message}"
    
    def execute_deploy(self, args: Dict) -> str:
        """نشر التطبيق (مثل Render)"""
        # تنفيذ أوامر النشر (يعتمد على المنصة)
        return "🚀 جارٍ النشر... (يحتاج إلى تكامل مع Render API)"
    
    # ===== 3. نظام التطور الذاتي =====
    def self_evolve(self) -> str:
        """تحسين النظام نفسه"""
        # 1. تحليل الأخطاء الشائعة
        error_log = self.execute_search({"pattern": "error", "path": "."})
        
        # 2. طلب تحسينات من الذكاء الاصطناعي
        prompt = f"""
        أنت وكيل سيبراني ذاتي التطور. قم بتحليل الأخطاء التالية واقترح تحسينات للكود:
        
        {error_log[:500]}
        
        أرسل قائمة بالتغييرات المطلوبة (كل تغيير في سطر منفصل).
        """
        improvements = self.ask_model("openrouter", prompt)
        
        # 3. تنفيذ التحسينات
        for improvement in improvements.split('\n'):
            if improvement.strip():
                self.execute_command("modify", {
                    "file_path": "agent_core.py",
                    "changes": improvement
                })
        
        # 4. تسجيل التطور
        self.evolution_log.append({
            "timestamp": datetime.now().isoformat(),
            "improvements": improvements,
            "status": "completed"
        })
        
        return f"✅ تم التطور الذاتي:\n{improvements[:200]}..."
    
    # ===== 4. المصادقة وإدارة المفاتيح =====
    def authenticate(self, service: str, credentials: Dict) -> bool:
        """تسجيل الدخول إلى خدمات خارجية"""
        if service == "github":
            self.github_token = credentials.get("token")
            return bool(self.github_token)
        elif service == "email":
            self.email = credentials.get("email")
            return bool(self.email)
        else:
            return False
    
    # ===== 5. الواجهة الرئيسية (تلقي الأوامر) =====
    def process_command(self, user_input: str) -> str:
        """معالجة الأوامر الطبيعية من المستخدم"""
        # تحليل الأمر الطبيعي باستخدام الذكاء الاصطناعي
        prompt = f"""
        أنت وكيل سيبراني ذكي. المستخدم طلب: "{user_input}"
        
        قم بتحويل هذا الطلب إلى أمر من الأوامر التالية:
        - clone: استنساخ مستودع
        - search: بحث في الملفات
        - modify: تعديل ملف
        - analyze: تحليل الكود
        - push: رفع التغييرات
        - deploy: نشر التطبيق
        - evolve: التطور الذاتي
        
        أرسل الإجابة بصيغة JSON:
        {{"command": "اسم_الأمر", "args": {{"key": "value"}}}}
        """
        
        response = self.ask_model("openrouter", prompt)
        try:
            # استخراج JSON من الرد
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                command = data.get("command")
                args = data.get("args", {})
                return self.execute_command(command, args)
            else:
                return "❌ لم أفهم الأمر، حاول مرة أخرى"
        except Exception as e:
            return f"❌ خطأ في تحليل الأمر: {str(e)}"
