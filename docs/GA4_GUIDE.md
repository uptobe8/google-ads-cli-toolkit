# Google Analytics 4 (GA4) — Guía

Auditar y operar GA4 sigue un patrón análogo al de Google Ads: hay
una capa **manual** (UI) y una capa **programática** (APIs). Esta guía
cubre las dos.

---

## Sección 1 — Auditoría manual rápida

Si acabas de recuperar el control de Google Ads de un externo, haz
esta auditoría en GA4 cuanto antes.

### 1. Confirmar accesos a la propiedad

1. https://analytics.google.com → selecciona la propiedad GA4.
2. **Admin → Acceso a la propiedad**.
3. Revisa la lista de usuarios y roles.
4. Remueve cualquier email externo que ya no debería tener acceso.
   - Roles posibles: Administrator, Editor, Marketer, Analyst, Viewer.
   - Cualquier ex-operador con Editor o Administrator: removerlo.

### 2. Confirmar eventos personalizados clave

1. **Admin → Eventos** (en la columna de la propiedad).
2. Revisa la lista de eventos personalizados que has definido.
3. Confirma que existen y están activos los eventos críticos para tu
   negocio. Ejemplos comunes:
   - `form_complete` (envío de formulario de contacto)
   - `purchase` (compra)
   - `sign_up` (registro)
   - `whatsapp_click` (clic a WhatsApp)
   - `phone_click` (clic a teléfono)
4. Si algún evento clave no aparece, revisa el container GTM
   (ver [GTM_GUIDE.md](GTM_GUIDE.md)) — probablemente el tag está
   apagado o nunca disparó en producción.

### 3. Confirmar vinculación con Google Ads

1. **Admin → Vinculaciones de productos → Google Ads**.
2. Tu cuenta de Google Ads debe estar en la lista, vinculada.
3. Si no está: **Vincular** → selecciona tu cuenta cliente de Google
   Ads → habilita las opciones recomendadas (importar audiencias,
   importar conversiones).
4. Si hay una cuenta vinculada que no es tuya (ej. del ex-operador):
   desvincúlala.

### 4. Confirmar configuración de conversiones

1. **Admin → Conversiones** (o **Eventos clave** en versiones
   recientes de GA4).
2. Los eventos marcados como conversión deben coincidir con los
   que importas a Google Ads.
3. Patrón común roto:
   - Tienes `form_complete` marcado como conversión en GA4.
   - Pero en Google Ads importas `purchase`, no `form_complete`.
   - Resultado: las conversiones no llegan a Google Ads aunque GA4
     las registra.

### 5. Confirmar exclusión de tráfico interno

1. **Admin → Configuración de datos → Filtros de datos**.
2. Confirma que los filtros excluyen las IPs/dominios de tu equipo
   (para que tus visitas no inflen los datos).

---

## Sección 2 — GA4 Data API (opcional)

Útil para auditoría programática y reconciliación con Google Ads.

### Requisitos

1. **Habilitar Google Analytics Data API** en tu proyecto de Google
   Cloud:
   https://console.cloud.google.com → APIs y servicios → Biblioteca
   → buscar "Google Analytics Data API" → Habilitar.

2. **Crear un Service Account** (no OAuth — GA4 Data API trabaja
   mejor con service account):
   - APIs y servicios → Credenciales → Crear credenciales →
     **Cuenta de servicio**.
   - Nombre: `ga4-reader`. Concede rol "Viewer" del proyecto.
   - Una vez creada, abre la cuenta → pestaña **Claves** → **Agregar
     clave → Crear nueva clave → JSON**. Descarga el JSON y guárdalo
     en lugar seguro (no lo subas a Git — el `.gitignore` ya excluye
     `service-account*.json`).

3. **Dar acceso al service account en GA4**:
   - Anota el **email** del service account (algo como
     `ga4-reader@tu-proyecto.iam.gserviceaccount.com`).
   - GA4 Admin → **Acceso a la propiedad → +**.
   - Pega el email, asigna rol **Visor**, guarda.

4. **Llenar `.env`**:
   ```
   GA4_PROPERTY_ID=123456789
   GOOGLE_APPLICATION_CREDENTIALS=/ruta/absoluta/al/service-account.json
   ```
   El Property ID está en GA4 Admin → Configuración de la propiedad
   → ID de la propiedad (sólo dígitos).

5. **Instalar la librería de Python**:
   ```bash
   pip install google-analytics-data
   ```
   (Está comentada en `requirements.txt`; descoméntala si vas a usar
   esta sección.)

### Recipes que puedes pedirle a Claude Code

- "Lista los 20 eventos más frecuentes en mi propiedad GA4 los
  últimos 30 días, con su conteo."
- "Compara las conversiones de `form_complete` en GA4 vs. las
  conversiones importadas a Google Ads del mismo nombre."
- "Dame el funnel: sesiones → page_view de /aplicar →
  form_complete, en los últimos 30 días."
- "Exporta los eventos de los últimos 7 días a un CSV."

### Snippet mínimo de prueba

```python
import os
from dotenv import load_dotenv
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest,
)

load_dotenv()
PROPERTY_ID = os.getenv("GA4_PROPERTY_ID")

client = BetaAnalyticsDataClient()  # usa GOOGLE_APPLICATION_CREDENTIALS

req = RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    dimensions=[Dimension(name="eventName")],
    metrics=[Metric(name="eventCount")],
    date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
)
resp = client.run_report(req)
for row in resp.rows:
    event = row.dimension_values[0].value
    count = row.metric_values[0].value
    print(f"{event:40s} {count}")
```

Si te funciona ese snippet básico, pídele a Claude Code que escriba
recipes más complejos en función de tu caso.

---

## Sección 3 — GA4 Admin API (opcional, avanzado)

Para auditar configuración (no datos): usuarios, eventos marcados
como conversión, propiedades, streams.

- Habilitar: **Google Analytics Admin API** en GCP.
- Mismo service account funciona.
- Librería: `pip install google-analytics-admin`.
- Doc: https://developers.google.com/analytics/devguides/config/admin/v1

Recipes típicos:

- "Lista todos los usuarios con acceso a mi propiedad y su rol".
- "Lista los eventos marcados como conversión".
- "Verifica si la vinculación con Google Ads existe y a qué cuenta
  apunta".

Pídele a Claude Code que arme cada recipe con la API de Admin —
sigue el mismo patrón que el snippet del Data API.

---

## Buenas prácticas

- **Reconcilia GA4 con Google Ads regularmente.** Cuando los números
  divergen mucho, casi siempre es un problema de tracking (tag mal
  disparando, conversion action duplicada, lookback diferente).
- **No le des Editor/Administrator a externos sin necesidad.**
  Marketer es suficiente para la mayoría de agencias.
- **Service accounts > OAuth para automatización.** No expira, no
  requiere consentimiento interactivo, fácil de rotar.
- **Backup periódico de configuración GA4** (eventos custom,
  conversions, audiencias) — no hay export oficial, pero el Admin API
  te deja snapshotear los recursos clave a JSON.
