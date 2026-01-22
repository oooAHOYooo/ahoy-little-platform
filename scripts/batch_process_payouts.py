#!/usr/bin/env python3
"""
Batch process all pending payouts via Stripe Connect.

This script allows you to:
1. Review collected payouts
2. Automatically process all pending payouts that have Stripe Connect configured
3. Create pending records for artists without Stripe Connect

Usage:
    # Preview what would be processed
    python scripts/batch_process_payouts.py --dry-run

    # Process all pending payouts with Stripe Connect
    python scripts/batch_process_payouts.py --auto-process

    # Process only payouts above minimum amount
    python scripts/batch_process_payouts.py --auto-process --min-amount 10.00
"""
import os
import sys
import argparse
from decimal import Decimal
from typing import List, Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_session
from models import ArtistPayout, Tip
from scripts.send_artist_payout import (
    _configure_stripe,
    _get_artist_name,
    _get_artist_stripe_account,
    send_stripe_transfer,
    get_pending_tips_for_artist
)
from datetime import datetime


def process_pending_payouts(
    dry_run: bool = False,
    auto_process: bool = False,
    min_amount: Optional[Decimal] = None
) -> Dict[str, Any]:
    """
    Process all pending payouts.
    
    Returns summary of processed, failed, and manual payouts.
    """
    _configure_stripe()
    stripe_configured = bool(os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_SECRET_KEY_TEST"))
    
    with get_session() as db_session:
        # Get all pending payouts
        pending_payouts = db_session.query(ArtistPayout).filter(
            ArtistPayout.status == "pending"
        ).order_by(ArtistPayout.created_at).all()
        
        if not pending_payouts:
            print("✅ No pending payouts to process")
            return {
                "processed": [],
                "failed": [],
                "manual": [],
                "skipped": []
            }
        
        print(f"\n📋 Found {len(pending_payouts)} pending payout(s)\n")
        
        processed = []
        failed = []
        manual = []
        skipped = []
        
        for payout in pending_payouts:
            artist_id = payout.artist_id
            amount = payout.amount
            artist_name = _get_artist_name(artist_id) or artist_id
            
            payout_info = {
                "payout_id": payout.id,
                "artist_id": artist_id,
                "artist_name": artist_name,
                "amount": float(amount),
                "created_at": payout.created_at
            }
            
            # Check minimum amount
            if min_amount and amount < min_amount:
                payout_info["reason"] = f"Below minimum amount (${min_amount:.2f})"
                skipped.append(payout_info)
                print(f"⏭️  Skipped {artist_name}: ${amount:.2f} (below minimum)")
                continue
            
            # Check if artist has Stripe Connect
            stripe_account = _get_artist_stripe_account(artist_id)
            
            if dry_run:
                # Preview mode
                if stripe_account:
                    payout_info["method"] = "stripe_connect (would process)"
                    print(f"🔍 Would process: {artist_name} - ${amount:.2f} via Stripe Connect")
                else:
                    payout_info["method"] = "manual (no Stripe Connect)"
                    print(f"📋 Would create manual record: {artist_name} - ${amount:.2f}")
                manual.append(payout_info)
                continue
            
            # Try Stripe Connect if available and auto_process is enabled
            if auto_process and stripe_account and stripe_configured:
                print(f"💸 Processing {artist_name}: ${amount:.2f} via Stripe Connect...")
                transfer_result = send_stripe_transfer(
                    artist_id=artist_id,
                    amount=amount,
                    destination_account=stripe_account,
                    description=f"Payout for {artist_name} (Payout ID: {payout.id})"
                )
                
                if transfer_result.get("success"):
                    # Update payout record
                    payout.status = "completed"
                    payout.stripe_transfer_id = transfer_result["transfer_id"]
                    payout.completed_at = datetime.utcnow()
                    payout.payment_method = "stripe_connect"
                    db_session.commit()
                    
                    payout_info["method"] = "stripe_connect"
                    payout_info["transfer_id"] = transfer_result["transfer_id"]
                    processed.append(payout_info)
                    print(f"✅ Processed ${amount:.2f} to {artist_name} (Transfer: {transfer_result['transfer_id']})")
                else:
                    # Transfer failed
                    payout.payment_method = "stripe_connect_failed"
                    payout.notes = (payout.notes or "") + f"\nTransfer failed: {transfer_result.get('error')}"
                    db_session.commit()
                    
                    payout_info["method"] = "stripe_connect_failed"
                    payout_info["error"] = transfer_result.get("error")
                    failed.append(payout_info)
                    print(f"❌ Failed to process {artist_name}: {transfer_result.get('error')}")
            else:
                # No Stripe Connect or auto_process disabled
                if not stripe_account:
                    payout_info["method"] = "manual (no Stripe Connect)"
                    payout_info["reason"] = "No Stripe Connect account configured"
                else:
                    payout_info["method"] = "manual (auto_process disabled)"
                    payout_info["reason"] = "Auto-process disabled"
                manual.append(payout_info)
                print(f"📋 Manual payout needed: {artist_name} - ${amount:.2f}")
        
        return {
            "processed": processed,
            "failed": failed,
            "manual": manual,
            "skipped": skipped
        }


def main():
    parser = argparse.ArgumentParser(description="Batch process pending payouts via Stripe")
    parser.add_argument("--dry-run", action="store_true", help="Preview what would be processed without actually doing it")
    parser.add_argument("--auto-process", action="store_true", help="Automatically process Stripe Connect transfers")
    parser.add_argument("--min-amount", type=float, help="Minimum amount to process (skip smaller payouts)")
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.auto_process:
        print("❌ Error: Must specify either --dry-run or --auto-process")
        parser.print_help()
        sys.exit(1)
    
    min_amount_decimal = Decimal(str(args.min_amount)) if args.min_amount else None
    
    results = process_pending_payouts(
        dry_run=args.dry_run,
        auto_process=args.auto_process,
        min_amount=min_amount_decimal
    )
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Processing Summary")
    print("=" * 60)
    print(f"✅ Processed (Stripe Connect): {len(results['processed'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    print(f"📋 Manual (no Stripe Connect): {len(results['manual'])}")
    if results['skipped']:
        print(f"⏭️  Skipped (below minimum): {len(results['skipped'])}")
    
    if results['processed']:
        print("\n✅ Successfully Processed:")
        total_processed = Decimal("0.00")
        for p in results['processed']:
            print(f"   - {p['artist_name']}: ${p['amount']:.2f} (Transfer: {p['transfer_id']})")
            total_processed += Decimal(str(p['amount']))
        print(f"\n   Total: ${total_processed:.2f}")
    
    if results['failed']:
        print("\n❌ Failed Transfers:")
        for p in results['failed']:
            print(f"   - {p['artist_name']}: ${p['amount']:.2f} - {p.get('error', 'Unknown error')}")
    
    if results['manual']:
        print("\n📋 Manual Payouts Needed:")
        total_manual = Decimal("0.00")
        for p in results['manual']:
            print(f"   - {p['artist_name']}: ${p['amount']:.2f} (Payout ID: {p['payout_id']})")
            if p.get('reason'):
                print(f"     Reason: {p['reason']}")
            total_manual += Decimal(str(p['amount']))
        print(f"\n   Total: ${total_manual:.2f}")
        print("\n   To process manually:")
        print("   python scripts/send_artist_payout.py --payout-id <ID> --mark-completed --reference 'YOUR_REFERENCE'")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
