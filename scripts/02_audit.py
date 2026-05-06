"""
Auditoría completa de la cuenta Google Ads configurada en .env.
No modifica nada. Solo lee y reporta.

Imprime: datos de la cuenta, usuarios con acceso, campañas con métricas
de los últimos 30 días, ad groups + keywords con performance, y todas
las conversion actions con su estado.
"""
import os
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient

load_dotenv()

CUSTOMER_ID = os.getenv("GOOGLE_ADS_CUSTOMER_ID")


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


def section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def audit_account(client):
    section("CUENTA")
    svc = client.get_service("GoogleAdsService")
    q = """
        SELECT customer.id, customer.descriptive_name, customer.currency_code,
               customer.time_zone, customer.status
        FROM customer
    """
    for r in svc.search(customer_id=CUSTOMER_ID, query=q):
        c = r.customer
        print(f"ID: {c.id}")
        print(f"Nombre: {c.descriptive_name}")
        print(f"Moneda: {c.currency_code}")
        print(f"TZ: {c.time_zone}")
        print(f"Estado: {c.status.name}")


def audit_campaigns(client):
    section("CAMPAÑAS (todas, últimos 30 días)")
    svc = client.get_service("GoogleAdsService")
    q = """
        SELECT campaign.id, campaign.name, campaign.status,
               campaign.advertising_channel_type,
               campaign.bidding_strategy_type,
               campaign.maximize_conversions.target_cpa_micros,
               campaign.network_settings.target_google_search,
               campaign.network_settings.target_search_network,
               campaign.network_settings.target_content_network,
               campaign.network_settings.target_partner_search_network,
               campaign_budget.amount_micros,
               metrics.cost_micros, metrics.clicks, metrics.impressions,
               metrics.conversions, metrics.conversions_value
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
        ORDER BY metrics.cost_micros DESC
    """
    for r in svc.search(customer_id=CUSTOMER_ID, query=q):
        c = r.campaign
        m = r.metrics
        b = r.campaign_budget
        print(f"\n• {c.name}")
        print(f"   ID: {c.id} | Estado: {c.status.name} | Tipo: {c.advertising_channel_type.name}")
        print(f"   Strategy: {c.bidding_strategy_type.name}")
        if c.bidding_strategy_type.name == "MAXIMIZE_CONVERSIONS":
            tcpa = c.maximize_conversions.target_cpa_micros / 1_000_000 if c.maximize_conversions.target_cpa_micros else 0
            print(f"   tCPA: {tcpa if tcpa > 0 else 'SIN OBJETIVO'}")
        print(f"   Budget diario: {b.amount_micros / 1_000_000:,.0f}")
        ns = c.network_settings
        print(f"   Redes: google_search={ns.target_google_search} search_partners={ns.target_search_network} display={ns.target_content_network} partner_sites={ns.target_partner_search_network}")
        print(f"   30d → costo={m.cost_micros / 1_000_000:,.0f} | clicks={m.clicks} | imp={m.impressions} | conv={m.conversions:.0f}")


def audit_ad_groups_keywords(client):
    section("AD GROUPS + KEYWORDS (con métricas 30d)")
    svc = client.get_service("GoogleAdsService")
    q = """
        SELECT campaign.name, ad_group.name, ad_group_criterion.keyword.text,
               ad_group_criterion.keyword.match_type, ad_group_criterion.status,
               metrics.clicks, metrics.impressions, metrics.cost_micros, metrics.conversions
        FROM keyword_view
        WHERE segments.date DURING LAST_30_DAYS
        ORDER BY campaign.name, ad_group.name, metrics.cost_micros DESC
    """
    last_group = None
    for r in svc.search(customer_id=CUSTOMER_ID, query=q):
        group_key = (r.campaign.name, r.ad_group.name)
        if group_key != last_group:
            print(f"\n[{r.campaign.name}] → {r.ad_group.name}")
            last_group = group_key
        kw = r.ad_group_criterion.keyword
        m = r.metrics
        print(f"   {kw.match_type.name:8s} | {r.ad_group_criterion.status.name:8s} | {kw.text:50s} | clk={m.clicks:4d} imp={m.impressions:6d} cost={m.cost_micros / 1_000_000:>8,.0f} conv={m.conversions:.1f}")


def audit_conversions(client):
    section("ACCIONES DE CONVERSIÓN")
    svc = client.get_service("GoogleAdsService")
    q = """
        SELECT conversion_action.id, conversion_action.name, conversion_action.status,
               conversion_action.category, conversion_action.type, conversion_action.primary_for_goal,
               conversion_action.counting_type, conversion_action.click_through_lookback_window_days,
               metrics.all_conversions
        FROM conversion_action
        ORDER BY conversion_action.status, conversion_action.name
    """
    for r in svc.search(customer_id=CUSTOMER_ID, query=q):
        ca = r.conversion_action
        primary = "PRIMARY" if ca.primary_for_goal else "secondary"
        print(f"\n• {ca.name}")
        print(f"   Estado: {ca.status.name} | Tipo: {ca.type_.name} | Categoría: {ca.category.name}")
        print(f"   {primary} | Counting: {ca.counting_type.name} | Lookback clk: {ca.click_through_lookback_window_days}d")
        print(f"   Total conv: {r.metrics.all_conversions:.0f}")


def audit_users(client):
    section("USUARIOS CON ACCESO")
    svc = client.get_service("GoogleAdsService")
    q = """
        SELECT customer_user_access.user_id, customer_user_access.email_address,
               customer_user_access.access_role, customer_user_access.access_creation_date_time
        FROM customer_user_access
    """
    try:
        for r in svc.search(customer_id=CUSTOMER_ID, query=q):
            u = r.customer_user_access
            print(f"  • {u.email_address} | rol: {u.access_role.name} | desde: {u.access_creation_date_time}")
    except Exception as e:
        print(f"  No accesible: {e}")


def main():
    client = build_client()
    audit_account(client)
    audit_users(client)
    audit_campaigns(client)
    audit_ad_groups_keywords(client)
    audit_conversions(client)
    print()
    print("=" * 70)
    print("FIN AUDITORÍA")
    print("=" * 70)


if __name__ == "__main__":
    main()
