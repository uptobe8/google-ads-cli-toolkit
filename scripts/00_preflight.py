import os
import sys
from dotenv import load_dotenv

load_dotenv()

REQUIRED = [
    'GOOGLE_ADS_DEVELOPER_TOKEN',
    'GOOGLE_ADS_CLIENT_ID',
    'GOOGLE_ADS_CLIENT_SECRET',
    'GOOGLE_ADS_REFRESH_TOKEN',
    'GOOGLE_ADS_LOGIN_CUSTOMER_ID',
    'GOOGLE_ADS_CUSTOMER_ID',
]

missing = [key for key in REQUIRED if not os.getenv(key)]

print('Preflight Google Ads CLI Toolkit')
print('-' * 40)

for key in REQUIRED:
    print(f"{key}: {'OK' if os.getenv(key) else 'MISSING'}")

if missing:
    print()
    print('Faltan variables obligatorias:')
    for key in missing:
        print(f'- {key}')
    sys.exit(1)

try:
    from google.ads.googleads.client import GoogleAdsClient
except Exception as e:
    print()
    print('No se puede importar google-ads. Ejecuta: pip install -r requirements.txt')
    print(str(e))
    sys.exit(1)

print()
print('Entorno preparado. Puedes ejecutar: python scripts/02_audit.py')
