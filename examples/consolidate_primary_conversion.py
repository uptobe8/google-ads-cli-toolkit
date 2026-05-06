"""
Baja una conversion action de PRIMARY a secondary, dejando una sola PRIMARY
en su categoría.

Por qué es útil:
  Cuando dos (o más) conversion actions de la misma categoría (ej.
  SUBMIT_LEAD_FORM) están marcadas como PRIMARY, Google Ads las cuenta
  ambas. Resultado: métricas infladas, el algoritmo de bidding ve "señales"
  que no existen y las decisiones de optimización se ensucian. Lo correcto
  es dejar 1 PRIMARY por categoría y bajar las demás a secondary.

Cómo encontrar el ID a demotar:
  1. Corre `python scripts/02_audit.py`
  2. En la sección "ACCIONES DE CONVERSIÓN", identifica la categoría con
     más de un PRIMARY.
  3. Decide cuál mantener como PRIMARY (la más confiable, con más
     conversiones históricas y el lookback más adecuado a tu ciclo).
  4. Copia el ID de la que vas a demotar abajo.

Nota técnica importante (proto3 + field masks):
  Cuando vas a setear un bool a False, proto3 lo trata como "unset" y el
  auto-generador del SDK omite ese campo del field_mask. Resultado: la API
  devuelve OK pero NO cambia nada. La solución es construir el field_mask
  explícitamente con `field_mask_pb2.FieldMask(paths=[...])`. Eso es lo
  que hace este script.
"""
import os
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.protobuf import field_mask_pb2

load_dotenv()

CUSTOMER_ID = os.getenv("GOOGLE_ADS_CUSTOMER_ID")

# === CONFIGURACIÓN — EDITA ESTO ===
# ID numérico de la conversion action que quieres BAJAR a secondary.
DEMOTE_ID = 0

# Categoría a re-listar después de la operación, para verificación.
# Ejemplos válidos: "SUBMIT_LEAD_FORM", "PURCHASE", "SIGN_UP", "PAGE_VIEW",
# "DOWNLOAD", "BOOK_APPOINTMENT", etc.
CATEGORY_FILTER = ""
# === FIN CONFIGURACIÓN ===


def build_client():
    return GoogleAdsClient.load_from_dict(
        {
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
            "use_proto_plus": True,
        }
    )


def main():
    if DEMOTE_ID == 0 or not CATEGORY_FILTER:
        print("ERROR: edita DEMOTE_ID y CATEGORY_FILTER arriba antes de correr.")
        print("Tip: corre `python scripts/02_audit.py` para ver tus conversion actions.")
        return

    client = build_client()
    svc = client.get_service("ConversionActionService")
    op = client.get_type("ConversionActionOperation")
    update = op.update
    update.resource_name = svc.conversion_action_path(CUSTOMER_ID, DEMOTE_ID)
    update.primary_for_goal = False

    # Field mask explícito: setear bool a False es indistinguible de "unset"
    # en proto3, así que el auto-generador lo salta. Forzamos el path.
    op.update_mask.MergeFrom(field_mask_pb2.FieldMask(paths=["primary_for_goal"]))

    response = svc.mutate_conversion_actions(
        customer_id=CUSTOMER_ID, operations=[op]
    )
    print(f"OK: {response.results[0].resource_name}")
    print(f"Conversion action id {DEMOTE_ID} → primary_for_goal=False")
    print()
    print(f"Verificación (PRIMARY/secondary en categoría {CATEGORY_FILTER}):")
    gas = client.get_service("GoogleAdsService")
    q = f"""
        SELECT conversion_action.id, conversion_action.name,
               conversion_action.primary_for_goal, conversion_action.category
        FROM conversion_action
        WHERE conversion_action.category = '{CATEGORY_FILTER}'
          AND conversion_action.status = 'ENABLED'
        ORDER BY conversion_action.name
    """
    for r in gas.search(customer_id=CUSTOMER_ID, query=q):
        ca = r.conversion_action
        flag = "PRIMARY" if ca.primary_for_goal else "secondary"
        print(f"  [{flag}] {ca.name} (id {ca.id})")


if __name__ == "__main__":
    main()
