# Reveal.js + MediaPipe Hand Gesture

To jest czysto webowy prototyp prezentacji Reveal.js sterowanej gestem dłoni.

## Co robi

- ładuje slajdy z pliku `slides.md`
- uruchamia kamerę w przeglądarce po kliknięciu przycisku startowego
- wykrywa otwartą dłoń przez MediaPipe Hand Landmarker
- po ruchu dłoni w prawo przechodzi do następnego slajdu
- po ruchu dłoni w lewo przechodzi do poprzedniego slajdu
- klawiszem `d` otwiera i zamyka panel debug/config
- klawiszem `f` przełącza fullscreen
- pokazuje czytelny komunikat o błędzie przy problemach z kamerą lub modelem

## Jak uruchomić

Reveal.js ładowany z zewnętrznego pliku Markdown wymaga uruchomienia przez lokalny serwer HTTP.
Nie otwieraj `index.html` przez `file://`.

Najwygodniej uruchomić jeden z dostarczonych skryptów:

### Windows

```bat
start-presentation.bat
```

### Linux / macOS

```sh
./start-presentation.sh
```

Możesz też uruchomić serwer ręcznie:

```bash
python -m http.server 8000
```

Następnie otwórz w przeglądarce:

```text
http://localhost:8000/
```

## Sterowanie

- `Uruchom kamerę` — ładuje model MediaPipe i prosi o dostęp do kamery
- `Wznów/Wstrzymaj detekcję` — pauza analizy
- `Następny` / `Poprzedni` — ręczne przełączanie slajdów
- `d` — pokazuje lub ukrywa panel debug/config
- `f` — włącza lub wyłącza pełny ekran

## Debug i konfiguracja

Panel debug pokazuje aktualne metryki detekcji:

- `deltaX`
- `deltaY`
- kierunek ruchu
- liczbę rozpoznanych wyprostowanych palców
- szerokość dłoni
- długość historii pomiarów

W panelu można stroić najważniejsze progi bez edycji kodu. Ustawienia zapisują się w `localStorage` przeglądarki.

## Typowe problemy

### Nie pojawia się obraz z kamery

- kliknij przycisk uruchomienia kamery na ekranie startowym
- sprawdź, czy przeglądarka dostała zgodę na kamerę
- zamknij inne aplikacje używające kamery, np. Teams, Zoom, aparat systemowy
- wciśnij `d`, aby zobaczyć dodatkowe metryki i komunikat błędu
- otwórz konsolę przeglądarki `F12`, jeśli problem nadal występuje

## Parametry wydajności

Najważniejsze ustawienia są w obiekcie `config` w pliku `index.html`:

- `frameSkip`
- `cooldownMs`
- `historyWindowMs`
- `minDeltaXRatio`
- `maxDeltaYRatio`
- `readyHoldMs`
- `openPalmMinExtendedFingers`
- `minPalmWidthRatio`

## Ograniczenia

- To steruje prezentacją webową Reveal.js na tej samej stronie.
- Nie emuluje globalnego klawisza spacji dla innych aplikacji systemowych.
- MediaPipe działa na głównym wątku; dla jeszcze niższego wpływu na UI można przenieść analizę do Web Workera.
