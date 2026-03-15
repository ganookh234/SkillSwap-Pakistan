from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, SkillOffering, SkillWanted, Message, Category

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Check if user is admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please sign in first.', 'info')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('Access denied. Admin only!', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@admin_required
def dashboard():
    total_users = User.query.count()
    total_skills = SkillOffering.query.count()
    total_wanted = SkillWanted.query.count()
    total_messages = Message.query.count()
    total_categories = Category.query.count()

    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()

    # City stats
    city_stats = db.session.query(
        User.city, db.func.count(User.id)
    ).filter(User.city.isnot(None), User.city != '').group_by(
        User.city
    ).order_by(db.func.count(User.id).desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_skills=total_skills,
                           total_wanted=total_wanted,
                           total_messages=total_messages,
                           total_categories=total_categories,
                           recent_users=recent_users,
                           city_stats=city_stats)


@admin_bp.route('/users')
@admin_required
def manage_users():
    search = request.args.get('search', '')
    if search:
        users = User.query.filter(
            User.full_name.ilike(f'%{search}%') |
            User.email.ilike(f'%{search}%') |
            User.city.ilike(f'%{search}%')
        ).order_by(User.created_at.desc()).all()
    else:
        users = User.query.order_by(User.created_at.desc()).all()

    return render_template('admin/users.html', users=users, search=search)


@admin_bp.route('/users/delete/<int:user_id>')
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Cannot delete admin user!', 'danger')
        return redirect(url_for('admin.manage_users'))

    # Delete related data
    SkillOffering.query.filter_by(user_id=user.id).delete()
    SkillWanted.query.filter_by(user_id=user.id).delete()
    Message.query.filter(
        (Message.sender_id == user.id) | (Message.receiver_id == user.id)
    ).delete()

    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.full_name} has been deleted.', 'success')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/users/toggle-admin/<int:user_id>')
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Cannot change your own admin status!', 'warning')
        return redirect(url_for('admin.manage_users'))

    user.is_admin = not user.is_admin
    db.session.commit()

    if user.is_admin:
        flash(f'{user.full_name} is now an admin.', 'success')
    else:
        flash(f'{user.full_name} is no longer an admin.', 'info')

    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def manage_categories():
    if request.method == 'POST':
        name = request.form.get('name')
        icon = request.form.get('icon')

        if Category.query.filter_by(name=name).first():
            flash('This category already exists!', 'warning')
        else:
            cat = Category(name=name, icon=icon)
            db.session.add(cat)
            db.session.commit()
            flash(f'Category "{name}" added!', 'success')

        return redirect(url_for('admin.manage_categories'))

    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/categories/delete/<int:cat_id>')
@admin_required
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    flash(f'Category "{cat.name}" deleted.', 'success')
    return redirect(url_for('admin.manage_categories'))


@admin_bp.route('/messages')
@admin_required
def view_messages():
    messages = Message.query.order_by(Message.sent_at.desc()).limit(50).all()
    return render_template('admin/messages.html', messages=messages)


@admin_bp.route('/make-admin')
def make_first_admin():
    """One-time route to make first user admin"""
    admin_exists = User.query.filter_by(is_admin=True).first()
    if admin_exists:
        flash('Admin already exists!', 'info')
        return redirect(url_for('main.index'))

    first_user = User.query.first()
    if first_user:
        first_user.is_admin = True
        db.session.commit()
        flash(f'{first_user.full_name} is now admin!', 'success')
    else:
        flash('No users found. Register first!', 'warning')

    return redirect(url_for('main.index'))