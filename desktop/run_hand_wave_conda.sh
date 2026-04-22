#!/usr/bin/env bash
set -euo pipefail

# Skrypt uruchamia desktopową aplikację przez środowisko Conda.
# Dzięki elastycznemu wykrywaniu Condy działa także wtedy, gdy `conda`
# nie jest dodana do PATH w nieinteraktywnych powłokach.

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

# Funkcja próbuje odszukać wykonywalny plik `conda` różnymi metodami.
# Zwraca 0 i wypisuje ścieżkę do polecenia, gdy wykrycie się powiedzie.
resolve_conda_cmd() {
  local candidate

  # 1) Najprostszy przypadek: conda jest w PATH.
  if command -v conda >/dev/null 2>&1; then
    command -v conda
    return 0
  fi

  # 2) W wielu instalacjach Conda jest dostępna jako CONDA_EXE.
  if [[ -n "${CONDA_EXE:-}" && -x "${CONDA_EXE}" ]]; then
    printf '%s\n' "${CONDA_EXE}"
    return 0
  fi

  # 3) Typowe lokalizacje Miniconda/Anaconda na Linux/macOS.
  local conda_home_candidates=(
    "${HOME}/miniconda3"
    "${HOME}/anaconda3"
    "/opt/miniconda3"
    "/opt/anaconda3"
  )

  for candidate in "${conda_home_candidates[@]}"; do
    if [[ -x "${candidate}/bin/conda" ]]; then
      printf '%s\n' "${candidate}/bin/conda"
      return 0
    fi
  done

  # 4) Ostatnia próba: załaduj hook Conda i sprawdź ponownie.
  for candidate in "${conda_home_candidates[@]}"; do
    if [[ -f "${candidate}/etc/profile.d/conda.sh" ]]; then
      # shellcheck disable=SC1090
      source "${candidate}/etc/profile.d/conda.sh"
      if command -v conda >/dev/null 2>&1; then
        command -v conda
        return 0
      fi
    fi
  done

  return 1
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

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "[ERROR] Brak pliku environment.yml: ${ENV_FILE}" >&2
  exit 1
fi

# Ustalenie działającego polecenia Conda (pełna ścieżka lub alias z PATH).
if ! CONDA_CMD="$(resolve_conda_cmd)"; then
  echo "[ERROR] Nie znaleziono polecenia 'conda'." >&2
  echo "[HINT] Zainstaluj Miniconda/Anaconda lub dodaj Condę do PATH." >&2
  echo "[HINT] Przykład: export PATH=\"\$HOME/miniconda3/bin:\$PATH\"" >&2
  exit 1
fi

if [[ ${CREATE_ENV} -eq 1 ]]; then
  # Aktualizacja środowiska jest idempotentna i bezpieczna przy wielokrotnym uruchomieniu.
  "${CONDA_CMD}" env update --name "${ENV_NAME}" --file "${ENV_FILE}" --prune
fi

# Uruchomienie aplikacji przez `conda run` bez ręcznej aktywacji środowiska.
exec "${CONDA_CMD}" run --no-capture-output -n "${ENV_NAME}" python "${SCRIPT_DIR}/hand_wave.py" "${PY_ARGS[@]}"
