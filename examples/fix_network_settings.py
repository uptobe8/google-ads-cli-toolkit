"""
Fuerza una campaña Search a operar SOLO en la Red de Búsqueda principal de
Google, desactivando Search Partners y Display Network.

Por qué es útil:
  Cuando una campaña fue creada como "Search", ciertos toggles (search_partners,
  display_network) suelen quemar presupuesto en inventario que no convierte
  para tu caso de uso. Una causa común de gasto inflado y CPL malo es tener
  estos toggles activos sin querer.

Estado deseado para Search puro:
  target_google_search          = True   (Red de Búsqueda principal)
  target_search_network         = False  (Search Partners — desactivado)
  target_content_network        = False  (Display Network — desactivado)
  target_partner_search_network = False  (Google Partner Sites — desactivado)

Antes de correr:
  1. Corre `python scripts/02_audit.py` y copia el nombre exacto de la
     campaña que quieres ajustar.
  2. Pégalo abajo en CAMPAIGN_NAME.
  3. Lee el script entero. Modifica sólo si quieres aplicar.
"""
import os
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.api_core import protobuf_helpers

load_dotenv()

CUSTOMER_ID = os.getenv("GOOGLE_ADS_CUSTOMER_ID")

# === CONFIGURACIÓN — EDITA ESTO ===
# Nombre EXACTO de la campaña (cópialo del output de 02_audit.py).
CAMPAIGN_NAME = "TU_CAMPAÑA_AQUÍ"

# Estado deseado de las 4 redes (cambia si tu caso es distinto).
DESIRED = {
    "target_google_search": True,
    "target_search_network": False,
    "target_content_network": False,
    "target_partner_search_network": False,
}
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


def get_campaign(client, name):
    svc = client.get_service("GoogleAdsService")
    q = f"""
        SELECT campaign.id, campaign.name, campaign.status,
               campaign.network_settings.target_google_search,
               campaign.network_settings.target_search_network,
               campaign.network_settings.target_content_network,
               campaign.network_settings.target_partner_search_network
        FROM campaign WHERE campaign.name = '{name}'
    """
    for r in svc.search(customer_id=CUSTOMER_ID, query=q):
        return r
    return None


def main():
    if CAMPAIGN_NAME == "TU_CAMPAÑA_AQUÍ":
        print("ERROR: edita la constante CAMPAIGN_NAME arriba antes de correr.")
        print("Tip: corre `python scripts/02_audit.py` para ver tus campañas.")
        return

    client = build_client()
    row = get_campaign(client, CAMPAIGN_NAME)
    if not row:
        print(f"ERROR: campaña no encontrada: {CAMPAIGN_NAME}")
        return

    c = row.campaign
    ns = c.network_settings
    current = {
        "target_google_search": ns.target_google_search,
        "target_search_network": ns.target_search_network,
        "target_content_network": ns.target_content_network,
        "target_partner_search_network": ns.target_partner_search_network,
    }

    print(f"Campaña: {c.name}")
    print(f"ID: {c.id} | Estado: {c.status.name}")
    print()
    print("ESTADO ACTUAL DE REDES:")
    labels = {
        "target_google_search": "Red de Búsqueda Google (principal)",
        "target_search_network": "Search Partners",
        "target_content_network": "Display Network",
        "target_partner_search_network": "Google Partner Sites",
    }
    for k, v in current.items():
        flag = "OK" if v == DESIRED[k] else "FIX"
        print(f"  [{flag}] {labels[k]:40s} = {v}  (deseado: {DESIRED[k]})")

    diffs = [k for k in current if current[k] != DESIRED[k]]
    if not diffs:
        print("\nNo hay cambios que aplicar. Configuración correcta.")
        return

    print(f"\nAplicando cambios en: {diffs}")

    campaign_service = client.get_service("CampaignService")
    op = client.get_type("CampaignOperation")
    update = op.update
    update.resource_name = campaign_service.campaign_path(CUSTOMER_ID, c.id)
    update.network_settings.target_google_search = DESIRED["target_google_search"]
    update.network_settings.target_search_network = DESIRED["target_search_network"]
    update.network_settings.target_content_network = DESIRED["target_content_network"]
    update.network_settings.target_partner_search_network = DESIRED["target_partner_search_network"]

    client.copy_from(
        op.update_mask,
        protobuf_helpers.field_mask(None, update._pb),
    )

    response = campaign_service.mutate_campaigns(
        customer_id=CUSTOMER_ID, operations=[op]
    )
    print(f"\nActualizado: {response.results[0].resource_name}")
    print("\nRe-verificando...")
    row2 = get_campaign(client, CAMPAIGN_NAME)
    ns2 = row2.campaign.network_settings
    print(f"  target_google_search          = {ns2.target_google_search}")
    print(f"  target_search_network         = {ns2.target_search_network}")
    print(f"  target_content_network        = {ns2.target_content_network}")
    print(f"  target_partner_search_network = {ns2.target_partner_search_network}")


if __name__ == "__main__":
    main()
