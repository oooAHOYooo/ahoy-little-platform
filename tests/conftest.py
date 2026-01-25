#!/usr/bin/env python3
"""
Pytest configuration and fixtures for Ahoy Indie Media tests
"""

import pytest
import os
from decimal import Decimal
from datetime import datetime

# Set test environment before importing app
os.environ['AHOY_ENV'] = 'test'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only'
os.environ['WTF_CSRF_ENABLED'] = 'false'

from app import create_app
from db import engine, SessionFactory, get_session
from models import Base, User, Tip, WalletTransaction, UserArtistPosition


@pytest.fixture(scope='session')
def app():
    """Create test app instance with test configuration."""
    test_app = create_app()
    test_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
    })

    # Create tables
    with test_app.app_context():
        Base.metadata.create_all(engine)

    yield test_app

    # Cleanup
    with test_app.app_context():
        Base.metadata.drop_all(engine)


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Provide a clean database session for each test."""
    with app.app_context():
        # Create fresh tables
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        with get_session() as session:
            yield session


@pytest.fixture
def test_user(db_session):
    """Create a test user with wallet balance."""
    from werkzeug.security import generate_password_hash

    user = User(
        email='testuser@example.com',
        username='testuser',
        password_hash=generate_password_hash('testpassword123'),
        wallet_balance=Decimal('100.00'),
        created_at=datetime.utcnow(),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_no_balance(db_session):
    """Create a test user with zero wallet balance."""
    from werkzeug.security import generate_password_hash

    user = User(
        email='brokeuser@example.com',
        username='brokeuser',
        password_hash=generate_password_hash('testpassword123'),
        wallet_balance=Decimal('0.00'),
        created_at=datetime.utcnow(),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def authenticated_client(app, client, test_user):
    """Client with authenticated session."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
        sess['user_id'] = test_user.id
    return client


@pytest.fixture
def sample_tip(db_session, test_user):
    """Create a sample tip record."""
    tip = Tip(
        user_id=test_user.id,
        artist_id='test-artist',
        amount=Decimal('10.00'),
        platform_fee=Decimal('0.75'),
        stripe_fee=Decimal('0.59'),
        total_paid=Decimal('11.34'),
        artist_payout=Decimal('10.00'),
        platform_revenue=Decimal('0.75'),
        stripe_checkout_session_id='cs_test_123',
        stripe_payment_intent_id='pi_test_123',
        created_at=datetime.utcnow(),
    )
    db_session.add(tip)
    db_session.commit()
    db_session.refresh(tip)
    return tip
