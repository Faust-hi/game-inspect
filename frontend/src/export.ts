/** Экспорт проекта в файл: JSON-снимок и печать отчёта (PDF). */
import type { ProjectProfile, RecommendationResult } from './types';

const EXPORT_VERSION = 1;

function triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/** Приводит название проекта к безопасному имени файла. */
function slugify(value: string): string {
  const normalized = value
    .trim()
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, '-')
    .replace(/^-+|-+$/g, '');
  return normalized || 'project';
}

function fileStamp(): string {
  const now = new Date();
  const pad = (part: number) => String(part).padStart(2, '0');
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
}

/** Полный снимок проекта: анкета, корзина решений и результат расчёта. */
export interface ProjectExport {
  format: 'gamedev-dss-project';
  version: number;
  exported_at: string;
  profile: ProjectProfile;
  basket: string[];
  result: RecommendationResult | null;
}

export function buildProjectExport(
  profile: ProjectProfile,
  basket: string[],
  result: RecommendationResult | null,
): ProjectExport {
  return {
    format: 'gamedev-dss-project',
    version: EXPORT_VERSION,
    exported_at: new Date().toISOString(),
    profile,
    basket,
    result,
  };
}

/** Выгружает проект в JSON: файл пригоден для повторной загрузки и для контроля расчёта. */
export function exportProjectJson(
  profile: ProjectProfile,
  basket: string[],
  result: RecommendationResult | null,
): void {
  const payload = buildProjectExport(profile, basket, result);
  const blob = new Blob([JSON.stringify(payload, null, 2)], {
    type: 'application/json;charset=utf-8',
  });
  triggerDownload(blob, `${slugify(profile.name)}-${fileStamp()}.json`);
}

/**
 * Экспорт в PDF выполняется средствами браузера через диалог печати.
 * Печатные стили скрывают навигацию, поэтому в печать уходит только отчёт.
 */
export function exportProjectPdf(): void {
  window.print();
}
