/** Проверки разбора ошибок, приходящих от backend-приложения. */
import { describe, expect, it } from 'vitest';
import { ApiRequestError, parseApiError } from '../api';

describe('parseApiError', () => {
  it('разбирает единый формат {error, details, request_id}', () => {
    const error = parseApiError(
      {
        error: 'Публикация невозможна',
        details: ['source_url: обязательное поле'],
        request_id: 'req-1',
      },
      409,
    );

    expect(error.status).toBe(409);
    expect(error.details).toEqual(['source_url: обязательное поле']);
    expect(error.requestId).toBe('req-1');
    // Пользователь должен видеть текст проблемы, а не «Ошибка 409».
    expect(error.message).toContain('Публикация невозможна');
    expect(error.message).toContain('source_url');
  });

  it('не теряет сообщение из формата FastAPI {detail}', () => {
    const error = parseApiError({ detail: 'Метод не найден' }, 404);

    expect(error.message).toBe('Метод не найден');
    expect(error.details).toEqual([]);
  });

  it('приводит элементы details к виду «поле: сообщение» без служебного префикса body.', () => {
    const error = parseApiError(
      {
        error: 'Ошибка валидации',
        details: [
          { field: 'body.profile.target_fps', message: 'должно быть не менее 15' },
          { field: 'body.profile.platforms', message: 'нужен хотя бы один элемент' },
        ],
      },
      422,
    );

    expect(error.details).toEqual([
      'profile.target_fps: должно быть не менее 15',
      'profile.platforms: нужен хотя бы один элемент',
    ]);
  });

  it('на серверной ошибке без подробностей сообщает код обращения', () => {
    const error = parseApiError({ error: 'Внутренняя ошибка', request_id: 'req-42' }, 500);

    expect(error.message).toContain('req-42');
    expect(error.details).toEqual([]);
  });

  it('без тела ответа оставляет понятное сообщение по коду состояния', () => {
    expect(parseApiError(null, 502).message).toBe('Ошибка 502');
    expect(parseApiError('не JSON', 500).message).toBe('Ошибка 500');
  });

  it('возвращает ApiRequestError — полноценную ошибку с сохранённым статусом', () => {
    const error = parseApiError({ error: 'нет доступа' }, 403);

    expect(error).toBeInstanceOf(ApiRequestError);
    expect(error).toBeInstanceOf(Error);
    expect(error.status).toBe(403);
    expect(error.requestId).toBeNull();
    expect(error.message).toBe('нет доступа');
  });
});
