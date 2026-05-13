"""
Agrega keywords (positivas) a uno o más ad groups y keywords negativas a
nivel campaña, en bulk.

Por qué es útil:
  - Bulk-add de keywords nuevas en EXACT/PHRASE evita el dolor de hacerlo
    una por una en la UI.
  - Las negativas a nivel campaña filtran tráfico no calificado de toda la
    campaña, no sólo un ad group.
  - El script es idempotente: si una keyword ya existe (mismo texto + mismo
    match type), la salta.

Antes de correr:
  1. Corre `python scripts/02_audit.py` para ver el nombre exacto de la
     campaña y los ad groups que existen.
  2. Llena CAMPAIGN_NAME y KEYWORDS_BY_AD_GROUP abajo.
  3. Llena las listas de negativas (PHRASE y/o EXACT) si aplica.
  4. Lee el script entero antes de correr.
"""
import os
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient

load_dotenv()

CUSTOMER_ID = os.getenv("GOOGLE_ADS_CUSTOMER_ID")

# === CONFIGURACIÓN — EDITA ESTO ===
# Nombre EXACTO de la campaña.
CAMPAIGN_NAME = "TU_CAMPAÑA_AQUÍ"

# Keywords positivas por ad group.
# Forma:
#   KEYWORDS_BY_AD_GROUP = {
#       "Nombre Ad Group 1": ["keyword uno", "keyword dos"],
#       "Nombre Ad Group 2": ["keyword tres"],
#   }
KEYWORDS_BY_AD_GROUP = {}

# Match type para todas las keywords positivas. Opciones: "EXACT", "PHRASE", "BROAD".
POSITIVE_MATCH_TYPE = "EXACT"

# Keywords negativas a nivel CAMPAÑA, match type PHRASE.
# Útiles para frases generales que aparecen embebidas en queries.
NEGATIVE_KEYWORDS_PHRASE = []

# Keywords negativas a nivel CAMPAÑA, match type EXACT.
# Útiles para queries específicas que sólo bloqueas si vienen tal cual.
NEGATIVE_KEYWORDS_EXACT = []
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


def get_campaign_and_groups(client):
    svc = client.get_service("GoogleAdsService")
    q = f"""
        SELECT campaign.id, campaign.name, ad_group.id, ad_group.name
        FROM ad_group
        WHERE campaign.name = '{CAMPAIGN_NAME}' AND ad_group.status = 'ENABLED'
    """
    campaign_id = None
    groups = {}
    for r in svc.search(customer_id=CUSTOMER_ID, query=q):
        campaign_id = r.campaign.id
        groups[r.ad_group.name] = r.ad_group.id
    return campaign_id, groups


def get_existing_keywords(client, ad_group_id):
    svc = client.get_service("GoogleAdsService")
    q = f"""
        SELECT ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type
        FROM ad_group_criterion
        WHERE ad_group.id = {ad_group_id}
          AND ad_group_criterion.type = 'KEYWORD'
          AND ad_group_criterion.status != 'REMOVED'
    """
    existing = set()
    for r in svc.search(customer_id=CUSTOMER_ID, query=q):
        kw = r.ad_group_criterion.keyword
        existing.add((kw.text.lower(), kw.match_type.name))
    return existing


def add_keywords_to_group(client, ad_group_id, keywords, match_type):
    ad_group_service = client.get_service("AdGroupService")
    crit_service = client.get_service("AdGroupCriterionService")

    existing = get_existing_keywords(client, ad_group_id)
    operations = []
    skipped = []
    for text in keywords:
        if (text.lower(), match_type) in existing:
            skipped.append(text)
            continue
        op = client.get_type("AdGroupCriterionOperation")
        crit = op.create
        crit.ad_group = ad_group_service.ad_group_path(CUSTOMER_ID, ad_group_id)
        crit.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        crit.keyword.text = text
        crit.keyword.match_type = client.enums.KeywordMatchTypeEnum[match_type]
        operations.append(op)

    if not operations:
        print(f"    Nada para crear (todos ya existen). Skipped: {len(skipped)}")
        return

    response = crit_service.mutate_ad_group_criteria(
        customer_id=CUSTOMER_ID, operations=operations
    )
    for r in response.results:
        print(f"    + {r.resource_name.split('/')[-1]}: creada")
    if skipped:
        print(f"    Skipped (ya existían): {skipped}")


def get_existing_campaign_negatives(client, campaign_id):
    svc = client.get_service("GoogleAdsService")
    q = f"""
        SELECT campaign_criterion.keyword.text, campaign_criterion.keyword.match_type
        FROM campaign_criterion
        WHERE campaign.id = {campaign_id}
          AND campaign_criterion.type = 'KEYWORD'
          AND campaign_criterion.negative = TRUE
    """
    existing = set()
    for r in svc.search(customer_id=CUSTOMER_ID, query=q):
        kw = r.campaign_criterion.keyword
        existing.add((kw.text.lower(), kw.match_type.name))
    return existing


def add_campaign_negatives(client, campaign_id, keywords, match_type):
    campaign_service = client.get_service("CampaignService")
    crit_service = client.get_service("CampaignCriterionService")

    existing = get_existing_campaign_negatives(client, campaign_id)
    operations = []
    skipped = []
    for text in keywords:
        if (text.lower(), match_type) in existing:
            skipped.append(text)
            continue
        op = client.get_type("CampaignCriterionOperation")
        crit = op.create
        crit.campaign = campaign_service.campaign_path(CUSTOMER_ID, campaign_id)
        crit.negative = True
        crit.keyword.text = text
        crit.keyword.match_type = client.enums.KeywordMatchTypeEnum[match_type]
        operations.append(op)

    if not operations:
        print(f"    Nada para crear. Skipped: {skipped}")
        return

    response = crit_service.mutate_campaign_criteria(
        customer_id=CUSTOMER_ID, operations=operations
    )
    for r in response.results:
        print(f"    + neg {match_type}: {r.resource_name.split('/')[-1]}")
    if skipped:
        print(f"    Skipped: {skipped}")


def main():
    nothing_to_do = (
        not KEYWORDS_BY_AD_GROUP
        and not NEGATIVE_KEYWORDS_PHRASE
        and not NEGATIVE_KEYWORDS_EXACT
    )
    if CAMPAIGN_NAME == "TU_CAMPAÑA_AQUÍ" or nothing_to_do:
        print("ERROR: edita la configuración arriba antes de correr.")
        print("  - CAMPAIGN_NAME debe apuntar a una campaña real.")
        print("  - Al menos uno de KEYWORDS_BY_AD_GROUP, NEGATIVE_KEYWORDS_PHRASE")
        print("    o NEGATIVE_KEYWORDS_EXACT debe estar lleno.")
        return

    client = build_client()

    print("Obteniendo campaña y grupos...")
    campaign_id, groups = get_campaign_and_groups(client)
    if not campaign_id:
        print(f"ERROR: campaña no encontrada o sin ad groups activos: {CAMPAIGN_NAME}")
        return
    print(f"  Campaña ID: {campaign_id}")
    for name, gid in groups.items():
        print(f"  Grupo '{name}' → {gid}")

    for ad_group_name, kw_list in KEYWORDS_BY_AD_GROUP.items():
        print(f"\n[+] Agregar {len(kw_list)} keywords {POSITIVE_MATCH_TYPE} a '{ad_group_name}'...")
        if ad_group_name in groups:
            add_keywords_to_group(client, groups[ad_group_name], kw_list, POSITIVE_MATCH_TYPE)
        else:
            print(f"  Ad group no encontrado: {ad_group_name}. Salto.")

    if NEGATIVE_KEYWORDS_PHRASE:
        print(f"\n[+] Agregar {len(NEGATIVE_KEYWORDS_PHRASE)} negativas PHRASE a la campaña...")
        add_campaign_negatives(client, campaign_id, NEGATIVE_KEYWORDS_PHRASE, "PHRASE")

    if NEGATIVE_KEYWORDS_EXACT:
        print(f"\n[+] Agregar {len(NEGATIVE_KEYWORDS_EXACT)} negativas EXACT a la campaña...")
        add_campaign_negatives(client, campaign_id, NEGATIVE_KEYWORDS_EXACT, "EXACT")

    print("\nHECHO.")


if __name__ == "__main__":
    main()
