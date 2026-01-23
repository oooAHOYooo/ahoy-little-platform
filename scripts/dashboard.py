#!/usr/bin/env python3
"""
Ahoy Platform Dashboard - Control Panel for All Scripts

Interactive terminal dashboard to manage and monitor all platform scripts.

Usage:
    python scripts/dashboard.py
"""
import os
import sys
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_session
from models import ArtistPayout, Tip, Purchase, WalletTransaction, User


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def clear_screen():
    """Clear terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{title.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 60}{Colors.ENDC}\n")


def print_section(title: str):
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}{title}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'-' * len(title)}{Colors.ENDC}")


def get_database_stats() -> Dict:
    """Get current database statistics."""
    stats = {}
    try:
        with get_session() as db_session:
            # Pending payouts
            pending_payouts = db_session.query(ArtistPayout).filter(
                ArtistPayout.status == 'pending'
            ).count()
            stats['pending_payouts'] = pending_payouts
            
            # Total pending amount
            pending_amount = db_session.query(ArtistPayout).filter(
                ArtistPayout.status == 'pending'
            ).all()
            stats['pending_amount'] = sum(float(p.amount) for p in pending_amount)
            
            # Completed payouts today
            today = datetime.now().date()
            completed_today = db_session.query(ArtistPayout).filter(
                ArtistPayout.status == 'completed',
                ArtistPayout.completed_at >= datetime.combine(today, datetime.min.time())
            ).count()
            stats['completed_today'] = completed_today
            
            # Tips today
            tips_today = db_session.query(Tip).filter(
                Tip.created_at >= datetime.combine(today, datetime.min.time())
            ).count()
            stats['tips_today'] = tips_today
            
            # Total tips
            total_tips = db_session.query(Tip).count()
            stats['total_tips'] = total_tips
            
            # Total tips amount
            all_tips = db_session.query(Tip).all()
            stats['total_tips_amount'] = sum(float(t.total_paid or t.amount) for t in all_tips)
            
    except Exception as e:
        stats['error'] = str(e)
    
    return stats


def format_table(data: List[Dict], columns: List[str], max_rows: int = 20):
    """Format data as a table."""
    if not data:
        return "  (No data)"
    
    # Truncate if too many rows
    display_data = data[:max_rows]
    
    # Calculate column widths
    widths = {col: len(col) for col in columns}
    for row in display_data:
        for col in columns:
            val = str(row.get(col, ''))
            widths[col] = max(widths[col], len(val))
    
    # Build table
    lines = []
    
    # Header
    header = "  " + " | ".join(col.ljust(widths[col]) for col in columns)
    lines.append(header)
    lines.append("  " + "-" * (len(header) - 2))
    
    # Rows
    for row in display_data:
        line = "  " + " | ".join(str(row.get(col, '')).ljust(widths[col]) for col in columns)
        lines.append(line)
    
    if len(data) > max_rows:
        lines.append(f"  ... and {len(data) - max_rows} more rows")
    
    return "\n".join(lines)


def show_recent_tips(limit: int = 20):
    """Show recent tips/boosts."""
    with get_session() as db_session:
        tips = db_session.query(Tip).order_by(Tip.created_at.desc()).limit(limit).all()
        
        data = []
        for tip in tips:
            artist_name = get_artist_name(tip.artist_id)
            data.append({
                'ID': tip.id,
                'Date': tip.created_at.strftime('%Y-%m-%d %H:%M'),
                'Artist': artist_name[:20],
                'Amount': f"${float(tip.amount):.2f}",
                'Total Paid': f"${float(tip.total_paid or tip.amount):.2f}",
                'User ID': tip.user_id or 'Guest',
            })
        
        return format_table(data, ['ID', 'Date', 'Artist', 'Amount', 'Total Paid', 'User ID'])


def show_recent_payouts(limit: int = 20):
    """Show recent payouts."""
    with get_session() as db_session:
        payouts = db_session.query(ArtistPayout).order_by(
            ArtistPayout.completed_at.desc().nulls_last(),
            ArtistPayout.created_at.desc()
        ).limit(limit).all()
        
        data = []
        for payout in payouts:
            artist_name = get_artist_name(payout.artist_id)
            status_color = Colors.OKGREEN if payout.status == 'completed' else Colors.WARNING if payout.status == 'pending' else Colors.FAIL
            status_display = f"{status_color}{payout.status}{Colors.ENDC}"
            
            completed_date = payout.completed_at.strftime('%Y-%m-%d') if payout.completed_at else 'Pending'
            
            data.append({
                'ID': payout.id,
                'Date': completed_date,
                'Artist': artist_name[:20],
                'Amount': f"${float(payout.amount):.2f}",
                'Status': payout.status,
                'Method': (payout.payment_method or 'manual')[:15],
            })
        
        return format_table(data, ['ID', 'Date', 'Artist', 'Amount', 'Status', 'Method'])


def show_pending_payouts():
    """Show all pending payouts."""
    with get_session() as db_session:
        payouts = db_session.query(ArtistPayout).filter(
            ArtistPayout.status == 'pending'
        ).order_by(ArtistPayout.created_at.desc()).all()
        
        if not payouts:
            return "  ✅ No pending payouts"
        
        data = []
        for payout in payouts:
            artist_name = get_artist_name(payout.artist_id)
            days_old = (datetime.now() - payout.created_at).days
            
            data.append({
                'ID': payout.id,
                'Created': payout.created_at.strftime('%Y-%m-%d'),
                'Days Old': days_old,
                'Artist': artist_name[:20],
                'Amount': f"${float(payout.amount):.2f}",
                'Method': (payout.payment_method or 'manual')[:15],
            })
        
        return format_table(data, ['ID', 'Created', 'Days Old', 'Artist', 'Amount', 'Method'])


def show_recent_purchases(limit: int = 20):
    """Show recent purchases."""
    with get_session() as db_session:
        purchases = db_session.query(Purchase).filter(
            Purchase.status == 'paid'
        ).order_by(Purchase.created_at.desc()).limit(limit).all()
        
        data = []
        for purchase in purchases:
            data.append({
                'ID': purchase.id,
                'Date': purchase.created_at.strftime('%Y-%m-%d %H:%M'),
                'Type': purchase.type[:15],
                'Amount': f"${float(purchase.amount):.2f}",
                'Total': f"${float(purchase.total):.2f}",
                'User ID': purchase.user_id or 'Guest',
            })
        
        return format_table(data, ['ID', 'Date', 'Type', 'Amount', 'Total', 'User ID'])


def show_recent_wallet_transactions(limit: int = 20):
    """Show recent wallet transactions."""
    with get_session() as db_session:
        transactions = db_session.query(WalletTransaction).order_by(
            WalletTransaction.created_at.desc()
        ).limit(limit).all()
        
        data = []
        for tx in transactions:
            type_color = Colors.OKGREEN if tx.type == 'fund' else Colors.WARNING if tx.type == 'spend' else Colors.OKCYAN
            type_display = f"{type_color}{tx.type}{Colors.ENDC}"
            
            data.append({
                'ID': tx.id,
                'Date': tx.created_at.strftime('%Y-%m-%d %H:%M'),
                'User ID': tx.user_id,
                'Type': tx.type,
                'Amount': f"${float(tx.amount):.2f}",
                'Balance': f"${float(tx.balance_after):.2f}",
            })
        
        return format_table(data, ['ID', 'Date', 'User ID', 'Type', 'Amount', 'Balance'])


def show_artist_summary():
    """Show summary by artist (pending tips)."""
    with get_session() as db_session:
        # Get all tips grouped by artist
        tips = db_session.query(Tip).all()
        
        # Get completed payouts
        completed_payouts = db_session.query(ArtistPayout).filter(
            ArtistPayout.status == 'completed'
        ).all()
        
        # Track paid tip IDs
        paid_tip_ids = set()
        for payout in completed_payouts:
            if payout.related_tip_ids:
                paid_tip_ids.update(payout.related_tip_ids)
        
        # Group by artist
        artist_data = {}
        for tip in tips:
            if tip.id in paid_tip_ids:
                continue  # Already paid
            
            if tip.artist_id not in artist_data:
                artist_data[tip.artist_id] = {
                    'artist_id': tip.artist_id,
                    'count': 0,
                    'total': Decimal('0'),
                }
            
            artist_data[tip.artist_id]['count'] += 1
            artist_data[tip.artist_id]['total'] += Decimal(str(tip.artist_payout or tip.amount))
        
        if not artist_data:
            return "  ✅ No pending tips for any artist"
        
        # Convert to list and sort
        data = []
        for artist_id, info in sorted(artist_data.items(), key=lambda x: x[1]['total'], reverse=True):
            artist_name = get_artist_name(artist_id)
            data.append({
                'Artist': artist_name[:25],
                'Pending Tips': info['count'],
                'Total Pending': f"${float(info['total']):.2f}",
            })
        
        return format_table(data, ['Artist', 'Pending Tips', 'Total Pending'])


def show_dashboard():
    """Display main dashboard with stats."""
    clear_screen()
    print_header("🎛️  Ahoy Platform Dashboard")
    
    # Database Stats
    print_section("📊 Current Status")
    stats = get_database_stats()
    
    if 'error' in stats:
        print(f"{Colors.FAIL}❌ Error loading stats: {stats['error']}{Colors.ENDC}")
    else:
        print(f"  {Colors.OKGREEN}Pending Payouts:{Colors.ENDC} {stats.get('pending_payouts', 0)}")
        print(f"  {Colors.WARNING}Pending Amount:{Colors.ENDC} ${stats.get('pending_amount', 0):,.2f}")
        print(f"  {Colors.OKGREEN}Completed Today:{Colors.ENDC} {stats.get('completed_today', 0)}")
        print(f"  {Colors.OKCYAN}Tips Today:{Colors.ENDC} {stats.get('tips_today', 0)}")
        print(f"  {Colors.OKCYAN}Total Tips:{Colors.ENDC} {stats.get('total_tips', 0)}")
        print(f"  {Colors.OKCYAN}Total Tips Amount:{Colors.ENDC} ${stats.get('total_tips_amount', 0):,.2f}")
    
    # Data Views
    print_section("📋 View Data")
    
    scripts = [
        {
            'name': 'Scan Artist Payouts',
            'script': 'scan_artist_payouts.py',
            'description': 'Find all artists with pending tips needing payouts',
            'command': 'python scripts/scan_artist_payouts.py'
        },
        {
            'name': 'Send Artist Payout',
            'script': 'send_artist_payout.py',
            'description': 'Process individual artist payouts',
            'command': 'python scripts/send_artist_payout.py --help',
            'interactive': True
        },
        {
            'name': 'Batch Process Payouts',
            'script': 'batch_process_payouts.py',
            'description': 'Batch process all pending payouts via Stripe',
            'command': 'python scripts/batch_process_payouts.py --dry-run',
            'interactive': True
        },
        {
            'name': 'Daily Payout Processor',
            'script': 'daily_payout_processor.py',
            'description': 'Automated daily payout processing (scan + process)',
            'command': 'python scripts/daily_payout_processor.py --dry-run',
            'interactive': True
        },
        {
            'name': 'Export Accounting',
            'script': 'export_accounting.py',
            'description': 'Generate tax-ready accounting reports (CSV)',
            'command': 'python scripts/export_accounting.py --type all --year 2024',
            'interactive': True
        },
        {
            'name': 'Test Email Notifications',
            'script': 'test_send_email_to_alex.py',
            'description': 'Test all email notification types',
            'command': 'python scripts/test_send_email_to_alex.py'
        },
        {
            'name': 'Check Email Config',
            'script': 'check_email_config.py',
            'description': 'Check email service configuration',
            'command': 'python scripts/check_email_config.py'
        },
    ]
    
    for i, script in enumerate(scripts, 1):
        interactive = "🔧" if script.get('interactive') else "▶️"
        print(f"  {Colors.BOLD}{i}.{Colors.ENDC} {interactive} {script['name']}")
        print(f"     {Colors.OKBLUE}{script['description']}{Colors.ENDC}")
        print(f"     {Colors.WARNING}Script:{Colors.ENDC} {script['script']}")
        print()
    
    print_section("⚙️  Quick Actions")
    print(f"  {Colors.BOLD}0.{Colors.ENDC} Refresh Dashboard")
    print(f"  {Colors.BOLD}q.{Colors.ENDC} Quit")
    print()


def run_script_interactive(script_info: Dict):
    """Run a script with interactive parameter input."""
    script_name = script_info['script']
    base_command = script_info['command']
    
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}Running: {script_name}{Colors.ENDC}\n")
    
    # Handle different script types
    if 'scan_artist_payouts' in script_name:
        # Simple script, just run it
        run_command(base_command.replace('--help', ''))
    
    elif 'send_artist_payout' in script_name:
        print(f"{Colors.WARNING}Interactive payout tool{Colors.ENDC}")
        print("Options:")
        print("  1. List pending payouts")
        print("  2. Auto payout for artist")
        print("  3. Mark payout as completed")
        print("  4. Show help")
        choice = input(f"\n{Colors.BOLD}Choice (1-4):{Colors.ENDC} ").strip()
        
        if choice == '1':
            run_command('python scripts/send_artist_payout.py --list-pending')
        elif choice == '2':
            artist_id = input(f"{Colors.BOLD}Artist ID:{Colors.ENDC} ").strip()
            if artist_id:
                run_command(f'python scripts/send_artist_payout.py --artist-id "{artist_id}" --auto')
        elif choice == '3':
            payout_id = input(f"{Colors.BOLD}Payout ID:{Colors.ENDC} ").strip()
            reference = input(f"{Colors.BOLD}Payment Reference:{Colors.ENDC} ").strip()
            if payout_id:
                cmd = f'python scripts/send_artist_payout.py --payout-id {payout_id} --mark-completed'
                if reference:
                    cmd += f' --reference "{reference}"'
                run_command(cmd)
        elif choice == '4':
            run_command('python scripts/send_artist_payout.py --help')
    
    elif 'batch_process_payouts' in script_name:
        print(f"{Colors.WARNING}Batch Process Payouts{Colors.ENDC}")
        print("Options:")
        print("  1. Dry run (preview)")
        print("  2. Process all (auto-process)")
        print("  3. Process with minimum amount")
        choice = input(f"\n{Colors.BOLD}Choice (1-3):{Colors.ENDC} ").strip()
        
        if choice == '1':
            run_command('python scripts/batch_process_payouts.py --dry-run')
        elif choice == '2':
            confirm = input(f"{Colors.FAIL}⚠️  This will process all pending payouts. Continue? (yes/no):{Colors.ENDC} ").strip().lower()
            if confirm == 'yes':
                run_command('python scripts/batch_process_payouts.py --auto-process')
        elif choice == '3':
            min_amount = input(f"{Colors.BOLD}Minimum amount (e.g., 10.00):{Colors.ENDC} ").strip()
            if min_amount:
                run_command(f'python scripts/batch_process_payouts.py --auto-process --min-amount {min_amount}')
    
    elif 'daily_payout_processor' in script_name:
        print(f"{Colors.WARNING}Daily Payout Processor{Colors.ENDC}")
        print("Options:")
        print("  1. Dry run (preview)")
        print("  2. Process with auto-transfer")
        print("  3. Process with minimum amount")
        choice = input(f"\n{Colors.BOLD}Choice (1-3):{Colors.ENDC} ").strip()
        
        if choice == '1':
            run_command('python scripts/daily_payout_processor.py --dry-run')
        elif choice == '2':
            confirm = input(f"{Colors.FAIL}⚠️  This will process payouts. Continue? (yes/no):{Colors.ENDC} ").strip().lower()
            if confirm == 'yes':
                run_command('python scripts/daily_payout_processor.py --auto-process')
        elif choice == '3':
            min_amount = input(f"{Colors.BOLD}Minimum amount (e.g., 10.00):{Colors.ENDC} ").strip()
            if min_amount:
                run_command(f'python scripts/daily_payout_processor.py --auto-process --min-amount {min_amount}')
    
    elif 'export_accounting' in script_name:
        print(f"{Colors.WARNING}Export Accounting Reports{Colors.ENDC}")
        print("Options:")
        print("  1. All reports")
        print("  2. Revenue only")
        print("  3. Expenses only")
        print("  4. Artist 1099-NEC")
        print("  5. Platform revenue")
        choice = input(f"\n{Colors.BOLD}Choice (1-5):{Colors.ENDC} ").strip()
        
        year = input(f"{Colors.BOLD}Year (default: {datetime.now().year}):{Colors.ENDC} ").strip() or str(datetime.now().year)
        
        if choice == '1':
            run_command(f'python scripts/export_accounting.py --type all --year {year}')
        elif choice == '2':
            run_command(f'python scripts/export_accounting.py --type revenue --year {year}')
        elif choice == '3':
            run_command(f'python scripts/export_accounting.py --type expenses --year {year}')
        elif choice == '4':
            run_command(f'python scripts/export_accounting.py --type artist-1099 --year {year}')
        elif choice == '5':
            run_command(f'python scripts/export_accounting.py --type platform-revenue --year {year}')
    
    elif 'test_send_email' in script_name or 'check_email' in script_name:
        # Simple scripts, just run them
        run_command(base_command)
    
    else:
        # Default: show help
        run_command(base_command)


def run_command(command: str):
    """Run a shell command and display output."""
    print(f"\n{Colors.BOLD}{Colors.OKGREEN}Executing:{Colors.ENDC} {command}\n")
    print(f"{Colors.OKCYAN}{'=' * 60}{Colors.ENDC}\n")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=False,
            text=True
        )
        print(f"\n{Colors.OKCYAN}{'=' * 60}{Colors.ENDC}")
        if result.returncode == 0:
            print(f"{Colors.OKGREEN}✅ Command completed successfully{Colors.ENDC}\n")
        else:
            print(f"{Colors.FAIL}❌ Command exited with code {result.returncode}{Colors.ENDC}\n")
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  Command interrupted by user{Colors.ENDC}\n")
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Error: {e}{Colors.ENDC}\n")
    
    input(f"{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")


def main():
    """Main dashboard loop."""
    scripts = [
        {
            'name': 'Scan Artist Payouts',
            'script': 'scan_artist_payouts.py',
            'description': 'Find all artists with pending tips needing payouts',
            'command': 'python scripts/scan_artist_payouts.py',
            'interactive': False
        },
        {
            'name': 'Send Artist Payout',
            'script': 'send_artist_payout.py',
            'description': 'Process individual artist payouts',
            'command': 'python scripts/send_artist_payout.py',
            'interactive': True
        },
        {
            'name': 'Batch Process Payouts',
            'script': 'batch_process_payouts.py',
            'description': 'Batch process all pending payouts via Stripe',
            'command': 'python scripts/batch_process_payouts.py',
            'interactive': True
        },
        {
            'name': 'Daily Payout Processor',
            'script': 'daily_payout_processor.py',
            'description': 'Automated daily payout processing (scan + process)',
            'command': 'python scripts/daily_payout_processor.py',
            'interactive': True
        },
        {
            'name': 'Export Accounting',
            'script': 'export_accounting.py',
            'description': 'Generate tax-ready accounting reports (CSV)',
            'command': 'python scripts/export_accounting.py',
            'interactive': True
        },
        {
            'name': 'Test Email Notifications',
            'script': 'test_send_email_to_alex.py',
            'description': 'Test all email notification types',
            'command': 'python scripts/test_send_email_to_alex.py',
            'interactive': False
        },
        {
            'name': 'Check Email Config',
            'script': 'check_email_config.py',
            'description': 'Check email service configuration',
            'command': 'python scripts/check_email_config.py',
            'interactive': False
        },
    ]
    
    while True:
        show_dashboard()
        
        choice = input(f"{Colors.BOLD}{Colors.OKGREEN}Select option:{Colors.ENDC} ").strip().lower()
        
        if choice == 'q' or choice == 'quit' or choice == 'exit':
            print(f"\n{Colors.OKGREEN}👋 Goodbye!{Colors.ENDC}\n")
            break
        elif choice == '0':
            continue  # Refresh dashboard
        elif choice == '8':
            show_data_view('recent_tips')
        elif choice == '9':
            show_data_view('recent_payouts')
        elif choice == '10':
            show_data_view('pending_payouts')
        elif choice == '11':
            show_data_view('recent_purchases')
        elif choice == '12':
            show_data_view('wallet_transactions')
        elif choice == '13':
            show_data_view('artist_summary')
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(scripts):
                run_script_interactive(scripts[idx])
            else:
                print(f"\n{Colors.FAIL}❌ Invalid option. Please try again.{Colors.ENDC}\n")
                input(f"{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}❌ Invalid option. Please try again.{Colors.ENDC}\n")
            input(f"{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.OKGREEN}👋 Goodbye!{Colors.ENDC}\n")
        sys.exit(0)
