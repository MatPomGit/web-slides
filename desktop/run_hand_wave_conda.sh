#!/usr/bin/env bash
set -euo pipefail

# Skrypt uruchamia desktopową aplikację przez środowisko Conda.
# Dzięki użyciu `conda run` nie wymaga ręcznej aktywacji środowiska.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/environment.yml"
ENV_NAME="hand-wave"

# Funkcja wypisuje pomoc i kończy działanie.
show_help() {
  cat <<'USAGE'
Użycie:
  ./run_hand_wave_conda.sh [--create-env] [--env-name NAME] [--] [ARGUMENTY_DLA_PYTHONA]

Opcje:
  --create-env      Utwórz lub zaktualizuj środowisko na podstawie environment.yml
  --env-name NAME   Nazwa środowiska Conda (domyślnie: hand-wave)
  -h, --help        Pokaż pomoc

Przykłady:
  ./run_hand_wave_conda.sh --create-env -- --debug
  ./run_hand_wave_conda.sh -- --headless --backend pynput
USAGE
}

CREATE_ENV=0
PY_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --create-env)
      CREATE_ENV=1
      shift
      ;;
    --env-name)
      ENV_NAME="$2"
      shift 2
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    --)
      shift
      PY_ARGS=("$@")
      break
      ;;
    *)
      PY_ARGS+=("$1")
      shift
      ;;
  esac
done

if ! command -v conda >/dev/null 2>&1; then
  echo "[ERROR] Nie znaleziono polecenia 'conda'. Zainstaluj Miniconda lub Anaconda." >&2
  exit 1
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "[ERROR] Brak pliku environment.yml: ${ENV_FILE}" >&2
  exit 1
fi

if [[ ${CREATE_ENV} -eq 1 ]]; then
  # Aktualizacja środowiska jest idempotentna i bezpieczna przy wielokrotnym uruchomieniu.
  conda env update --name "${ENV_NAME}" --file "${ENV_FILE}" --prune
fi

# Uruchomienie aplikacji przez conda run.
exec conda run --no-capture-output -n "${ENV_NAME}" python "${SCRIPT_DIR}/hand_wave.py" "${PY_ARGS[@]}"
