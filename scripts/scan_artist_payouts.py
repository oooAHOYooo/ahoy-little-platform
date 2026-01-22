#!/usr/bin/env python3
"""
Scan all artists and identify who needs to be paid out.

This script:
1. Loads all artists from artists.json
2. Checks database for pending tips for each artist
3. Calculates total unpaid amounts
4. Shows which artists need payouts

Usage:
    python scripts/scan_artist_payouts.py
    python scripts/scan_artist_payouts.py --min-amount 10.00  # Only show artists with $10+ pending
"""
import os
import sys
import argparse
from decimal import Decimal
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_session
from models import Tip, ArtistPayout


def load_artists():
    """Load all artists from artists.json"""
    try:
        import json
        from pathlib import Path
        
        artists_file = Path(__file__).parent.parent / 'static' / 'data' / 'artists.json'
        if artists_file.exists():
            with open(artists_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('artists', [])
    except Exception as e:
        print(f"⚠️  Error loading artists: {e}")
    return []


def get_pending_tips_for_artist(artist_id: str, db_session):
    """Get all tips that haven't been included in a completed payout."""
    # Get all tips for this artist
    all_tips = db_session.query(Tip).filter(
        Tip.artist_id == str(artist_id)
    ).order_by(Tip.created_at).all()
    
    # Get all completed payouts and their related tip IDs
    completed_payouts = db_session.query(ArtistPayout).filter(
        ArtistPayout.artist_id == str(artist_id),
        ArtistPayout.status == "completed"
    ).all()
    
    # Collect all tip IDs that have been paid out
    paid_tip_ids = set()
    for payout in completed_payouts:
        if payout.related_tip_ids:
            paid_tip_ids.update(payout.related_tip_ids)
    
    # Filter out tips that have been paid
    pending_tips = [tip for tip in all_tips if tip.id not in paid_tip_ids]
    return pending_tips


def scan_all_artists(min_amount: Decimal = Decimal("0.01")):
    """Scan all artists and find pending payouts."""
    artists = load_artists()
    
    if not artists:
        print("❌ No artists found in artists.json")
        return
    
    print(f"🔍 Scanning {len(artists)} artists for pending payouts...\n")
    
    results = []
    
    with get_session() as db_session:
        for artist in artists:
            artist_id = artist.get('id') or artist.get('slug') or artist.get('name', '')
            artist_name = artist.get('name', 'Unknown')
            artist_slug = artist.get('slug', '')
            
            # Try multiple identifiers
            identifiers = [str(artist_id), artist_slug, artist_name]
            
            pending_tips = []
            for identifier in identifiers:
                if identifier:
                    tips = get_pending_tips_for_artist(identifier, db_session)
                    if tips:
                        pending_tips = tips
                        break
            
            if pending_tips:
                # Calculate total pending amount
                total_pending = sum(
                    Decimal(str(tip.artist_payout or tip.amount)) 
                    for tip in pending_tips
                )
                
                if total_pending >= min_amount:
                    results.append({
                        'artist_id': artist_id,
                        'artist_slug': artist_slug or artist_id,
                        'artist_name': artist_name,
                        'pending_tips': pending_tips,
                        'total_pending': total_pending,
                        'tip_count': len(pending_tips)
                    })
    
    # Sort by total pending (highest first)
    results.sort(key=lambda x: x['total_pending'], reverse=True)
    
    return results


def print_results(results):
    """Print scan results in a formatted way."""
    if not results:
        print("✅ No artists with pending payouts found!")
        print("\n   All tips have been paid out, or no tips exist yet.")
        return
    
    total_pending = sum(r['total_pending'] for r in results)
    total_tips = sum(r['tip_count'] for r in results)
    
    print(f"💰 Found {len(results)} artist(s) with pending payouts:\n")
    print(f"   Total Pending: ${total_pending:.2f}")
    print(f"   Total Tips: {total_tips}\n")
    print("=" * 80)
    
    for i, result in enumerate(results, 1):
        artist_name = result['artist_name']
        artist_slug = result['artist_slug']
        total = result['total_pending']
        tip_count = result['tip_count']
        
        print(f"\n{i}. {artist_name}")
        print(f"   ID/Slug: {artist_slug}")
        print(f"   Pending Amount: ${total:.2f}")
        print(f"   Number of Tips: {tip_count}")
        
        # Show recent tips
        recent_tips = result['pending_tips'][:5]  # Show first 5
        if recent_tips:
            print(f"   Recent Tips:")
            for tip in recent_tips:
                amount = Decimal(str(tip.artist_payout or tip.amount))
                date = tip.created_at.strftime('%Y-%m-%d') if tip.created_at else 'Unknown'
                print(f"      - ${amount:.2f} on {date}")
        
        if len(result['pending_tips']) > 5:
            print(f"      ... and {len(result['pending_tips']) - 5} more")
        
        # Show payout command
        print(f"\n   💸 To pay out:")
        print(f"      python scripts/send_artist_payout.py --artist-id \"{artist_slug}\" --auto")
        print(f"      # OR")
        print(f"      python scripts/send_artist_payout.py --artist-id \"{artist_slug}\" --amount {total:.2f}")
    
    print("\n" + "=" * 80)
    print(f"\n📋 Summary:")
    print(f"   Artists needing payouts: {len(results)}")
    print(f"   Total amount to pay: ${total_pending:.2f}")
    print(f"   Total tips pending: {total_tips}")


def main():
    parser = argparse.ArgumentParser(description="Scan artists for pending payouts")
    parser.add_argument("--min-amount", type=float, default=0.01, 
                       help="Minimum amount to show (default: 0.01)")
    
    args = parser.parse_args()
    
    results = scan_all_artists(min_amount=Decimal(str(args.min_amount)))
    print_results(results)


if __name__ == "__main__":
    main()
