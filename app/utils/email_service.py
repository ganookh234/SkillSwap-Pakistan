import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ============================================
#  EMAIL SETTINGS - SIRF YAHAN 1 BAAR DALO
# ============================================
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'ganookh234@gmail.com'
SENDER_PASSWORD = 'udfq lmwt wvei paeh'    # ← SIRF YAHAN APP PASSWORD DALO
SENDER_NAME = 'SkillSwap'
# ============================================


def send_otp_email(to_email, otp_code, user_name):

    subject = f'SkillSwap - Your Verification Code: {otp_code}'

    html_body = f'''
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f8fafc; padding: 40px;">
        <div style="max-width: 500px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <div style="background: linear-gradient(135deg, #4F46E5, #7C3AED); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">🔐 SkillSwap</h1>
                <p style="color: rgba(255,255,255,0.8); margin: 8px 0 0;">Email Verification</p>
            </div>
            <div style="padding: 40px 30px; text-align: center;">
                <h2 style="color: #1e293b; margin-bottom: 8px;">Hello, {user_name}! 👋</h2>
                <p style="color: #64748b; font-size: 16px; margin-bottom: 30px;">
                    Use the following code to verify your account:
                </p>
                <div style="background: #f1f5f9; border-radius: 12px; padding: 25px; margin: 20px 0;">
                    <h1 style="color: #4F46E5; font-size: 42px; letter-spacing: 10px; margin: 0; font-family: monospace; font-weight: 900;">
                        {otp_code}
                    </h1>
                </div>
                <p style="color: #94a3b8; font-size: 14px; margin-top: 20px;">
                    ⏰ This code will expire in <strong>10 minutes</strong>
                </p>
                <p style="color: #94a3b8; font-size: 13px;">
                    If you didn't create an account on SkillSwap, please ignore this email.
                </p>
            </div>
            <div style="background: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="color: #94a3b8; font-size: 12px; margin: 0;">
                    © 2024 SkillSwap - Exchange Skills, Grow Together
                </p>
            </div>
        </div>
    </body>
    </html>
    '''

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f'{SENDER_NAME} <{SENDER_EMAIL}>'
        msg['To'] = to_email
        msg.attach(MIMEText(html_body, 'html'))

        print(f'📧 Connecting to Gmail SMTP...')
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        print(f'🔐 Logging in as {SENDER_EMAIL}...')
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        print(f'📨 Sending OTP to {to_email}...')
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()

        print(f'✅ OTP Email sent successfully to {to_email}!')
        return True

    except smtplib.SMTPAuthenticationError:
        print(f'❌ ERROR: Gmail login failed! Check app password')
        return False
    except Exception as e:
        print(f'❌ Email sending failed: {e}')
        return False


def send_reset_email(to_email, otp_code, user_name):

    subject = f'SkillSwap - Password Reset Code: {otp_code}'

    html_body = f'''
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f8fafc; padding: 40px;">
        <div style="max-width: 500px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <div style="background: linear-gradient(135deg, #F59E0B, #EF4444); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">🔑 SkillSwap</h1>
                <p style="color: rgba(255,255,255,0.8); margin: 8px 0 0;">Password Reset</p>
            </div>
            <div style="padding: 40px 30px; text-align: center;">
                <h2 style="color: #1e293b; margin-bottom: 8px;">Hello, {user_name}!</h2>
                <p style="color: #64748b; font-size: 16px; margin-bottom: 30px;">
                    You requested to reset your password. Use this code:
                </p>
                <div style="background: #f1f5f9; border-radius: 12px; padding: 25px; margin: 20px 0;">
                    <h1 style="color: #EF4444; font-size: 42px; letter-spacing: 10px; margin: 0; font-family: monospace; font-weight: 900;">
                        {otp_code}
                    </h1>
                </div>
                <p style="color: #94a3b8; font-size: 14px;">
                    ⏰ This code expires in <strong>10 minutes</strong>
                </p>
            </div>
            <div style="background: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="color: #94a3b8; font-size: 12px; margin: 0;">© 2024 SkillSwap</p>
            </div>
        </div>
    </body>
    </html>
    '''

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f'{SENDER_NAME} <{SENDER_EMAIL}>'
        msg['To'] = to_email
        msg.attach(MIMEText(html_body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()

        print(f'✅ Reset Email sent to {to_email}!')
        return True

    except Exception as e:
        print(f'❌ Email sending failed: {e}')
        return False