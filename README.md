# google-ads-cli-toolkit

## Quickstart con GitHub Codespaces + OpenAI Codex CLI

Este flujo no requiere instalar nada en tu ordenador. Todo corre en GitHub Codespaces desde navegador.

1. Abre este repositorio en GitHub.
2. Pulsa Code → Codespaces → Create codespace on main.
3. Espera a que Codespaces instale Python, dependencias y Codex CLI.
4. Abre la terminal del Codespace.
5. Ejecuta:

```bash
codex
```

Prompt recomendado:

Lee README.md, AGENTS.md y docs/SETUP.md.

Estoy usando GitHub Codespaces.
Quiero solo auditoría read-only.
No ejecutes examples.
No modifiques campañas.
No imprimas secretos.

Ejecuta:
python scripts/00_preflight.py
python scripts/02_audit.py

## Seguridad operativa

Permitido:
- scripts/00_preflight.py
- scripts/02_audit.py

Nunca:
- imprimir tokens
- commitear .env
- ejecutar scripts de examples sin revisar constantes
