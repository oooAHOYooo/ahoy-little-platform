#!/bin/bash
# Daily payout processor - Run this via cron or Render cron job
# 
# To schedule daily at 9 AM UTC:
# 0 9 * * * /path/to/scripts/schedule_daily_payouts.sh
#
# Or use Render Cron Job:
# - Command: python scripts/daily_payout_processor.py --auto-process
# - Schedule: 0 9 * * * (9 AM UTC daily)

cd "$(dirname "$0")/.." || exit 1

# Run the daily payout processor with auto-processing enabled
python scripts/daily_payout_processor.py --auto-process --min-amount 1.00
