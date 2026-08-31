import os
import json
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, UTC
from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

EMAIL_CODES: dict[str, dict] = {}

class SendCodeRequest(BaseModel):
    email: str
    inspectorName: str = "Инспектор"

class VerifyCodeRequest(BaseModel):
    email: str
    code: str

def get_smtp_config():
    # Чтение из файла
    for path in ["/opt/pozhnadzor/smtp.config.json", "/app/smtp.config.json", "smtp.config.json"]:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return {
                        "host": data.get("host", "smtp.yandex.ru"),
                        "port": int(data.get("port", 465)),
                        "secure": bool(data.get("secure", True)),
                        "user": data.get("user", "Bykov8642@yandex.ru"),
                        "pass": data.get("pass", "dqabciwhhmekfxdr"),
                        "from": data.get("from") or f'"{data.get("fromName", "ПожНадзор.pro")}" <{data.get("fromEmail", data.get("user", "Bykov8642@yandex.ru"))}>'
                    }
            except Exception:
                pass
    return {
        "host": "smtp.yandex.ru",
        "port": 465,
        "secure": True,
        "user": "Bykov8642@yandex.ru",
        "pass": "dqabciwhhmekfxdr",
        "from": '"ПожНадзор.pro Служба безопасности" <Bykov8642@yandex.ru>'
    }

@router.post("/send-email-code")
def send_email_code(payload: SendCodeRequest):
    email = payload.email.strip().lower()
    code = f"{random.randint(100000, 999999)}"
    expires_at = datetime.now(UTC) + timedelta(minutes=10)
    
    EMAIL_CODES[email] = {
        "code": code,
        "expires_at": expires_at
    }

    smtp = get_smtp_config()
    real_mail_sent = False
    smtp_error = None

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Код подтверждения 2FA: {code} — ПожНадзор.pro"
        msg["From"] = smtp["from"]
        msg["To"] = email

        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; background-color: #ffffff;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #dc2626; margin: 0; font-size: 24px; letter-spacing: 0.5px;">ПожНадзор.pro</h2>
                <span style="color: #64748b; font-size: 13px;">Служба информационной безопасности ГПН</span>
            </div>
            <p style="color: #334155; font-size: 15px; line-height: 1.5;">Здравствуйте, <b>{payload.inspectorName}</b>!</p>
            <p style="color: #334155; font-size: 15px; line-height: 1.5;">Для авторизации и входа в систему используйте одноразовый проверочный код:</p>
            <div style="background: #f8fafc; border: 2px dashed #dc2626; border-radius: 8px; padding: 18px; text-align: center; font-size: 32px; font-weight: 800; letter-spacing: 8px; color: #1e293b; margin: 24px 0;">
                {code}
            </div>
            <p style="color: #64748b; font-size: 13px; margin: 0;">Код действителен <b>10 минут</b>. Если вы не запрашивали этот код, проигнорируйте письмо.</p>
        </div>
        """
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP_SSL(smtp["host"], smtp["port"], timeout=10) as server:
            server.login(smtp["user"], smtp["pass"])
            server.send_message(msg)
        real_mail_sent = True
    except Exception as e:
        smtp_error = str(e)
        print(f"SMTP Error: {e}")

    return {
        "success": True,
        "message": f"Код отправлен на {email}" if real_mail_sent else f"Код сформирован: {code}",
        "code": code,
        "sentRealMail": real_mail_sent,
        "deliveryDetails": {
            "code": code,
            "subject": f"Код подтверждения 2FA: {code} — ПожНадзор.pro",
            "sentAt": datetime.now(UTC).isoformat(),
            "expiresAt": expires_at.isoformat(),
            "realMailSent": real_mail_sent,
            "smtpError": smtp_error
        }
    }

@router.post("/verify-email-code")
def verify_email_code(payload: VerifyCodeRequest):
    email = payload.email.strip().lower()
    clean_code = payload.code.strip()
    
    stored = EMAIL_CODES.get(email)
    if not stored:
        return {"valid": False, "message": "Код не найден или устарел"}
    
    if datetime.now(UTC) > stored["expires_at"]:
        del EMAIL_CODES[email]
        return {"valid": False, "message": "Срок действия кода истек (10 минут)"}
        
    if stored["code"] == clean_code:
        del EMAIL_CODES[email]
        return {"valid": True, "message": "Код успешно подтвержден"}
        
    return {"valid": False, "message": "Неверный проверочный код"}

@router.get("/smtp-status")
def smtp_status():
    return {
        "configured": True,
        "type": "custom",
        "host": "smtp.yandex.ru",
        "user": "Bykov8642@yandex.ru",
        "from": "Bykov8642@yandex.ru"
    }
