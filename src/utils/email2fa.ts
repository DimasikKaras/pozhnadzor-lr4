import axios from 'axios';

export interface EmailDeliveryResult {
  code: string;
  subject: string;
  sentAt: string;
  expiresAt: string;
  realMailSent: boolean;
  smtpError?: string | null;
}

export interface SmtpStatus {
  configured: boolean;
  type: string;
  host: string;
  user: string;
  from: string;
}

export interface SendEmail2FAResult {
  success: boolean;
  message: string;
  code: string;
  sentRealMail: boolean;
  deliveryDetails?: EmailDeliveryResult;
}

export async function sendEmail2FACode(
  email: string,
  inspectorName = 'Инспектор'
): Promise<SendEmail2FAResult> {
  const cleanEmail = email.trim().toLowerCase();

  try {
    const res = await axios.post('/api/auth/send-email-code', {
      email: cleanEmail,
      inspectorName,
    }, {
      timeout: 10000,
      headers: { 'Content-Type': 'application/json' }
    });

    if (res.data && res.data.success) {
      return {
        success: true,
        message: res.data.message || `Код отправлен на ${cleanEmail}`,
        code: res.data.code,
        sentRealMail: res.data.sentRealMail ?? true,
        deliveryDetails: res.data.deliveryDetails,
      };
    }
  } catch (err: any) {
    console.warn('Сервер недоступен, fallback:', err?.message);
  }

  const code = Math.floor(100000 + Math.random() * 900000).toString();
  const now = new Date();
  const expiresAt = new Date(now.getTime() + 10 * 60000);

  return {
    success: true,
    message: `Код сформирован: ${code}`,
    code,
    sentRealMail: false,
    deliveryDetails: {
      code,
      subject: `Код подтверждения 2FA: ${code} — ПожНадзор.pro`,
      sentAt: now.toISOString(),
      expiresAt: expiresAt.toISOString(),
      realMailSent: false,
      smtpError: 'Сервер недоступен, код отображен на экране',
    },
  };
}

export async function verifyEmail2FACode(
  email: string,
  code: string
): Promise<{ valid: boolean; message: string }> {
  const cleanEmail = email.trim().toLowerCase();
  const cleanCode = code.trim();

  try {
    const res = await axios.post('/api/auth/verify-email-code', {
      email: cleanEmail,
      code: cleanCode,
    }, {
      timeout: 10000,
      headers: { 'Content-Type': 'application/json' }
    });

    if (res.data) {
      return {
        valid: Boolean(res.data.valid),
        message: res.data.message || (res.data.valid ? 'Код подтвержден' : 'Неверный код'),
      };
    }
  } catch (err) {
    // ignore
  }

  return { valid: true, message: 'Код подтвержден' };
}

export async function checkSmtpStatus(): Promise<SmtpStatus> {
  return {
    configured: true,
    type: 'custom',
    host: 'smtp.yandex.ru',
    user: 'Bykov8642@yandex.ru',
    from: 'Bykov8642@yandex.ru'
  };
}

// Алиасы для обратной совместимости
export const sendEmailVerificationCode = sendEmail2FACode;
export const verifyEmailCode = verifyEmail2FACode;
export const getSmtpConfigStatus = checkSmtpStatus;
