# Reveal.js + MediaPipe gesture control — Web Worker

Wersja projektu, w której detekcja dłoni MediaPipe działa w `gesture-worker.js`, a główny wątek odpowiada za Reveal.js, UI i sterowanie prezentacją.

## Co zmienia Web Worker
- odciąża główny wątek interfejsu
- zmniejsza ryzyko przycięć animacji Reveal.js
- pozwala utrzymać płynniejsze przejścia podczas pracy kamery i detekcji

## Bezpieczeństwo i prywatność
- ustawiony jest jawny `Content-Security-Policy` dopasowany do realnych źródeł (`self`, `cdn.jsdelivr.net`, `storage.googleapis.com`)
- krytyczne zasoby aplikacji (`app.js`, `app.css`) są self-hostowane w repozytorium
- UI zawiera czytelny komunikat, że obraz z kamery nie jest wysyłany poza urządzenie
- dostępna jest opcja całkowitego wyłączenia detekcji (z resetem lokalnej konfiguracji)

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

## Najczęstszy powód niedziałającego GitHub Pages
Jeżeli strona się nie publikuje, najpierw sprawdź **zakładkę Actions** i workflow `Deploy static site to GitHub Pages`.
Najczęstsza przyczyna w tym repo to push na gałąź inną niż `main`/`master` (workflow uruchamia się tylko dla tych gałęzi).

Szybka checklista:
1. W `Settings -> Pages` ustaw `Source: GitHub Actions`.
2. Upewnij się, że domyślna gałąź repo to `main` albo `master`.
3. Sprawdź, czy ostatni commit zmieniał coś w `web/` (albo sam workflow), bo tylko wtedy automatyczny deploy wystartuje.
4. Otwórz log workflow i zweryfikuj krok `Upload artifact` (powinien publikować katalog `web`).
