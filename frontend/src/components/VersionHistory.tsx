/** История версий набора решений: патчи и обновления проекта. */
import { useMemo, useState } from 'react';
import { useStore } from '../store';
import { diffVersion, nextVersionLabel, versionTitle } from '../versions';
import { Badge, Callout, Empty } from './ui';
import type { ProjectVersion, VersionDiff } from '../types';

export function VersionHistory() {
  const {
    profile,
    basket,
    result,
    versions,
    hasUnsavedChanges,
    catalog,
    saveVersion,
    restoreVersion,
    deleteVersion,
  } = useStore();

  const [label, setLabel] = useState('');
  const [note, setNote] = useState('');
  const [compareId, setCompareId] = useState<string | null>(null);

  const methodsByCode = useMemo(
    () => new Map(catalog.methods.map((method) => [method.code, method])),
    [catalog.methods],
  );
  const nameOf = (code: string) => methodsByCode.get(code)?.name ?? code;

  const compared = compareId ? versions.find((item) => item.id === compareId) ?? null : null;
  const diff: VersionDiff | null = useMemo(
    () => (compared ? diffVersion(compared, profile, basket, result) : null),
    [compared, profile, basket, result],
  );

  const suggested = nextVersionLabel(versions.length, profile.stage);

  const onSave = () => {
    saveVersion(label.trim() || suggested, note);
    setLabel('');
    setNote('');
  };

  return (
    <>
      <div className="btn-row" style={{ alignItems: 'flex-end', marginBottom: 12 }}>
        <div className="field" style={{ flex: 1 }}>
          <label>Название версии</label>
          <input
            value={label}
            placeholder={suggested}
            onChange={(event) => setLabel(event.target.value)}
          />
        </div>
        <div className="field" style={{ flex: 2 }}>
          <label>Что изменилось</label>
          <input
            value={note}
            placeholder="например: патч 1.1 — переработан стриминг текстур"
            onChange={(event) => setNote(event.target.value)}
          />
        </div>
        <button className="btn" onClick={onSave}>
          Подтвердить изменения
        </button>
      </div>

      {hasUnsavedChanges && (
        <Callout tone="warn" title="Есть несохранённые изменения">
          Набор или анкета изменились после сохранения версии {versions[versions.length - 1].number}.
          Подтвердите изменения, чтобы зафиксировать новую версию: прежняя останется в истории для
          сравнения.
        </Callout>
      )}

      {!result && versions.length > 0 && (
        <Callout tone="info" title="Расчёт не выполнен">
          Сводка сохраняется вместе с версией. Без расчёта версия будет сохранена без аппаратной
          оценки, и сравнение покажет только изменение набора решений.
        </Callout>
      )}

      {versions.length === 0 ? (
        <Empty>
          Версий пока нет. Подтвердите текущий набор — он станет базой, с которой сравниваются
          следующие патчи и обновления.
        </Empty>
      ) : (
        <div style={{ marginTop: 12 }}>
          {[...versions].reverse().map((version) => (
            <VersionRow
              key={version.id}
              version={version}
              expanded={compared?.id === version.id}
              diff={compared?.id === version.id ? diff : null}
              nameOf={nameOf}
              onCompare={() => setCompareId(compared?.id === version.id ? null : version.id)}
              onRestore={() => restoreVersion(version.id)}
              onDelete={() => {
                if (compared?.id === version.id) setCompareId(null);
                deleteVersion(version.id);
              }}
            />
          ))}
        </div>
      )}
    </>
  );
}

function VersionRow({
  version,
  expanded,
  diff,
  nameOf,
  onCompare,
  onRestore,
  onDelete,
}: {
  version: ProjectVersion;
  expanded: boolean;
  diff: VersionDiff | null;
  nameOf: (code: string) => string;
  onCompare: () => void;
  onRestore: () => void;
  onDelete: () => void;
}) {
  const hardware = version.summary?.hardware ?? null;
  return (
    <div className="method-row" style={{ marginBottom: 10 }}>
      <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <strong>{versionTitle(version)}</strong>
          {version.note && <p className="small muted" style={{ marginTop: 4 }}>{version.note}</p>}
          <div className="btn-row" style={{ marginTop: 6 }}>
            <Badge tone="info">решений: {version.summary?.basket_size ?? version.basket.length}</Badge>
            {hardware?.estimated_ram_gb !== null && hardware?.estimated_ram_gb !== undefined && (
              <Badge tone="neutral">RAM: {hardware.estimated_ram_gb} ГБ</Badge>
            )}
            {hardware?.estimated_vram_gb !== null && hardware?.estimated_vram_gb !== undefined && (
              <Badge tone="neutral">VRAM: {hardware.estimated_vram_gb} ГБ</Badge>
            )}
            {hardware?.reference_gpu && <Badge tone="neutral">{hardware.reference_gpu}</Badge>}
            {version.summary && version.summary.conflict_count > 0 && (
              <Badge tone="danger">конфликтов: {version.summary.conflict_count}</Badge>
            )}
            {!version.summary && <Badge tone="warn">без сводки расчёта</Badge>}
          </div>
        </div>
        <div className="btn-row" style={{ flexDirection: 'column', alignItems: 'stretch' }}>
          <button className="btn btn-sm" onClick={onCompare}>
            {expanded ? 'Скрыть сравнение' : 'Сравнить с текущей'}
          </button>
          <button className="btn btn-sm" onClick={onRestore}>
            Восстановить
          </button>
          <button className="btn btn-sm btn-danger" onClick={onDelete}>
            Удалить
          </button>
        </div>
      </div>

      {expanded && diff && <DiffView diff={diff} version={version} nameOf={nameOf} />}
    </div>
  );
}

function DiffView({
  diff,
  version,
  nameOf,
}: {
  diff: VersionDiff;
  version: ProjectVersion;
  nameOf: (code: string) => string;
}) {
  const nothingChanged =
    diff.added.length === 0 && diff.removed.length === 0 && diff.profile_changes.length === 0;

  return (
    <div style={{ marginTop: 12, borderTop: '1px solid var(--border)', paddingTop: 10 }}>
      <div className="xsmall faint" style={{ marginBottom: 6 }}>
        Разница с текущим набором
      </div>

      {nothingChanged ? (
        <Callout tone="ok" title="Изменений нет">
          Текущий набор совпадает с версией {version.number}.
        </Callout>
      ) : (
        <>
          {diff.added.length > 0 && (
            <div style={{ marginBottom: 8 }}>
              <Badge tone="ok">добавлено: {diff.added.length}</Badge>
              <ul className="reason-list">
                {diff.added.map((code) => (
                  <li key={code}>{nameOf(code)}</li>
                ))}
              </ul>
            </div>
          )}
          {diff.removed.length > 0 && (
            <div style={{ marginBottom: 8 }}>
              <Badge tone="danger">убрано: {diff.removed.length}</Badge>
              <ul className="reason-list">
                {diff.removed.map((code) => (
                  <li key={code}>{nameOf(code)}</li>
                ))}
              </ul>
            </div>
          )}
          {diff.profile_changes.length > 0 && (
            <div style={{ marginBottom: 8 }}>
              <Badge tone="warn">изменения анкеты: {diff.profile_changes.length}</Badge>
              <ul className="reason-list">
                {diff.profile_changes.map((change) => (
                  <li key={change.field}>
                    <strong>{change.label}</strong>: {change.from} → {change.to}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}

      {diff.hardware && (
        <div className="btn-row" style={{ marginTop: 8 }}>
          {diff.hardware.ram_delta_gb !== null && (
            <Badge tone={diff.hardware.ram_delta_gb > 0 ? 'danger' : 'ok'}>
              RAM: {signed(diff.hardware.ram_delta_gb)} ГБ
            </Badge>
          )}
          {diff.hardware.vram_delta_gb !== null && (
            <Badge tone={diff.hardware.vram_delta_gb > 0 ? 'danger' : 'ok'}>
              VRAM: {signed(diff.hardware.vram_delta_gb)} ГБ
            </Badge>
          )}
          {diff.hardware.gpu_changed && <Badge tone="info">изменился ориентир GPU</Badge>}
          {diff.hardware.cpu_changed && <Badge tone="info">изменился ориентир CPU</Badge>}
          {diff.hardware.bottleneck_changed && <Badge tone="info">изменилось узкое место</Badge>}
        </div>
      )}
    </div>
  );
}

function signed(value: number): string {
  return value > 0 ? `+${value}` : String(value);
}
