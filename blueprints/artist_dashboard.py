#!/usr/bin/env python3
"""
Artist Dashboard Blueprint for Ahoy Indie Media

Provides:
- Artist profile claiming
- Artist dashboard with earnings, plays, and audience stats
- Payout history and settings
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from decimal import Decimal
from datetime import datetime, timedelta
import json
import os
import uuid

from db import get_session
from models import ArtistClaim, Tip, User, ListeningSession, UserArtistFollow, ArtistPayout

bp = Blueprint("artist_dashboard", __name__, url_prefix="/artist-dashboard")


def load_artists():
    """Load artists from JSON file."""
    try:
        with open('static/data/artists.json', 'r') as f:
            data = json.load(f)
            return data.get('artists', [])
    except Exception:
        return []


def find_artist_by_id(artist_id):
    """Find an artist by ID or slug."""
    artists = load_artists()
    for artist in artists:
        if (str(artist.get('id', '')) == str(artist_id) or
            artist.get('slug', '').lower() == str(artist_id).lower() or
            artist.get('name', '').lower() == str(artist_id).lower()):
            return artist
    return None


def get_user_artist_claims(user_id):
    """Get all artist claims for a user."""
    with get_session() as db_session:
        claims = db_session.query(ArtistClaim).filter(
            ArtistClaim.user_id == user_id
        ).all()
        return [
            {
                'id': c.id,
                'artist_id': c.artist_id,
                'artist_name': c.artist_name,
                'status': c.status,
                'created_at': c.created_at.isoformat() if c.created_at else None,
                'verified_at': c.verified_at.isoformat() if c.verified_at else None,
            }
            for c in claims
        ]


@bp.route('/')
@login_required
def dashboard_home():
    """Artist dashboard home - shows list of claimed artists or claim form."""
    claims = get_user_artist_claims(current_user.id)
    verified_claims = [c for c in claims if c['status'] == 'verified']

    if verified_claims:
        # Redirect to first verified artist's dashboard
        return redirect(url_for('artist_dashboard.artist_stats', artist_id=verified_claims[0]['artist_id']))

    return render_template('artist_dashboard/home.html', claims=claims)


@bp.route('/claim', methods=['GET', 'POST'])
@login_required
def claim_artist():
    """Claim an artist profile."""
    if request.method == 'GET':
        artists = load_artists()
        # Filter out already claimed artists
        with get_session() as db_session:
            claimed_ids = {c.artist_id for c in db_session.query(ArtistClaim.artist_id).filter(
                ArtistClaim.status.in_(['pending', 'verified'])
            ).all()}
        available_artists = [a for a in artists if a.get('slug') not in claimed_ids and a.get('id') not in claimed_ids]
        return render_template('artist_dashboard/claim.html', artists=available_artists)

    # POST - submit claim
    data = request.get_json(silent=True) or request.form.to_dict()
    artist_id = data.get('artist_id')

    if not artist_id:
        if request.is_json:
            return jsonify({'error': 'Artist ID required'}), 400
        flash('Please select an artist to claim', 'error')
        return redirect(url_for('artist_dashboard.claim_artist'))

    artist = find_artist_by_id(artist_id)
    if not artist:
        if request.is_json:
            return jsonify({'error': 'Artist not found'}), 404
        flash('Artist not found', 'error')
        return redirect(url_for('artist_dashboard.claim_artist'))

    try:
        with get_session() as db_session:
            # Check if already claimed
            existing = db_session.query(ArtistClaim).filter(
                ArtistClaim.artist_id == artist.get('slug', artist.get('id'))
            ).first()
            if existing:
                if request.is_json:
                    return jsonify({'error': 'This artist has already been claimed'}), 400
                flash('This artist has already been claimed', 'error')
                return redirect(url_for('artist_dashboard.claim_artist'))

            # Create claim
            verification_code = str(uuid.uuid4())[:8].upper()
            claim = ArtistClaim(
                user_id=current_user.id,
                artist_id=artist.get('slug', artist.get('id')),
                artist_name=artist.get('name'),
                status='pending',
                verification_code=verification_code,
                created_at=datetime.utcnow(),
            )
            db_session.add(claim)
            db_session.commit()

            # TODO: Send verification email to admin
            # For now, auto-verify for testing (remove in production)
            if os.getenv('AHOY_ENV') != 'production':
                claim.status = 'verified'
                claim.verified_at = datetime.utcnow()
                db_session.commit()

            if request.is_json:
                return jsonify({
                    'success': True,
                    'claim_id': claim.id,
                    'status': claim.status,
                    'verification_code': verification_code,
                }), 201

            flash(f'Claim submitted for {artist.get("name")}! Status: {claim.status}', 'success')
            return redirect(url_for('artist_dashboard.dashboard_home'))

    except Exception as e:
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Error submitting claim: {str(e)}', 'error')
        return redirect(url_for('artist_dashboard.claim_artist'))


@bp.route('/stats/<artist_id>')
@login_required
def artist_stats(artist_id):
    """Show artist dashboard with stats."""
    # Verify user owns this artist claim
    with get_session() as db_session:
        claim = db_session.query(ArtistClaim).filter(
            ArtistClaim.user_id == current_user.id,
            ArtistClaim.artist_id == artist_id,
            ArtistClaim.status == 'verified'
        ).first()

        if not claim:
            flash('You do not have access to this artist dashboard', 'error')
            return redirect(url_for('artist_dashboard.dashboard_home'))

        artist = find_artist_by_id(artist_id)
        if not artist:
            flash('Artist not found', 'error')
            return redirect(url_for('artist_dashboard.dashboard_home'))

        # Get all user's verified claims for sidebar
        all_claims = db_session.query(ArtistClaim).filter(
            ArtistClaim.user_id == current_user.id,
            ArtistClaim.status == 'verified'
        ).all()

        return render_template('artist_dashboard/stats.html',
                               artist=artist,
                               artist_id=artist_id,
                               claim=claim,
                               all_claims=all_claims)


@bp.route('/api/stats/<artist_id>')
@login_required
def api_artist_stats(artist_id):
    """API endpoint for artist statistics."""
    # Verify user owns this artist claim
    with get_session() as db_session:
        claim = db_session.query(ArtistClaim).filter(
            ArtistClaim.user_id == current_user.id,
            ArtistClaim.artist_id == artist_id,
            ArtistClaim.status == 'verified'
        ).first()

        if not claim:
            return jsonify({'error': 'Unauthorized'}), 403

        # Get earnings
        tips = db_session.query(Tip).filter(Tip.artist_id == artist_id).all()
        total_earnings = sum(float(t.artist_payout or t.amount) for t in tips)
        total_boosts = len(tips)
        pending_payout = total_earnings  # TODO: subtract completed payouts

        # Get completed payouts
        payouts = db_session.query(ArtistPayout).filter(
            ArtistPayout.artist_id == artist_id,
            ArtistPayout.status == 'completed'
        ).all()
        total_paid_out = sum(float(p.amount) for p in payouts)
        pending_payout = total_earnings - total_paid_out

        # Get follower count
        follower_count = db_session.query(UserArtistFollow).filter(
            UserArtistFollow.artist_id == artist_id
        ).count()

        # Get play stats (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        # Load artist's music/shows to get media IDs
        artist = find_artist_by_id(artist_id)
        media_ids = []
        if artist:
            for track in artist.get('tracks', []) + artist.get('albums', []):
                media_ids.append(str(track.get('id', '')))
            for show in artist.get('shows', []):
                media_ids.append(str(show.get('id', '')))

        play_count = 0
        total_listen_time = 0
        if media_ids:
            sessions = db_session.query(ListeningSession).filter(
                ListeningSession.media_id.in_(media_ids),
                ListeningSession.started_at >= thirty_days_ago
            ).all()
            play_count = len(sessions)
            total_listen_time = sum(s.seconds or 0 for s in sessions)

        # Recent boosts
        recent_tips = sorted(tips, key=lambda t: t.created_at or datetime.min, reverse=True)[:10]

        return jsonify({
            'artist_id': artist_id,
            'artist_name': claim.artist_name,
            'earnings': {
                'total': round(total_earnings, 2),
                'pending_payout': round(pending_payout, 2),
                'total_paid_out': round(total_paid_out, 2),
                'boost_count': total_boosts,
            },
            'audience': {
                'followers': follower_count,
                'plays_30d': play_count,
                'listen_time_30d_minutes': round(total_listen_time / 60, 1),
            },
            'recent_boosts': [
                {
                    'amount': float(t.amount),
                    'artist_payout': float(t.artist_payout) if t.artist_payout else float(t.amount),
                    'created_at': t.created_at.isoformat() if t.created_at else None,
                }
                for t in recent_tips
            ],
        })


@bp.route('/api/payouts/<artist_id>')
@login_required
def api_artist_payouts(artist_id):
    """API endpoint for artist payout history."""
    with get_session() as db_session:
        # Verify ownership
        claim = db_session.query(ArtistClaim).filter(
            ArtistClaim.user_id == current_user.id,
            ArtistClaim.artist_id == artist_id,
            ArtistClaim.status == 'verified'
        ).first()

        if not claim:
            return jsonify({'error': 'Unauthorized'}), 403

        payouts = db_session.query(ArtistPayout).filter(
            ArtistPayout.artist_id == artist_id
        ).order_by(ArtistPayout.created_at.desc()).limit(50).all()

        return jsonify({
            'payouts': [
                {
                    'id': p.id,
                    'amount': float(p.amount),
                    'status': p.status,
                    'payment_method': p.payment_method,
                    'created_at': p.created_at.isoformat() if p.created_at else None,
                    'completed_at': p.completed_at.isoformat() if p.completed_at else None,
                }
                for p in payouts
            ]
        })


@bp.route('/settings/<artist_id>', methods=['GET', 'POST'])
@login_required
def artist_settings(artist_id):
    """Artist settings page."""
    with get_session() as db_session:
        claim = db_session.query(ArtistClaim).filter(
            ArtistClaim.user_id == current_user.id,
            ArtistClaim.artist_id == artist_id,
            ArtistClaim.status == 'verified'
        ).first()

        if not claim:
            flash('Unauthorized', 'error')
            return redirect(url_for('artist_dashboard.dashboard_home'))

        if request.method == 'POST':
            data = request.form.to_dict()
            claim.payout_email = data.get('payout_email', claim.payout_email)
            db_session.commit()
            flash('Settings updated', 'success')
            return redirect(url_for('artist_dashboard.artist_settings', artist_id=artist_id))

        artist = find_artist_by_id(artist_id)
        all_claims = db_session.query(ArtistClaim).filter(
            ArtistClaim.user_id == current_user.id,
            ArtistClaim.status == 'verified'
        ).all()

        return render_template('artist_dashboard/settings.html',
                               artist=artist,
                               artist_id=artist_id,
                               claim=claim,
                               all_claims=all_claims)
