# Poza Empatią z Korelacji

### Projektowanie architektur systemowych w inkluzywnej robotyce afektywnej
### Od laboratoryjnej precyzji do bezpieczeństwa w realnym świecie

dr inż. Mateusz Pomianek  
Katedra Informatyki i Automatyki, Politechnika Rzeszowska

---

# Iluzja wysokiej dokładności

## Luka między benchmarkiem a wdrożeniem

**Środowisko testowe**
- kontrolowane datasety i wąska pula uczestników
- pozornie dobrze znane ekspresje
- uproszczone warunki sensoryczne
- metryki sukcesu: accuracy, F1, niska latencja

**Rzeczywistość wdrożeniowa**
- użytkownicy neuroróżnorodni i heterogeniczni
- zmienny kontekst, szum i dystrybucje tła
- stany afektywne mieszane z obciążeniem zadaniami
- kryteria zgodności, bezpieczeństwa psychologicznego i dobrostanu

**Wniosek**
Wysoka skuteczność w laboratorium nie chroni przed kosztownymi błędami społecznymi w świecie rzeczywistym.

---

# Anatomia błędu

## Architektura „empatii przez korelację”

1. **Wejście multimodalne**
   - sygnały wizualne i akustyczne
2. **Czarna skrzynka**
   - model dopasowuje wzorce statystyczne
   - brak analizy przyczyn
3. **Wymuszona interpretacja**
   - system przypisuje etykietę nawet przy niepewności
4. **Decyzja**
   - automat wykonuje skrypt zoptymalizowany pod etykietę

**Asymetria epistemiczna**
System uczy się statystycznego dopasowania znaków, ale nie rozumie pragmatyki sytuacji.

---

# Problem podwójnej empatii

**Fałszywe założenie**
- użytkownik odstaje od „normy”
- system ma go korygować lub dopasowywać do wzorca neurotypowego

**Rzeczywisty problem**
- różne systemy norm, komunikacji i ekspresji
- robot może być nieczytelny dla użytkownika
- użytkownik może być błędnie interpretowany przez robota

**Teza**
Niezrozumienie nie jest błędem tylko po stronie człowieka.  
To zderzenie dwóch różnych logik afektywnych i komunikacyjnych.

---

# Prawdziwy koszt błędu

## Dlaczego accuracy to zła metryka optymalizacji?

**False Positive — fałszywy alarm**
- technicznie: błędna klasyfikacja stanu
- psychologicznie: nieadekwatna interwencja, utrata godności

**False Negative — przeoczenie**
- technicznie: brak detekcji stanu krytycznego
- psychologicznie: brak wsparcia w kluczowym momencie

**Uncertainty Failure — brak kalibracji niepewności**
- technicznie: system komunikuje się z nadmierną pewnością
- psychologicznie: spadek bezpieczeństwa relacji i zaufania

**Wniosek**
System trzeba optymalizować pod bezpieczeństwo, zaufanie i jakość relacji — nie tylko pod trafność etykiet.

---

# Zmiana paradygmatu

## Od modelu deficytu do projektowania afirmującego neuroróżnorodność

**Model deficytu**
- cel: normalizacja i korekta
- logika: wymuszanie normatywnego sposobu ekspresji
- rola użytkownika: pasywny obiekt interwencji

**Projektowanie afirmujące**
- cel: adaptacja systemu do użytkownika i jego warunków
- logika: różnica komunikacyjna to legalna wariacja, nie błąd danych
- rola użytkownika: współtwórca i aktywny partner

**Konsekwencja architektoniczna**
Trzeba projektować systemy współkształtowane przez użytkownika, a nie tylko uczone na nim.

---

# Architektura inkluzywnej robotyki afektywnej

1. **Percepcja**
   - integracja multimodalna
   - estymacja i kalibracja niepewności
2. **Personalizacja**
   - priory i parametry specyficzne dla użytkownika
   - uczenie online w pętli
3. **Decyzja**
   - modele przyczynowe
   - bezpieczne polityki działania
   - wstrzymanie decyzji przy niskiej pewności
4. **Ekspresja**
   - cyfrowa persona
   - czytelne affordancje społeczne: tempo, dystans, kanał

**Zasada**
Robot musi umieć bezpiecznie i przejrzyście komunikować, że czegoś nie wie.

---

# Warstwa 1

## Percepcja i estymacja świadoma niepewności

**Wejścia**
- kamera
- mikrofon
- inne sensory

**Mechanizmy**
- dynamiczna, niejednoznaczna reprezentacja stanów
- agregacja multimodalna z wagami redukującymi wpływ szumu
- modelowanie probabilistyczne zamiast sztywnej etykiety

**Cel**
Śledzenie stanów ukrytych w czasie przy naturalnym pochłanianiu niepewności.

---

# Warstwa 2

## Polityka bezpieczeństwa — moc powstrzymania się

**Mechanika decyzji**
- progi pewności określające, kiedy system może działać
- tryb abstynencji przy niskiej pewności
- human-in-the-loop przy wysokiej stawce i niejednoznaczności

**Kluczowa idea**
Brak reakcji bywa bezpieczniejszy niż arbitralna reakcja społeczna.

---

# Warstwa 3

## Od korelacji do wnioskowania przyczynowego

**Układ korelacyjny**
- obserwacja → etykieta stanu

**Układ przyczynowy**
- obserwacja → hipotezy przyczyn
- rozróżnienie możliwych źródeł podobnych sygnałów

**Przykład**
Objaw: wycofanie  
Możliwe przyczyny:
- przeciążenie hałasem
- frustracja zadaniem
- zwykłe zmęczenie

**Dlaczego to ważne**
Różne przyczyny wymagają radykalnie innych interwencji.

---

# Warstwa 4

## Cyfrowa persona i pętla afektywna

**Cyfrowa persona**
- nie symuluje fałszywej głębi psychologicznej
- przewidywalnie komunikuje stan maszyny

**Adaptacja w czasie rzeczywistym**
- tempo
- głośność
- dystans
- progi reakcji

**Affordancje społeczne**
- robot musi być czytelny dla użytkownika
- przewidywalność redukuje szok sensoryczny i buduje zaufanie

---

# Współprojektowanie

## Zmiana źródła wymagań architektonicznych

**Nowa rola użytkownika**
- użytkownik nie jest obiektem badania
- staje się aktywnym współtwórcą systemu

**Podejścia**
- co-design circle
- scaffolding poznawczy
- obserwacja realnych zachowań i potrzeb

**Wniosek**
Kryteria sukcesu robota powinny być definiowane wspólnie z użytkownikami już na etapie planowania architektury.

---

# Przykłady inkluzywnych architektur HRI

## KASPAR
- minimalistyczny humanoid
- ograniczona ekspresja ciała
- czytelne sygnały i user-driven design

## (A)MICO
- system do przestrzeni pracy
- współprojektowany z pracownikami
- wykorzystuje akustyczne kanały do zarządzania przeciążeniem sensorycznym

## JARI
- modułowy robot zoomorficzny
- ograniczona, nieantropocentryczna interpretacja
- kontakt oparty bardziej na komunikacji presji i rytmu niż „udawanej emocji”

## EmoTrustBot
- adaptacja przez uczenie ze wzmocnieniem
- dopasowanie zachowań do konkretnego pacjenta

---

# Wielowymiarowa ewaluacja

## Jak mierzyć sukces HRI?

Nie tylko:
- accuracy
- F1-score

Ale także:
- **bezpieczeństwo emocjonalne**
- **jakość relacji i zaufania**
- **zgodność z autonomią użytkownika**
- **kalibrację niepewności**
- **przewidywalność cyfrowej persony**

**Teza**
Skuteczność robota nie może być oceniana wyłącznie wskaźnikami detekcji laboratoryjnej.

---

# Inżynieria pokory epistemicznej

## Podsumowanie

1. **Poza korelację**
   - potrzebne jest wnioskowanie przyczynowe i rozumienie kontekstu
2. **Neuroróżnorodność jako fundament**
   - różnica nie jest błędem danych
3. **Kalibracja niepewności**
   - system powinien umieć komunikować, że nie wie
4. **Partycypacyjne projektowanie**
   - wymagania muszą współpowstawać z użytkownikami
5. **Nowa funkcja celu**
   - ochrona dobrostanu i godności człowieka jako nadrzędna metryka sukcesu

---

# Dziękuję

### Pytania?
