#!/usr/bin/env python3
"""
Export accounting data for tax-ready reports.

Generates CSV/Excel files with:
- Revenue (tips, purchases, wallet funding)
- Expenses (artist payouts, Stripe fees)
- Artist 1099-NEC data
- Platform revenue

Usage:
    # Revenue report for 2024
    python scripts/export_accounting.py --type revenue --year 2024 --format csv

    # Expense report
    python scripts/export_accounting.py --type expenses --year 2024 --format csv

    # Artist 1099-NEC report
    python scripts/export_accounting.py --type artist-1099 --year 2024 --format csv

    # Platform revenue
    python scripts/export_accounting.py --type platform-revenue --year 2024 --format csv

    # All reports at once
    python scripts/export_accounting.py --type all --year 2024 --format csv
"""
import os
import sys
import argparse
import csv
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_session
from models import Tip, ArtistPayout, Purchase, WalletTransaction, User


def get_artist_name(artist_id: str) -> str:
    """Get artist name from artists.json."""
    try:
        from app import load_json_data
        artists_data = load_json_data('artists.json', {'artists': []})
        for artist in artists_data.get('artists', []):
            if (str(artist.get('id', '')) == str(artist_id) or
                artist.get('slug', '').lower() == str(artist_id).lower() or
                artist.get('name', '').lower() == str(artist_id).lower()):
                return artist.get('name', artist_id)
    except Exception:
        pass
    return artist_id


def export_revenue(year: int, output_file: Optional[str] = None) -> str:
    """Export all revenue (tips, purchases, wallet funding) for a year."""
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)
    
    with get_session() as db_session:
        rows = []
        
        # Tips/Boosts
        tips = db_session.query(Tip).filter(
            Tip.created_at >= start_date,
            Tip.created_at < end_date
        ).order_by(Tip.created_at).all()
        
        for tip in tips:
            rows.append({
                'Date': tip.created_at.strftime('%Y-%m-%d'),
                'Type': 'Boost/Tip',
                'Description': f"Boost to {get_artist_name(tip.artist_id)}",
                'Gross Revenue': float(tip.total_paid or tip.amount),
                'Stripe Fee': float(tip.stripe_fee or 0),
                'Platform Revenue': float(tip.platform_revenue or 0),
                'Artist Payout': float(tip.artist_payout or tip.amount),
                'Stripe Session ID': tip.stripe_checkout_session_id or '',
                'Payment Intent ID': tip.stripe_payment_intent_id or '',
                'User ID': tip.user_id or '',
                'Artist ID': tip.artist_id,
            })
        
        # Merch Purchases
        purchases = db_session.query(Purchase).filter(
            Purchase.created_at >= start_date,
            Purchase.created_at < end_date,
            Purchase.status == 'paid'
        ).order_by(Purchase.created_at).all()
        
        for purchase in purchases:
            rows.append({
                'Date': purchase.created_at.strftime('%Y-%m-%d'),
                'Type': 'Merch Purchase',
                'Description': f"Merch purchase #{purchase.id}",
                'Gross Revenue': float(purchase.total),
                'Stripe Fee': 0,  # Fees already included in tip records if applicable
                'Platform Revenue': float(purchase.total),  # Assuming 100% of merch is platform revenue
                'Artist Payout': 0,
                'Stripe Session ID': purchase.stripe_id or '',
                'Payment Intent ID': '',
                'User ID': purchase.user_id or '',
                'Artist ID': '',
            })
        
        # Wallet Funding
        wallet_funding = db_session.query(WalletTransaction).filter(
            WalletTransaction.created_at >= start_date,
            WalletTransaction.created_at < end_date,
            WalletTransaction.type == 'fund'
        ).order_by(WalletTransaction.created_at).all()
        
        for tx in wallet_funding:
            rows.append({
                'Date': tx.created_at.strftime('%Y-%m-%d'),
                'Type': 'Wallet Funding',
                'Description': f"Wallet funding for user {tx.user_id}",
                'Gross Revenue': float(tx.amount),
                'Stripe Fee': 0,  # Fees paid at funding time
                'Platform Revenue': 0,  # Not revenue until spent
                'Artist Payout': 0,
                'Stripe Session ID': tx.reference_id if tx.reference_type == 'stripe_checkout' else '',
                'Payment Intent ID': '',
                'User ID': tx.user_id,
                'Artist ID': '',
            })
        
        # Sort by date
        rows.sort(key=lambda x: x['Date'])
        
        # Write to CSV
        if not output_file:
            output_file = f"revenue_{year}.csv"
        
        with open(output_file, 'w', newline='') as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
                
                # Add summary
                total_revenue = sum(r['Gross Revenue'] for r in rows)
                total_fees = sum(r['Stripe Fee'] for r in rows)
                total_platform = sum(r['Platform Revenue'] for r in rows)
                
                writer.writerow({})
                writer.writerow({
                    'Date': 'TOTAL',
                    'Type': '',
                    'Description': '',
                    'Gross Revenue': total_revenue,
                    'Stripe Fee': total_fees,
                    'Platform Revenue': total_platform,
                    'Artist Payout': 0,
                    'Stripe Session ID': '',
                    'Payment Intent ID': '',
                    'User ID': '',
                    'Artist ID': '',
                })
        
        print(f"✅ Exported {len(rows)} revenue transactions to {output_file}")
        if rows:
            total = sum(r['Gross Revenue'] for r in rows)
            print(f"   Total Revenue: ${total:,.2f}")
        
        return output_file


def export_expenses(year: int, output_file: Optional[str] = None) -> str:
    """Export all expenses (artist payouts, Stripe fees) for a year."""
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)
    
    with get_session() as db_session:
        rows = []
        
        # Artist Payouts
        payouts = db_session.query(ArtistPayout).filter(
            ArtistPayout.completed_at >= start_date,
            ArtistPayout.completed_at < end_date,
            ArtistPayout.status == 'completed'
        ).order_by(ArtistPayout.completed_at).all()
        
        for payout in payouts:
            artist_name = get_artist_name(payout.artist_id)
            rows.append({
                'Date': payout.completed_at.strftime('%Y-%m-%d') if payout.completed_at else '',
                'Type': 'Artist Payout',
                'Description': f"Payout to {artist_name}",
                'Amount': float(payout.amount),
                'Payment Method': payout.payment_method or 'manual',
                'Stripe Transfer ID': payout.stripe_transfer_id or '',
                'Payment Reference': payout.payment_reference or '',
                'Artist ID': payout.artist_id,
                'Payout ID': payout.id,
            })
        
        # Stripe Fees (from tips)
        tips = db_session.query(Tip).filter(
            Tip.created_at >= start_date,
            Tip.created_at < end_date
        ).all()
        
        total_stripe_fees = sum(float(tip.stripe_fee or 0) for tip in tips)
        if total_stripe_fees > 0:
            rows.append({
                'Date': f"{year} Summary",
                'Type': 'Stripe Processing Fees',
                'Description': f"Total Stripe fees for {year}",
                'Amount': total_stripe_fees,
                'Payment Method': 'stripe_fee',
                'Stripe Transfer ID': '',
                'Payment Reference': f"Sum of all transaction fees",
                'Artist ID': '',
                'Payout ID': '',
            })
        
        # Write to CSV
        if not output_file:
            output_file = f"expenses_{year}.csv"
        
        with open(output_file, 'w', newline='') as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
                
                # Add summary
                total_expenses = sum(r['Amount'] for r in rows)
                writer.writerow({})
                writer.writerow({
                    'Date': 'TOTAL',
                    'Type': '',
                    'Description': '',
                    'Amount': total_expenses,
                    'Payment Method': '',
                    'Stripe Transfer ID': '',
                    'Payment Reference': '',
                    'Artist ID': '',
                    'Payout ID': '',
                })
        
        print(f"✅ Exported {len(rows)} expense transactions to {output_file}")
        if rows:
            total = sum(r['Amount'] for r in rows)
            print(f"   Total Expenses: ${total:,.2f}")
        
        return output_file


def export_artist_1099(year: int, output_file: Optional[str] = None) -> str:
    """Export artist 1099-NEC data (total paid to each artist)."""
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)
    
    with get_session() as db_session:
        # Get all completed payouts for the year
        payouts = db_session.query(ArtistPayout).filter(
            ArtistPayout.completed_at >= start_date,
            ArtistPayout.completed_at < end_date,
            ArtistPayout.status == 'completed'
        ).all()
        
        # Group by artist
        artist_totals = defaultdict(lambda: {'amount': Decimal('0'), 'payouts': []})
        for payout in payouts:
            artist_totals[payout.artist_id]['amount'] += payout.amount
            artist_totals[payout.artist_id]['payouts'].append(payout)
        
        rows = []
        for artist_id, data in sorted(artist_totals.items()):
            artist_name = get_artist_name(artist_id)
            rows.append({
                'Artist ID': artist_id,
                'Artist Name': artist_name,
                'Total Paid': float(data['amount']),
                'Number of Payouts': len(data['payouts']),
                'Requires 1099-NEC': 'Yes' if float(data['amount']) >= 600 else 'No',
            })
        
        # Write to CSV
        if not output_file:
            output_file = f"artist_1099_{year}.csv"
        
        with open(output_file, 'w', newline='') as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
                
                # Add summary
                total_paid = sum(r['Total Paid'] for r in rows)
                requires_1099 = sum(1 for r in rows if r['Requires 1099-NEC'] == 'Yes')
                writer.writerow({})
                writer.writerow({
                    'Artist ID': 'TOTAL',
                    'Artist Name': '',
                    'Total Paid': total_paid,
                    'Number of Payouts': sum(r['Number of Payouts'] for r in rows),
                    'Requires 1099-NEC': f"{requires_1099} artists require 1099-NEC",
                })
        
        print(f"✅ Exported 1099 data for {len(rows)} artists to {output_file}")
        if rows:
            total = sum(r['Total Paid'] for r in rows)
            print(f"   Total Paid to Artists: ${total:,.2f}")
            requires_1099 = sum(1 for r in rows if r['Requires 1099-NEC'] == 'Yes')
            print(f"   Artists Requiring 1099-NEC: {requires_1099}")
        
        return output_file


def export_platform_revenue(year: int, output_file: Optional[str] = None) -> str:
    """Export platform revenue (your net income)."""
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)
    
    with get_session() as db_session:
        rows = []
        
        # Platform revenue from tips
        tips = db_session.query(Tip).filter(
            Tip.created_at >= start_date,
            Tip.created_at < end_date
        ).all()
        
        total_platform_revenue = Decimal('0')
        for tip in tips:
            platform_rev = tip.platform_revenue or Decimal('0')
            total_platform_revenue += platform_rev
            
            rows.append({
                'Date': tip.created_at.strftime('%Y-%m-%d'),
                'Type': 'Platform Fee',
                'Description': f"Platform fee from boost to {get_artist_name(tip.artist_id)}",
                'Amount': float(platform_rev),
                'Stripe Session ID': tip.stripe_checkout_session_id or '',
            })
        
        # Merch revenue (assuming 100% is platform revenue)
        purchases = db_session.query(Purchase).filter(
            Purchase.created_at >= start_date,
            Purchase.created_at < end_date,
            Purchase.status == 'paid'
        ).all()
        
        for purchase in purchases:
            total_platform_revenue += purchase.total
            rows.append({
                'Date': purchase.created_at.strftime('%Y-%m-%d'),
                'Type': 'Merch Revenue',
                'Description': f"Merch purchase #{purchase.id}",
                'Amount': float(purchase.total),
                'Stripe Session ID': purchase.stripe_id or '',
            })
        
        # Write to CSV
        if not output_file:
            output_file = f"platform_revenue_{year}.csv"
        
        with open(output_file, 'w', newline='') as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
                
                # Add summary
                writer.writerow({})
                writer.writerow({
                    'Date': 'TOTAL',
                    'Type': '',
                    'Description': '',
                    'Amount': float(total_platform_revenue),
                    'Stripe Session ID': '',
                })
        
        print(f"✅ Exported platform revenue to {output_file}")
        print(f"   Total Platform Revenue: ${float(total_platform_revenue):,.2f}")
        
        return output_file


def main():
    parser = argparse.ArgumentParser(description="Export accounting data for tax-ready reports")
    parser.add_argument("--type", choices=['revenue', 'expenses', 'artist-1099', 'platform-revenue', 'all'],
                       required=True, help="Type of report to generate")
    parser.add_argument("--year", type=int, default=datetime.now().year, help="Year to export (default: current year)")
    parser.add_argument("--format", choices=['csv', 'excel'], default='csv', help="Output format (default: csv)")
    parser.add_argument("--output-dir", default='.', help="Output directory (default: current directory)")
    
    args = parser.parse_args()
    
    if args.type == 'all':
        print(f"📊 Generating all accounting reports for {args.year}...\n")
        export_revenue(args.year, os.path.join(args.output_dir, f"revenue_{args.year}.csv"))
        print()
        export_expenses(args.year, os.path.join(args.output_dir, f"expenses_{args.year}.csv"))
        print()
        export_artist_1099(args.year, os.path.join(args.output_dir, f"artist_1099_{args.year}.csv"))
        print()
        export_platform_revenue(args.year, os.path.join(args.output_dir, f"platform_revenue_{args.year}.csv"))
        print("\n✅ All reports generated!")
    elif args.type == 'revenue':
        export_revenue(args.year)
    elif args.type == 'expenses':
        export_expenses(args.year)
    elif args.type == 'artist-1099':
        export_artist_1099(args.year)
    elif args.type == 'platform-revenue':
        export_platform_revenue(args.year)


if __name__ == "__main__":
    main()
