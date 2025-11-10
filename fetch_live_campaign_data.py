#!/usr/bin/env python3
"""
Fetch live campaign data from Google Ads API for Daisy MD Care
Provides real-time metrics, ad sets, ads, and campaign status
"""

from datetime import datetime, timedelta
from google.ads.googleads.client import GoogleAdsClient
import json

# Configuration
CUSTOMER_ID = "9357633546"  # Poppy Marketing account
CAMPAIGN_ID = "23159502389"

def initialize_client():
    """Initialize Google Ads API client"""
    try:
        client = GoogleAdsClient.load_from_storage()
        return client
    except Exception as e:
        print(f"Error initializing Google Ads client: {e}")
        return None

def get_campaign_info(client):
    """Get campaign details"""
    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.start_date,
            campaign.end_date
        FROM campaign
        WHERE campaign.id = {CAMPAIGN_ID}
    """

    try:
        ga_service = client.get_service("GoogleAdsService")
        results = ga_service.search_stream(customer_id=CUSTOMER_ID, query=query)

        campaign_info = {}
        for batch in results:
            for row in batch.results:
                campaign = row.campaign
                campaign_info = {
                    'id': campaign.id,
                    'name': campaign.name,
                    'status': campaign.status.name,
                    'start_date': campaign.start_date,
                    'end_date': campaign.end_date
                }
        return campaign_info
    except Exception as e:
        print(f"Error fetching campaign info: {e}")
        return {}

def get_campaign_performance(client, start_date, end_date):
    """Get campaign performance metrics for all resources"""
    query = f"""
        SELECT
            segments.date,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.cost_micros,
            metrics.ctr,
            metrics.average_cpc
        FROM campaign
        WHERE campaign.id = {CAMPAIGN_ID}
        AND segments.date BETWEEN '{start_date}' AND '{end_date}'
    """

    try:
        ga_service = client.get_service("GoogleAdsService")
        results = ga_service.search_stream(customer_id=CUSTOMER_ID, query=query)

        totals = {
            'impressions': 0,
            'clicks': 0,
            'conversions': 0,
            'cost_micros': 0,
            'ctr': 0,
            'avg_cpc': 0,
            'days': 0
        }

        for batch in results:
            for row in batch.results:
                metrics = row.metrics
                totals['impressions'] += metrics.impressions
                totals['clicks'] += metrics.clicks
                totals['conversions'] += int(metrics.conversions)
                totals['cost_micros'] += metrics.cost_micros
                totals['days'] += 1
                if metrics.ctr:
                    totals['ctr'] = metrics.ctr
                if metrics.average_cpc:
                    totals['avg_cpc'] = metrics.average_cpc

        return totals
    except Exception as e:
        print(f"Error fetching campaign performance: {e}")
        return {}

def get_ad_groups_performance(client):
    """Get ad group performance"""
    query = f"""
        SELECT
            ad_group.id,
            ad_group.name,
            ad_group.status,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.cost_micros,
            metrics.ctr
        FROM ad_group
        WHERE campaign.id = {CAMPAIGN_ID}
    """

    try:
        ga_service = client.get_service("GoogleAdsService")
        results = ga_service.search_stream(customer_id=CUSTOMER_ID, query=query)

        ad_groups = []
        for batch in results:
            for row in batch.results:
                ag = row.ad_group
                metrics = row.metrics
                ad_groups.append({
                    'id': ag.id,
                    'name': ag.name,
                    'status': ag.status.name,
                    'impressions': metrics.impressions,
                    'clicks': metrics.clicks,
                    'conversions': int(metrics.conversions),
                    'cost_micros': metrics.cost_micros,
                    'ctr': f"{metrics.ctr * 100:.2f}%" if metrics.ctr else "0%"
                })

        return ad_groups
    except Exception as e:
        print(f"Error fetching ad groups: {e}")
        return []

def get_ads_performance(client):
    """Get ad performance"""
    query = f"""
        SELECT
            ad.id,
            ad.name,
            ad.type,
            ad_group.id,
            ad_group.name,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.cost_micros,
            metrics.ctr
        FROM ad
        WHERE campaign.id = {CAMPAIGN_ID}
    """

    try:
        ga_service = client.get_service("GoogleAdsService")
        results = ga_service.search_stream(customer_id=CUSTOMER_ID, query=query)

        ads = []
        for batch in results:
            for row in batch.results:
                ad = row.ad
                ag = row.ad_group
                metrics = row.metrics
                ads.append({
                    'ad_id': ad.id,
                    'ad_name': ad.name,
                    'type': ad.type.name,
                    'ad_group_id': ag.id,
                    'ad_group_name': ag.name,
                    'impressions': metrics.impressions,
                    'clicks': metrics.clicks,
                    'conversions': int(metrics.conversions),
                    'cost_micros': metrics.cost_micros,
                    'ctr': f"{metrics.ctr * 100:.2f}%" if metrics.ctr else "0%"
                })

        return ads
    except Exception as e:
        print(f"Error fetching ads: {e}")
        return []

def main():
    """Main function to fetch and display live data"""
    print("=" * 80)
    print("DAISY MD CARE - LIVE CAMPAIGN DATA")
    print("=" * 80)
    print(f"Fetched at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    client = initialize_client()
    if not client:
        print("Failed to initialize Google Ads client")
        return

    # Get campaign info
    print("CAMPAIGN INFORMATION")
    print("-" * 80)
    campaign_info = get_campaign_info(client)
    if campaign_info:
        print(f"Campaign ID: {campaign_info.get('id')}")
        print(f"Campaign Name: {campaign_info.get('name')}")
        print(f"Status: {campaign_info.get('status')}")
        print(f"Start Date: {campaign_info.get('start_date')}")
        print(f"End Date: {campaign_info.get('end_date')}")

        # Calculate days active
        if campaign_info.get('start_date'):
            from datetime import datetime as dt
            start = dt.strptime(campaign_info.get('start_date'), '%Y-%m-%d')
            today = dt.now()
            days_active = (today - start).days
            print(f"Days Active: {days_active}")
        print()
    else:
        print("No campaign info found\n")

    # Get performance metrics (last 7 days)
    print("CAMPAIGN PERFORMANCE (Last 7 Days)")
    print("-" * 80)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    print(f"Period: {start_date} to {end_date}\n")

    metrics = get_campaign_performance(client, start_date, end_date)
    if metrics and metrics.get('impressions', 0) > 0:
        print(f"Impressions: {metrics.get('impressions'):,}")
        print(f"Clicks: {metrics.get('clicks'):,}")
        print(f"Conversions: {metrics.get('conversions')}")
        cost = metrics.get('cost_micros', 0) / 1_000_000
        print(f"Total Cost: ${cost:.2f}")
        ctr = metrics.get('ctr', 0) * 100
        print(f"CTR: {ctr:.2f}%")
        avg_cpc = metrics.get('avg_cpc', 0) / 1_000_000
        if avg_cpc > 0:
            print(f"Avg CPC: ${avg_cpc:.2f}")
        if metrics.get('clicks') > 0:
            cpl = cost / metrics.get('clicks')
            print(f"Cost Per Click: ${cpl:.2f}")
        print()
    else:
        print("No performance data available\n")

    # Get ad groups
    print("AD GROUPS / AD SETS")
    print("-" * 80)
    ad_groups = get_ad_groups_performance(client)
    if ad_groups:
        print(f"Total Ad Groups: {len(ad_groups)}\n")
        for i, ag in enumerate(ad_groups, 1):
            print(f"{i}. {ag['name']}")
            print(f"   Status: {ag['status']}")
            print(f"   Impressions: {ag['impressions']:,} | Clicks: {ag['clicks']} | CTR: {ag['ctr']}")
            cost = ag['cost_micros'] / 1_000_000
            print(f"   Cost: ${cost:.2f} | Conversions: {ag['conversions']}")
            print()
    else:
        print("No ad groups found\n")

    # Get ads
    print("ADS")
    print("-" * 80)
    ads = get_ads_performance(client)
    if ads:
        print(f"Total Ads: {len(ads)}\n")
        current_ad_group = None
        for ad in ads:
            if ad['ad_group_name'] != current_ad_group:
                current_ad_group = ad['ad_group_name']
                print(f"\n📌 Ad Group: {current_ad_group}")
                print("-" * 76)

            print(f"  • {ad['ad_name']}")
            print(f"    Type: {ad['type']} | Impressions: {ad['impressions']:,} | Clicks: {ad['clicks']} | CTR: {ad['ctr']}")
            cost = ad['cost_micros'] / 1_000_000
            print(f"    Cost: ${cost:.2f} | Conversions: {ad['conversions']}")
    else:
        print("No ads found\n")

    print("\n" + "=" * 80)

    # Save to JSON for report use
    live_data = {
        'timestamp': datetime.now().isoformat(),
        'campaign': campaign_info,
        'metrics': metrics,
        'ad_groups': ad_groups,
        'ads': ads,
        'fetch_start_date': start_date,
        'fetch_end_date': end_date,
        'total_ads': len(ads),
        'total_ad_groups': len(ad_groups)
    }

    with open('/tmp/daisy-google-ads/live_campaign_data.json', 'w') as f:
        json.dump(live_data, f, indent=2)

    print("\n✅ Live data saved to live_campaign_data.json")
    print(f"Total Ads Found: {len(ads)}")
    print(f"Total Ad Groups: {len(ad_groups)}")

if __name__ == "__main__":
    main()
