"""
Centralized fee calculation for payments and boosts.

All payment-related fee constants and calculations should be here
to ensure consistency across the platform.
"""
from decimal import Decimal


# Fee Constants - single source of truth
PLATFORM_FEE_PERCENT = Decimal("0.075")  # 7.5%
STRIPE_PERCENTAGE = Decimal("0.029")     # 2.9%
STRIPE_FIXED = Decimal("0.30")           # $0.30


def calculate_boost_fees(boost_amount: Decimal):
    """
    Calculate all fees for a boost.

    Logic:
    - Artist receives 100% of boost_amount
    - Tipper pays: boost_amount + stripe_fee + platform_fee

    Args:
        boost_amount: The amount the tipper wants to give to the artist

    Returns:
        tuple: (stripe_fee, platform_fee, total_charge, artist_payout, platform_revenue)
    """
    # Round boost amount to 2 decimals
    boost_amount = round(boost_amount, 2)

    # Calculate Stripe fee: (boost_amount * 2.9%) + $0.30
    stripe_fee = round((boost_amount * STRIPE_PERCENTAGE) + STRIPE_FIXED, 2)

    # Calculate platform fee: boost_amount * 7.5%
    platform_fee = round(boost_amount * PLATFORM_FEE_PERCENT, 2)

    # Total charge to tipper
    total_charge = round(boost_amount + stripe_fee + platform_fee, 2)

    # Artist receives 100% of boost amount
    artist_payout = boost_amount

    # Platform revenue is the platform fee
    platform_revenue = platform_fee

    return stripe_fee, platform_fee, total_charge, artist_payout, platform_revenue


def calculate_fee_and_net(amount: Decimal):
    """
    Calculate platform fee and net amount after fee.

    Used for simple fee calculations where we just need to know
    the platform's cut and what remains.

    Args:
        amount: The total amount

    Returns:
        tuple: (fee, net) where fee is platform's cut and net is remainder
    """
    fee = amount * PLATFORM_FEE_PERCENT
    net = amount - fee
    return fee, net
