# Проверки сверки

Дата: 2026-09-07. Приложение не исправлялось. Исходные пользовательские изменения сохранены.

Из каталога backend, с PYTHONDONTWRITEBYTECODE=1:

```powershell
../.venv/Scripts/python.exe -m pytest tests/test_operational.py tests/test_hardware_semantics.py tests/test_publication.py -q -p no:cacheprovider --tb=short
```

Результат: 64 passed, 3 warnings in 6.57s; exit code 0. Предупреждения касаются Starlette/httpx, BlockingPortal и переименования HTTP_422_UNPROCESSABLE_ENTITY. Тесты используют временную БД согласно conftest.

Из корня:

```powershell
.venv/Scripts/python.exe audit-2026-09-07/comparison/comparison_probes.py
```

Итоговый прогон: exit code 0, доказательства записаны в comparison_evidence.json. Все 91 SHA-256 исходного аудита совпадают. Обе копии внешних отчётов совпадают с исходными файлами по SHA-256. В COMPARISON.md сохранены 55 строк A1–A11/B1–B44 без пропусков.

Контроль Alembic выполнен на отдельной временной SQLite-БД: upgrade head → check проходит; добавление audit_unmapped без изменения revision → check завершается ошибкой с remove_table. Эта ожидаемая ошибка доказывает сравнение DDL, а не неисправность миграций проекта.

При разработке проверочного скрипта первое удаление его временной БД не удалось из-за незакрытого соединения sqlite3. В скрипт добавлен явный close, оставшийся собственный временный файл удалён, итоговый повторный прогон и очистка завершились успешно. Рабочая БД не затрагивалась.

Полный frontend/backend gate повторно не запускался: исходники не изменены, для расхождений выполнены адресные проверки. Исторические результаты первого аудита обозначены отдельно в COMPARISON.md.
