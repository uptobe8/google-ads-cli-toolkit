# Setup detallado — Google Ads API

## OAuth recomendado para GitHub Codespaces

Si estás usando GitHub Codespaces, no uses el script scripts/01_generate_refresh_token.py como método principal.

Usa Google OAuth Playground:

1. Entra en Google Cloud Console.
2. Abre o crea un proyecto.
3. Activa Google Ads API.
4. Ve a APIs & Services → Credentials.
5. Crea un OAuth Client:
   - Application type: Web application
   - Authorized redirect URI:
     https://developers.google.com/oauthplayground
6. Copia:
   - Client ID
   - Client Secret
7. Abre OAuth Playground.
8. Activa Use your own OAuth credentials.
9. Pega Client ID y Client Secret.
10. Usa el scope:
    https://www.googleapis.com/auth/adwords
11. Authorize APIs.
12. Exchange authorization code for tokens.
13. Copia el Refresh Token.
14. Guárdalo como secreto de Codespaces:
    GOOGLE_ADS_REFRESH_TOKEN.

## Variables requeridas

GOOGLE_ADS_DEVELOPER_TOKEN
GOOGLE_ADS_CLIENT_ID
GOOGLE_ADS_CLIENT_SECRET
GOOGLE_ADS_REFRESH_TOKEN
GOOGLE_ADS_LOGIN_CUSTOMER_ID
GOOGLE_ADS_CUSTOMER_ID

Ejemplo:

Cuenta MCC: 123-456-7890 → GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890
Cuenta cliente: 987-654-3210 → GOOGLE_ADS_CUSTOMER_ID=9876543210
