from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user
import uuid
import hashlib
from datetime import datetime

from db import get_session
from models import Feedback

bp = Blueprint("api_feedback", __name__, url_prefix="/api/feedback")

def generate_claim_code(user_id, message):
    """Generate a unique sticker claim code"""
    # Create a unique-ish string for the claim code
    seed = f"{user_id or 'anon'}-{message[:20]}-{uuid.uuid4()}"
    return hashlib.md5(seed.encode()).hexdigest()[:8].upper()

@bp.post("/")
def submit_feedback():
    data = request.get_json(silent=True) or {}
    fb_type = data.get("type", "general")
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "message_required"}), 400

    user_id = current_user.id if current_user.is_authenticated else None
    claim_code = generate_claim_code(user_id, message)

    try:
        with get_session() as db_session:
            feedback = Feedback(
                user_id=user_id,
                message=message,
                type=fb_type,
                claim_code=claim_code
            )
            db_session.add(feedback)
            db_session.commit()

            return jsonify({
                "success": True,
                "claim_code": claim_code
            }), 201
    except Exception as e:
        current_app.logger.exception("Feedback submission failed")
        return jsonify({"error": "submission_failed", "detail": str(e)}), 500
