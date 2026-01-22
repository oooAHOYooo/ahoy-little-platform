#!/usr/bin/env python3
"""
Script to send money to artists for boosts and merch purchases.

This script can:
1. Send money via Stripe Connect (if artist has Stripe account connected)
2. Send money via Stripe Transfer (manual)
3. Track payouts in the database
4. Generate payment instructions for manual transfers

Usage:
    # Send payout for a specific artist
    python scripts/send_artist_payout.py --artist-id "rob-meglio" --amount 25.00

    # Send payout for all pending tips for an artist
    python scripts/send_artist_payout.py --artist-id "rob-meglio" --auto

    # List pending payouts
    python scripts/send_artist_payout.py --list-pending

    # Mark payout as completed (manual transfer)
    python scripts/send_artist_payout.py --payout-id 123 --mark-completed --reference "BANK_TRANSFER_12345"
"""
import os
import sys
import argparse
from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_session
from models import Tip, ArtistPayout, User
import stripe


def _configure_stripe():
    """Configure Stripe API key from environment."""
    api_key = os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_SECRET_KEY_TEST")
    if not api_key:
        print("❌ Error: STRIPE_SECRET_KEY not set in environment")
        sys.exit(1)
    stripe.api_key = api_key
    return api_key


def _get_artist_name(artist_id: str) -> Optional[str]:
    """Get artist name from artists.json."""
    try:
        from app import load_json_data
        artists_data = load_json_data('artists.json', {'artists': []})
        for artist in artists_data.get('artists', []):
            if (str(artist.get('id', '')) == str(artist_id) or
                artist.get('slug', '').lower() == str(artist_id).lower() or
                artist.get('name', '').lower() == str(artist_id).lower()):
                return artist.get('name')
    except Exception:
        pass
    return None


def _get_artist_stripe_account(artist_id: str) -> Optional[str]:
    """
    Get artist's Stripe Connect account ID.
    Can be set via environment variable: ARTIST_STRIPE_ACCOUNT_<artist_id>
    """
    env_key = f"ARTIST_STRIPE_ACCOUNT_{artist_id.upper().replace('-', '_').replace(' ', '_')}"
    account_id = os.getenv(env_key) or os.getenv(env_key.lower())
    return account_id.strip() if account_id else None


def get_pending_tips_for_artist(artist_id: str, db_session) -> List[Tip]:
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


def create_payout(
    artist_id: str,
    amount: Decimal,
    tip_ids: Optional[List[int]] = None,
    payment_method: str = "manual",
    notes: Optional[str] = None
) -> ArtistPayout:
    """Create a payout record in the database."""
    with get_session() as db_session:
        payout = ArtistPayout(
            artist_id=str(artist_id),
            amount=amount,
            status="pending",
            payment_method=payment_method,
            notes=notes,
            related_tip_ids=tip_ids or [],
            created_at=datetime.utcnow()
        )
        db_session.add(payout)
        db_session.commit()
        db_session.refresh(payout)
        return payout


def send_stripe_transfer(
    artist_id: str,
    amount: Decimal,
    destination_account: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send money to artist via Stripe Connect Transfer.
    Requires the artist to have a connected Stripe account.
    """
    _configure_stripe()
    
    try:
        transfer = stripe.Transfer.create(
            amount=int(amount * 100),  # Convert to cents
            currency="usd",
            destination=destination_account,
            description=description or f"Payout to {artist_id}",
        )
        return {"success": True, "transfer_id": transfer.id, "transfer": transfer}
    except stripe.error.StripeError as e:
        return {"success": False, "error": str(e)}


def send_payout(
    artist_id: str,
    amount: Decimal,
    payment_method: str = "manual",
    tip_ids: Optional[List[int]] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send payout to artist.
    
    Returns dict with success status and payout information.
    """
    artist_name = _get_artist_name(artist_id) or artist_id
    
    # Create payout record
    payout = create_payout(
        artist_id=artist_id,
        amount=amount,
        tip_ids=tip_ids,
        payment_method=payment_method,
        notes=notes
    )
    
    result = {"payout_id": payout.id, "artist_id": artist_id, "amount": float(amount)}
    
    # Try Stripe Connect if configured
    if payment_method == "stripe_connect":
        stripe_account = _get_artist_stripe_account(artist_id)
        if stripe_account:
            transfer_result = send_stripe_transfer(
                artist_id=artist_id,
                amount=amount,
                destination_account=stripe_account,
                description=f"Payout for {artist_name}"
            )
            if transfer_result.get("success"):
                # Update payout record
                with get_session() as db_session:
                    payout = db_session.query(ArtistPayout).filter(ArtistPayout.id == payout.id).first()
                    if payout:
                        payout.status = "completed"
                        payout.stripe_transfer_id = transfer_result["transfer_id"]
                        payout.completed_at = datetime.utcnow()
                        db_session.commit()
                result["success"] = True
                result["transfer_id"] = transfer_result["transfer_id"]
                result["method"] = "stripe_connect"
                print(f"✅ Sent ${amount:.2f} to {artist_name} via Stripe Connect (Transfer: {transfer_result['transfer_id']})")
                return result
            else:
                result["error"] = transfer_result.get("error")
                result["method"] = "stripe_connect_failed"
                print(f"❌ Stripe Connect transfer failed: {transfer_result.get('error')}")
        else:
            result["error"] = "No Stripe Connect account configured for artist"
            result["method"] = "stripe_connect_not_configured"
    
    # Manual payment (default)
    result["success"] = True
    result["method"] = "manual"
    result["instructions"] = f"""
📋 Manual Payout Instructions:

Artist: {artist_name} ({artist_id})
Amount: ${amount:.2f}
Payout ID: {payout.id}

Next steps:
1. Transfer ${amount:.2f} to the artist's payment method
2. Record the payment reference (bank transfer ID, PayPal transaction ID, etc.)
3. Mark as completed using:
   python scripts/send_artist_payout.py --payout-id {payout.id} --mark-completed --reference "YOUR_REFERENCE"
"""
    print(result["instructions"])
    return result


def mark_payout_completed(payout_id: int, reference: Optional[str] = None, notes: Optional[str] = None):
    """Mark a payout as completed (for manual transfers)."""
    with get_session() as db_session:
        payout = db_session.query(ArtistPayout).filter(ArtistPayout.id == payout_id).first()
        if not payout:
            print(f"❌ Payout {payout_id} not found")
            return False
        
        if payout.status == "completed":
            print(f"⚠️  Payout {payout_id} is already completed")
            return False
        
        payout.status = "completed"
        payout.completed_at = datetime.utcnow()
        if reference:
            payout.payment_reference = reference
        if notes:
            payout.notes = (payout.notes or "") + f"\n{notes}"
        
        db_session.commit()
        print(f"✅ Marked payout {payout_id} as completed")
        return True


def list_pending_payouts(artist_id: Optional[str] = None):
    """List all pending payouts."""
    with get_session() as db_session:
        query = db_session.query(ArtistPayout).filter(ArtistPayout.status == "pending")
        if artist_id:
            query = query.filter(ArtistPayout.artist_id == str(artist_id))
        
        payouts = query.order_by(ArtistPayout.created_at).all()
        
        if not payouts:
            print("✅ No pending payouts")
            return
        
        print(f"\n📋 Pending Payouts ({len(payouts)}):\n")
        for payout in payouts:
            artist_name = _get_artist_name(payout.artist_id) or payout.artist_id
            print(f"  ID: {payout.id}")
            print(f"  Artist: {artist_name} ({payout.artist_id})")
            print(f"  Amount: ${payout.amount:.2f}")
            print(f"  Method: {payout.payment_method or 'manual'}")
            print(f"  Created: {payout.created_at}")
            if payout.notes:
                print(f"  Notes: {payout.notes}")
            print()


def auto_payout_artist(artist_id: str):
    """Automatically create payout for all pending tips for an artist."""
    with get_session() as db_session:
        pending_tips = get_pending_tips_for_artist(artist_id, db_session)
        
        if not pending_tips:
            print(f"✅ No pending tips for artist {artist_id}")
            return
        
        total_amount = sum(Decimal(str(tip.artist_payout or tip.amount)) for tip in pending_tips)
        tip_ids = [tip.id for tip in pending_tips]
        
        artist_name = _get_artist_name(artist_id) or artist_id
        print(f"\n💰 Creating payout for {artist_name}:")
        print(f"   {len(pending_tips)} tips totaling ${total_amount:.2f}\n")
        
        # Try Stripe Connect first, fall back to manual
        payment_method = "manual"
        stripe_account = _get_artist_stripe_account(artist_id)
        if stripe_account:
            payment_method = "stripe_connect"
        
        result = send_payout(
            artist_id=artist_id,
            amount=total_amount,
            payment_method=payment_method,
            tip_ids=tip_ids,
            notes=f"Auto payout for {len(pending_tips)} tips"
        )
        
        return result


def main():
    parser = argparse.ArgumentParser(description="Send payouts to artists")
    parser.add_argument("--artist-id", help="Artist ID, slug, or name")
    parser.add_argument("--amount", type=float, help="Amount to pay out (for single payout)")
    parser.add_argument("--auto", action="store_true", help="Auto payout all pending tips for artist")
    parser.add_argument("--list-pending", action="store_true", help="List all pending payouts")
    parser.add_argument("--payout-id", type=int, help="Payout ID (for marking as completed)")
    parser.add_argument("--mark-completed", action="store_true", help="Mark payout as completed")
    parser.add_argument("--reference", help="Payment reference (for marking as completed)")
    parser.add_argument("--method", choices=["manual", "stripe_connect"], default="manual", help="Payment method")
    parser.add_argument("--notes", help="Notes for the payout")
    
    args = parser.parse_args()
    
    if args.list_pending:
        list_pending_payouts(args.artist_id)
        return
    
    if args.mark_completed:
        if not args.payout_id:
            print("❌ --payout-id required when using --mark-completed")
            sys.exit(1)
        mark_payout_completed(args.payout_id, args.reference, args.notes)
        return
    
    if args.auto:
        if not args.artist_id:
            print("❌ --artist-id required when using --auto")
            sys.exit(1)
        auto_payout_artist(args.artist_id)
        return
    
    if args.artist_id and args.amount:
        send_payout(
            artist_id=args.artist_id,
            amount=Decimal(str(args.amount)),
            payment_method=args.method,
            notes=args.notes
        )
        return
    
    parser.print_help()


if __name__ == "__main__":
    main()
