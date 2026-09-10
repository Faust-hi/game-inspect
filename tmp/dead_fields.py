"""Поля типов frontend, которых нет ни в одном ответе backend.

Имя поля ищется в исходниках backend (модели, схемы, сериализаторы).
Отсутствие во всех них означает, что ветка интерфейса не может получить данные.
"""
import pathlib
import re

ROOT = pathlib.Path(r"C:\Users\user\Desktop\game-inspect")
types_src = (ROOT / "frontend" / "src" / "types.ts").read_text(encoding="utf-8")

backend_text = []
for pattern in ("app/**/*.py",):
    for path in (ROOT / "backend").glob(pattern):
        if "__pycache__" not in str(path):
            backend_text.append(path.read_text(encoding="utf-8", errors="ignore"))
backend = "\n".join(backend_text)

fields = set()
for match in re.finditer(r"^\s{2}([a-z_][a-z0-9_]*)\s*\??\s*:", types_src, re.M):
    fields.add(match.group(1))

# Поля интерфейса: служебные и чисто интерфейсные отсекаем по словарю.
frontend_only = {
    "key", "label", "tone", "hint", "tabs", "rows", "items", "title",
}
missing = []
for field in sorted(fields):
    if field in frontend_only:
        continue
    if not re.search(rf"\b{field}\b", backend):
        missing.append(field)

print("Полей в типах:", len(fields))
print("Не встречаются в backend:", missing)
