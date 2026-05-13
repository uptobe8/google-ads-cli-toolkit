# Google Tag Manager (GTM) — Guía

Si tu container GTM productivo está bajo cuenta de un freelancer o
agencia, no controlas tu propio tracking. Esta guía cubre cómo
migrarlo a tu propia cuenta, y cómo opcionalmente operar GTM via API.

---

## Sección 1 — Migrar tu container GTM a tu propia cuenta

**Por qué importa:** mientras el container viva en cuenta del externo,
no puedes publicar cambios sin su intervención. Si el container es
suyo, puede revocarte acceso o hacer cambios sin que te enteres.

**Tiempo estimado:** ~30 min de trabajo + 24-48h de verificación.

### Paso 1 — Exportar el container actual a JSON

Necesitas acceso de Edit (al menos) al container actual. Si el
externo todavía no te lo retiró, hazlo ya. Si ya te lo retiró,
necesitarás pedírselo de vuelta o reconstruir desde cero.

1. https://tagmanager.google.com → selecciona el container actual.
2. **Administrador → Exportar contenedor**.
3. Selecciona el workspace activo (o "Versión publicada" si quieres
   sólo lo que está en producción).
4. Descarga el JSON. Guárdalo en un lugar seguro — es tu backup.

### Paso 2 — Crear container nuevo en tu propia cuenta

1. https://tagmanager.google.com (entra con tu cuenta de Google,
   no la del externo).
2. **Crear cuenta** → nombre: el de tu negocio. País: el tuyo.
3. **Configuración del contenedor**:
   - Nombre: tu dominio (ej. `mibumio.com`).
   - Plataforma: **Web** (o la que aplique).
4. Acepta los TOS. Anota el nuevo ID `GTM-XXXXX` — es lo que vas a
   instalar en tu sitio.

### Paso 3 — Importar el JSON

Dentro del container nuevo:

1. **Administrador → Importar contenedor**.
2. Carga el JSON exportado en el paso 1.
3. **Workspace destino**: Default Workspace (o crea uno nuevo).
4. **Modo de importación**: **Combinar** + opción **Sobrescribir**
   tags/triggers/variables existentes (el container nuevo está vacío,
   así que no hay riesgo de pisar nada útil).
5. Confirma. GTM importa todo.

### Paso 4 — Revisar que se importó bien

1. Revisa que **Tags**, **Triggers** y **Variables** se ven idénticos
   al container viejo.
2. Si tienes variables específicas de cuenta (ej. ID de GA4 — ver
   [GA4_GUIDE.md](GA4_GUIDE.md), o ID de Google Ads conversion), revisa
   que apunten a TUS IDs, no a los del externo.
3. Cualquier referencia a workspaces, environments o tags propios del
   externo: revísala y actualiza.

### Paso 5 — Publicar versión inicial

1. Botón **Submit** (arriba a la derecha) → **Publish**.
2. Nombre de la versión: algo como `Initial migration`.

### Paso 6 — Cambiar el snippet GTM en el sitio

El snippet vive típicamente en dos lugares del HTML:
- En `<head>`: el script principal.
- Justo después de `<body>`: el `<noscript>` fallback.

Reemplaza el `GTM-XXXXX` viejo por el nuevo en ambos lugares. Despliega
a producción.

> Si no controlas el código del sitio, pídele a tu desarrollador que
> haga el reemplazo. Mándale el snippet nuevo desde
> **Administrador → Instalar Google Tag Manager** del container nuevo.

### Paso 7 — Verificar 24-48h con GTM Preview

1. Antes de eliminar el container viejo, espera 24-48h.
2. Activa GTM Preview en el container **nuevo** y navega tu sitio.
   Confirma que los tags clave (GA4, Google Ads conversion, eventos
   personalizados) están disparando.
3. Cruza con datos en Google Ads (¿siguen llegando conversiones?) y
   GA4 (¿siguen llegando eventos?).

### Paso 8 — Eliminar container viejo y revocar accesos

Cuando confirmes que el nuevo funciona:

1. En el container viejo: **Administrador → Configuración del
   contenedor → Eliminar contenedor**.
2. Si el externo todavía tiene acceso a tu cuenta GTM nueva (no
   debería, pero verifica): **Administrador → Permisos de la cuenta**
   → remueve cualquier email que no sea tuyo o de tu equipo.

---

## Sección 2 — GTM API (opcional)

Para usuarios que quieren ir más allá de la UI: GTM tiene una API
REST que permite gestionar containers, workspaces, tags, triggers y
variables programáticamente. Útil para:

- Versionar tu container en Git (snapshot periódico exportado a JSON).
- Aplicar cambios masivos que serían tediosos en la UI.
- Auditar configuración (qué tags están activos, qué triggers
  apuntan a dónde).

### Requisitos

1. Habilitar **Tag Manager API** en el mismo proyecto de Google Cloud
   que usaste para Google Ads:
   - https://console.cloud.google.com → APIs y servicios → Biblioteca
     → buscar "Tag Manager API" → Habilitar.

2. Usar el mismo OAuth client que ya tienes (el de Desktop App), pero
   con scopes adicionales:
   - `https://www.googleapis.com/auth/tagmanager.readonly` (lectura)
   - `https://www.googleapis.com/auth/tagmanager.edit.containers` (edición)

3. Generar un nuevo refresh token con esos scopes (puedes adaptar
   `scripts/01_generate_refresh_token.py` agregándolos al array `SCOPES`).

4. Llenar en `.env`:
   ```
   GTM_ACCOUNT_ID=...
   GTM_CONTAINER_ID=...
   ```

### Recipes que puedes pedirle a Codex CLI

- "Lista todos los tags de mi container GTM y dame un resumen".
- "Exporta mi container a JSON y guárdalo en `out/gtm-snapshot-FECHA.json`".
- "Encuentra todos los tags que disparan en `pageview` y ordénalos
  por nombre".
- "Crea un trigger nuevo de tipo Form Submission con esta condición..."

Codex puede escribir scripts contra la API directamente. Apóyalo con
la documentación oficial:

- API reference: https://developers.google.com/tag-manager/api/v2
- Autenticación: https://developers.google.com/tag-manager/api/v2/authorization
- Ejemplos en Python: https://github.com/googleapis/google-api-python-client/tree/main/samples/tagmanager

### Snippet mínimo de prueba

Después de habilitar el API y tener el refresh token con los scopes
correctos, este snippet lista las cuentas GTM accesibles:

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

creds = Credentials(
    token=None,
    refresh_token=os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
    client_id=os.getenv("GOOGLE_ADS_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
    token_uri="https://oauth2.googleapis.com/token",
)
service = build("tagmanager", "v2", credentials=creds)
accounts = service.accounts().list().execute()
for acct in accounts.get("account", []):
    print(acct["accountId"], acct["name"])
```

(Requiere `pip install google-api-python-client google-auth` — descomentar
las líneas correspondientes en `requirements.txt`.)

Si necesitas más, pídele a Codex CLI que arme un script completo con
el caso específico.
