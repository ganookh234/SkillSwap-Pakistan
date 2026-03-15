from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Notification

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/notifications')
@login_required
def all_notifications():
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).limit(50).all()

    return render_template('notifications.html', notifications=notifications)


@notifications_bp.route('/notifications/read/<int:notif_id>')
@login_required
def mark_read(notif_id):
    notif = Notification.query.get_or_404(notif_id)

    if notif.user_id != current_user.id:
        flash('Unauthorized!', 'danger')
        return redirect(url_for('main.dashboard'))

    notif.is_read = True
    db.session.commit()

    if notif.link:
        return redirect(notif.link)

    return redirect(url_for('notifications.all_notifications'))


@notifications_bp.route('/notifications/read-all')
@login_required
def mark_all_read():
    Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).update({'is_read': True})
    db.session.commit()

    flash('All notifications marked as read!', 'success')
    return redirect(url_for('notifications.all_notifications'))


@notifications_bp.route('/notifications/delete/<int:notif_id>')
@login_required
def delete_notification(notif_id):
    notif = Notification.query.get_or_404(notif_id)

    if notif.user_id != current_user.id:
        flash('Unauthorized!', 'danger')
        return redirect(url_for('main.dashboard'))

    db.session.delete(notif)
    db.session.commit()

    return redirect(url_for('notifications.all_notifications'))


@notifications_bp.route('/notifications/clear-all')
@login_required
def clear_all():
    Notification.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()

    flash('All notifications cleared!', 'success')
    return redirect(url_for('notifications.all_notifications'))