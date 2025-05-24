import os
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from typing import Dict, List, Any, Optional

def setup_google_ads_client() -> Optional[GoogleAdsClient]:
    """
    Google Ads API istemcisini ayarlar.
    
    Returns:
        Optional[GoogleAdsClient]: Google Ads API istemcisi
    """
    try:
        credentials = {
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            "use_proto_plus": True,
        }
        
        return GoogleAdsClient.load_from_dict(credentials)
    except Exception as e:
        print(f"Google Ads API istemcisi ayarlama hatası: {e}")
        return None

def create_campaign(client: GoogleAdsClient, customer_id: str, campaign_name: str, budget: float) -> Optional[str]:
    """
    Yeni bir kampanya oluşturur.
    
    Args:
        client: Google Ads API istemcisi
        customer_id: Müşteri ID'si
        campaign_name: Kampanya adı
        budget: Kampanya bütçesi
        
    Returns:
        Optional[str]: Kampanya ID'si
    """
    try:
        campaign_service = client.get_service("CampaignService")
        campaign_budget_service = client.get_service("CampaignBudgetService")
        campaign_operation = client.get_type("CampaignOperation")
        
        # Kampanya bütçesi oluştur
        campaign_budget_operation = client.get_type("CampaignBudgetOperation")
        campaign_budget = campaign_budget_operation.create
        campaign_budget.name = f"{campaign_name} Budget"
        campaign_budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
        campaign_budget.amount_micros = int(budget * 1000000)  # Mikro birimlere dönüştür
        
        # Kampanya bütçesini kaydet
        campaign_budget_response = campaign_budget_service.mutate_campaign_budgets(
            customer_id=customer_id,
            operations=[campaign_budget_operation]
        )
        campaign_budget_resource_name = campaign_budget_response.results[0].resource_name
        
        # Kampanya oluştur
        campaign = campaign_operation.create
        campaign.name = campaign_name
        campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
        campaign.status = client.enums.CampaignStatusEnum.ENABLED
        campaign.campaign_budget = campaign_budget_resource_name
        
        # Kampanyayı kaydet
        campaign_response = campaign_service.mutate_campaigns(
            customer_id=customer_id,
            operations=[campaign_operation]
        )
        
        return campaign_response.results[0].resource_name
    except GoogleAdsException as e:
        print(f"Google Ads API hatası: {e}")
        return None

def create_ad_group(client: GoogleAdsClient, customer_id: str, campaign_id: str, ad_group_name: str) -> Optional[str]:
    """
    Yeni bir reklam grubu oluşturur.
    
    Args:
        client: Google Ads API istemcisi
        customer_id: Müşteri ID'si
        campaign_id: Kampanya ID'si
        ad_group_name: Reklam grubu adı
        
    Returns:
        Optional[str]: Reklam grubu ID'si
    """
    try:
        ad_group_service = client.get_service("AdGroupService")
        ad_group_operation = client.get_type("AdGroupOperation")
        
        # Reklam grubu oluştur
        ad_group = ad_group_operation.create
        ad_group.name = ad_group_name
        ad_group.campaign = campaign_id
        ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
        ad_group.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
        
        # Reklam grubunu kaydet
        ad_group_response = ad_group_service.mutate_ad_groups(
            customer_id=customer_id,
            operations=[ad_group_operation]
        )
        
        return ad_group_response.results[0].resource_name
    except GoogleAdsException as e:
        print(f"Google Ads API hatası: {e}")
        return None

def create_ad(client: GoogleAdsClient, customer_id: str, ad_group_id: str, headline: str, description: str, final_url: str) -> Optional[str]:
    """
    Yeni bir reklam oluşturur.
    
    Args:
        client: Google Ads API istemcisi
        customer_id: Müşteri ID'si
        ad_group_id: Reklam grubu ID'si
        headline: Reklam başlığı
        description: Reklam açıklaması
        final_url: Reklam URL'si
        
    Returns:
        Optional[str]: Reklam ID'si
    """
    try:
        ad_service = client.get_service("AdService")
        ad_operation = client.get_type("AdOperation")
        
        # Reklam oluştur
        ad = ad_operation.create
        ad.ad_group = ad_group_id
        ad.status = client.enums.AdStatusEnum.ENABLED
        
        # Reklam içeriği
        responsive_search_ad = ad.responsive_search_ad
        responsive_search_ad.headlines.append(client.get_type("AdTextAsset").create(
            text=headline
        ))
        responsive_search_ad.descriptions.append(client.get_type("AdTextAsset").create(
            text=description
        ))
        
        # Reklam URL'si
        ad.final_urls.append(final_url)
        
        # Reklamı kaydet
        ad_response = ad_service.mutate_ads(
            customer_id=customer_id,
            operations=[ad_operation]
        )
        
        return ad_response.results[0].resource_name
    except GoogleAdsException as e:
        print(f"Google Ads API hatası: {e}")
        return None

def get_campaign_performance(client: GoogleAdsClient, customer_id: str, campaign_id: str) -> Dict[str, Any]:
    """
    Kampanya performansını getirir.
    
    Args:
        client: Google Ads API istemcisi
        customer_id: Müşteri ID'si
        campaign_id: Kampanya ID'si
        
    Returns:
        Dict[str, Any]: Kampanya performans verileri
    """
    try:
        ga_service = client.get_service("GoogleAdsService")
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions
            FROM campaign
            WHERE campaign.id = {campaign_id}
        """
        
        response = ga_service.search(
            customer_id=customer_id,
            query=query
        )
        
        for row in response:
            return {
                "campaign_id": row.campaign.id,
                "campaign_name": row.campaign.name,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "cost": row.metrics.cost_micros / 1000000,  # Mikro birimlerden normal birimlere dönüştür
                "conversions": row.metrics.conversions
            }
        
        return {}
    except GoogleAdsException as e:
        print(f"Google Ads API hatası: {e}")
        return {} 