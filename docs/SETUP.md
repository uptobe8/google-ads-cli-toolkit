# Setup detallado — Google Ads API

Walkthrough completo para conectar este toolkit a tu cuenta de Google
Ads. Si en cualquier paso te atascas, abre Claude Code en el folder y
pídele ayuda — está diseñado para guiarte.

**Tiempo total:** ~30 min de tu lado + 24-72h de espera para que Google
apruebe el Developer Token.

## Pre-requisitos

- Una cuenta de Google Ads ya activa, donde tú (o tu organización) son
  el dueño legal de la cuenta.
- Acceso a tu cuenta de Google con la que iniciarás sesión (cuenta
  personal de Gmail o cuenta de Google Workspace).
- Python 3.9+ instalado en tu computador.
- Este repo clonado y un virtualenv listo:
  ```bash
  cd google-ads-cli-toolkit
  python -m venv .venv
  source .venv/bin/activate            # macOS / Linux
  # .venv\Scripts\activate             # Windows
  pip install -r requirements.txt
  ```

---

## Paso 1 — Crear cuenta MCC ("Manager")

**Por qué necesitas un MCC:** el "API Center" donde se solicita el
Developer Token sólo existe en cuentas de tipo Manager (MCC). Si tu
cuenta actual es una cuenta cliente regular, necesitas crear un MCC y
vincularla al MCC.

1. Ve a https://ads.google.com/intl/es/home/tools/manager-accounts/ y
   haz clic en **"Crear cuenta de administrador"**.
2. Inicia sesión con la cuenta de Google que será dueña del MCC.
3. Llena los datos:
   - **Nombre del MCC**: algo descriptivo (ej. `Mi Negocio Manager`).
   - **Uso**: selecciona **"Administrar mis propias cuentas"**.
   - **País**: el tuyo. **Zona horaria** y **Moneda**: las que
     correspondan a tu operación.
4. Una vez creado, anota el **Customer ID** del MCC (10 dígitos, formato
   `XXX-XXX-XXXX`). Sin guiones va en `.env` como
   `GOOGLE_ADS_LOGIN_CUSTOMER_ID`.

---

## Paso 2 — Vincular tu cuenta cliente al MCC

1. Dentro del MCC: **Cuentas → Subcuentas → "+ Vincular cuenta
   existente"**.
2. Pega el ID de tu cuenta cliente (sin guiones).
3. Google envía una solicitud a la cuenta cliente.
4. Cambia a la cuenta cliente (en el switcher arriba a la derecha) y
   ve a **Administrador → Acceso y seguridad → Cuentas de administrador
   → Aceptar**.

Anota el ID de la cuenta cliente (sin guiones) — irá en `.env` como
`GOOGLE_ADS_CUSTOMER_ID`.

> ⚠️ **No confundir los dos IDs.** El `LOGIN_CUSTOMER_ID` es el MCC
> (desde donde autenticas). El `CUSTOMER_ID` es la cuenta cliente
> (contra la que operas). Confundirlos da `authentication failed`.

---

## Paso 3 — Solicitar Developer Token

1. Estando dentro del MCC, ve a https://ads.google.com/aw/apicenter
2. Acepta los Términos de Servicio del API.
3. Llena el formulario:
   - **Nombre del producto**: algo como `Mi Toolkit Interno`.
   - **Sitio web**: el de tu negocio (o el repo de GitHub si vas a
     publicar).
   - **Caso de uso**: "Internal account management, auditing and
     reporting tools" (o equivalente en español).
   - **Nivel solicitado**: **Basic** (suficiente para auditoría +
     cambios manuales en una sola cuenta).
4. Te dan un **token de prueba inmediato** (sirve para 15 operaciones
   por día — alcanza para arrancar) y la solicitud Basic se aprueba en
   24-72h.
5. Pega el token en `.env` como `GOOGLE_ADS_DEVELOPER_TOKEN`.

---

## Paso 4 — Crear proyecto en Google Cloud + habilitar Google Ads API

1. Ve a https://console.cloud.google.com
2. Si no tienes proyecto: **Seleccionar proyecto → Nuevo proyecto**.
   Nombre sugerido: `mi-negocio-ads`.
3. Con el proyecto seleccionado, ve a **APIs y servicios → Biblioteca**,
   busca **"Google Ads API"**, y haz clic en **Habilitar**.
4. (Si te lo pide) Configura la **OAuth consent screen**:
   **APIs y servicios → OAuth consent screen** → tipo **Internal**
   (si usas Google Workspace) o **External** (si usas Gmail personal).
   Llena los datos básicos.

---

## Paso 5 — Crear OAuth client (tipo Desktop App)

1. **APIs y servicios → Credenciales → Crear credenciales → ID de
   cliente de OAuth**.
2. Tipo de aplicación: **Aplicación de escritorio**.
3. Nombre: `Google Ads CLI` (o lo que prefieras).
4. Crea y copia los dos valores:
   - **ID de cliente** → `.env` como `GOOGLE_ADS_CLIENT_ID`.
   - **Secreto del cliente** → `.env` como `GOOGLE_ADS_CLIENT_SECRET`.

---

## Paso 6 — Generar refresh token

```bash
cd google-ads-cli-toolkit
source .venv/bin/activate
python scripts/01_generate_refresh_token.py "$GOOGLE_ADS_CLIENT_ID" "$GOOGLE_ADS_CLIENT_SECRET"
```

(O reemplaza `"$GOOGLE_ADS_CLIENT_ID"` y `"$GOOGLE_ADS_CLIENT_SECRET"`
con los valores literales si aún no tienes el `.env` cargado.)

Qué pasa:
1. Se abre tu navegador con la pantalla de consentimiento de Google.
2. Selecciona la cuenta de Google con la que creaste el MCC.
3. Acepta los permisos.
4. La pestaña dice "Listo. Volvé a la terminal."
5. La terminal imprime un `refresh_token` largo. Cópialo a `.env` como
   `GOOGLE_ADS_REFRESH_TOKEN`.

> Si el navegador no abre automáticamente, copia la URL que imprime el
> script y pégala manualmente.

---

## Paso 7 — Validar

Tu `.env` ya debe estar lleno. Confírmalo:

```bash
cat .env
```

Debes ver valores en todas estas variables:
- `GOOGLE_ADS_DEVELOPER_TOKEN`
- `GOOGLE_ADS_CLIENT_ID`
- `GOOGLE_ADS_CLIENT_SECRET`
- `GOOGLE_ADS_REFRESH_TOKEN`
- `GOOGLE_ADS_LOGIN_CUSTOMER_ID`
- `GOOGLE_ADS_CUSTOMER_ID`

Corre la auditoría:

```bash
python scripts/02_audit.py
```

Deberías ver:
- Datos de tu cuenta (ID, moneda, zona horaria).
- Lista de usuarios con acceso.
- Tus campañas con métricas de los últimos 30 días.
- Todos tus keywords con performance.
- Todas tus conversion actions con su estado.

Si lo ves: **listo. El acceso programático funciona.** Comparte el
output con Claude Code para empezar el diagnóstico.

---

## Troubleshooting

### `authentication failed` o `permission denied`

- Verifica que `GOOGLE_ADS_LOGIN_CUSTOMER_ID` es el del MCC y
  `GOOGLE_ADS_CUSTOMER_ID` es el de la cuenta cliente. Confundirlos es
  el error más común.
- Verifica que la cuenta cliente está vinculada al MCC y la solicitud
  fue aceptada (paso 2).

### `developer_token: invalid` o `developer-token-not-approved`

- Revisa que el token está pegado correctamente, sin espacios.
- Si Google todavía no aprobó tu solicitud Basic, usas el token de
  prueba — alcanza para 15 operaciones diarias. Espera la aprobación
  para volumen mayor.

### `quota_error: USER_RATE_LIMIT_EXCEEDED`

- Estás haciendo demasiadas llamadas seguidas. Espera unos minutos.
- Si necesitas más volumen, considera solicitar nivel Standard del
  Developer Token (formulario más detallado, ~1 semana de revisión).

### El script `01_generate_refresh_token.py` se cuelga

- Otra cosa puede estar usando el puerto 8765. Cierra apps de
  desarrollo activas o reinicia la terminal.

### Cualquier otro error

Pásale el mensaje completo a Claude Code en el chat. Lo más probable
es que sepa qué pasa y te dé el fix.
