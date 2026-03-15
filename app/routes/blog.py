from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import BlogPost
import re

blog_bp = Blueprint('blog', __name__)


def create_slug(title):
    slug = title.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '-', slug)
    return slug


@blog_bp.route('/blog')
def blog_list():
    posts = BlogPost.query.filter_by(
        is_published=True
    ).order_by(BlogPost.created_at.desc()).all()

    return render_template('blog.html', posts=posts)


@blog_bp.route('/blog/<string:slug>')
def blog_detail(slug):
    post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()

    recent_posts = BlogPost.query.filter(
        BlogPost.id != post.id,
        BlogPost.is_published == True
    ).order_by(BlogPost.created_at.desc()).limit(3).all()

    return render_template('blog_detail.html', post=post, recent_posts=recent_posts)


@blog_bp.route('/blog/new', methods=['GET', 'POST'])
@login_required
def create_post():
    if not current_user.is_admin:
        flash('Only admins can create blog posts!', 'danger')
        return redirect(url_for('blog.blog_list'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        excerpt = request.form.get('excerpt')
        category = request.form.get('category')

        slug = create_slug(title)

        # Make slug unique
        existing = BlogPost.query.filter_by(slug=slug).first()
        if existing:
            slug = slug + '-' + str(BlogPost.query.count() + 1)

        post = BlogPost(
            title=title,
            slug=slug,
            content=content,
            excerpt=excerpt,
            category=category,
            author_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()

        flash('Blog post published successfully!', 'success')
        return redirect(url_for('blog.blog_detail', slug=slug))

    return render_template('blog_create.html')


@blog_bp.route('/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    if not current_user.is_admin:
        flash('Only admins can edit blog posts!', 'danger')
        return redirect(url_for('blog.blog_list'))

    post = BlogPost.query.get_or_404(post_id)

    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.excerpt = request.form.get('excerpt')
        post.category = request.form.get('category')

        db.session.commit()

        flash('Blog post updated!', 'success')
        return redirect(url_for('blog.blog_detail', slug=post.slug))

    return render_template('blog_create.html', post=post)


@blog_bp.route('/blog/delete/<int:post_id>')
@login_required
def delete_post(post_id):
    if not current_user.is_admin:
        flash('Only admins can delete blog posts!', 'danger')
        return redirect(url_for('blog.blog_list'))

    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()

    flash('Blog post deleted!', 'success')
    return redirect(url_for('blog.blog_list'))