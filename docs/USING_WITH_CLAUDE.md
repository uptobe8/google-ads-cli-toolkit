# Trabajar con Claude Code

Este toolkit está diseñado para usarse con [Claude Code](https://claude.com/claude-code),
el cliente de terminal de Anthropic. Tú hablas en español, Claude lee
el repo, escribe scripts y los corre por ti.

## Instalación de Claude Code

Sigue las instrucciones oficiales en https://claude.com/claude-code

Disponible para macOS, Windows, Linux. Una vez instalado, puedes
abrirlo en cualquier folder con:

```bash
cd google-ads-cli-toolkit
claude
```

## Frases típicas para arrancar

### Setup inicial

> "Léete el README.md y el CLAUDE.md, y guíame paso a paso para
> conectar mi cuenta de Google Ads."

Claude leerá los docs y te preguntará en qué punto del setup estás.
Empezará desde el primer paso que falte.

### Auditoría

> "Mi `.env` ya está lleno. Corre la auditoría y dame un diagnóstico
> en lenguaje claro, sin jerga técnica."

Claude correrá `scripts/02_audit.py`, leerá el output, y te resumirá
los hallazgos. Si ve banderas rojas (ver lista en [CLAUDE.md](../CLAUDE.md))
te las propondrá como mejoras.

### Diagnóstico de un problema específico

> "Mi campaña X está gastando mucho y converte poco. ¿Qué puede estar
> pasando?"

Claude correrá la auditoría, mirará los datos de esa campaña en
particular (estrategia de puja, redes activas, keywords, conversion
actions) y te dará hipótesis con evidencia.

### Aplicar un fix

> "Quiero apagar Search Partners en mi campaña [NOMBRE]. ¿Cómo lo hago?"

Claude editará `examples/fix_network_settings.py` con el nombre de tu
campaña, te mostrará el script, te explicará el efecto, y lo correrá
cuando le confirmes.

### Hacer algo que no está cubierto

> "Quiero pausar todas las campañas que no convirtieron en los últimos
> 30 días."

Claude escribirá un script nuevo en `scripts/` (con el siguiente
prefijo numérico), siguiendo el patrón de los existentes, te mostrará
el código y lo correrá cuando le confirmes.

## Buenas prácticas

### Antes de mutar, audita

Pídele a Claude que corra `02_audit.py` antes de aplicar cualquier
cambio. Eso te da un snapshot del estado actual al que volver si algo
sale mal.

### Si afecta presupuesto, cuestiona el cambio

Si Claude propone activar/desactivar una estrategia de puja o cambiar
budgets, pídele que estime el impacto en gasto antes de aplicar:

> "Antes de correr eso, dime qué impacto esperado tiene en el gasto
> diario y semanal."

### Lee el script antes de correr

Claude te muestra el script antes de ejecutarlo. Léelo aunque sea por
encima. Si algo no entiendes, pregunta:

> "Explícame línea por línea qué hace este script."

### Nunca compartas tu `.env`

El `.env` contiene tokens que dan acceso completo a tu cuenta. No lo
mandes a nadie. No lo subas a Git (el `.gitignore` ya lo excluye).
Si necesitas compartir output con alguien, pídele a Claude que omita
los IDs de cuenta y cualquier dato sensible.

### Si Claude pide ejecutar algo peligroso, léelo

Claude pide permiso antes de correr cada comando. Si lo que va a correr
toca tu cuenta de Google Ads, GTM, GA4, o el sistema operativo, leelo
entero antes de aprobar. Si dudas, pregunta:

> "¿Por qué necesitas ese comando? ¿Qué pasa si lo cancelo?"

## Trucos útiles

### Pídele que documente lo que hizo

Después de aplicar varios cambios, di:

> "Resúmeme en un par de párrafos qué cambios hicimos hoy, en lenguaje
> de negocio."

Útil para mandárselo a tu equipo o tener registro de las decisiones.

### Pídele que estime impacto futuro

> "Asumiendo que mi tráfico se mantiene igual, ¿qué impacto esperas que
> tenga este cambio en mi CPL en los próximos 30 días?"

No es predicción exacta — es razonamiento estructurado sobre tus
datos. Útil para tomar decisiones informadas.

### Reusa los outputs de auditoría como contexto

Si abres una sesión nueva, dile:

> "Acabo de correr `python scripts/02_audit.py`. Aquí está el output:
> [pega el output]. ¿Qué ves?"

Claude trabaja mejor con datos a la vista que pidiéndole correr todo
desde cero.

## Cuando Claude se equivoca

Puede pasar. Algunas señales:

- Te dice que un campo de la API existe y la API responde "field not
  found". Solución: pídele que corra el query con un campo más simple
  primero, y que itere desde ahí.
- Edita un script y rompe la sintaxis. Solución: dile "ese script
  ahora falla con [error]. Lee el archivo y arregla."
- Asume que ya hiciste algo que no hiciste. Solución: corrige
  explícitamente y pide que recomience.

En general: si una conversación se descarrila, abre una sesión nueva
y dale el contexto desde cero (el repo + el output de la auditoría
más reciente).
