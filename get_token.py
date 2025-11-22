import requests

login_url = "https://xvserzimz6ofnmxbghdkqpgpma0horhq.lambda-url.us-east-2.on.aws/login"
credentials = {"username": "admin", "password": "password123"}

print("🔐 正在获取新 Token...\n")
response = requests.post(login_url, json=credentials)

if response.status_code == 200:
    data = response.json()
    token = data['access_token']
    print("✅ 成功！\n")
    print("="*70)
    print("新 Token:")
    print("="*70)
    print(token)
    print("="*70)
    print(f"\n⏱️  有效期: {data['expires_in']} 秒")
else:
    print(f"❌ 失败: {response.status_code}")
    print(response.text)
