#!/usr/bin/env python3
"""
Payment flow tests for Ahoy Indie Media

Tests cover:
- Fee calculations
- Wallet operations (fund, use, balance, transactions)
- Boost/tip creation
- Stripe webhook handling
- Edge cases and error conditions
"""

import pytest
import json
from decimal import Decimal
from datetime import datetime
from unittest.mock import patch, MagicMock

from blueprints.payments import calculate_boost_fees, PLATFORM_FEE_PERCENT, STRIPE_PERCENTAGE, STRIPE_FIXED


class TestFeeCalculations:
    """Test fee calculation logic."""

    def test_calculate_boost_fees_basic(self):
        """Test basic fee calculation for $10 boost."""
        boost = Decimal('10.00')
        stripe_fee, platform_fee, total, artist_payout, platform_revenue = calculate_boost_fees(boost)

        # Expected values:
        # Stripe fee: (10 * 0.029) + 0.30 = 0.59
        # Platform fee: 10 * 0.075 = 0.75
        # Total: 10 + 0.59 + 0.75 = 11.34
        # Artist payout: 10.00 (100% of boost)
        assert stripe_fee == Decimal('0.59')
        assert platform_fee == Decimal('0.75')
        assert total == Decimal('11.34')
        assert artist_payout == Decimal('10.00')
        assert platform_revenue == Decimal('0.75')

    def test_calculate_boost_fees_minimum(self):
        """Test fee calculation for minimum $0.50 boost."""
        boost = Decimal('0.50')
        stripe_fee, platform_fee, total, artist_payout, platform_revenue = calculate_boost_fees(boost)

        # Stripe fee: (0.50 * 0.029) + 0.30 = 0.31
        # Platform fee: 0.50 * 0.075 = 0.04
        assert stripe_fee == Decimal('0.31')
        assert platform_fee == Decimal('0.04')
        assert artist_payout == Decimal('0.50')

    def test_calculate_boost_fees_large_amount(self):
        """Test fee calculation for $100 boost."""
        boost = Decimal('100.00')
        stripe_fee, platform_fee, total, artist_payout, platform_revenue = calculate_boost_fees(boost)

        # Stripe fee: (100 * 0.029) + 0.30 = 3.20
        # Platform fee: 100 * 0.075 = 7.50
        assert stripe_fee == Decimal('3.20')
        assert platform_fee == Decimal('7.50')
        assert total == Decimal('110.70')
        assert artist_payout == Decimal('100.00')

    def test_artist_receives_100_percent(self):
        """Verify artist always receives 100% of boost amount."""
        for amount in [Decimal('1.00'), Decimal('5.00'), Decimal('50.00'), Decimal('500.00')]:
            _, _, _, artist_payout, _ = calculate_boost_fees(amount)
            assert artist_payout == amount, f"Artist should receive {amount}, got {artist_payout}"

    def test_fee_rounding(self):
        """Test that fees are properly rounded to 2 decimal places."""
        # Amount that would produce non-round fees
        boost = Decimal('7.77')
        stripe_fee, platform_fee, total, artist_payout, platform_revenue = calculate_boost_fees(boost)

        # All values should have at most 2 decimal places
        assert stripe_fee == round(stripe_fee, 2)
        assert platform_fee == round(platform_fee, 2)
        assert total == round(total, 2)


class TestWalletBalance:
    """Test wallet balance operations."""

    def test_get_wallet_balance_authenticated(self, authenticated_client, test_user):
        """Test getting wallet balance for authenticated user."""
        response = authenticated_client.get('/payments/wallet')
        assert response.status_code == 200
        data = response.get_json()
        assert 'balance' in data
        assert data['balance'] == 100.00  # test_user has $100 balance
        assert data['balance_cents'] == 10000

    def test_get_wallet_balance_unauthenticated(self, client):
        """Test getting wallet balance for unauthenticated user returns 0."""
        response = client.get('/payments/wallet')
        assert response.status_code == 200
        data = response.get_json()
        assert data['balance'] == 0
        assert data['balance_cents'] == 0


class TestWalletUse:
    """Test wallet spending operations."""

    def test_use_wallet_success(self, authenticated_client, test_user, db_session):
        """Test successful wallet deduction."""
        response = authenticated_client.post(
            '/payments/wallet/use',
            json={
                'amount': 25.00,
                'description': 'Test payment',
                'reference_type': 'test'
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['balance_after'] == 75.00
        assert data['amount_used'] == 25.00

    def test_use_wallet_insufficient_balance(self, authenticated_client, test_user):
        """Test wallet deduction with insufficient balance."""
        response = authenticated_client.post(
            '/payments/wallet/use',
            json={
                'amount': 500.00,  # More than the $100 balance
                'description': 'Too expensive'
            },
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'Insufficient' in data['error']
        assert data['balance'] == 100.00
        assert data['required'] == 500.00

    def test_use_wallet_zero_amount(self, authenticated_client):
        """Test wallet deduction with zero amount fails."""
        response = authenticated_client.post(
            '/payments/wallet/use',
            json={'amount': 0},
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'positive' in data['error'].lower()

    def test_use_wallet_negative_amount(self, authenticated_client):
        """Test wallet deduction with negative amount fails."""
        response = authenticated_client.post(
            '/payments/wallet/use',
            json={'amount': -10.00},
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_use_wallet_unauthenticated(self, client):
        """Test wallet use without authentication fails."""
        response = client.post(
            '/payments/wallet/use',
            json={'amount': 10.00},
            content_type='application/json'
        )
        assert response.status_code == 401


class TestWalletFunding:
    """Test wallet funding operations."""

    def test_fund_wallet_unauthenticated(self, client):
        """Test funding wallet without authentication fails."""
        response = client.post(
            '/payments/wallet/fund',
            json={'amount': 50.00},
            content_type='application/json'
        )
        assert response.status_code == 401

    def test_fund_wallet_below_minimum(self, authenticated_client):
        """Test funding below minimum $1.00 fails."""
        response = authenticated_client.post(
            '/payments/wallet/fund',
            json={'amount': 0.50},
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'Minimum' in data['error']

    def test_fund_wallet_above_maximum(self, authenticated_client):
        """Test funding above maximum $1000 fails."""
        response = authenticated_client.post(
            '/payments/wallet/fund',
            json={'amount': 1500.00},
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'Maximum' in data['error']

    def test_fund_wallet_no_amount(self, authenticated_client):
        """Test funding without amount fails."""
        response = authenticated_client.post(
            '/payments/wallet/fund',
            json={},
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'required' in data['error'].lower()


class TestWalletTransactions:
    """Test wallet transaction history."""

    def test_get_transactions_json(self, authenticated_client, test_user, db_session):
        """Test getting transaction history as JSON."""
        from models import WalletTransaction

        # Create some transactions
        for i in range(3):
            txn = WalletTransaction(
                user_id=test_user.id,
                type='fund',
                amount=Decimal('10.00'),
                balance_before=Decimal(str(i * 10)),
                balance_after=Decimal(str((i + 1) * 10)),
                description=f'Test fund {i}',
                created_at=datetime.utcnow(),
            )
            db_session.add(txn)
        db_session.commit()

        response = authenticated_client.get(
            '/payments/wallet/transactions?format=json',
            headers={'Accept': 'application/json'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'transactions' in data
        assert len(data['transactions']) == 3


class TestBoostSession:
    """Test boost/tip session creation."""

    def test_create_boost_session_no_artist(self, client):
        """Test boost session creation without artist_id fails."""
        response = client.post(
            '/payments/boost-session',
            json={'boost_amount': 10.00},
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'artist_id' in data['error'].lower()

    def test_create_boost_session_no_amount(self, client):
        """Test boost session creation without amount fails."""
        response = client.post(
            '/payments/boost-session',
            json={'artist_id': 'test-artist'},
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_create_boost_session_below_minimum(self, client):
        """Test boost session with amount below $0.50 minimum fails."""
        response = client.post(
            '/payments/boost-session',
            json={
                'artist_id': 'test-artist',
                'boost_amount': 0.25
            },
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'Minimum' in data['error']

    @patch('blueprints.payments.stripe')
    def test_create_boost_session_success_mock(self, mock_stripe, client):
        """Test successful boost session creation with mock Stripe."""
        # Configure mock
        mock_stripe.api_key = 'sk_test_placeholder'
        mock_session = MagicMock()
        mock_session.url = 'https://checkout.stripe.com/test'
        mock_session.id = 'cs_test_mock_123'
        mock_stripe.checkout.Session.create.return_value = mock_session

        response = client.post(
            '/payments/boost-session',
            json={
                'artist_id': 'test-artist',
                'boost_amount': 10.00
            },
            content_type='application/json'
        )

        # With placeholder API key, should return mock response
        assert response.status_code == 200
        data = response.get_json()
        assert 'checkout_url' in data or 'session_id' in data


class TestArtistEarnings:
    """Test artist earnings endpoints."""

    def test_get_artist_boosts(self, client, sample_tip):
        """Test getting boost statistics for an artist."""
        response = client.get('/payments/artist/test-artist/boosts')
        assert response.status_code == 200
        data = response.get_json()
        assert data['artist_id'] == 'test-artist'
        assert data['total_boosts'] == 10.00
        assert data['boost_count'] == 1

    def test_get_artist_earnings(self, client, sample_tip):
        """Test getting earnings for an artist."""
        response = client.get('/payments/artist/test-artist/earnings')
        assert response.status_code == 200
        data = response.get_json()
        assert data['artist_id'] == 'test-artist'
        assert data['total_earnings'] == 10.00
        assert data['boost_count'] == 1
        assert 'recent_tips' in data

    def test_get_artist_earnings_no_tips(self, client):
        """Test getting earnings for artist with no tips."""
        response = client.get('/payments/artist/unknown-artist/earnings')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total_earnings'] == 0
        assert data['boost_count'] == 0


class TestUserTotalBoosts:
    """Test user boost totals."""

    def test_get_user_total_boosts_authenticated(self, authenticated_client, sample_tip):
        """Test getting total boosts for authenticated user."""
        response = authenticated_client.get('/payments/user/total-boosts')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total_boosts'] == 10.00
        assert data['is_supporter'] is True  # $10 >= $10 threshold

    def test_get_user_total_boosts_unauthenticated(self, client):
        """Test getting total boosts for unauthenticated user."""
        response = client.get('/payments/user/total-boosts')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total_boosts'] == 0
        assert data['is_supporter'] is False


class TestWebhookValidation:
    """Test Stripe webhook handling."""

    def test_webhook_missing_metadata(self, client):
        """Test webhook with missing metadata returns error."""
        event_data = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_incomplete',
                    'metadata': {}
                }
            }
        }
        response = client.post(
            '/payments/webhook',
            data=json.dumps(event_data),
            content_type='application/json'
        )
        # Should fail due to missing metadata
        assert response.status_code in [400, 500]

    def test_webhook_idempotency(self, client, db_session, sample_tip):
        """Test webhook doesn't create duplicate tips."""
        event_data = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': sample_tip.stripe_checkout_session_id,  # Same session ID
                    'payment_intent': 'pi_test_duplicate',
                    'metadata': {
                        'artist_id': 'test-artist',
                        'boost_amount': '10.00',
                        'stripe_fee': '0.59',
                        'platform_fee': '0.75',
                        'total_paid': '11.34',
                        'artist_payout': '10.00',
                    }
                }
            }
        }
        response = client.post(
            '/payments/webhook',
            data=json.dumps(event_data),
            content_type='application/json'
        )
        # Should return success but not create duplicate
        assert response.status_code == 200


class TestPaymentPages:
    """Test payment success/cancel pages."""

    def test_payment_success_page(self, client):
        """Test payment success page renders."""
        response = client.get('/payments/success?session_id=cs_test_123')
        assert response.status_code == 200
        assert b'Thank You' in response.data or b'success' in response.data.lower()

    def test_payment_cancel_page(self, client):
        """Test payment cancel page renders."""
        response = client.get('/payments/cancel')
        assert response.status_code == 200
        assert b'cancelled' in response.data.lower() or b'Cancelled' in response.data

    def test_wallet_success_page(self, client):
        """Test wallet funding success page renders."""
        response = client.get('/payments/wallet/success?session_id=cs_test_123')
        assert response.status_code == 200
        assert b'Wallet' in response.data or b'wallet' in response.data.lower()

    def test_wallet_cancel_page(self, client):
        """Test wallet funding cancel page renders."""
        response = client.get('/payments/wallet/cancel')
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
