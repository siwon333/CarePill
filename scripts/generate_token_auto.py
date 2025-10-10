"""
Automatic Token Generation Script (Non-interactive)
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicine_project.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Get or create user
user, created = User.objects.get_or_create(
    username='voice_user',
    defaults={'email': 'voice@carepill.local'}
)

if created:
    user.set_password('1234')
    user.save()
    print(f"✓ Created new user: {user.username}")
else:
    print(f"✓ User '{user.username}' already exists")

# Generate or get token
token, token_created = Token.objects.get_or_create(user=user)

if token_created:
    print(f"✓ Generated new API token")
else:
    print(f"✓ Retrieved existing API token")

print("\n" + "=" * 60)
print("DJANGO TTS API TOKEN")
print("=" * 60)
print(f"\nUser: {user.username}")
print(f"Token: {token.key}")
print("\n" + "=" * 60)
print("\n.env 파일에 다음을 추가하세요:")
print(f"DJANGO_TTS_TOKEN={token.key}")
print("=" * 60)

# Write to file
with open("API_TOKEN.txt", "w") as f:
    f.write(f"User: {user.username}\n")
    f.write(f"Token: {token.key}\n")
    f.write(f"\n.env 파일에 추가:\n")
    f.write(f"DJANGO_TTS_TOKEN={token.key}\n")

print("\n✓ 토큰이 API_TOKEN.txt 파일에 저장되었습니다")
print("  (복사 후 이 파일은 삭제하세요)\n")
