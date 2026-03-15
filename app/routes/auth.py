from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Category, Notification

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        phone = request.form.get('phone')
        city = request.form.get('city')

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('This email is already registered!', 'danger')
            return redirect(url_for('auth.register'))

        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            city=city,
            is_verified=False
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        otp = user.generate_otp(purpose='verify')

        email_sent = False
        try:
            from app.utils.email_service import send_otp_email
            email_sent = send_otp_email(email, otp, full_name)
        except Exception as e:
            print(f'Email error: {e}')

        session['otp_user_id'] = user.id

        add_default_categories()

        if email_sent:
            flash(f'Verification code sent to {email}! Check your inbox.', 'success')
        else:
            flash('Email could not be sent. Please try again.', 'warning')

        return redirect(url_for('auth.verify_otp'))

    return render_template('register.html')


@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    user_id = session.get('otp_user_id')

    if not user_id:
        flash('Please register first!', 'warning')
        return redirect(url_for('auth.register'))

    user = User.query.get(user_id)

    if not user:
        flash('User not found! Please register again.', 'danger')
        return redirect(url_for('auth.register'))

    if user.is_verified:
        flash('Account already verified! Please sign in.', 'info')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        otp_input = request.form.get('otp')

        if user.verify_otp(otp_input, purpose='verify'):
            user.is_verified = True
            db.session.commit()

            notif = Notification(
                user_id=user.id,
                title='Welcome to SkillSwap! 🎉',
                message='Your account has been verified. Start by adding your skills!',
                link='/skills/add',
                notif_type='success'
            )
            db.session.add(notif)
            db.session.commit()

            session.pop('otp_user_id', None)

            flash('Account verified successfully! Please sign in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid or expired OTP! Please try again.', 'danger')

    return render_template('verify_otp.html', user=user)


@auth_bp.route('/resend-otp')
def resend_otp():
    user_id = session.get('otp_user_id')

    if not user_id:
        flash('Please register first!', 'warning')
        return redirect(url_for('auth.register'))

    user = User.query.get(user_id)

    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('auth.register'))

    if user.is_verified:
        flash('Account already verified!', 'info')
        return redirect(url_for('auth.login'))

    otp = user.generate_otp(purpose='verify')

    email_sent = False
    try:
        from app.utils.email_service import send_otp_email
        email_sent = send_otp_email(user.email, otp, user.full_name)
    except Exception as e:
        print(f'Email error: {e}')

    if email_sent:
        flash(f'New verification code sent to {user.email}!', 'success')
    else:
        flash('Email could not be sent. Please try again.', 'warning')

    return redirect(url_for('auth.verify_otp'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.is_verified:
                session['otp_user_id'] = user.id

                otp = user.generate_otp(purpose='verify')

                try:
                    from app.utils.email_service import send_otp_email
                    send_otp_email(user.email, otp, user.full_name)
                except:
                    pass

                flash('Please verify your account first! New code sent to your email.', 'warning')
                return redirect(url_for('auth.verify_otp'))

            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash('Welcome back, ' + user.full_name + '!', 'success')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Invalid email or password!', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            otp = user.generate_otp(purpose='reset')
            session['reset_user_id'] = user.id

            try:
                from app.utils.email_service import send_otp_email
                send_otp_email(user.email, otp, user.full_name)
            except:
                pass

            flash(f'Reset code sent to {email}! Check your inbox.', 'success')
            return redirect(url_for('auth.verify_reset_otp'))
        else:
            flash('If that email exists, a reset code has been sent.', 'info')

    return render_template('forgot_password.html')


@auth_bp.route('/verify-reset-otp', methods=['GET', 'POST'])
def verify_reset_otp():
    user_id = session.get('reset_user_id')

    if not user_id:
        flash('Please request a password reset first!', 'warning')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.get(user_id)

    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        otp_input = request.form.get('otp')

        if user.verify_otp(otp_input, purpose='reset'):
            session['reset_verified'] = True
            flash('Code verified! Now set your new password.', 'success')
            return redirect(url_for('auth.reset_password_new'))
        else:
            flash('Invalid or expired code!', 'danger')

    return render_template('verify_reset_otp.html', user=user)


@auth_bp.route('/reset-password-new', methods=['GET', 'POST'])
def reset_password_new():
    user_id = session.get('reset_user_id')
    verified = session.get('reset_verified')

    if not user_id or not verified:
        flash('Please verify your reset code first!', 'warning')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.get(user_id)

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.reset_password_new'))

        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'danger')
            return redirect(url_for('auth.reset_password_new'))

        user.set_password(password)
        db.session.commit()

        session.pop('reset_user_id', None)
        session.pop('reset_verified', None)

        flash('Password reset successfully! Please sign in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()

    if not user:
        flash('Invalid or expired reset link!', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.reset_password', token=token))

        user.set_password(password)
        user.reset_token = None
        db.session.commit()

        flash('Password reset successfully!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html')


def add_default_categories():
    categories = [
        {'name': 'Programming', 'icon': 'fa-code'},
        {'name': 'Languages', 'icon': 'fa-language'},
        {'name': 'Design & Art', 'icon': 'fa-paint-brush'},
        {'name': 'Music', 'icon': 'fa-music'},
        {'name': 'Business', 'icon': 'fa-chart-line'},
        {'name': 'Photography', 'icon': 'fa-camera'},
        {'name': 'Cooking', 'icon': 'fa-utensils'},
        {'name': 'Health & Fitness', 'icon': 'fa-heartbeat'},
        {'name': 'Writing', 'icon': 'fa-pen'},
        {'name': 'Marketing', 'icon': 'fa-bullhorn'},
        {'name': 'Academic', 'icon': 'fa-graduation-cap'},
        {'name': 'Other', 'icon': 'fa-ellipsis-h'},
    ]

    for cat in categories:
        if not Category.query.filter_by(name=cat['name']).first():
            new_cat = Category(name=cat['name'], icon=cat['icon'])
            db.session.add(new_cat)

    db.session.commit()