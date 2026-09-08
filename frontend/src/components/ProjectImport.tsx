/** Импорт анкеты из файлов проекта движка (.uproject, ProjectSettings, project.godot, .ini). */
import { useRef, useState } from 'react';
import { api } from '../api';
import { useStore } from '../store';
import type { ProjectImport as ImportResult } from '../types';
import { Callout, Card } from './ui';

/** Короткое представление значения поля для показа различий. */
function formatValue(value: unknown): string {
  if (value === null || value === undefined) return '—';
  if (Array.isArray(value)) return value.length > 0 ? value.join(', ') : '—';
  if (typeof value === 'boolean') return value ? 'да' : 'нет';
  return String(value);
}

export function ProjectImport() {
  const { basket, profile, updateProfile, toggleBasket } = useStore();
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [imported, setImported] = useState<ImportResult | null>(null);

  // Импорт накладывает только извлечённые поля: пустой результат не должен
  // сбрасывать уже заполненную анкету.
  const changes = imported
    ? imported.filled
        .map((field) => ({
          field,
          from: formatValue(profile[field as keyof typeof profile]),
          to: formatValue(imported.patch[field as keyof typeof imported.patch]),
        }))
        .filter((change) => change.from !== change.to)
    : [];

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setBusy(true);
    setError(null);
    try {
      const data = await api.importProject(Array.from(files));
      setImported(data);
    } catch (err) {
      setError((err as Error).message);
      setImported(null);
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card
      title="Импорт из проекта движка"
      hint="Загрузите .uproject, ProjectSettings.asset, ProjectVersion.txt, URP-ассет, project.godot или Default*.ini — надёжно извлечённые поля подставятся в анкету."
    >
      <div className="btn-row">
        <input
          ref={inputRef}
          type="file"
          multiple
          style={{ display: 'none' }}
          onChange={(e) => void handleFiles(e.target.files)}
        />
        <button
          className="btn btn-sm"
          disabled={busy}
          onClick={() => inputRef.current?.click()}
        >
          {busy ? 'Чтение файлов…' : 'Выбрать файлы'}
        </button>
        {imported && Object.keys(imported.patch).length > 0 && (
          <button
            className="btn btn-sm btn-primary"
            onClick={() => updateProfile(imported.patch)}
          >
            Применить {imported.filled.length === 1 ? 'поле' : 'поля'}
          </button>
        )}
      </div>

      {error && (
        <div style={{ marginTop: 10 }}>
          <Callout tone="danger" title="Не удалось разобрать файлы">{error}</Callout>
        </div>
      )}

      {imported && (
        <div style={{ marginTop: 10 }}>
          {imported.filled.length === 0 && (
            <p className="small muted">
              Из файлов не извлечено ни одного поля анкеты: применять нечего,
              текущие ответы не изменены.
            </p>
          )}
          {imported.filled.length > 0 && (
            <p className="small">
              Извлечено полей: <span className="mono">{imported.filled.join(', ')}</span>
              {changes.length === 0 && ' — значения уже совпадают с анкетой.'}
            </p>
          )}
          {changes.length > 0 && (
            <table className="table" style={{ marginTop: 8 }}>
              <thead>
                <tr>
                  <th>Поле</th>
                  <th>Сейчас</th>
                  <th>Будет</th>
                </tr>
              </thead>
              <tbody>
                {changes.map((change) => (
                  <tr key={change.field}>
                    <td className="mono small">{change.field}</td>
                    <td className="small muted">{change.from}</td>
                    <td className="small">{change.to}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {imported.suggested.length > 0 && (
            <div style={{ marginTop: 8 }}>
              <div className="xsmall faint">Найдены кандидаты в корзину</div>
              {imported.suggested.map((item) => (
                <div key={item.method_code} className="method-row">
                  <span className="mono small">{item.method_code}</span>
                  <span className="small muted"> — {item.reason}</span>{' '}
                  <button
                    className="btn btn-sm"
                    disabled={basket.includes(item.method_code)}
                    onClick={() => toggleBasket(item.method_code)}
                  >
                    {basket.includes(item.method_code) ? 'В корзине' : 'В корзину'}
                  </button>
                </div>
              ))}
            </div>
          )}
          {imported.detected.length > 0 && (
            <ul className="reason-list" style={{ marginTop: 8 }}>
              {imported.detected.map((line, index) => (
                <li key={index} className="small muted">{line}</li>
              ))}
            </ul>
          )}
          {imported.warnings.length > 0 && (
            <div style={{ marginTop: 8 }}>
              <Callout tone="warn" title="Требует внимания">
                {imported.warnings.join(' ')}
              </Callout>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
