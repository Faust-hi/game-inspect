/** Клиент HTTP-интерфейса backend-приложения. */
import type {
  AdminOverview,
  Conflict,
  Engine,
  Enums,
  GameExample,
  GameFunction,
  HardwareCPU,
  HardwareGPU,
  LoadProfile,
  Method,
  ProjectProfile,
  RecommendationResult,
  SimilarGame,
  ValidationIssue,
} from './types';

const BASE = '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    let detail = `Ошибка ${response.status}`;
    try {
      const payload = await response.json();
      detail = payload?.detail ?? detail;
    } catch {
      /* ответ без тела — оставляем сообщение по умолчанию */
    }
    throw new Error(detail);
  }
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

  recommend: (profile: ProjectProfile, basket: string[]) =>
    request<RecommendationResult>('/recommend', {
      method: 'POST',
      body: JSON.stringify({ profile, basket }),
    }),

  loadProfile: (profile: ProjectProfile, basket: string[]) =>
    request<LoadProfile>('/load-profile', {
      method: 'POST',
      body: JSON.stringify({ profile, basket }),
    }),

  similarGames: (profile: ProjectProfile, basket: string[]) =>
    request<SimilarGame[]>('/similar-games', {
      method: 'POST',
      body: JSON.stringify({ profile, basket }),
    }),

  hardwareEstimate: (profile: ProjectProfile, basket: string[]) =>
    request<import('./types').HardwareEstimate>('/hardware-estimate', {
      method: 'POST',
      body: JSON.stringify({ profile, basket }),
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
};

/** Административный раздел. Токен хранится в localStorage. */
export function adminToken(): string {
  return localStorage.getItem('dss_admin_token') ?? '';
}

export function setAdminToken(token: string): void {
  localStorage.setItem('dss_admin_token', token);
}

function adminHeaders(): Record<string, string> {
  return { 'x-admin-token': adminToken() };
}

async function adminRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { ...adminHeaders(), ...(init?.headers ?? {}) },
  });
  if (!response.ok) {
    let detail = `Ошибка ${response.status}`;
    try {
      const payload = await response.json();
      detail = payload?.detail ?? detail;
    } catch {
      /* ответ без тела */
    }
    throw new Error(detail);
  }
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
      headers: { ...adminHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    }),
  deleteMethod: (code: string) =>
    adminRequest<{ deleted: string }>(`/admin/methods/${code}`, { method: 'DELETE' }),

  importEntity: async (entity: string, file: File) => {
    const form = new FormData();
    form.append('file', file);
    const response = await fetch(`${BASE}/admin/import/${entity}`, {
      method: 'POST',
      headers: adminHeaders(),
      body: form,
    });
    if (!response.ok) {
      throw new Error(`Ошибка импорта: ${response.status}`);
    }
    return (await response.json()) as { entity: string; created: number; updated: number; skipped: number };
  },
};
