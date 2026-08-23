import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from abc import ABC, abstractmethod

from app.core.config import settings
from app.core.logging import logger


class EmailProvider(ABC):
    @abstractmethod
    async def send_otp(self, to_email: str, otp: str, purpose: str) -> bool:
        pass


class SMTPEmailProvider(EmailProvider):
    def _render_otp_html(self, to_email: str, otp: str, purpose: str) -> str:
        otp_spaced = "  ".join(list(otp))
        title_text = "Verify Your Email Address" if purpose == "verification" else "KNORA Account Login Verification"
        subtitle_text = (
            "Complete your account verification to access university academics, ATS resume tools, AI portfolio builder, and Guru.AI."
            if purpose == "verification"
            else "Use the verification code below to log in to your KNORA student account."
        )

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_text}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f6f9; font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #111111;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #f4f6f9; padding: 40px 10px;">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 580px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.06); border: 1px solid #e5e7eb;">
                    
                    <!-- Header Banner -->
                    <tr>
                        <td style="background-color: #0b0f19; padding: 32px 40px; text-align: center; border-bottom: 3px solid #1A73E8;">
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td align="center">
                                        <div style="display: inline-block; background-color: #1A73E8; width: 42px; height: 42px; border-radius: 10px; line-height: 42px; color: #ffffff; font-weight: 800; font-size: 20px; text-align: center;">K</div>
                                        <span style="display: inline-block; font-size: 26px; font-weight: 800; color: #ffffff; letter-spacing: 0.5px; vertical-align: middle; margin-left: 10px;">KNORA<span style="color: #1A73E8;">.in</span></span>
                                    </td>
                                </tr>
                            </table>
                            <p style="margin: 8px 0 0 0; color: #9ca3af; font-size: 13px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;">Official Student Platform</p>
                        </td>
                    </tr>

                    <!-- Body Content -->
                    <tr>
                        <td style="padding: 40px 40px 32px 40px;">
                            <h1 style="margin: 0 0 12px 0; font-size: 22px; font-weight: 800; color: #111827; text-align: center;">{title_text}</h1>
                            <p style="margin: 0 0 28px 0; font-size: 15px; color: #4b5563; line-height: 1.6; text-align: center;">{subtitle_text}</p>
                            
                            <!-- OTP Display Box -->
                            <div style="background: #f0f7ff; border: 2px dashed #1A73E8; border-radius: 14px; padding: 24px; text-align: center; margin-bottom: 28px;">
                                <span style="display: block; font-size: 12px; font-weight: 800; color: #1A73E8; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 10px;">Your 6-Digit Verification Code</span>
                                <div style="font-family: 'Courier New', Courier, monospace; font-size: 38px; font-weight: 800; color: #1A73E8; letter-spacing: 10px; line-height: 1;">{otp_spaced}</div>
                            </div>

                            <!-- Meta / Expiry Box -->
                            <div style="background-color: #f9fafb; border-radius: 10px; padding: 16px; border: 1px solid #e5e7eb; margin-bottom: 28px;">
                                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                    <tr>
                                        <td style="font-size: 13px; color: #6b7280; line-height: 1.5;">
                                            <strong>⏰ Code Expiration:</strong> Valid for <strong>{settings.OTP_EXPIRE_MINUTES} minutes</strong>.<br>
                                            <strong>🛡️ Security Warning:</strong> Do not share this OTP with anyone. KNORA staff will never ask for your verification code or password.
                                        </td>
                                    </tr>
                                </table>
                            </div>

                            <p style="margin: 0; font-size: 14px; color: #6b7280; text-align: center;">
                                If you did not request this email, you can safely ignore it.
                            </p>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 24px 40px; text-align: center; border-top: 1px solid #e5e7eb; font-size: 12px; color: #9ca3af;">
                            <p style="margin: 0 0 6px 0; font-weight: 700; color: #4b5563;">KNORA — Learn. Build. Grow. Get Hired.</p>
                            <p style="margin: 0;">© 2026 KNORA Technology & Education Platform. All rights reserved.</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    def _sync_send(self, to_email: str, otp: str, purpose: str) -> bool:
        msg = MIMEMultipart("alternative")
        subject_action = "Verification Code" if purpose == "verification" else "Login Code"
        msg["Subject"] = f"[{otp}] {subject_action} for your KNORA Account"
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to_email

        text_content = f"Your KNORA verification code is: {otp}. This code expires in {settings.OTP_EXPIRE_MINUTES} minutes."
        html_content = self._render_otp_html(to_email, otp, purpose)

        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=12.0) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_USER, [to_email], msg.as_string())
            logger.info(f"[REAL SMTP EMAIL SENT] To: {to_email} | OTP: {otp} | Purpose: {purpose}")
            return True
        except Exception as err:
            logger.error(f"[SMTP EMAIL ERROR] Failed sending to {to_email}: {err}")
            raise err

    async def send_otp(self, to_email: str, otp: str, purpose: str) -> bool:
        return await asyncio.to_thread(self._sync_send, to_email, otp, purpose)


class DevEmailProvider(EmailProvider):
    async def send_otp(self, to_email: str, otp: str, purpose: str) -> bool:
        if settings.ENABLE_DEV_OTP_LOGGING:
            logger.info(f"[DEV EMAIL OTP] Sent to: {to_email} | Purpose: {purpose} | OTP: {otp}")
        return True


def get_email_provider() -> EmailProvider:
    provider_name = settings.EMAIL_PROVIDER.lower()
    if provider_name in ["smtp", "gmail"]:
        return SMTPEmailProvider()
    return DevEmailProvider()


email_service = get_email_provider()
