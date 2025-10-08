from flask import Blueprint, request, render_template, jsonify, redirect, url_for, flash
from sqlalchemy import func, text, asc, desc

from db import get_session
from models import User, Playlist, PlaylistItem, Bookmark, Feedback
from utils.auth import admin_required, set_impersonate, clear_impersonate
from utils.csrf import csrf_protect, generate_csrf_token


bp = Blueprint("admin", __name__, url_prefix="/admin")


def parse_pagination():
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except Exception:
        page = 1
    try:
        per_page = int(request.args.get("per_page", 50))
    except Exception:
        per_page = 50
    per_page = max(1, min(per_page, 200))
    offset = (page - 1) * per_page
    return page, per_page, offset


def parse_sort(default_field: str = "created_at"):
    sort_raw = (request.args.get("sort") or f"{default_field} desc").strip()
    parts = sort_raw.split()
    field = parts[0]
    direction = parts[1].lower() if len(parts) > 1 else "asc"
    return field, direction


def apply_search(query, model, q):
    if not q:
        return query
    like = f"%{q.lower()}%"
    if model is User:
        return query.filter(func.lower(User.email).like(like))
    if model is Playlist:
        return query.filter(func.lower(Playlist.name).like(like))
    if model is Bookmark:
        return query.filter(func.lower(Bookmark.media_id).like(like))
    if model is Feedback:
        return query.filter(func.lower(Feedback.message).like(like))
    return query


def csv_response(header: list[str], rows: list[tuple]):
    import csv
    from io import StringIO
    si = StringIO()
    w = csv.writer(si)
    w.writerow(header)
    w.writerows(rows)
    from flask import Response
    return Response(si.getvalue(), mimetype='text/csv')


@bp.get("")
@admin_required
def dashboard():
    with get_session() as session:
        counts = {
            'users': session.query(func.count(User.id)).scalar() or 0,
            'playlists': session.query(func.count(Playlist.id)).scalar() or 0,
            'bookmarks': session.query(func.count(Bookmark.id)).scalar() or 0,
            'feedback': session.query(func.count(Feedback.id)).scalar() or 0,
        }
        recent = {
            'users': session.query(User).order_by(desc(User.created_at)).limit(5).all(),
            'playlists': session.query(Playlist).order_by(desc(Playlist.created_at)).limit(5).all(),
            'bookmarks': session.query(Bookmark).order_by(desc(Bookmark.created_at)).limit(5).all(),
            'feedback': session.query(Feedback).order_by(desc(Feedback.created_at)).limit(5).all(),
        }
    return render_template('admin/dashboard.html', counts=counts, recent=recent, csrf_token=generate_csrf_token())


# USERS
@bp.get("/users")
@admin_required
def users_list():
    q = request.args.get("q")
    page, per_page, offset = parse_pagination()
    field, direction = parse_sort("created_at")
    with get_session() as session:
        base = apply_search(session.query(User), User, q)
        total = base.count()
        order_col = getattr(User, field, User.created_at)
        order = desc(order_col) if direction == 'desc' else asc(order_col)
        rows = base.order_by(order).offset(offset).limit(per_page).all()
    return render_template('admin/users_list.html', items=rows, page=page, per_page=per_page, total=total, q=q, sort=f"{field} {direction}", csrf_token=generate_csrf_token())


@bp.get("/users/export.csv")
@admin_required
def users_export():
    q = request.args.get("q")
    field, direction = parse_sort("created_at")
    with get_session() as session:
        base = apply_search(session.query(User), User, q)
        order_col = getattr(User, field, User.created_at)
        order = desc(order_col) if direction == 'desc' else asc(order_col)
        rows = base.order_by(order).all()
        data = [(u.id, u.email, u.is_admin, getattr(u, 'disabled', False), u.created_at.isoformat()) for u in rows]
    return csv_response(["id", "email", "is_admin", "disabled", "created_at"], data)


@bp.get("/users/<int:user_id>")
@admin_required
def users_detail(user_id: int):
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            return redirect(url_for('admin.users_list'))
        playlists = session.query(Playlist).filter(Playlist.user_id == user_id).order_by(desc(Playlist.created_at)).limit(50).all()
        bookmarks = session.query(Bookmark).filter(Bookmark.user_id == user_id).order_by(desc(Bookmark.created_at)).limit(50).all()
    return render_template('admin/users_detail.html', user=user, playlists=playlists, bookmarks=bookmarks, csrf_token=generate_csrf_token())


@bp.post("/users/<int:user_id>/disable")
@admin_required
@csrf_protect
def users_disable(user_id: int):
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            flash("User not found", "warning")
            return redirect(url_for('admin.users_list'))
        # toggle
        current = getattr(user, 'disabled', False)
        user.disabled = not current
        flash("User disabled" if user.disabled else "User enabled", "success")
    return redirect(url_for('admin.users_list'))


@bp.post("/users/<int:user_id>/impersonate")
@admin_required
@csrf_protect
def users_impersonate(user_id: int):
    return set_impersonate(user_id)


@bp.post("/stop-impersonate")
@admin_required
@csrf_protect
def stop_impersonate():
    return clear_impersonate()


# PLAYLISTS
@bp.get("/playlists")
@admin_required
def playlists_list():
    q = request.args.get("q")
    page, per_page, offset = parse_pagination()
    field, direction = parse_sort("created_at")
    with get_session() as session:
        base = apply_search(session.query(Playlist), Playlist, q)
        total = base.count()
        order_col = getattr(Playlist, field, Playlist.created_at)
        order = desc(order_col) if direction == 'desc' else asc(order_col)
        rows = base.order_by(order).offset(offset).limit(per_page).all()
    return render_template('admin/playlists_list.html', items=rows, page=page, per_page=per_page, total=total, q=q, sort=f"{field} {direction}", csrf_token=generate_csrf_token())


@bp.get("/playlists/export.csv")
@admin_required
def playlists_export():
    q = request.args.get("q")
    field, direction = parse_sort("created_at")
    with get_session() as session:
        base = apply_search(session.query(Playlist), Playlist, q)
        order_col = getattr(Playlist, field, Playlist.created_at)
        order = desc(order_col) if direction == 'desc' else asc(order_col)
        rows = base.order_by(order).all()
        data = [(p.id, p.user_id, p.name, p.created_at.isoformat(), p.updated_at.isoformat() if p.updated_at else None) for p in rows]
    return csv_response(["id", "user_id", "name", "created_at", "updated_at"], data)


@bp.post("/playlists/<int:playlist_id>/delete")
@admin_required
@csrf_protect
def playlists_delete(playlist_id: int):
    with get_session() as session:
        pl = session.get(Playlist, playlist_id)
        if not pl:
            flash("Playlist not found", "warning")
        else:
            session.delete(pl)
            flash("Playlist deleted", "success")
    return redirect(url_for('admin.playlists_list'))


# BOOKMARKS
@bp.get("/bookmarks")
@admin_required
def bookmarks_list():
    q = request.args.get("q")
    page, per_page, offset = parse_pagination()
    field, direction = parse_sort("created_at")
    with get_session() as session:
        base = apply_search(session.query(Bookmark), Bookmark, q)
        total = base.count()
        order_col = getattr(Bookmark, field, Bookmark.created_at)
        order = desc(order_col) if direction == 'desc' else asc(order_col)
        rows = base.order_by(order).offset(offset).limit(per_page).all()
    return render_template('admin/bookmarks_list.html', items=rows, page=page, per_page=per_page, total=total, q=q, sort=f"{field} {direction}", csrf_token=generate_csrf_token())


@bp.get("/bookmarks/export.csv")
@admin_required
def bookmarks_export():
    q = request.args.get("q")
    field, direction = parse_sort("created_at")
    with get_session() as session:
        base = apply_search(session.query(Bookmark), Bookmark, q)
        order_col = getattr(Bookmark, field, Bookmark.created_at)
        order = desc(order_col) if direction == 'desc' else asc(order_col)
        rows = base.order_by(order).all()
        data = [(b.id, b.user_id, b.media_id, b.media_type, b.created_at.isoformat()) for b in rows]
    return csv_response(["id", "user_id", "media_id", "media_type", "created_at"], data)


@bp.post("/bookmarks/<int:bookmark_id>/delete")
@admin_required
@csrf_protect
def bookmarks_delete(bookmark_id: int):
    with get_session() as session:
        b = session.get(Bookmark, bookmark_id)
        if not b:
            flash("Bookmark not found", "warning")
        else:
            session.delete(b)
            flash("Bookmark deleted", "success")
    return redirect(url_for('admin.bookmarks_list'))


# FEEDBACK
@bp.get("/feedback")
@admin_required
def feedback_list():
    q = request.args.get("q")
    page, per_page, offset = parse_pagination()
    field, direction = parse_sort("created_at")
    with get_session() as session:
        base = apply_search(session.query(Feedback), Feedback, q)
        total = base.count()
        order_col = getattr(Feedback, field, Feedback.created_at)
        order = desc(order_col) if direction == 'desc' else asc(order_col)
        rows = base.order_by(order).offset(offset).limit(per_page).all()
    return render_template('admin/feedback_list.html', items=rows, page=page, per_page=per_page, total=total, q=q, sort=f"{field} {direction}", csrf_token=generate_csrf_token())


@bp.get("/feedback/export.csv")
@admin_required
def feedback_export():
    q = request.args.get("q")
    field, direction = parse_sort("created_at")
    with get_session() as session:
        base = apply_search(session.query(Feedback), Feedback, q)
        order_col = getattr(Feedback, field, Feedback.created_at)
        order = desc(order_col) if direction == 'desc' else asc(order_col)
        rows = base.order_by(order).all()
        data = [(f.id, f.user_id, f.message, f.created_at.isoformat()) for f in rows]
    return csv_response(["id", "user_id", "message", "created_at"], data)


@bp.post("/feedback/<int:feedback_id>/delete")
@admin_required
@csrf_protect
def feedback_delete(feedback_id: int):
    with get_session() as session:
        f = session.get(Feedback, feedback_id)
        if not f:
            flash("Feedback not found", "warning")
        else:
            session.delete(f)
            flash("Feedback deleted", "success")
    return redirect(url_for('admin.feedback_list'))


