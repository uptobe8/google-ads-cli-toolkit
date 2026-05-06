# google-ads-cli-toolkit

**Toma control de tu Google Ads, GTM y GA4 desde la terminal — con un asistente IA que te guía paso a paso.**

Un kit mínimo y abierto para auditar y operar tu propia cuenta de Google
Ads vía API, sin depender de un freelancer o agencia. Diseñado para
trabajar de la mano con [Claude Code](https://claude.com/claude-code) (u
otro agente IA): tú le hablas en español, él lee el repo y ejecuta los
comandos por ti.

---

## Por qué existe esto

Cuando contratas a una agencia o freelancer de pauta, casi siempre les
das acceso de administrador a tu cuenta de Google Ads. Mientras la
relación va bien, no es problema. Cuando la relación se rompe, el riesgo
es real: en cuestión de minutos, antes de perder accesos, un operador
externo puede:

- Cambiar la estrategia de puja para que la cuenta no entregue (o
  entregue mal).
- Activar Search Partners y Display Network, quemando presupuesto en
  inventario que no convierte.
- Duplicar conversion actions PRIMARY para inflar métricas y desorientar
  al algoritmo de bidding.
- Reescribir tus mejores keywords en match types más laxos para que
  pujen contra todo.
- Dejar tracking de GTM y GA4 bajo cuentas que les pertenecen, no a ti.

Recuperar el control desde la UI, cuando no eres experto en Google Ads,
es lento y propenso a errores. Este repo empaqueta el set mínimo de
herramientas programáticas para que tú — con la ayuda de Claude Code —
puedas **auditar, diagnosticar y arreglar tu cuenta en minutos, no
semanas**, y dejar todo bajo tu control.

## Para quién es

- Dueños y operadores de negocio que pautan en Google Ads y dependen
  (o dependieron) de un tercero para operar la cuenta.
- Equipos pequeños sin un especialista interno de PPC.
- Cualquiera que quiera entender qué está pasando en su cuenta sin
  tener que confiar en el resumen del proveedor.

**No necesitas saber Python.** Sólo necesitas instalar dos cosas en tu
computador (Python y Claude Code) y seguir los pasos.

## Cómo funciona

La [Google Ads API](https://developers.google.com/google-ads/api/docs/start)
te permite hacer todo lo que harías en la UI, vía scripts. Este repo trae
los scripts base. Claude Code es tu copiloto: tú le hablas, él lee el
repo, escribe y corre los comandos por ti.

```
Tú  ←→  Claude Code  ←→  Scripts Python  ←→  Google Ads API  ←→  Tu cuenta
```

## Lo que vas a obtener

- ✅ Acceso programático verificable a tu cuenta — sin intermediarios.
- ✅ Una auditoría completa que muestra el estado real de la cuenta,
  no la versión que te cuenta un tercero.
- ✅ Capacidad de aplicar correcciones en bulk: keywords, negativas,
  estrategia de puja, redes activas, conversion actions.
- ✅ Un agente IA que entiende el contexto de la API y puede escribir
  un script nuevo cuando hace falta.
- ✅ Un patrón equivalente para GTM y GA4 (ver [docs/GTM_GUIDE.md](docs/GTM_GUIDE.md)
  y [docs/GA4_GUIDE.md](docs/GA4_GUIDE.md)).

---

## Quickstart con Claude Code

```bash
# 1. Instala Claude Code:  https://claude.com/claude-code
# 2. Clona este repo
git clone https://github.com/nicolasmaldonadoj/google-ads-cli-toolkit
cd google-ads-cli-toolkit

# 3. Abre Claude Code en este folder
claude

# 4. En el chat, pídele:
#    "Léete el README.md y CLAUDE.md, y guíame paso a paso para
#     conectar mi cuenta de Google Ads y auditarla."
```

Eso es todo. Claude leerá [CLAUDE.md](CLAUDE.md), entenderá el flujo, y
te llevará por cada paso del setup, la auditoría, y las mejoras.

Si prefieres hacerlo manualmente, sigue [docs/SETUP.md](docs/SETUP.md).

---

## Setup en 6 pasos (resumen)

Detalle completo en [docs/SETUP.md](docs/SETUP.md).

1. **Crear cuenta MCC** ("Manager") en Google Ads — necesaria para
   acceder al API Center.
2. **Vincular tu cuenta cliente al MCC** y aceptar la solicitud.
3. **Solicitar Developer Token** desde el MCC (24-72h de aprobación
   para nivel Basic, que alcanza para la mayoría de casos).
4. **Crear OAuth client** tipo Desktop App en
   [Google Cloud Console](https://console.cloud.google.com).
5. **Generar refresh token** corriendo
   `python scripts/01_generate_refresh_token.py CLIENT_ID CLIENT_SECRET`.
6. **Llenar `.env`** con todos los valores y validar con
   `python scripts/02_audit.py`.

---

## Próximos pasos

Una vez tengas Google Ads operando bajo tu control, puedes hacer lo
equivalente para GTM y GA4:

- [docs/GTM_GUIDE.md](docs/GTM_GUIDE.md) — Migrar tu container GTM a
  tu propia cuenta + uso opcional del GTM API.
- [docs/GA4_GUIDE.md](docs/GA4_GUIDE.md) — Auditar accesos, eventos y
  vinculaciones de GA4 + uso opcional del GA4 Data API.
- [docs/COMMON_FIXES.md](docs/COMMON_FIXES.md) — Recetas en lenguaje
  natural para los problemas más comunes (mapeadas a los scripts).
- [docs/USING_WITH_CLAUDE.md](docs/USING_WITH_CLAUDE.md) — Frases
  típicas y buenas prácticas para trabajar con Claude Code.

---

## Estructura del repo

```
google-ads-cli-toolkit/
├── README.md                         # Este archivo
├── CLAUDE.md                         # Playbook para el agente IA
├── LICENSE                           # MIT
├── .env.example                      # Plantilla de credenciales
├── .gitignore
├── requirements.txt
├── scripts/
│   ├── 01_generate_refresh_token.py  # Genera el refresh token OAuth
│   └── 02_audit.py                   # Auditoría read-only de tu cuenta
├── examples/
│   ├── README.md
│   ├── fix_network_settings.py       # Forzar Search puro (apaga Display/Partners)
│   ├── consolidate_primary_conversion.py  # Dejar 1 PRIMARY por categoría
│   └── add_keywords_and_negatives.py # Bulk-add keywords y negativas
└── docs/
    ├── SETUP.md                      # Setup detallado paso a paso
    ├── USING_WITH_CLAUDE.md          # Cómo trabajar con Claude Code
    ├── COMMON_FIXES.md               # Recetas para problemas frecuentes
    ├── GTM_GUIDE.md                  # Guía Google Tag Manager
    └── GA4_GUIDE.md                  # Guía Google Analytics 4
```

---

## Disclaimer y seguridad

- `scripts/02_audit.py` es **read-only**. Nunca modifica tu cuenta.
- Los scripts de `examples/` **modifican tu cuenta**. Léelos completos
  antes de correr. Cada uno trae un guard que aborta si los placeholders
  de configuración no han sido editados.
- **Nunca compartas tu archivo `.env`.** Nunca lo subas a Git. Contiene
  tokens que dan acceso completo a tu cuenta. El `.gitignore` ya está
  configurado para excluirlo.
- Este repo no recolecta nada. Corre 100% local en tu computador,
  llamando directamente a las APIs oficiales de Google.

---

## Contribuir

Issues y pull requests son bienvenidos. Si encuentras un patrón de
sabotaje o un fix común que no está cubierto, agrégalo a
[docs/COMMON_FIXES.md](docs/COMMON_FIXES.md) o como un nuevo script en
`examples/`.

## Licencia

[MIT](LICENSE) — usa, modifica y redistribuye libremente.
