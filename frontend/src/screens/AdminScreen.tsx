/** Административный раздел: наполнение, проверка и публикация базы знаний (раздел 6 плана). */
import { useCallback, useEffect, useMemo, useState } from 'react';
import { adminApi } from '../api';
import { Badge, Callout, Card, Empty, Field, Loading, Metric, Select } from '../components/ui';
import type { AdminOverview, Method, ValidationIssue } from '../types';

const IMPORT_ENTITIES = [
  { value: 'methods', label: 'Методы и варианты реализации' },
  { value: 'game_functions', label: 'Игровые функции' },
  { value: 'engine_tools', label: 'Инструменты движков' },
  { value: 'game_examples', label: 'Примеры игр' },
  { value: 'hardware_cpu', label: 'Процессоры' },
  { value: 'hardware_gpu', label: 'Видеокарты' },
  { value: 'conflicts', label: 'Конфликты и зависимости' },
];

const STATUS_OPTIONS = [
  { value: 'draft', label: 'черновик' },
  { value: 'reviewed', label: 'проверено' },
  { value: 'published', label: 'опубликовано' },
];

const COUNT_LABELS: Record<string, string> = {
  game_functions: 'Игровые функции',
  methods: 'Методы, всего',
  methods_published: 'Из них опубликовано',
  engines: 'Движки',
  engine_tools: 'Инструменты движков',
  method_engine_links: 'Связи метод — движок',
  conflicts: 'Конфликты и зависимости',
  game_examples: 'Примеры игр',
  hardware_cpu: 'Процессоры',
  hardware_gpu: 'Видеокарты',
  projects: 'Сохранённые проекты',
};

function statusTone(status: string): 'neutral' | 'info' | 'ok' {
  if (status === 'published') return 'ok';
  if (status === 'reviewed') return 'info';
  return 'neutral';
}

export function AdminScreen() {
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [methods, setMethods] = useState<Method[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [importEntity, setImportEntity] = useState('methods');

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [nextOverview, nextMethods] = await Promise.all([
        adminApi.overview(),
        adminApi.methods(),
      ]);
      setOverview(nextOverview);
      setMethods(nextMethods);
    } catch (err) {
      setError((err as Error).message);
      setOverview(null);
      setMethods(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const handleValidate = async () => {
    try {
      const result = await adminApi.validate();
      setNotice(`Проверка завершена. Замечаний: ${result.total}`);
      await load();
    } catch (err) {
      setNotice(`Проверка не выполнена: ${(err as Error).message}`);
    }
  };

  const handleSeed = async () => {
    try {
      await adminApi.seed();
      setNotice('База заполнена демонстрационными данными');
      await load();
    } catch (err) {
      setNotice(`Заполнение не выполнено: ${(err as Error).message}`);
    }
  };

  const handleStatus = async (code: string, status: string) => {
    try {
      await adminApi.setStatus(code, status);
      setMethods((prev) =>
        (prev ?? []).map((m) => (m.code === code ? { ...m, status } : m)),
      );
      setNotice(`Статус изменён: ${code} → ${status}`);
    } catch (err) {
      setNotice(`Не удалось изменить статус: ${(err as Error).message}`);
    }
  };

  const handleDelete = async (code: string) => {
    if (!window.confirm(`Удалить метод «${code}»? Действие необратимо.`)) return;
    try {
      await adminApi.deleteMethod(code);
      setMethods((prev) => (prev ?? []).filter((m) => m.code !== code));
      setNotice(`Метод удалён: ${code}`);
    } catch (err) {
      setNotice(`Не удалось удалить метод: ${(err as Error).message}`);
    }
  };

  const handleImport = async (file: File | undefined) => {
    if (!file) return;
    try {
      const result = await adminApi.importEntity(importEntity, file);
      setNotice(
        `Импорт завершён: создано ${result.created}, обновлено ${result.updated}, пропущено ${result.skipped}`,
      );
      await load();
    } catch (err) {
      setNotice(`Импорт не выполнен: ${(err as Error).message}`);
    }
  };

  const sortedMethods = useMemo(
    () => [...(methods ?? [])].sort((a, b) => a.code.localeCompare(b.code)),
    [methods],
  );

  return (
    <>
      {notice && (
        <Callout tone="info" title="Сообщение">
          {notice}
        </Callout>
      )}
      {error && (
        <Callout tone="danger" title="Ошибка загрузки">
          {error}
        </Callout>
      )}

      <Card
        title="Наполнение базы знаний"
        hint="Объём каталогов и число связей между общими методами и инструментами движков."
        actions={
          <div className="btn-row">
            <button className="btn btn-sm" onClick={() => void handleValidate()}>
              Проверить целостность
            </button>
            <button className="btn btn-sm" onClick={() => void handleSeed()}>
              Заполнить демоданными
            </button>
          </div>
        }
      >
        {loading && !overview ? (
          <Loading text="Загрузка сводки…" />
        ) : (
          overview && (
            <div className="stat-grid">
              {Object.entries(overview.counts).map(([key, value]) => (
                <Metric key={key} label={COUNT_LABELS[key] ?? key} value={value} />
              ))}
            </div>
          )
        )}
      </Card>

      {overview && (
        <Card
          title="Ошибки и конфликты базы"
          hint="Проверка выявляет записи без источника, ссылки на несуществующие коды и дубликаты."
          actions={
            <div className="btn-row">
              <Badge tone={overview.issues_by_severity.error > 0 ? 'danger' : 'ok'}>
                ошибок: {overview.issues_by_severity.error}
              </Badge>
              <Badge tone={overview.issues_by_severity.warning > 0 ? 'warn' : 'ok'}>
                предупреждений: {overview.issues_by_severity.warning}
              </Badge>
            </div>
          }
        >
          {overview.issues.length === 0 ? (
            <Callout tone="ok" title="Замечаний нет">
              Целостность базы знаний подтверждена.
            </Callout>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Сущность</th>
                    <th>Код</th>
                    <th>Уровень</th>
                    <th>Сообщение</th>
                  </tr>
                </thead>
                <tbody>
                  {overview.issues.map((issue: ValidationIssue, index) => (
                    <tr key={`${issue.entity}-${issue.entity_code}-${index}`}>
                      <td className="small">{issue.entity}</td>
                      <td className="small mono">{issue.entity_code}</td>
                      <td>
                        <Badge tone={issue.severity === 'error' ? 'danger' : 'warn'}>
                          {issue.severity === 'error' ? 'ошибка' : 'предупреждение'}
                        </Badge>
                      </td>
                      <td className="small">{issue.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      <Card
        title="Импорт данных"
        hint="Поддерживаются CSV и JSON. Ключевое поле — code; для оборудования — model. Списочные поля разделяются точкой с запятой."
      >
        <div className="grid grid-2">
          <Field label="Тип записей">
            <Select value={importEntity} options={IMPORT_ENTITIES} onChange={setImportEntity} />
          </Field>
          <Field label="Файл">
            <input
              type="file"
              accept=".csv,.json"
              onChange={(event) => void handleImport(event.target.files?.[0])}
            />
          </Field>
        </div>
      </Card>

      <Card
        title="Публикация записей"
        hint="В публичных рекомендациях используются только опубликованные записи с указанным источником."
        actions={<Badge tone="neutral">записей: {sortedMethods.length}</Badge>}
      >
        {sortedMethods.length === 0 ? (
          <Empty>Записи отсутствуют.</Empty>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Код</th>
                  <th>Название</th>
                  <th>Уровень</th>
                  <th>Источник</th>
                  <th>Статус</th>
                  <th className="no-print">Действие</th>
                </tr>
              </thead>
              <tbody>
                {sortedMethods.map((method) => (
                  <tr key={method.code}>
                    <td className="small mono">{method.code}</td>
                    <td className="small">{method.name}</td>
                    <td className="small">{method.level_label}</td>
                    <td className="small">
                      {method.source_url ? (
                        <a href={method.source_url} target="_blank" rel="noreferrer">
                          {method.source_title || 'открыть'}
                        </a>
                      ) : (
                        <Badge tone="danger">отсутствует</Badge>
                      )}
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <Badge tone={statusTone(method.status)}>
                          {STATUS_OPTIONS.find((o) => o.value === method.status)?.label ?? method.status}
                        </Badge>
                      </div>
                    </td>
                    <td className="no-print">
                      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        <Select
                          value={method.status}
                          options={STATUS_OPTIONS}
                          onChange={(value) => void handleStatus(method.code, value)}
                        />
                        <button
                          className="btn btn-sm btn-danger"
                          onClick={() => void handleDelete(method.code)}
                        >
                          Удалить
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </>
  );
}
