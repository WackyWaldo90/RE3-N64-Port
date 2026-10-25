#!/usr/bin/env bash
set -Eeuo pipefail
mkdir -p artifacts/re-tools
exec > >(tee artifacts/re-tools/install.log) 2>&1
python3 -m venv /tmp/re3-n64-tools-venv
source /tmp/re3-n64-tools-venv/bin/activate
python -m pip install --upgrade pip
# Python utilities, sourced from their public upstream repositories.
python -m pip install 'splat64' 'spimdisasm' 'rabbitizer' 'n64img' || {
  echo 'One or more Python packages failed installation; see log.'
  exit 1
}
for tool in splat spimdisasm; do
  if command -v "$tool" >/dev/null; then "$tool" --help > "artifacts/re-tools/${tool}-help.txt" 2>&1 || true; fi
done
python - <<'PY' > artifacts/re-tools/python-imports.txt
import importlib
for name in ('rabbitizer', 'spimdisasm', 'splat', 'n64img'):
    try:
        mod = importlib.import_module(name)
        print(f'{name}: OK {getattr(mod, "__file__", "built-in")}')
    except Exception as exc:
        print(f'{name}: UNAVAILABLE ({type(exc).__name__}: {exc})')
PY
