from dotenv import load_dotenv
import os

# 加载.env文件
load_dotenv()

print("="*60)
print("环境变量检查")
print("="*60)
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY', 'NOT FOUND')[:20]}...")
print(f"OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL', 'NOT FOUND')}")
print(f"QWEN_MODEL: {os.getenv('QWEN_MODEL', 'NOT FOUND')}")
print("="*60)
