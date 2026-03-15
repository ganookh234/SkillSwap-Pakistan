from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Review, Notification

reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.route('/review/<int:user_id>', methods=['GET', 'POST'])
@login_required
def write_review(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('You cannot review yourself!', 'warning')
        return redirect(url_for('profile.my_profile'))

    # Check if already reviewed
    existing = Review.query.filter_by(
        reviewer_id=current_user.id,
        reviewed_user_id=user_id
    ).first()

    if existing:
        flash('You have already reviewed this user!', 'warning')
        return redirect(url_for('profile.view_profile', user_id=user_id))

    if request.method == 'POST':
        rating = int(request.form.get('rating', 5))
        review_text = request.form.get('review_text', '')
        skill_name = request.form.get('skill_name', '')

        if rating < 1 or rating > 5:
            flash('Rating must be between 1 and 5!', 'danger')
            return redirect(url_for('reviews.write_review', user_id=user_id))

        review = Review(
            reviewer_id=current_user.id,
            reviewed_user_id=user_id,
            rating=rating,
            review_text=review_text,
            skill_name=skill_name
        )
        db.session.add(review)

        # Send notification
        notif = Notification(
            user_id=user_id,
            title='New Review!',
            message=f'{current_user.full_name} gave you a {rating}-star review!',
            link=f'/profile/{user_id}',
            notif_type='review'
        )
        db.session.add(notif)

        db.session.commit()

        flash('Review submitted successfully!', 'success')
        return redirect(url_for('profile.view_profile', user_id=user_id))

    return render_template('write_review.html', user=user)


@reviews_bp.route('/reviews/<int:user_id>')
def user_reviews(user_id):
    user = User.query.get_or_404(user_id)
    reviews = Review.query.filter_by(
        reviewed_user_id=user_id
    ).order_by(Review.created_at.desc()).all()

    return render_template('user_reviews.html', user=user, reviews=reviews)


@reviews_bp.route('/review/delete/<int:review_id>')
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)

    if review.reviewer_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('main.dashboard'))

    user_id = review.reviewed_user_id
    db.session.delete(review)
    db.session.commit()

    flash('Review deleted successfully!', 'success')
    return redirect(url_for('reviews.user_reviews', user_id=user_id))