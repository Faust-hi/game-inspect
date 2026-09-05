/** Клиент HTTP-интерфейса backend-приложения. */
import type {
  AdminOverview,
  Conflict,
  Engine,
  Enums,
  FeedbackSummary,
  FeedbackVote,
  GameExample,
  GameFunction,
  HardwareCPU,
  HardwareGPU,
  Method,
  PresetFile,
  ProjectImport,
  ProjectProfile,
  RecommendationResult,
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

export const api = {
  health: () => request<{ status: string; version: string; database: string }>('/health'),

  enums: () => request<Enums>('/meta/enums'),

  functions: () => request<GameFunction[]>('/catalog/functions'),
  methods: () => request<Method[]>('/catalog/methods'),
  method: (code: string) => request<Method>(`/catalog/methods/${code}`),
  engines: () => request<Engine[]>('/catalog/engines'),
  conflicts: () => request<Conflict[]>('/catalog/conflicts'),
  examples: () => request<GameExample[]>('/catalog/examples'),
  hardware: () => request<{ cpu: HardwareCPU[]; gpu: HardwareGPU[] }>('/catalog/hardware'),

  recommend: (profile: ProjectProfile, basket: string[], signal?: AbortSignal) =>
    request<RecommendationResult>('/recommend', {
      method: 'POST',
      body: JSON.stringify({ profile, basket }),
      signal,
    }),

  saveProject: (profile: ProjectProfile, basket: string[]) =>
    request<{ public_id: string }>('/projects', {
      method: 'POST',
      body: JSON.stringify({ profile, basket }),
    }),

  loadProject: (publicId: string) =>
    request<{ public_id: string; name: string; profile: ProjectProfile; basket: string[] }>(
      `/projects/${publicId}`,
    ),

  feedback: (publicId: string, methodCode: string, useful: boolean) =>
    request<FeedbackVote>(`/projects/${publicId}/feedback`, {
      method: 'POST',
      body: JSON.stringify({ method_code: methodCode, useful }),
    }),

  importProject: async (files: File[]) => {
    const form = new FormData();
    for (const file of files) form.append('files', file);
    const response = await fetch(`${BASE}/project-import`, {
      method: 'POST',
      body: form,
    });
    await throwIfError(response);
    return (await response.json()) as ProjectImport;
  },

  presets: (profile: ProjectProfile, basket: string[]) =>
    request<{ files: PresetFile[] }>('/project-presets', {
      method: 'POST',
      body: JSON.stringify({ profile, basket }),
    }),

  feedbackSummary: () => adminRequest<FeedbackSummary>('/admin/feedback-summary'),
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
  seed: () => adminRequest<Record<string, number>>('/admin/seed', { method: 'POST' }),
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
    const response = await fetch(`${BASE}/admin/import/${entity}`, {
      method: 'POST',
      body: form,
    });
    await throwIfError(response);
    return (await response.json()) as { entity: string; created: number; updated: number; skipped: number };
  },
};
