#!/usr/bin/env python3
"""
Daily automated payout processor.

This script:
1. Scans all artists for pending payouts
2. Automatically processes payouts via Stripe (if configured)
3. Sends email summary to admin
4. Creates payout records for manual transfers

Can be run manually or scheduled (cron, Render cron job, etc.)

Usage:
    python scripts/daily_payout_processor.py
    python scripts/daily_payout_processor.py --dry-run  # Preview without processing
    python scripts/daily_payout_processor.py --min-amount 50.00  # Only process $50+
    python scripts/daily_payout_processor.py --auto-process  # Automatically send via Stripe
"""
import os
import sys
import argparse
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_session
from models import Tip, ArtistPayout
from services.notifications import _get_admin_email
from services.emailer import send_email, can_send_email
import stripe


def _configure_stripe():
    """Configure Stripe API key from environment."""
    api_key = os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_SECRET_KEY_TEST")
    if api_key:
        stripe.api_key = api_key
        return True
    return False


def _get_artist_name(artist_id: str) -> Optional[str]:
    """Get artist name from artists.json."""
    try:
        import json
        from pathlib import Path
        
        artists_file = Path(__file__).parent.parent / 'static' / 'data' / 'artists.json'
        if artists_file.exists():
            with open(artists_file, 'r', encoding='utf-8') as f:
                artists_data = json.load(f)
                for artist in artists_data.get('artists', []):
                    if (str(artist.get('id', '')) == str(artist_id) or
                        artist.get('slug', '').lower() == str(artist_id).lower() or
                        artist.get('name', '').lower() == str(artist_id).lower()):
                        return artist.get('name')
    except Exception:
        pass
    return None


def _get_artist_stripe_account(artist_id: str) -> Optional[str]:
    """Get artist's Stripe Connect account ID from environment."""
    env_key = f"ARTIST_STRIPE_ACCOUNT_{artist_id.upper().replace('-', '_').replace(' ', '_')}"
    account_id = os.getenv(env_key) or os.getenv(env_key.lower())
    return account_id.strip() if account_id else None


def _get_artist_email(artist_id: str) -> Optional[str]:
    """Get artist email from environment or artists.json."""
    # Try environment variable first
    env_key = f"ARTIST_EMAIL_{artist_id.upper().replace('-', '_').replace(' ', '_')}"
    email = os.getenv(env_key) or os.getenv(env_key.lower())
    if email:
        return email.strip()
    
    # Try loading from artist data
    try:
        import json
        from pathlib import Path
        
        artists_file = Path(__file__).parent.parent / 'static' / 'data' / 'artists.json'
        if artists_file.exists():
            with open(artists_file, 'r', encoding='utf-8') as f:
                artists_data = json.load(f)
                for artist in artists_data.get('artists', []):
                    if (str(artist.get('id', '')) == str(artist_id) or
                        artist.get('slug', '').lower() == str(artist_id).lower()):
                        if 'email' in artist:
                            return artist['email'].strip()
    except Exception:
        pass
    
    return None


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


def load_all_artists():
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


def scan_pending_payouts(min_amount: Decimal = Decimal("0.01")) -> List[Dict[str, Any]]:
    """Scan all artists and find pending payouts."""
    artists = load_all_artists()
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
                        'tip_count': len(pending_tips),
                        'artist_email': _get_artist_email(artist_slug or artist_id),
                        'stripe_account': _get_artist_stripe_account(artist_slug or artist_id)
                    })
    
    # Sort by total pending (highest first)
    results.sort(key=lambda x: x['total_pending'], reverse=True)
    return results


def process_stripe_transfer(artist_id: str, artist_name: str, amount: Decimal, stripe_account: str) -> Dict[str, Any]:
    """Process automatic payout via Stripe Connect Transfer."""
    try:
        transfer = stripe.Transfer.create(
            amount=int(amount * 100),  # Convert to cents
            currency="usd",
            destination=stripe_account,
            description=f"Payout to {artist_name}",
        )
        return {
            "success": True,
            "transfer_id": transfer.id,
            "method": "stripe_connect"
        }
    except stripe.error.StripeError as e:
        return {
            "success": False,
            "error": str(e),
            "method": "stripe_connect"
        }


def create_payout_record(artist_id: str, amount: Decimal, tip_ids: List[int], payment_method: str, stripe_transfer_id: Optional[str] = None) -> ArtistPayout:
    """Create a payout record in the database."""
    with get_session() as db_session:
        payout = ArtistPayout(
            artist_id=str(artist_id),
            amount=amount,
            status="completed" if stripe_transfer_id else "pending",
            payment_method=payment_method,
            stripe_transfer_id=stripe_transfer_id,
            related_tip_ids=tip_ids,
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow() if stripe_transfer_id else None
        )
        db_session.add(payout)
        db_session.commit()
        db_session.refresh(payout)
        return payout


def process_payouts(results: List[Dict[str, Any]], auto_process: bool = False, dry_run: bool = False) -> Dict[str, Any]:
    """Process payouts for all artists with pending tips."""
    processed = []
    failed = []
    manual = []
    
    stripe_configured = _configure_stripe()
    
    for result in results:
        artist_id = result['artist_slug']
        artist_name = result['artist_name']
        amount = result['total_pending']
        tip_ids = [tip.id for tip in result['pending_tips']]
        stripe_account = result.get('stripe_account')
        
        payout_info = {
            'artist_id': artist_id,
            'artist_name': artist_name,
            'amount': amount,
            'tip_count': result['tip_count'],
            'method': None,
            'payout_id': None,
            'transfer_id': None,
            'error': None
        }
        
        if dry_run:
            # Just preview, don't process
            if stripe_account:
                payout_info['method'] = 'stripe_connect (would process)'
            else:
                payout_info['method'] = 'manual (would create record)'
            manual.append(payout_info)
            continue
        
        # Try automatic Stripe Connect if available and auto_process is enabled
        if auto_process and stripe_account and stripe_configured:
            transfer_result = process_stripe_transfer(artist_id, artist_name, amount, stripe_account)
            
            if transfer_result['success']:
                # Create completed payout record
                payout = create_payout_record(
                    artist_id=artist_id,
                    amount=amount,
                    tip_ids=tip_ids,
                    payment_method="stripe_connect",
                    stripe_transfer_id=transfer_result['transfer_id']
                )
                payout_info['method'] = 'stripe_connect'
                payout_info['payout_id'] = payout.id
                payout_info['transfer_id'] = transfer_result['transfer_id']
                processed.append(payout_info)
                print(f"✅ Processed ${amount:.2f} to {artist_name} via Stripe Connect (Transfer: {transfer_result['transfer_id']})")
            else:
                # Stripe transfer failed, create pending record for manual processing
                payout = create_payout_record(
                    artist_id=artist_id,
                    amount=amount,
                    tip_ids=tip_ids,
                    payment_method="stripe_connect_failed"
                )
                payout_info['method'] = 'stripe_connect_failed'
                payout_info['payout_id'] = payout.id
                payout_info['error'] = transfer_result['error']
                failed.append(payout_info)
                print(f"❌ Failed to process ${amount:.2f} to {artist_name}: {transfer_result['error']}")
        else:
            # Create pending payout record for manual processing
            payout = create_payout_record(
                artist_id=artist_id,
                amount=amount,
                tip_ids=tip_ids,
                payment_method="manual"
            )
            payout_info['method'] = 'manual'
            payout_info['payout_id'] = payout.id
            manual.append(payout_info)
            print(f"📋 Created pending payout record for {artist_name}: ${amount:.2f} (Payout ID: {payout.id})")
    
    return {
        'processed': processed,
        'failed': failed,
        'manual': manual
    }


def send_summary_email(results: List[Dict[str, Any]], processing_results: Dict[str, Any]):
    """Send email summary to admin."""
    admin_email = _get_admin_email()
    
    if not admin_email or not can_send_email():
        print("⚠️  Email not configured, skipping email summary")
        return
    
    total_pending = sum(r['total_pending'] for r in results)
    total_tips = sum(r['tip_count'] for r in results)
    
    processed_count = len(processing_results['processed'])
    failed_count = len(processing_results['failed'])
    manual_count = len(processing_results['manual'])
    
    subject = f"💰 Daily Payout Scan - ${total_pending:.2f} Pending ({len(results)} artists)"
    
    # Build text summary
    text_lines = [
        f"Daily Payout Scan Results - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        f"Total Pending: ${total_pending:.2f}",
        f"Total Tips: {total_tips}",
        f"Artists Needing Payouts: {len(results)}",
        "",
    ]
    
    if processing_results['processed']:
        text_lines.extend([
            f"✅ Automatically Processed: {processed_count}",
            ""
        ])
        for p in processing_results['processed']:
            text_lines.append(f"  - {p['artist_name']}: ${p['amount']:.2f} (Stripe Transfer: {p['transfer_id']})")
        text_lines.append("")
    
    if processing_results['failed']:
        text_lines.extend([
            f"❌ Failed (needs manual review): {failed_count}",
            ""
        ])
        for f in processing_results['failed']:
            text_lines.append(f"  - {f['artist_name']}: ${f['amount']:.2f} - {f['error']}")
        text_lines.append("")
    
    if processing_results['manual']:
        text_lines.extend([
            f"📋 Manual Payouts Needed: {manual_count}",
            ""
        ])
        for m in processing_results['manual']:
            text_lines.append(f"  - {m['artist_name']}: ${m['amount']:.2f} ({m['tip_count']} tips)")
            text_lines.append(f"    Payout ID: {m['payout_id']}")
            text_lines.append(f"    Command: python scripts/send_artist_payout.py --payout-id {m['payout_id']} --mark-completed --reference \"YOUR_REFERENCE\"")
            text_lines.append("")
    
    text_lines.extend([
        "Artists Needing Payouts:",
        ""
    ])
    
    for i, result in enumerate(results, 1):
        text_lines.append(f"{i}. {result['artist_name']} ({result['artist_slug']})")
        text_lines.append(f"   Pending: ${result['total_pending']:.2f} ({result['tip_count']} tips)")
        if result.get('stripe_account'):
            text_lines.append(f"   Stripe Connect: Configured")
        else:
            text_lines.append(f"   Payment Method: Manual transfer needed")
        text_lines.append("")
    
    text = "\n".join(text_lines)
    
    # Build HTML summary
    html = f"""
    <h2>💰 Daily Payout Scan Results</h2>
    <p><strong>Date:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    
    <h3>Summary</h3>
    <ul>
        <li><strong>Total Pending:</strong> ${total_pending:.2f}</li>
        <li><strong>Total Tips:</strong> {total_tips}</li>
        <li><strong>Artists Needing Payouts:</strong> {len(results)}</li>
    </ul>
    """
    
    if processing_results['processed']:
        html += f"""
        <h3>✅ Automatically Processed ({processed_count})</h3>
        <ul>
        """
        for p in processing_results['processed']:
            html += f"<li>{p['artist_name']}: ${p['amount']:.2f} (Stripe Transfer: {p['transfer_id']})</li>"
        html += "</ul>"
    
    if processing_results['failed']:
        html += f"""
        <h3>❌ Failed - Needs Manual Review ({failed_count})</h3>
        <ul>
        """
        for f in processing_results['failed']:
            html += f"<li>{f['artist_name']}: ${f['amount']:.2f} - {f['error']}</li>"
        html += "</ul>"
    
    if processing_results['manual']:
        html += f"""
        <h3>📋 Manual Payouts Needed ({manual_count})</h3>
        <ul>
        """
        for m in processing_results['manual']:
            html += f"""
            <li>
                <strong>{m['artist_name']}:</strong> ${m['amount']:.2f} ({m['tip_count']} tips)<br>
                Payout ID: {m['payout_id']}<br>
                <code>python scripts/send_artist_payout.py --payout-id {m['payout_id']} --mark-completed --reference "YOUR_REFERENCE"</code>
            </li>
            """
        html += "</ul>"
    
    html += """
    <h3>All Artists Needing Payouts</h3>
    <table border="1" cellpadding="5" style="border-collapse: collapse;">
        <tr>
            <th>Artist</th>
            <th>Pending Amount</th>
            <th>Tips</th>
            <th>Payment Method</th>
        </tr>
    """
    
    for result in results:
        method = "Stripe Connect" if result.get('stripe_account') else "Manual"
        html += f"""
        <tr>
            <td>{result['artist_name']} ({result['artist_slug']})</td>
            <td>${result['total_pending']:.2f}</td>
            <td>{result['tip_count']}</td>
            <td>{method}</td>
        </tr>
        """
    
    html += "</table>"
    
    result = send_email(admin_email, subject, text, html)
    if result.get("ok"):
        print(f"✅ Summary email sent to {admin_email}")
    else:
        print(f"⚠️  Failed to send email: {result.get('detail')}")


def main():
    parser = argparse.ArgumentParser(description="Daily automated payout processor")
    parser.add_argument("--dry-run", action="store_true", help="Preview without processing")
    parser.add_argument("--min-amount", type=float, default=0.01, help="Minimum amount to process (default: 0.01)")
    parser.add_argument("--auto-process", action="store_true", help="Automatically process Stripe Connect payouts")
    
    args = parser.parse_args()
    
    print("🔍 Scanning for pending payouts...\n")
    
    # Scan for pending payouts
    results = scan_pending_payouts(min_amount=Decimal(str(args.min_amount)))
    
    if not results:
        print("✅ No artists with pending payouts found!")
        return
    
    print(f"💰 Found {len(results)} artist(s) with pending payouts:\n")
    total_pending = sum(r['total_pending'] for r in results)
    print(f"   Total Pending: ${total_pending:.2f}\n")
    
    # Process payouts
    if args.dry_run:
        print("🔍 DRY RUN MODE - Preview only\n")
        processing_results = process_payouts(results, auto_process=False, dry_run=True)
    else:
        processing_results = process_payouts(results, auto_process=args.auto_process, dry_run=False)
    
    # Send summary email
    send_summary_email(results, processing_results)
    
    # Print summary
    print(f"\n📊 Summary:")
    print(f"   Processed: {len(processing_results['processed'])}")
    print(f"   Failed: {len(processing_results['failed'])}")
    print(f"   Manual: {len(processing_results['manual'])}")


if __name__ == "__main__":
    main()
