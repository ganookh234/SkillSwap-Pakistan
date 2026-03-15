from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, SkillOffering, SkillWanted, Category

skills_bp = Blueprint('skills', __name__)


@skills_bp.route('/skills/add', methods=['GET', 'POST'])
@login_required
def add_skill():
    if request.method == 'POST':
        skill_name = request.form.get('skill_name')
        category_id = request.form.get('category_id')
        skill_level = request.form.get('skill_level')
        skill_type = request.form.get('skill_type')
        description = request.form.get('description')

        if skill_type == 'offering':
            skill = SkillOffering(
                user_id=current_user.id,
                skill_name=skill_name,
                category_id=category_id,
                skill_level=skill_level,
                description=description
            )
            db.session.add(skill)
            db.session.commit()
            flash('Teaching skill added successfully!', 'success')

        elif skill_type == 'wanted':
            skill = SkillWanted(
                user_id=current_user.id,
                skill_name=skill_name,
                category_id=category_id
            )
            db.session.add(skill)
            db.session.commit()
            flash('Learning goal added successfully!', 'success')

        return redirect(url_for('main.dashboard'))

    categories = Category.query.all()
    return render_template('add_skill.html', categories=categories)


@skills_bp.route('/skills/delete/<string:skill_type>/<int:skill_id>')
@login_required
def delete_skill(skill_type, skill_id):
    if skill_type == 'offering':
        skill = SkillOffering.query.get_or_404(skill_id)
    else:
        skill = SkillWanted.query.get_or_404(skill_id)

    if skill.user_id != current_user.id:
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('main.dashboard'))

    db.session.delete(skill)
    db.session.commit()
    flash('Skill removed successfully!', 'success')
    return redirect(url_for('main.dashboard'))


@skills_bp.route('/explore')
def explore():
    search = request.args.get('search', '')
    category_id = request.args.get('category', '')
    city = request.args.get('city', '')

    query = User.query

    if search:
        query = query.join(SkillOffering).filter(
            SkillOffering.skill_name.ilike(f'%{search}%')
        )

    if city:
        query = query.filter(User.city == city)

    users = query.all()

    # Filter users who have at least 1 skill
    users_with_skills = []
    for user in users:
        if len(user.skills_offering) > 0:
            users_with_skills.append(user)

    categories = Category.query.all()

    cities = db.session.query(User.city).filter(
        User.city.isnot(None),
        User.city != ''
    ).distinct().all()
    cities = [c[0] for c in cities]

    return render_template('explore.html',
                           users=users_with_skills,
                           categories=categories,
                           cities=cities,
                           search=search,
                           selected_city=city)