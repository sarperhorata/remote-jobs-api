from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from ..database import get_db
from ..models.user import User
from ..utils.auth import get_current_active_user
from ..utils.ads import (
    setup_google_ads_client,
    create_campaign,
    create_ad_group,
    create_ad,
    get_campaign_performance
)

router = APIRouter()

@router.post("/campaigns")
async def create_new_campaign(
    campaign_name: str,
    budget: float,
    customer_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Yeni bir kampanya oluşturur.
    
    Args:
        campaign_name: Kampanya adı
        budget: Kampanya bütçesi
        customer_id: Müşteri ID'si
        current_user: Mevcut kullanıcı
        db: Veritabanı oturumu
        
    Returns:
        Dict[str, str]: Kampanya ID'si
    """
    client = setup_google_ads_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google Ads API istemcisi ayarlanamadı"
        )
    
    campaign_id = create_campaign(client, customer_id, campaign_name, budget)
    if not campaign_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kampanya oluşturulamadı"
        )
    
    return {"campaign_id": campaign_id}

@router.post("/ad-groups")
async def create_new_ad_group(
    campaign_id: str,
    ad_group_name: str,
    customer_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Yeni bir reklam grubu oluşturur.
    
    Args:
        campaign_id: Kampanya ID'si
        ad_group_name: Reklam grubu adı
        customer_id: Müşteri ID'si
        current_user: Mevcut kullanıcı
        db: Veritabanı oturumu
        
    Returns:
        Dict[str, str]: Reklam grubu ID'si
    """
    client = setup_google_ads_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google Ads API istemcisi ayarlanamadı"
        )
    
    ad_group_id = create_ad_group(client, customer_id, campaign_id, ad_group_name)
    if not ad_group_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reklam grubu oluşturulamadı"
        )
    
    return {"ad_group_id": ad_group_id}

@router.post("/ads")
async def create_new_ad(
    ad_group_id: str,
    headline: str,
    description: str,
    final_url: str,
    customer_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Yeni bir reklam oluşturur.
    
    Args:
        ad_group_id: Reklam grubu ID'si
        headline: Reklam başlığı
        description: Reklam açıklaması
        final_url: Reklam URL'si
        customer_id: Müşteri ID'si
        current_user: Mevcut kullanıcı
        db: Veritabanı oturumu
        
    Returns:
        Dict[str, str]: Reklam ID'si
    """
    client = setup_google_ads_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google Ads API istemcisi ayarlanamadı"
        )
    
    ad_id = create_ad(client, customer_id, ad_group_id, headline, description, final_url)
    if not ad_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reklam oluşturulamadı"
        )
    
    return {"ad_id": ad_id}

@router.get("/campaigns/{campaign_id}/performance")
async def get_campaign_stats(
    campaign_id: str,
    customer_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Kampanya performansını getirir.
    
    Args:
        campaign_id: Kampanya ID'si
        customer_id: Müşteri ID'si
        current_user: Mevcut kullanıcı
        db: Veritabanı oturumu
        
    Returns:
        Dict[str, Any]: Kampanya performans verileri
    """
    client = setup_google_ads_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google Ads API istemcisi ayarlanamadı"
        )
    
    performance_data = get_campaign_performance(client, customer_id, campaign_id)
    if not performance_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kampanya performans verileri bulunamadı"
        )
    
    return performance_data 