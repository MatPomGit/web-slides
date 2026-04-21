# Reveal.js + MediaPipe gesture control

Projekt prezentacji Reveal.js sterowanej gestami dłoni z użyciem MediaPipe Hand Landmarker.
Wersja w tym katalogu jest przygotowana do publikacji na GitHub Pages.

## Co zawiera
- `index.html` — aplikacja Reveal.js + sterowanie gestami
- `slides.md` — prezentacja ładowana z Markdown
- `favicon.svg` — favicon
- `.nojekyll` — wyłącza Jekyll na GitHub Pages
- `.github/workflows/deploy-pages.yml` — automatyczne wdrażanie na GitHub Pages

## Jak opublikować na GitHub Pages
1. Utwórz repozytorium na GitHub.
2. Wgraj całą zawartość tego katalogu do gałęzi `main`.
3. W ustawieniach repozytorium otwórz **Pages** i ustaw źródło na **GitHub Actions**.
4. Wypchnij zmiany. Workflow opublikuje stronę automatycznie.
5. Po wdrożeniu otwórz adres w stylu:
   `https://NAZWA_UZYTKOWNIKA.github.io/NAZWA_REPOZYTORIUM/`

## Kamera i uprawnienia
GitHub Pages działa po HTTPS, więc `getUserMedia()` może działać poprawnie po przyznaniu uprawnień do kamery.
Przy pierwszym uruchomieniu kliknij przycisk startu i zaakceptuj dostęp do kamery w przeglądarce.

## Sterowanie
- machnięcie w prawo — następny slajd
- machnięcie w lewo — poprzedni slajd
- `d` — panel debug/config
- `f` — fullscreen

## Uwagi
- Strona jest statyczna i nie wymaga backendu.
- Plik `slides.md` możesz dowolnie edytować bez zmian w kodzie aplikacji.
- Lokalne pliki `.bat` i `.sh` nie są potrzebne na GitHub Pages, ale mogą być używane lokalnie.


## Animacje i przejścia
Rozbudowano `slides.md` o per-slajdowe `data-transition`, gradientowe tła oraz fragmenty Reveal.js (`fragment`, `fade-*`, `highlight-*`, `current-visible`, `r-stack`, `r-hstack`).
