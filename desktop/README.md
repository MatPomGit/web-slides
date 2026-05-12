# Hand Wave Slide Controller (Desktop)

Aplikacja desktopowa pozwala sterować slajdami gestem dłoni wykrywanym przez kamerę.

## Co zostało ulepszone

- dodano prosty launcher `run_hand_wave_conda.sh`, który uruchamia aplikację przez `conda run` bez ręcznej aktywacji środowiska,
- dodano opcję automatycznego utworzenia/aktualizacji środowiska (`--create-env`),
- uporządkowano dokumentację i przykłady uruchamiania.

## Wymagania

- Linux/macOS (dla skryptu `.sh`),
- zainstalowana **Conda** (Miniconda lub Anaconda),
- kamera dostępna jako urządzenie systemowe.

## Struktura folderu

- `hand_wave.py` – główna aplikacja,
- `run_logger.py` – konfiguracja logowania do pliku i konsoli,
- `environment.yml` – zależności Conda,
- `run_hand_wave_conda.sh` – launcher przez Condę.
- `gui_configurator.py` – GUI (PyQt) do konfiguracji parametrów detekcji,


## Szybki start (Conda)

### 1) Pierwsze uruchomienie (tworzenie środowiska)

```bash
cd desktop
./run_hand_wave_conda.sh --create-env -- --debug
```

### 2) Kolejne uruchomienia

```bash
cd desktop
./run_hand_wave_conda.sh -- --debug
```

### 3) Tryb bez okna podglądu (headless)

```bash
cd desktop
./run_hand_wave_conda.sh -- --headless
```

## Alternatywnie: klasyczne uruchomienie Conda

```bash
cd desktop
conda env create -f environment.yml
conda activate hand-wave
python hand_wave.py --debug
```

> **Uwaga:** nie uruchamiaj aplikacji z przypadkowego środowiska bazowego (np. `base`), bo może to dać konflikt binarny NumPy/MediaPipe. Najbezpieczniej uruchamiać przez `run_hand_wave_conda.sh`.

## Najważniejsze argumenty programu

- `--debug` – pokazuje okno podglądu i status detekcji,
- `--headless` – uruchamia bez GUI,
- `--backend pyautogui|pynput` – wybór backendu wysyłania klawiszy,
- `--roi X1 Y1 X2 Y2` – obszar aktywnej detekcji w proporcjach kadru,
- `--wave-min-delta-x-px` – minimalny ruch poziomy,
- `--min-horizontal-velocity-px-s` – minimalna prędkość ruchu,
- `--log-dir` – katalog, gdzie zapisywane są logi kolejnych uruchomień.
- `--no-quiet-third-party-logs` – pokazuje pełne logi bibliotek zewnętrznych (domyślnie są wyciszone),
- `--show-protobuf-deprecation-warning` – pokazuje ostrzeżenie deprecacyjne protobuf (domyślnie ukryte).

Pełna pomoc:

```bash
./run_hand_wave_conda.sh -- --help
```

## Strojenie detekcji

Jeśli wykrywa **za dużo**:

- zwiększ `--wave-min-delta-x-px`,
- zwiększ `--cooldown-sec`,
- zwiększ `--min-extended-fingers`.

Jeśli wykrywa **za rzadko**:

- zmniejsz `--wave-min-delta-x-px`,
- zmniejsz `--min-horizontal-velocity-px-s`,
- ustaw `--process-every-n-frames 1`.

## Rozwiązywanie problemów

0. **`PackagesNotFoundError: mediapipe` podczas `--create-env`**  
   W `environment.yml` pakiet `mediapipe` jest instalowany przez `pip` (sekcja `pip:`), ponieważ często nie jest dostępny jako pakiet Conda dla bieżącej platformy.

1. **`conda: command not found`**  
   Launcher automatycznie próbuje wykryć Condę w typowych lokalizacjach (`~/miniconda3`, `~/anaconda3`, `/opt/miniconda3`, `/opt/anaconda3`). Jeśli błąd nadal występuje, zainstaluj Minicondę/Anacondę lub dodaj Condę do `PATH`, np. `export PATH="$HOME/miniconda3/bin:$PATH"`.

2. **Brak obrazu z kamery**  
   Spróbuj `--camera-id 1` albo zamknij inne aplikacje, które używają kamery.

3. **Brak reakcji na gesty**  
   Uruchom z `--debug` i dostrój parametry ROI oraz progi wykrywania.

4. **`RuntimeError: Nie znaleziono modułu MediaPipe Hands (solutions.hands)`**  
   Zainstalowałeś wydanie `mediapipe`, które nie wystawia legacy API `solutions`. Ten projekt używa API `mp.solutions.hands`, dlatego przypnij wersję pakietu:

   ```bash
   pip uninstall -y mediapipe
   pip install mediapipe==0.10.14
   ```

   Następnie uruchom aplikację ponownie.

5. **Błąd ABI NumPy (`A module that was compiled using NumPy 1.x cannot be run in NumPy 2.x`)**  
   To oznacza konflikt wersji binarnych pakietów. Użyj dedykowanego środowiska projektu:

   ```bash
   cd desktop
   ./run_hand_wave_conda.sh --create-env -- --debug
   ```

   Jeśli uruchamiasz ręcznie, przypnij `numpy<2` i odtwórz środowisko.

## GUI konfiguracji

Uruchom lokalny konfigurator:

```bash
cd desktop
python gui_configurator.py
# wymaga: pip install pyqt6
```

GUI (PyQt) pozwala edytować `gesture_config.yaml`, obsługuje wyszukiwanie parametrów, import/eksport ustawień, automatyczny backup przed zapisem oraz sekcję przyszłych modułów (nieaktywne przyciski roadmapy).

Szczegółowy plan rozwoju znajdziesz w `desktop/docs/plan_rozwoju_desktop.md`.
