# examples/

Scripts plantilla para los problemas más comunes en cuentas de Google
Ads. **Cada uno modifica tu cuenta**. Léelos completos antes de correr.

## Cómo usarlos

Cada ejemplo tiene un bloque `# === CONFIGURACIÓN — EDITA ESTO ===` al
inicio. Edita los valores ahí (nombre de campaña, IDs, listas de
keywords) antes de correr. Si dejas los placeholders, el script aborta
con un mensaje claro — no muta nada.

Flujo recomendado:

1. Antes de cualquier cambio: `python scripts/02_audit.py`
   (snapshot del estado actual).
2. Edita las constantes del ejemplo que vas a usar.
3. Corre el ejemplo: `python examples/<nombre>.py`.
4. Vuelve a correr `python scripts/02_audit.py` para verificar que
   el cambio se aplicó.

Si trabajas con Codex CLI, dile algo como: "Quiero apagar Search
Partners en mi campaña X. Edita `examples/fix_network_settings.py`
con los valores correctos, muéstrame el script, y córrelo cuando te
confirme."

## Ejemplos disponibles

| Script | Para qué sirve |
|---|---|
| [fix_network_settings.py](fix_network_settings.py) | Forzar una campaña Search a operar SOLO en la Red de Búsqueda principal (apaga Search Partners y Display Network). |
| [consolidate_primary_conversion.py](consolidate_primary_conversion.py) | Bajar una conversion action de PRIMARY a secondary, dejando una sola PRIMARY por categoría (evita doble conteo). |
| [add_keywords_and_negatives.py](add_keywords_and_negatives.py) | Bulk-add de keywords positivas a uno o más ad groups y negativas a nivel campaña. Idempotente — salta lo que ya existe. |

## Adaptar / extender

Si tu caso no calza con ninguno de los ejemplos, puedes:

- Pedirle a Codex CLI que te escriba un script nuevo en `scripts/`
  con el siguiente prefijo numérico (`03_`, `04_`, …), siguiendo el
  patrón de los existentes.
- Hacer un fork y agregar tu ejemplo aquí. Pull requests son
  bienvenidos en el repo principal.
