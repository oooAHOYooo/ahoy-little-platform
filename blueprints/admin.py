from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import text
from db import get_session
from models import User, Tip, Purchase, Feedback, ArtistClaim, ArtistTip

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@bp.before_request
def admin_only():
    if not current_user.is_authenticated or not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403

@bp.route('/stats', methods=['GET'])
def get_stats():
    with get_session() as session:
        user_count = session.query(User).count()
        tip_count = session.query(Tip).count()
        purchase_count = session.query(Purchase).count()
        revenue = session.execute(text("SELECT SUM(total) FROM purchases WHERE status = 'paid'")).scalar() or 0
        tip_total = session.execute(text("SELECT SUM(amount) FROM tips")).scalar() or 0
        
    return jsonify({
        'users': user_count,
        'tips': tip_count,
        'purchases': purchase_count,
        'revenue': float(revenue),
        'tip_total': float(tip_total)
    })

@bp.route('/activity', methods=['GET'])
def get_activity():
    with get_session() as session:
        # Recent Users
        users = session.query(User).order_by(User.created_at.desc()).limit(10).all()
        user_events = [{
            'type': 'signup',
            'text': f"New user signed up: {u.username or u.email}",
            'date': u.created_at,
            'user_id': u.id
        } for u in users]

        # Recent Tips
        tips = session.query(Tip).order_by(Tip.created_at.desc()).limit(10).all()
        tip_events = [{
            'type': 'tip',
            'text': f"Tip of ${t.amount} to {t.artist_id}",
            'date': t.created_at,
            'user_id': t.user_id
        } for t in tips]
        
        # Recent Purchases
        purchases = session.query(Purchase).order_by(Purchase.created_at.desc()).limit(10).all()
        purchase_events = [{
            'type': 'purchase',
            'text': f"Purchase of {p.item_id} for ${p.total}",
            'date': p.created_at,
            'user_id': p.user_id
        } for p in purchases]
        
        # Recent Feedback
        feedbacks = session.query(Feedback).order_by(Feedback.created_at.desc()).limit(10).all()
        feedback_events = [{
            'type': 'feedback',
            'text': f"Feedback: {f.message[:50]}...",
            'date': f.created_at,
            'user_id': f.user_id,
            'id': f.id
        } for f in feedbacks]
        
        # Claims
        claims = session.query(ArtistClaim).order_by(ArtistClaim.created_at.desc()).limit(10).all()
        claim_events = [{
            'type': 'claim',
            'text': f"Artist Claim: {c.artist_id} by User {c.user_id}",
            'date': c.created_at,
            'user_id': c.user_id
        } for c in claims]

        all_events = user_events + tip_events + purchase_events + feedback_events + claim_events
        all_events.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify(all_events[:50])

@bp.route('/users', methods=['GET'])
def get_users():
    query = request.args.get('q', '')
    with get_session() as session:
        q = session.query(User)
        if query:
            q = q.filter(User.email.ilike(f"%{query}%") | User.username.ilike(f"%{query}%"))
        
        users = q.order_by(User.created_at.desc()).limit(50).all()
        return jsonify([{
            'id': u.id,
            'email': u.email,
            'username': u.username,
            'is_admin': u.is_admin,
            'disabled': u.disabled,
            'created_at': u.created_at
        } for u in users])

@bp.route('/actions', methods=['GET'])
def get_actions():
    with get_session() as session:
        pending_claims = session.query(ArtistClaim).filter(ArtistClaim.status == 'pending').all()
        claims_data = [{
            'id': c.id,
            'type': 'claim',
            'title': f"Artist Claim: {c.artist_id}",
            'description': f"User {c.user_id} wants to claim {c.artist_id}",
            'created_at': c.created_at
        } for c in pending_claims]
        
        # Example: Unread feedback could be added here if we had a status column
        
    return jsonify(claims_data)

@bp.route('/actions/claim/<int:claim_id>', methods=['POST'])
def handle_claim(claim_id):
    action = request.json.get('action') # approve, reject
    with get_session() as session:
        claim = session.query(ArtistClaim).get(claim_id)
        if not claim:
            return jsonify({'error': 'Claim not found'}), 404
            
        if action == 'approve':
            claim.status = 'verified'
            claim.verified_at = text("NOW()")
        elif action == 'reject':
            claim.status = 'rejected'
        else:
            return jsonify({'error': 'Invalid action'}), 400
            

@bp.route('/analytics/event', methods=['POST'])
def track_event():
    # Public endpoint, but maybe rate limited or checked for session
    data = request.json
    if not data:
        return jsonify({'error': 'No data'}), 400
        
    with get_session() as session:
        event = AnalyticsEvent(
            user_id=current_user.id if current_user.is_authenticated else None,
            event_type=data.get('type', 'page_view'),
            path=data.get('path'),
            metadata_json=data.get('metadata'),
            session_id=session.get('session_id') # If we had one
        )
        session.add(event)
        session.commit()
    return jsonify({'ok': True})

@bp.route('/heatmap', methods=['GET'])
def get_heatmap():
    # Aggregated page views by path
    with get_session() as session:
        # Group by path and count, filter by last 30 days
        # SQLAlchemy simplified grouping
        results = session.execute(text("""
            SELECT path, COUNT(*) as count 
            FROM analytics_events 
            WHERE event_type = 'page_view' 
            GROUP BY path 
            ORDER BY count DESC 
            LIMIT 50
        """)).fetchall()
        
        heatmap_data = [{'path': r[0], 'count': r[1]} for r in results]
        

@bp.route('/users/<int:user_id>/toggle_status', methods=['POST'])
def toggle_user_status(user_id):
    with get_session() as session:
        user = session.query(User).get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent disabling self
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot disable your own account'}), 400
            
        user.disabled = not user.disabled
        session.commit()
        
        status = "disabled" if user.disabled else "enabled"
    return jsonify({'ok': True, 'status': status, 'disabled': user.disabled})

@bp.route('/users/export', methods=['GET'])
def export_users_csv():
    import csv
    import io
    from flask import make_response
    
    with get_session() as session:
        users = session.query(User).order_by(User.created_at.desc()).all()
        
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(['ID', 'Email', 'Username', 'Joined', 'Is Admin', 'Status', 'Wallet Balance'])
        
        for u in users:
            cw.writerow([
                u.id, 
                u.email, 
                u.username or '', 
                u.created_at.isoformat(), 
                'Yes' if u.is_admin else 'No',
                'Disabled' if u.disabled else 'Active',
                u.wallet_balance
            ])
            
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=users_export.csv"
        output.headers["Content-type"] = "text/csv"
        return output
