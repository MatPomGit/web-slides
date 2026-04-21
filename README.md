# Reveal.js + MediaPipe gesture control — Web Worker

Wersja projektu, w której detekcja dłoni MediaPipe działa w `gesture-worker.js`, a główny wątek odpowiada za Reveal.js, UI i sterowanie prezentacją.

## Co zmienia Web Worker
- odciąża główny wątek interfejsu
- zmniejsza ryzyko przycięć animacji Reveal.js
- pozwala utrzymać płynniejsze przejścia podczas pracy kamery i detekcji

## Pliki
- `index.html` — aplikacja Reveal.js
- `slides.md` — prezentacja ładowana z Markdown
- `gesture-worker.js` — worker z MediaPipe Hand Landmarker
- `favicon.svg` — favicon
- `.nojekyll` — zgodność z GitHub Pages
- `.github/workflows/deploy-pages.yml` — automatyczne wdrażanie na GitHub Pages

## Jak działa
1. Główny wątek pobiera obraz z kamery.
2. Każda wybrana klatka jest zamieniana na `ImageBitmap`.
3. `ImageBitmap` trafia do workera.
4. Worker wykonuje detekcję landmarków dłoni i logikę gestów.
5. Worker odsyła wynik i akcję `next` / `prev`.
6. Główny wątek steruje Reveal.js.

## Sterowanie
- machnięcie w prawo — następny slajd
- machnięcie w lewo — poprzedni slajd
- `d` — panel debug/config
- `f` — fullscreen

## GitHub Pages
Projekt jest przygotowany do publikacji jako statyczna strona na GitHub Pages.
