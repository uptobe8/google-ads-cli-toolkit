# AGENTS.md — Playbook del agente

## Contexto operativo

El usuario puede estar usando GitHub Codespaces desde navegador.
Las credenciales pueden existir únicamente como Codespaces Secrets y variables de entorno.

## Seguridad operativa

Fase 1: solo auditoría.

Permitido:
- python scripts/00_preflight.py
- python scripts/02_audit.py

Prohibido sin aprobación explícita:
- examples/fix_network_settings.py
- examples/consolidate_primary_conversion.py
- examples/add_keywords_and_negatives.py
- cualquier script que use mutate, update, create, remove o remove_all

Nunca:
- imprimir tokens
- commitear .env
- hacer git add de secretos
- ejecutar scripts de examples sin revisar constantes internas
