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
- `environment.yml` – zależności Conda,
- `run_hand_wave_conda.sh` – launcher przez Condę.

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

## Najważniejsze argumenty programu

- `--debug` – pokazuje okno podglądu i status detekcji,
- `--headless` – uruchamia bez GUI,
- `--backend pyautogui|pynput` – wybór backendu wysyłania klawiszy,
- `--roi X1 Y1 X2 Y2` – obszar aktywnej detekcji w proporcjach kadru,
- `--wave-min-delta-x-px` – minimalny ruch poziomy,
- `--min-horizontal-velocity-px-s` – minimalna prędkość ruchu.

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

1. **`conda: command not found`**  
   Zainstaluj Minicondę/Anacondę i uruchom nową sesję terminala.

2. **Brak obrazu z kamery**  
   Spróbuj `--camera-id 1` albo zamknij inne aplikacje, które używają kamery.

3. **Brak reakcji na gesty**  
   Uruchom z `--debug` i dostrój parametry ROI oraz progi wykrywania.
