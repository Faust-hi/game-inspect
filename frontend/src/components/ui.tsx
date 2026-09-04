/** Базовые элементы интерфейса. */
import { useEffect, type ReactNode } from 'react';

export function Card({
  title,
  hint,
  actions,
  children,
  tight,
  className = '',
}: {
  title?: ReactNode;
  hint?: ReactNode;
  actions?: ReactNode;
  children: ReactNode;
  tight?: boolean;
  className?: string;
}) {
  return (
    <section className={`card ${tight ? 'tight' : ''} ${className}`}>
      {(title || actions) && (
        <div className="card-title">
          <h2 style={{ flex: 1 }}>{title}</h2>
          {actions}
        </div>
      )}
      {hint && <div className="card-hint">{hint}</div>}
      {children}
    </section>
  );
}

export function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <div className="field">
      <label>{label}</label>
      {children}
      {hint && <span className="hint">{hint}</span>}
    </div>
  );
}

export function Select({
  value,
  options,
  onChange,
  disabled,
  placeholder,
}: {
  value: string;
  options: { value: string; label: string }[];
  onChange: (value: string) => void;
  disabled?: boolean;
  placeholder?: string;
}) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)} disabled={disabled}>
      {placeholder !== undefined && <option value="">{placeholder}</option>}
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}

export function NumberInput({
  value,
  onChange,
  min,
  max,
  step,
  placeholder,
}: {
  value: number | null;
  onChange: (value: number | null) => void;
  min?: number;
  max?: number;
  step?: number;
  placeholder?: string;
}) {
  return (
    <input
      type="number"
      value={value ?? ''}
      min={min}
      max={max}
      step={step}
      placeholder={placeholder}
      onChange={(e) => {
        const raw = e.target.value;
        if (raw === '') {
          onChange(null);
          return;
        }
        const next = Number(raw);
        onChange(Number.isNaN(next) ? null : next);
      }}
    />
  );
}

export function Toggle({
  checked,
  onChange,
  label,
}: {
  checked: boolean;
  onChange: (value: boolean) => void;
  label: string;
}) {
  return (
    <label className="chip" style={{ cursor: 'pointer', userSelect: 'none' }}>
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        style={{ width: 'auto', margin: 0 }}
      />
      {label}
    </label>
  );
}

export function Badge({
  tone = 'neutral',
  children,
  title,
}: {
  tone?: 'neutral' | 'ok' | 'warn' | 'danger' | 'info';
  children: ReactNode;
  title?: string;
}) {
  return (
    <span className={`badge badge-${tone}`} title={title}>
      {children}
    </span>
  );
}

/** Пометки решений из раздела 7 плана. */
const FLAG_TONE: Record<string, 'ok' | 'warn' | 'danger' | 'info' | 'neutral'> = {
  recommended: 'ok',
  conditional: 'info',
  implement_now: 'ok',
  late_difficult: 'danger',
  needs_prototyping: 'warn',
  may_reduce_quality: 'warn',
  may_change_concept: 'danger',
  not_recommended: 'danger',
};

export function Flag({ code, label }: { code: string; label: string }) {
  return <Badge tone={FLAG_TONE[code] ?? 'neutral'}>{label}</Badge>;
}

export function Bar({ value, tone = 'accent' }: { value: number; tone?: 'accent' | 'ok' | 'danger' }) {
  const color = tone === 'ok' ? 'var(--ok)' : tone === 'danger' ? 'var(--danger)' : 'var(--accent)';
  return (
    <div className="bar-track">
      <div className="bar-fill" style={{ width: `${Math.max(0, Math.min(100, value))}%`, background: color }} />
    </div>
  );
}

const RESOURCE_KEYS = ['cpu', 'gpu', 'ram', 'vram', 'disk', 'network'] as const;
const RESOURCE_LABELS: Record<string, string> = {
  cpu: 'CPU',
  gpu: 'GPU',
  ram: 'RAM',
  vram: 'VRAM',
  disk: 'Диск',
  network: 'Сеть',
};

export function ImpactGrid({
  impacts,
}: {
  impacts: Record<string, number>;
}) {
  return (
    <div className="impact-grid">
      {RESOURCE_KEYS.map((key) => {
        const value = impacts[key] ?? 0;
        const tone = value < 0 ? 'down' : value > 0 ? 'up' : '';
        return (
          <div key={key} className={`impact-cell ${tone}`}>
            <div className="label">{RESOURCE_LABELS[key]}</div>
            <div className="value">{value > 0 ? `+${value}` : value}</div>
          </div>
        );
      })}
    </div>
  );
}

export function Callout({
  tone = 'info',
  title,
  children,
}: {
  tone?: 'info' | 'warn' | 'danger' | 'ok';
  title?: string;
  children: ReactNode;
}) {
  return (
    <div className={`callout ${tone}`}>
      {title && <strong>{title}: </strong>}
      {children}
    </div>
  );
}

export function Empty({ children }: { children: ReactNode }) {
  return <div className="empty">{children}</div>;
}

export function Loading({ text = 'Загрузка…' }: { text?: string }) {
  return (
    <div className="loading">
      <span className="spinner" />
      {text}
    </div>
  );
}

export function Modal({
  title,
  subtitle,
  onClose,
  children,
  footer,
}: {
  title: ReactNode;
  subtitle?: ReactNode;
  onClose: () => void;
  children: ReactNode;
  footer?: ReactNode;
}) {
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  return (
    <div className="modal-backdrop" onClick={onClose} role="presentation">
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <div style={{ flex: 1 }}>
            <h3>{title}</h3>
            {subtitle && <div className="small muted">{subtitle}</div>}
          </div>
          <button className="btn btn-sm" onClick={onClose}>
            Закрыть
          </button>
        </div>
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-foot">{footer}</div>}
      </div>
    </div>
  );
}

export function Tabs({
  tabs,
  active,
  onChange,
}: {
  tabs: { key: string; label: ReactNode; count?: number }[];
  active: string;
  onChange: (key: string) => void;
}) {
  return (
    <div className="tabs">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          className={`tab ${tab.key === active ? 'active' : ''}`}
          onClick={() => onChange(tab.key)}
        >
          {tab.label}
          {tab.count !== undefined && <span className="faint"> ({tab.count})</span>}
        </button>
      ))}
    </div>
  );
}

export function SourceLink({ url, title }: { url: string; title?: string }) {
  if (!url) return null;
  return (
    <div className="source-link">
      Источник:{' '}
      <a href={url} target="_blank" rel="noreferrer">
        {title || url}
      </a>
    </div>
  );
}

export function Toast({ message, onDone }: { message: string; onDone: () => void }) {
  useEffect(() => {
    const timer = setTimeout(onDone, 2600);
    return () => clearTimeout(timer);
  }, [message, onDone]);
  return <div className="toast">{message}</div>;
}

export function Metric({ label, value, hint }: { label: string; value: ReactNode; hint?: ReactNode }) {
  return (
    <div className="metric">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
      {hint && <div className="xsmall muted">{hint}</div>}
    </div>
  );
}
