/** Клиент HTTP-интерфейса backend-приложения. */
import type {
  ImplementationBaseline,
  AdminOverview,
  Conflict,
  Dependency,
  Engine,
  Enums,
  EvidenceClaim,
  EvidenceSource,
  EvidenceSummary,
  GameFunction,
  GameCase,
  GraphChecks,
  Method,
  ProjectProfile,
  RecommendationResult,
  ReportData,
  Schedule,
  SeedReport,
  StageGuidance,
  TeamScenario,
  ValidationIssue,
} from './types';

const BASE = '/api';

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/** Приводит элемент массива `details` к тексту: «поле: сообщение». */
function detailToText(item: unknown): string {
  if (typeof item === 'string') return item;
  if (isRecord(item)) {
    // Поле приходит как «body.profile.name»: пользователю понятнее без служебного префикса.
    const field = typeof item.field === 'string' ? item.field.replace(/^body\./, '') : '';
    const message = typeof item.message === 'string' ? item.message : '';
    if (field && message) return `${field}: ${message}`;
    return message || field;
  }
  return String(item);
}

/**
 * Разбирает ответ об ошибке.
 *
 * Backend отвечает единым форматом `{error, details, request_id}`, но часть
 * ошибок приходит от самого FastAPI в виде `{detail}`. Раньше клиент искал
 * только `detail` и при расхождении formats показывал «Ошибка 422» вместо
 * текста, поэтому разбираются оба варианта.
 */
export function parseApiError(payload: unknown, status: number): ApiRequestError {
  const record = isRecord(payload) ? payload : {};
  const rawMessage =
    typeof record.error === 'string'
      ? record.error
      : typeof record.detail === 'string'
        ? record.detail
        : null;
  const details = Array.isArray(record.details)
    ? record.details.map(detailToText).filter(Boolean)
    : [];
  const requestId = typeof record.request_id === 'string' ? record.request_id : null;
  return new ApiRequestError(rawMessage ?? `Ошибка ${status}`, status, details, requestId);
}

/** Ошибка запроса с сохранением разобранных подробностей. */
export class ApiRequestError extends Error {
  readonly status: number;
  readonly details: string[];
  readonly requestId: string | null;

  constructor(message: string, status: number, details: string[], requestId: string | null) {
    const suffix =
      details.length > 0
        ? `: ${details.slice(0, 5).join('; ')}`
        : requestId && status >= 500
          ? ` (код обращения ${requestId})`
          : '';
    super(message + suffix);
    this.name = 'ApiRequestError';
    this.status = status;
    this.details = details;
    this.requestId = requestId;
  }
}

async function throwIfError(response: Response): Promise<void> {
  if (response.ok) return;
  let payload: unknown = null;
  try {
    payload = await response.json();
  } catch {
    /* ответ без тела — остаётся сообщение по коду состояния */
  }
  throw parseApiError(payload, response.status);
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  });
  await throwIfError(response);
  return (await response.json()) as T;
}

/** POST с формой (импорт файлов): без JSON-заголовка, boundary ставит браузер. */
async function postForm<T>(path: string, form: FormData, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, { method: 'POST', ...init, body: form });
  await throwIfError(response);
  return (await response.json()) as T;
}

export const api = {
  enums: () => request<Enums>('/meta/enums'),

  functions: () => request<GameFunction[]>('/catalog/functions'),
  methods: () => request<Method[]>('/catalog/methods'),
  engines: () => request<Engine[]>('/catalog/engines'),
  conflicts: () => request<Conflict[]>('/catalog/conflicts'),
  sources: () => request<EvidenceSource[]>('/catalog/sources'),
  evidence: (entity?: string, entityCode?: string) => {
    const query = new URLSearchParams();
    if (entity) query.set('entity', entity);
    if (entityCode) query.set('entity_code', entityCode);
    return request<EvidenceClaim[]>(`/catalog/evidence${query.toString() ? `?${query}` : ''}`);
  },
  evidenceSummary: () => request<EvidenceSummary>('/catalog/evidence-summary'),
  cases: () => request<GameCase[]>('/catalog/cases'),
  dependencies: () => request<Dependency[]>('/catalog/dependencies'),
  graphChecks: (options?: { basket?: string[]; engine?: string; engineVersion?: string; renderApi?: string }) => {
    const query = new URLSearchParams();
    (options?.basket ?? []).forEach(code => query.append('basket', code));
    if (options?.engine) query.set('engine', options.engine);
    if (options?.engineVersion) query.set('engine_version', options.engineVersion);
    if (options?.renderApi) query.set('render_api', options.renderApi);
    return request<GraphChecks>(`/catalog/graph-checks${query.toString() ? `?${query}` : ''}`);
  },
  teams: () => request<TeamScenario[]>('/catalog/teams'),
  stageGuidance: (stage: string) =>
    request<StageGuidance>(`/catalog/stage-guidance?stage=${encodeURIComponent(stage)}`),

  recommend: (profile: ProjectProfile, basket: string[], signal?: AbortSignal, baseline?: ImplementationBaseline | null) =>
    request<RecommendationResult>('/recommend', {
      method: 'POST',
      body: JSON.stringify({ profile, basket, ...(baseline ? { baseline } : {}) }),
      signal,
    }),

  schedule: (profile: ProjectProfile, basket: string[], team = 'small_2_5', includeDependencies = true) =>
    request<Schedule>('/schedule', {
      method: 'POST',
      body: JSON.stringify({ profile, basket, team, include_dependencies: includeDependencies }),
    }),

  reportData: (profile: ProjectProfile, basket: string[], baseline?: ImplementationBaseline | null) =>
    request<ReportData>('/report-data', {
      method: 'POST',
      body: JSON.stringify({ profile, basket, ...(baseline ? { baseline } : {}) }),
    }),

};

/** Административный раздел. Локальный режим: без токена. */
async function adminRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, init);
  await throwIfError(response);
  return (await response.json()) as T;
}

export const adminApi = {
  overview: () => adminRequest<AdminOverview>('/admin/overview'),
  validate: () => adminRequest<{ issues: ValidationIssue[]; total: number }>('/admin/validate', { method: 'POST' }),
  /** `restoreDemo` — явное согласие заменить существующие записи демоданными. */
  seed: (restoreDemo = false) =>
    adminRequest<SeedReport>('/admin/seed', {
      method: 'POST',
      body: JSON.stringify({ restore_demo: restoreDemo }),
    }),
  methods: () => adminRequest<Method[]>('/admin/methods'),
  setStatus: (code: string, status: string) =>
    adminRequest<{ code: string; status: string }>(`/admin/methods/${code}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    }),
  deleteMethod: (code: string) =>
    adminRequest<{ deleted: string }>(`/admin/methods/${code}`, { method: 'DELETE' }),

  importEntity: async (entity: string, file: File) => {
    const form = new FormData();
    form.append('file', file);
    return postForm<{ entity: string; created: number; updated: number; skipped: number }>(
      `/admin/import/${entity}`,
      form,
    );
  },
};
