# Recetas para problemas comunes

Cada receta tiene 4 partes:
1. **Síntoma** — qué ves en el audit o en la cuenta.
2. **Causa probable** — por qué pasa.
3. **Fix** — qué hacer.
4. **Cómo aplicarlo** — script o paso manual.

Si trabajas con Claude Code, puedes pegarle el síntoma y pedirle que
identifique cuál de estas recetas aplica.

---

## 1. Mi campaña Search está gastando en Display o Search Partners

**Síntoma**
En el audit, una campaña con `advertising_channel_type=SEARCH` muestra:
```
Redes: google_search=True search_partners=True display=True ...
```

**Causa probable**
Los toggles de "incluir Search Partners" e "incluir Display Network"
quedaron activos al crear la campaña (o alguien los activó después).
Estos toggles pueden quemar presupuesto sin convertir.

**Fix**
Apagar `target_search_network` y `target_content_network`. Dejar sólo
`target_google_search=True`.

**Cómo aplicarlo**
[examples/fix_network_settings.py](../examples/fix_network_settings.py).
Edita `CAMPAIGN_NAME` con el nombre exacto de tu campaña, corre.

---

## 2. Tengo doble PRIMARY en una categoría de conversion action

**Síntoma**
En el audit, en la sección de conversion actions, ves dos (o más)
acciones marcadas como **PRIMARY** en la misma categoría (ej.
`SUBMIT_LEAD_FORM`, `PURCHASE`).

**Causa probable**
Al implementar tracking, alguien creó tags duplicados (uno desde
Google Ads UI directo, otro vía GTM, por ejemplo). Resultado: el mismo
evento se cuenta dos veces. Métricas infladas y bidding confundido.

**Fix**
Decidir cuál tag es la fuente de verdad (la que tiene más conversiones
históricas y el lookback más adecuado), mantener esa como PRIMARY, y
bajar las demás a **secondary**. Las secondary se siguen registrando
pero no entran al optimizador.

**Cómo aplicarlo**
[examples/consolidate_primary_conversion.py](../examples/consolidate_primary_conversion.py).
Edita `DEMOTE_ID` con el ID de la action que vas a bajar y
`CATEGORY_FILTER` con la categoría (ej. `"SUBMIT_LEAD_FORM"`).

---

## 3. Mis keywords están todas en BROAD y queman presupuesto

**Síntoma**
En el audit, los ad groups muestran muchos keywords con
`match_type=BROAD` que tienen alto `cost_micros` y bajas
`conversions`.

**Causa probable**
BROAD match expande agresivamente — Google muestra tu anuncio para
queries lejanamente relacionadas a la keyword. Si no tienes una buena
política de negativas, gastas en queries irrelevantes.

**Fix**
Re-crear las keywords core en **EXACT** (control máximo) o **PHRASE**
(balance entre alcance y precisión). Mantener BROAD sólo para
descubrimiento controlado, con negativas robustas.

**Cómo aplicarlo**
[examples/add_keywords_and_negatives.py](../examples/add_keywords_and_negatives.py).
Llena `KEYWORDS_BY_AD_GROUP` con las keywords que quieres en EXACT,
y considera agregar negativas a nivel campaña en
`NEGATIVE_KEYWORDS_PHRASE` o `NEGATIVE_KEYWORDS_EXACT`.

---

## 4. Mi tCPA es absurdo y la campaña no entrega (o entrega mal)

**Síntoma**
En el audit, ves `bidding_strategy_type=MAXIMIZE_CONVERSIONS` y un
`tCPA` muy bajo (ej. 1/10 de tu CPA real) o muy alto (10x tu CPA real).
Las impresiones caen drásticamente o el gasto se dispara.

**Causa probable**
- tCPA muy bajo: Google no encuentra impresiones que cumplan ese
  costo, deja de mostrar tu anuncio.
- tCPA muy alto: Google entrega a cualquier costo, gastas mal.
- A veces se setea por error, otras es sabotaje.

**Fix**
Dos opciones:
- Quitar el tCPA: estrategia "MAXIMIZE_CONVERSIONS sin objetivo" —
  Google optimiza dentro del budget diario.
- Ajustar el tCPA a un valor realista (cercano a tu CPA histórico).

**Cómo aplicarlo**
Pídele a Claude Code que escriba un script `scripts/0X_fix_bidding.py`
basado en el patrón de [examples/fix_network_settings.py](../examples/fix_network_settings.py).
La operación es un `CampaignOperation.update` sobre
`campaign.maximize_conversions.target_cpa_micros`. Si quieres
"sin objetivo", setealo a 0 con field_mask explícito (recuerda el
truco proto3 — ver [examples/consolidate_primary_conversion.py](../examples/consolidate_primary_conversion.py)).

---

## 5. Hay un usuario externo con acceso Admin que ya no trabaja conmigo

**Síntoma**
En el audit, en "USUARIOS CON ACCESO" aparecen emails de personas o
agencias con quienes ya no trabajas, con rol `ADMIN` o `STANDARD`.

**Causa probable**
Cuando contrataste a la agencia/freelancer le diste acceso de admin
para que operaran. Al terminar el contrato no se removió.

**Fix**
Removerlos. La Google Ads API tiene endpoints para gestión de usuarios,
pero suelen estar limitados; lo más confiable es la UI:

1. Google Ads → Administrador → Acceso y seguridad → Usuarios.
2. Encuentra el email externo.
3. Clic en su nombre → Quitar acceso.

Si tienes una **MCC** vinculada que pertenece al ex-operador, también
revoca su acceso a tu cuenta cliente:
1. Cuenta cliente → Administrador → Acceso y seguridad → Cuentas de
   administrador.
2. Encuentra el MCC del ex-operador.
3. Clic → Quitar como administrador.

---

## 6. Mi lookback window de conversiones es muy corto para mi ciclo de venta

**Síntoma**
En el audit, una conversion action clave muestra
`Lookback clk=30d` (default) cuando tu ciclo real de decisión es de
60 o 90 días.

**Causa probable**
Default de Google. Para ciclos largos (inmobiliario, B2B, autos,
educación, productos high-ticket), 30 días pierde muchas conversiones
atribuibles al click original.

**Fix**
Subir el `click_through_lookback_window_days` a 60 o 90.

**Cómo aplicarlo**
Pídele a Claude Code que escriba un script `scripts/0X_extend_lookback.py`.
La operación es:

```python
update = op.update
update.resource_name = svc.conversion_action_path(CUSTOMER_ID, ACTION_ID)
update.click_through_lookback_window_days = 90
op.update_mask.MergeFrom(field_mask_pb2.FieldMask(
    paths=["click_through_lookback_window_days"]
))
```

(Usa el field_mask explícito porque `90` no es 0/False, pero es una
buena práctica.)

---

## 7. Faltan negativas que filtren tráfico obvio no calificado

**Síntoma**
Las queries que dispararon tus anuncios (Search Terms Report en la UI,
o `search_term_view` en la API) muestran términos claramente
irrelevantes para tu negocio.

**Causa probable**
Cuando creaste la campaña no pusiste suficientes negativas, o el
match type de tus keywords es muy laxo (ver receta #3).

**Fix**
Agregar negativas a nivel campaña. Patrón típico:
- **PHRASE** para frases generales que aparecen embebidas
  ("alquiler", "gratis", "barato", "empleo", etc.).
- **EXACT** para queries específicas que sólo bloqueas tal cual.

**Cómo aplicarlo**
[examples/add_keywords_and_negatives.py](../examples/add_keywords_and_negatives.py).
Llena `NEGATIVE_KEYWORDS_PHRASE` y/o `NEGATIVE_KEYWORDS_EXACT`.

---

## ¿No encuentras tu caso?

Pásale a Claude Code el output del audit y describe el síntoma. Te
puede armar el script a medida o sugerir el fix manual desde la UI.
