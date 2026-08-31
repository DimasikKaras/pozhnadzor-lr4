import React, { useState } from 'react';
import {
  Mail,
  ShieldCheck,
  Clock,
  Check,
  Copy,
  AlertTriangle,
  Send,
  ExternalLink,
  X,
  Sparkles,
  Inbox,
  CheckCircle2
} from 'lucide-react';
import { EmailDeliveryResult } from '../utils/email2fa';

interface Email2FAInboxModalProps {
  isOpen: boolean;
  onClose: () => void;
  deliveryResult: EmailDeliveryResult | null;
  onApplyCode: (code: string) => void;
  onResendEmail: () => void;
  cooldownSeconds: number;
}

export function Email2FAInboxModal({
  isOpen,
  onClose,
  deliveryResult,
  onApplyCode,
  onResendEmail,
  cooldownSeconds
}: Email2FAInboxModalProps) {
  const [copied, setCopied] = useState(false);
  const [applied, setApplied] = useState(false);

  if (!isOpen) return null;

  const code = deliveryResult?.deliveryDetails?.code || '';
  const formattedCode = code ? `${code.slice(0, 3)} ${code.slice(3)}` : '------';
  const sentTime = deliveryResult?.deliveryDetails?.sentAt
    ? new Date(deliveryResult.deliveryDetails.sentAt).toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    : new Date().toLocaleTimeString('ru-RU');

  const handleCopy = () => {
    if (!code) return;
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleApply = () => {
    if (!code) return;
    onApplyCode(code);
    setApplied(true);
    setTimeout(() => {
      setApplied(false);
      onClose();
    }, 400);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white w-full max-w-xl rounded-3xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="bg-slate-900 text-white p-5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-red-600/20 border border-red-500/30 text-red-400 flex items-center justify-center">
              <Inbox className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-sm text-white">
                  Почтовый ящик инспектора
                </h3>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-500/20 text-red-300 border border-red-500/30">
                  1 входящее
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Служебные уведомления службы безопасности ГПН
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 cursor-pointer transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Email Container */}
        <div className="p-6 overflow-y-auto space-y-4 flex-1">
          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 text-xs space-y-2">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 pb-2 border-b border-slate-200">
              <span className="font-bold text-slate-900 text-sm">
                🔐 {deliveryResult?.deliveryDetails?.subject || `Код подтверждения 2FA: ${code} — ПожНадзор.pro`}
              </span>
              <span className="text-[11px] text-slate-500 font-mono flex items-center gap-1">
                <Clock className="w-3 h-3" /> {sentTime}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] text-slate-600">
              <div>
                <span className="text-slate-400">От:</span>{' '}
                <strong className="text-slate-800 font-mono">noreply@pozhnadzor.pro</strong>
              </div>
              <div>
                <span className="text-slate-400">Кому:</span>{' '}
                <strong className="text-slate-800 font-mono">{deliveryResult?.email || 'инспектору'}</strong>
              </div>
            </div>

            <div className="pt-1 flex items-center justify-between">
              {deliveryResult?.sentRealMail ? (
                <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
                  <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Реальная доставка через SMTP ({deliveryResult?.email})
                </span>
              ) : (
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center gap-1 text-[11px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-md border border-blue-200">
                    <ShieldCheck className="w-3 h-3 text-blue-600" /> Сервер безопасности ПожНадзор
                  </span>
                  <span className="text-[10px] text-slate-500 font-medium">
                    (SMTP настраивается в файле smtp.config.json)
                  </span>
                </div>
              )}
            </div>
          </div>

          <div className="border border-slate-200 rounded-2xl p-5 bg-white shadow-xs space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-red-600 text-white font-black text-xs flex items-center justify-center">
                ГПН
              </div>
              <div>
                <div className="text-xs font-bold text-slate-900 uppercase tracking-wide">
                  Государственный пожарный надзор МЧС России
                </div>
                <div className="text-[10px] text-slate-500">
                  Автоматизированная система «ПожНадзор.pro»
                </div>
              </div>
            </div>

            <div className="text-xs text-slate-700 leading-relaxed">
              Зафиксирован запрос на авторизацию в системе. Для подтверждения личности введите
              одноразовый 6-значный проверочный код:
            </div>

            <div className="p-4 bg-gradient-to-br from-slate-50 to-slate-100 rounded-2xl border-2 border-dashed border-red-300 text-center space-y-2">
              <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500">
                Ваш 6-значный код подтверждения:
              </div>
              <div className="text-3xl sm:text-4xl font-mono font-black tracking-[0.25em] text-red-600 select-all">
                {formattedCode}
              </div>
              <div className="text-[11px] text-slate-500 font-medium flex items-center justify-center gap-1">
                <Clock className="w-3.5 h-3.5 text-slate-400" /> Действителен в течение 10 минут
              </div>
            </div>

            <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-[11px] text-amber-900 flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <span>
                Никому не передавайте данный код. Сотрудники технической поддержки никогда не
                запрашивают коды авторизации.
              </span>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3">
          <button
            type="button"
            disabled={cooldownSeconds > 0}
            onClick={onResendEmail}
            className="w-full sm:w-auto px-4 py-2 text-xs font-bold text-slate-600 hover:text-slate-900 disabled:text-slate-400 rounded-xl hover:bg-slate-200 transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
          >
            <Send className="w-3.5 h-3.5" />
            <span>{cooldownSeconds > 0 ? `Повтор через ${cooldownSeconds}с` : 'Отправить код заново'}</span>
          </button>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <button
              type="button"
              onClick={handleCopy}
              className="flex-1 sm:flex-initial px-3.5 py-2.5 bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 cursor-pointer transition-all shadow-xs"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Скопирован' : 'Скопировать'}</span>
            </button>

            <button
              type="button"
              onClick={handleApply}
              className="flex-1 sm:flex-initial px-5 py-2.5 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 shadow-md shadow-red-600/30 cursor-pointer active:scale-95 transition-all"
            >
              {applied ? <Check className="w-4 h-4 stroke-[3]" /> : <Sparkles className="w-4 h-4" />}
              <span>Вставить код в форму</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
