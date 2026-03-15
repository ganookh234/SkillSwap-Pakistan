from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import User, SkillOffering, SkillWanted

matching_bp = Blueprint('matching', __name__)


@matching_bp.route('/matches')
@login_required
def find_matches():
    my_offerings = SkillOffering.query.filter_by(user_id=current_user.id).all()
    my_wanted = SkillWanted.query.filter_by(user_id=current_user.id).all()

    potential_matches = []

    for wanted in my_wanted:
        matching_skills = SkillOffering.query.filter(
            SkillOffering.skill_name.ilike(f'%{wanted.skill_name}%'),
            SkillOffering.user_id != current_user.id
        ).all()

        for match_skill in matching_skills:
            other_user = User.query.get(match_skill.user_id)

            # Check if other user wants what I offer
            mutual = False
            exchange_skill = ''
            for offering in my_offerings:
                other_wanted = SkillWanted.query.filter(
                    SkillWanted.user_id == other_user.id,
                    SkillWanted.skill_name.ilike(f'%{offering.skill_name}%')
                ).first()

                if other_wanted:
                    mutual = True
                    exchange_skill = offering.skill_name
                    break

            # Calculate score
            score = 0
            score += 40  # skill match base score

            if mutual:
                score += 30  # mutual match bonus

            if current_user.city and other_user.city:
                if current_user.city.lower() == other_user.city.lower():
                    score += 20  # same city bonus

            if match_skill.skill_level == 'expert':
                score += 10
            elif match_skill.skill_level == 'intermediate':
                score += 5

            # Avoid duplicates
            already_added = False
            for pm in potential_matches:
                if pm['user'].id == other_user.id:
                    already_added = True
                    break

            if not already_added:
                potential_matches.append({
                    'user': other_user,
                    'their_skill': match_skill.skill_name,
                    'their_level': match_skill.skill_level or 'Not specified',
                    'my_wanted_skill': wanted.skill_name,
                    'mutual': mutual,
                    'exchange_skill': exchange_skill,
                    'score': min(score, 100)
                })

    # Sort by score
    potential_matches.sort(key=lambda x: x['score'], reverse=True)

    return render_template('matches.html', matches=potential_matches)