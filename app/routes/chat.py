from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Message, User

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/chat')
@login_required
def chat_list():
    # Get all unique chat partners
    sent = db.session.query(Message.receiver_id).filter(
        Message.sender_id == current_user.id
    ).distinct().all()

    received = db.session.query(Message.sender_id).filter(
        Message.receiver_id == current_user.id
    ).distinct().all()

    partner_ids = set()
    for s in sent:
        partner_ids.add(s[0])
    for r in received:
        partner_ids.add(r[0])

    # Get partner details with last message
    conversations = []
    for pid in partner_ids:
        partner = User.query.get(pid)
        if partner:
            last_msg = Message.query.filter(
                ((Message.sender_id == current_user.id) & (Message.receiver_id == pid)) |
                ((Message.sender_id == pid) & (Message.receiver_id == current_user.id))
            ).order_by(Message.sent_at.desc()).first()

            unread = Message.query.filter_by(
                sender_id=pid,
                receiver_id=current_user.id,
                is_read=False
            ).count()

            conversations.append({
                'partner': partner,
                'last_message': last_msg,
                'unread': unread
            })

    # Sort by last message time
    conversations.sort(
        key=lambda x: x['last_message'].sent_at if x['last_message'] else '',
        reverse=True
    )

    return render_template('chat_list.html', conversations=conversations)


@chat_bp.route('/chat/<int:user_id>', methods=['GET', 'POST'])
@login_required
def chat_room(user_id):
    other_user = User.query.get_or_404(user_id)

    if other_user.id == current_user.id:
        flash('You cannot chat with yourself!', 'warning')
        return redirect(url_for('chat.chat_list'))

    if request.method == 'POST':
        message_text = request.form.get('message')
        if message_text and message_text.strip():
            msg = Message(
                sender_id=current_user.id,
                receiver_id=user_id,
                message_text=message_text.strip()
            )
            db.session.add(msg)
            db.session.commit()
        return redirect(url_for('chat.chat_room', user_id=user_id))

    # Get all messages between two users
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.sent_at.asc()).all()

    # Mark unread messages as read
    unread = Message.query.filter_by(
        sender_id=user_id,
        receiver_id=current_user.id,
        is_read=False
    ).all()
    for msg in unread:
        msg.is_read = True
    db.session.commit()

    return render_template('chat_room.html',
                           other_user=other_user,
                           messages=messages)


@chat_bp.route('/chat/start/<int:user_id>')
@login_required
def start_chat(user_id):
    other_user = User.query.get_or_404(user_id)
    if other_user.id == current_user.id:
        flash('You cannot chat with yourself!', 'warning')
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('chat.chat_room', user_id=user_id))