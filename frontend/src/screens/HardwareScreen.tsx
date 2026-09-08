/** Экран 9. Ориентировочный минимальный класс оборудования (раздел 5 плана). */
import { useEnsureResult, useStore } from '../store';
import { Badge, Callout, Card, Empty, Loading, Metric, SourceLink } from '../components/ui';
import type { HardwareCPU, HardwareGPU } from '../types';

const STORAGE_LABELS: Record<string, string> = {
  hdd: 'HDD',
  sata_ssd: 'SATA SSD',
  nvme: 'NVMe SSD',
};

function CpuSpec({ cpu }: { cpu: HardwareCPU }) {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, flexWrap: 'wrap' }}>
        <strong>{cpu.model}</strong>
        <Badge tone="info">класс {cpu.perf_class}</Badge>
      </div>
      <div className="xsmall faint" style={{ marginTop: 2 }}>
        {cpu.vendor} · {cpu.generation} · {cpu.architecture} · {cpu.release_year}
      </div>
      <dl className="kv" style={{ marginTop: 8 }}>
        <dt>Ядра / потоки</dt>
        <dd>
          {cpu.cores} / {cpu.threads}
        </dd>
        <dt>Однопоточный индекс</dt>
        <dd className="mono">{cpu.single_thread_score.toFixed(2)}</dd>
        <dt>Многопоточный индекс</dt>
        <dd className="mono">{cpu.multi_thread_score.toFixed(2)}</dd>
        <dt>Поддерживаемая память</dt>
        <dd>{cpu.memory_support || 'не указана'}</dd>
        <dt>TDP</dt>
        <dd>{cpu.tdp_w ? `${cpu.tdp_w} Вт` : 'не указан'}</dd>
      </dl>
      {cpu.notes && <p className="xsmall muted">{cpu.notes}</p>}
      <SourceLink url={cpu.source_url} title={cpu.source_title} />
    </div>
  );
}

function GpuSpec({ gpu }: { gpu: HardwareGPU }) {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, flexWrap: 'wrap' }}>
        <strong>{gpu.model}</strong>
        <Badge tone="info">класс {gpu.perf_class}</Badge>
      </div>
      <div className="xsmall faint" style={{ marginTop: 2 }}>
        {gpu.vendor} · {gpu.generation} · {gpu.architecture} · {gpu.release_year}
      </div>
      <dl className="kv" style={{ marginTop: 8 }}>
        <dt>Память</dt>
        <dd>
          {gpu.vram_gb} ГБ {gpu.vram_type}
        </dd>
        <dt>Пропускная способность</dt>
        <dd>{gpu.memory_bandwidth_gbs ? `${gpu.memory_bandwidth_gbs} ГБ/с` : 'не указана'}</dd>
        <dt>Индекс растеризации</dt>
        <dd className="mono">{gpu.raster_score.toFixed(2)}</dd>
        <dt>Индекс трассировки лучей</dt>
        <dd className="mono">{gpu.rt_score.toFixed(2)}</dd>
        <dt>TDP</dt>
        <dd>{gpu.tdp_w ? `${gpu.tdp_w} Вт` : 'не указан'}</dd>
      </dl>
      {gpu.api_support.length > 0 && (
        <div className="chip-row">
          {gpu.api_support.map((api) => (
            <span key={api} className="chip">
              {api}
            </span>
          ))}
        </div>
      )}
      {gpu.notes && <p className="xsmall muted">{gpu.notes}</p>}
      <SourceLink url={gpu.source_url} title={gpu.source_title} />
    </div>
  );
}

export function HardwareScreen() {
  const { result, calculating } = useStore();

  useEnsureResult();

  if (calculating) return <Loading text="Расчёт аппаратной оценки…" />;

  if (!result || !result.hardware) {
    return <Empty>Расчёт ещё не выполнен. Выполните расчёт на этапе «Варианты реализации».</Empty>;
  }

  const hw = result.hardware;
  const confidenceTone = hw.confidence >= 0.7 ? 'ok' : hw.confidence >= 0.45 ? 'warn' : 'danger';

  return (
    <>
      <Card
        title="Референсная минимальная конфигурация"
        hint="Класс рассчитан по характеристикам проекта, целевому разрешению, качеству и FPS с учётом выбранного набора решений."
        actions={
          <Badge tone={confidenceTone}>
            полнота исходных данных: {hw.confidence_label}
          </Badge>
        }
      >
        <Callout tone="warn" title="Результат ориентировочный">
          Это минимальный класс оборудования, а не гарантия конкретного FPS. Система не располагает
          данными профилирования вашей сборки: требуется проверка на прототипе.
        </Callout>

        {hw.exceeds_catalog && (
          <div style={{ marginTop: 12 }}>
            <Callout tone="danger" title="Подходящая конфигурация не найдена">
              Каталог не покрывает все требования. Причины и ограничения перечислены ниже.
            </Callout>
          </div>
        )}

        {hw.unmet_limits.length > 0 && (
          <div style={{ marginTop: 12 }}>
            <Callout tone="danger" title="Заданные пределы не выполнены">
              <ul style={{ margin: '6px 0 0', paddingLeft: 18 }}>
                {hw.unmet_limits.map((limit) => (
                  <li key={limit}>{limit}</li>
                ))}
              </ul>
              <div style={{ marginTop: 8 }}>
                Конфигурация ниже приведена как ориентир: в заданный бюджет она не укладывается.
              </div>
            </Callout>
          </div>
        )}

        {(hw.applicability_limits ?? []).length > 0 && (
          <div style={{ marginTop: 12 }}>
            <Callout tone="danger" title="Вне области применимости модели">
              <ul style={{ margin: '6px 0 0', paddingLeft: 18 }}>
                {(hw.applicability_limits ?? []).map((limit) => (
                  <li key={limit}>{limit}</li>
                ))}
              </ul>
            </Callout>
          </div>
        )}

        <div className="stat-grid" style={{ marginTop: 16 }}>
          <Metric label="Класс GPU" value={hw.gpu_class} hint="из 5" />
          <Metric label="Класс CPU" value={hw.cpu_class} hint="из 5" />
          <Metric label="Оценка VRAM" value={`${hw.estimated_vram_gb} ГБ`} />
          <Metric label="Оценка RAM" value={`${hw.estimated_ram_gb} ГБ`} />
          <Metric
            label="Накопитель"
            value={STORAGE_LABELS[hw.recommended_storage] ?? hw.recommended_storage}
            hint="минимальный ориентир"
          />
          <Metric label="Оценка draw calls" value={hw.estimated_draw_calls.toLocaleString('ru-RU')} />
          <Metric label="Индекс GPU" value={hw.required_gpu_index.toFixed(2)} hint="нормированная шкала" />
          <Metric label="Индекс CPU" value={hw.required_cpu_index.toFixed(2)} hint="нормированная шкала" />
        </div>
      </Card>

      {(hw.non_client_methods ?? []).length > 0 && (
        <Card
          title="Решения, не вошедшие в расчёт"
          hint="Полезные решения, чей эффект проявляется не на компьютере игрока: они не уменьшают требования к нему."
        >
          <ul className="reason-list">
            {hw.non_client_methods.map((item) => (
              <li key={item.code}>
                <strong>{item.name}</strong> — {item.reason}.
              </li>
            ))}
          </ul>
        </Card>
      )}

      {hw.modeling_gaps.length > 0 && (
        <Card
          title="Неопределённые параметры модели"
          hint="Это не ошибка запроса: система фиксирует, какие технические входы не были заданы и поэтому ограничивают точность оценки."
        >
          <ul className="reason-list">
            {hw.modeling_gaps.map((gap, index) => (
              <li key={index}>{gap}</li>
            ))}
          </ul>
        </Card>
      )}

      <Card title="Референсная пара CPU + GPU">
        <div className="grid grid-2">
          <div>
            <h4 style={{ marginBottom: 6 }}>Процессор</h4>
            {hw.reference_cpu ? (
              <CpuSpec cpu={hw.reference_cpu} />
            ) : (
              <p className="muted">Подходящая запись в каталоге не найдена.</p>
            )}
          </div>
          <div>
            <h4 style={{ marginBottom: 6 }}>Видеокарта</h4>
            {hw.reference_gpu ? (
              <GpuSpec gpu={hw.reference_gpu} />
            ) : (
              <p className="muted">Подходящая запись в каталоге не найдена.</p>
            )}
          </div>
        </div>
      </Card>

      {hw.required_hw_features.length > 0 && (
        <Card
          title="Обязательные аппаратные возможности"
          hint="Эти требования накладываются выбранными решениями: оборудование без их поддержки не подходит."
        >
          <div className="chip-row">
            {hw.required_hw_features.map((feature) => (
              <span key={feature} className="chip">
                {feature}
              </span>
            ))}
          </div>
        </Card>
      )}

      {(hw.alternative_gpus.length > 0 || hw.alternative_cpus.length > 0) && (
        <Card
          title="Альтернативы того же класса"
          hint="Записи сопоставимой производительности: окончательный выбор определяется доступностью и ценой."
        >
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Тип</th>
                  <th>Модель</th>
                  <th>Год</th>
                  <th>Класс</th>
                  <th>Ключевой показатель</th>
                </tr>
              </thead>
              <tbody>
                {hw.alternative_cpus.map((cpu) => (
                  <tr key={`cpu-${cpu.model}`}>
                    <td className="small muted">CPU</td>
                    <td className="small">{cpu.model}</td>
                    <td className="small mono">{cpu.release_year}</td>
                    <td className="small mono">{cpu.perf_class}</td>
                    <td className="small mono">многопоточный {cpu.multi_thread_score.toFixed(2)}</td>
                  </tr>
                ))}
                {hw.alternative_gpus.map((gpu) => (
                  <tr key={`gpu-${gpu.model}`}>
                    <td className="small muted">GPU</td>
                    <td className="small">{gpu.model}</td>
                    <td className="small mono">{gpu.release_year}</td>
                    <td className="small mono">{gpu.perf_class}</td>
                    <td className="small mono">растеризация {gpu.raster_score.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {hw.caveats.length > 0 && (
        <Card
          title="Ограничения оценки"
          hint="Условия, при которых расчёт теряет точность и требует экспериментальной проверки."
        >
          <ul className="reason-list">
            {hw.caveats.map((caveat, index) => (
              <li key={index}>{caveat}</li>
            ))}
          </ul>
        </Card>
      )}
    </>
  );
}
