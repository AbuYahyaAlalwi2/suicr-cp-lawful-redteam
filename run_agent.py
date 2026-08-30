# run_agent.py
from agent_core import AutonomousAgent

# ===== تهيئة الوكيل مع المفاتيح =====
agent = AutonomousAgent(
    email="your_email@example.com",
    github_token="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",
    model_keys={
        "openrouter": "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",
        "gemini": "your_gemini_key",
        "claude": "your_claude_key"
    }
)

# ===== حلقة القيادة (أوامر من المستخدم) =====
while True:
    user_input = input("\n🛡️ أدخل أمرك (أو exit للخروج): ")
    if user_input.lower() == "exit":
        break
    result = agent.process_command(user_input)
    print(f"\n📌 النتيجة: {result}")
