from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import User, SkillOffering, SkillWanted, Category, Message

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    total_users = User.query.count()
    total_skills = SkillOffering.query.count()
    return render_template('index.html',
                           total_users=total_users,
                           total_skills=total_skills)


@main_bp.route('/dashboard')
@login_required
def dashboard():
    my_offerings = SkillOffering.query.filter_by(user_id=current_user.id).all()
    my_wanted = SkillWanted.query.filter_by(user_id=current_user.id).all()

    unread_count = Message.query.filter_by(
        receiver_id=current_user.id,
        is_read=False
    ).count()

    return render_template('dashboard.html',
                           my_offerings=my_offerings,
                           my_wanted=my_wanted,
                           unread_count=unread_count)


@main_bp.route('/about')
def about():
    total_users = User.query.count()
    return render_template('about.html', total_users=total_users)


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash('Thank you! Your message has been sent successfully.', 'success')
        return redirect(url_for('main.contact'))
    return render_template('contact.html')


@main_bp.route('/pricing')
def pricing():
    return render_template('pricing.html')