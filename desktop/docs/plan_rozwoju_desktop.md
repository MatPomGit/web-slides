# Plan rozwoju wersji desktop

## Cel
Rozwinąć obecną aplikację sterowania slajdami gestami w kierunku pełnoprawnego narzędzia desktopowego z czytelnym interfejsem konfiguracji, diagnostyką i możliwością personalizacji.

## Etap 1: GUI konfiguracji (zrealizowane jako MVP)
- Formularz do edycji parametrów `gesture_config.yaml`.
- Szybkie akcje: **Wczytaj** / **Zapisz**.
- Sekcja „Planowana rozbudowa GUI” z nieaktywnymi przyciskami reprezentującymi kolejne moduły.

## Etap 2: Profile konfiguracji
- Wieloprofilowe ustawienia (np. „Prezentacja mała sala”, „Duża sala”, „Słabe oświetlenie”).
- Import/eksport profili do plików YAML.
- Szybkie przełączanie profilu z poziomu GUI.

## Etap 3: Kreator kalibracji gestów
- Interaktywny wizard prowadzący użytkownika przez kalibrację czułości.
- Automatyczny pomiar prędkości i zakresu ruchu dłoni na podstawie próbki.
- Proponowanie rekomendowanych progów detekcji.

## Etap 4: Podgląd kamery i ROI
- Wbudowany podgląd obrazu z kamery bezpośrednio w GUI.
- Graficzne ustawianie ROI metodą „przeciągnij i upuść”.
- Podgląd statusu detekcji gestu w czasie rzeczywistym.

## Etap 5: Makra i skróty klawiszowe
- Rozszerzenie mapowania gestów na dowolne klawisze lub sekwencje.
- Definiowanie akcji specjalnych (np. czarny ekran, timer, wskaźnik laserowy).
- Integracja presetów dla popularnych aplikacji prezentacyjnych.

## Etap 6: Diagnostyka i logi
- Przegląd logów uruchomień z poziomu GUI.
- Podstawowa analityka: liczba wykrytych gestów, odsetek fałszywych detekcji.
- Eksport pakietu diagnostycznego do zgłaszania problemów.

## Etap 7: Stabilizacja i dystrybucja
- Instalator desktopowy (Windows/macOS/Linux).
- Mechanizm aktualizacji aplikacji.
- Testy automatyczne GUI i regresji parametrów detekcji.
