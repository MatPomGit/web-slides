<!-- .slide: data-transition="zoom" data-background-gradient="linear-gradient(135deg, #07111f, #0f2740 55%, #133b5c)" -->

# Poza Empatią z Korelacji

### Projektowanie architektur systemowych w inkluzywnej robotyce afektywnej
### Od laboratoryjnej precyzji do bezpieczeństwa w realnym świecie

<br>

dr inż. Mateusz Pomianek  
Katedra Informatyki i Automatyki, Politechnika Rzeszowska

<p class="fragment fade-in-then-semi-out">Prezentacja opracowana do Reveal.js z sekwencyjnym odsłanianiem treści.</p>

---

<!-- .slide: data-transition="slide" data-background-gradient="linear-gradient(135deg, #101820, #1f2d3d)" -->

# Iluzja wysokiej dokładności

## Luka między benchmarkiem a wdrożeniem

<div class="r-stack">
<div>

**Środowisko testowe**
- <span class="fragment fade-right">kontrolowane datasety i wąska pula uczestników</span>
- <span class="fragment fade-right">pozornie dobrze znane ekspresje</span>
- <span class="fragment fade-right">uproszczone warunki sensoryczne</span>
- <span class="fragment fade-right">metryki sukcesu: accuracy, F1, niska latencja</span>

</div>
<div class="fragment fade-in">

**Rzeczywistość wdrożeniowa**
- użytkownicy neuroróżnorodni i heterogeniczni
- zmienny kontekst, szum i dystrybucje tła
- stany afektywne mieszane z obciążeniem zadaniami
- kryteria zgodności, bezpieczeństwa psychologicznego i dobrostanu

</div>
</div>

<p class="fragment highlight-red">Wysoka skuteczność w laboratorium nie chroni przed kosztownymi błędami społecznymi w świecie rzeczywistym.</p>

---

<!-- .slide: data-transition="convex" data-background-gradient="linear-gradient(135deg, #141414, #243b55)" -->

# Anatomia błędu

## Architektura „empatii przez korelację”

1. <span class="fragment fade-up"><strong>Wejście multimodalne</strong> — sygnały wizualne i akustyczne</span>
2. <span class="fragment fade-up"><strong>Czarna skrzynka</strong> — model dopasowuje wzorce statystyczne</span>
3. <span class="fragment fade-up"><strong>Wymuszona interpretacja</strong> — etykieta nawet przy niepewności</span>
4. <span class="fragment fade-up"><strong>Decyzja</strong> — wykonanie skryptu zoptymalizowanego pod etykietę</span>

<br>

> <span class="fragment fade-in-then-semi-out">Asymetria epistemiczna: system dopasowuje znaki, ale nie rozumie pragmatyki sytuacji.</span>

---

<!-- .slide: data-transition="concave" data-background-gradient="linear-gradient(135deg, #1b1b1b, #2c5364)" -->

# Problem podwójnej empatii

<div class="r-hstack" style="gap: 2rem; align-items: flex-start;">

<div style="width:48%;">

### Fałszywe założenie
- <span class="fragment fade-right">użytkownik odstaje od „normy”</span>
- <span class="fragment fade-right">system ma go korygować</span>
- <span class="fragment fade-right">preferowany jest wzorzec neurotypowy</span>

</div>

<div style="width:48%;">

### Rzeczywisty problem
- <span class="fragment fade-left">różne systemy norm i komunikacji</span>
- <span class="fragment fade-left">robot może być nieczytelny</span>
- <span class="fragment fade-left">użytkownik może być błędnie interpretowany</span>

</div>

</div>

<p class="fragment highlight-current-blue">Niezrozumienie nie jest błędem tylko po stronie człowieka.</p>

---

<!-- .slide: data-transition="fade" data-background-gradient="linear-gradient(135deg, #151515, #4b6b8a)" -->

# Prawdziwy koszt błędu

## Dlaczego accuracy to zła metryka optymalizacji?

- <span class="fragment"><strong>False Positive</strong> — nieadekwatna interwencja, utrata godności</span>
- <span class="fragment"><strong>False Negative</strong> — brak wsparcia w kluczowym momencie</span>
- <span class="fragment"><strong>Uncertainty Failure</strong> — nadmierna pewność i spadek zaufania</span>

<br>

<p class="fragment fade-in"><strong>Wniosek:</strong> optymalizacja musi obejmować bezpieczeństwo, relację i dobrostan, nie tylko trafność etykiet.</p>

---

<!-- .slide: data-transition="zoom" data-background-gradient="linear-gradient(135deg, #0c1f2e, #16324f 60%, #274060)" -->

# Zmiana paradygmatu

## Od modelu deficytu do projektowania afirmującego neuroróżnorodność

<div class="r-stack">

<div class="fragment fade-out" data-fragment-index="0">

### Model deficytu
- cel: normalizacja i korekta
- logika: wymuszanie normatywnego sposobu ekspresji
- rola użytkownika: pasywny obiekt interwencji

</div>

<div class="fragment current-visible" data-fragment-index="0">

### Projektowanie afirmujące
- cel: adaptacja systemu do użytkownika i jego warunków
- logika: różnica komunikacyjna to legalna wariacja, nie błąd danych
- rola użytkownika: współtwórca i aktywny partner

</div>

</div>

<p class="fragment fade-in">Architektura musi być współkształtowana przez użytkownika, a nie tylko uczona na nim.</p>

---

<!-- .slide: data-transition="slide" data-background-gradient="linear-gradient(135deg, #102030, #203a43, #2c5364)" -->

# Architektura inkluzywnej robotyki afektywnej

1. <span class="fragment highlight-current-blue">Percepcja</span>
2. <span class="fragment highlight-current-blue">Personalizacja</span>
3. <span class="fragment highlight-current-blue">Decyzja</span>
4. <span class="fragment highlight-current-blue">Ekspresja</span>

<div class="fragment fade-in">
<br>

**Zasada**
Robot musi umieć bezpiecznie i przejrzyście komunikować, że czegoś nie wie.
</div>

---

<!-- .slide: data-transition="convex" data-background-gradient="linear-gradient(135deg, #0f2027, #203a43)" -->

# Warstwa 1

## Percepcja i estymacja świadoma niepewności

- <span class="fragment fade-up">kamera, mikrofon, inne sensory</span>
- <span class="fragment fade-up">reprezentacja stanów niejednoznacznych</span>
- <span class="fragment fade-up">agregacja multimodalna odporna na szum</span>
- <span class="fragment fade-up">modelowanie probabilistyczne zamiast sztywnej etykiety</span>

<p class="fragment fade-in-then-semi-out">Cel: śledzenie stanów ukrytych w czasie przy naturalnym pochłanianiu niepewności.</p>

---

<!-- .slide: data-transition="concave" data-background-gradient="linear-gradient(135deg, #121212, #355c7d)" -->

# Warstwa 2

## Polityka bezpieczeństwa — moc powstrzymania się

- <span class="fragment fade-right">progi pewności określające, kiedy system może działać</span>
- <span class="fragment fade-right">tryb abstynencji przy niskiej pewności</span>
- <span class="fragment fade-right">human-in-the-loop przy wysokiej stawce i niejednoznaczności</span>

<br>

<p class="fragment highlight-red">Brak reakcji bywa bezpieczniejszy niż arbitralna reakcja społeczna.</p>

---

<!-- .slide: data-transition="fade" data-background-gradient="linear-gradient(135deg, #16222a, #3a6073)" -->

# Warstwa 3

## Od korelacji do wnioskowania przyczynowego

<div class="r-hstack" style="gap: 2rem; align-items: flex-start;">
<div style="width:45%;">

### Układ korelacyjny
- <span class="fragment">obserwacja → etykieta stanu</span>

</div>
<div style="width:55%;">

### Układ przyczynowy
- <span class="fragment">obserwacja → hipotezy przyczyn</span>
- <span class="fragment">rozróżnianie źródeł podobnych sygnałów</span>

</div>
</div>

<div class="fragment fade-in">
<br>

**Przykład:** wycofanie może oznaczać przeciążenie hałasem, frustrację zadaniem albo zwykłe zmęczenie.
</div>

---

<!-- .slide: data-transition="zoom" data-background-gradient="linear-gradient(135deg, #1e130c, #355c7d)" -->

# Warstwa 4

## Cyfrowa persona i pętla afektywna

- <span class="fragment fade-up">przewidywalna komunikacja stanu maszyny</span>
- <span class="fragment fade-up">adaptacja: tempo, głośność, dystans, progi reakcji</span>
- <span class="fragment fade-up">czytelne affordancje społeczne dla użytkownika</span>

<p class="fragment fade-in">Przewidywalność redukuje szok sensoryczny i buduje zaufanie.</p>

---

<!-- .slide: data-transition="slide" data-background-gradient="linear-gradient(135deg, #232526, #414345)" -->

# Współprojektowanie

## Zmiana źródła wymagań architektonicznych

- <span class="fragment fade-right">użytkownik nie jest obiektem badania</span>
- <span class="fragment fade-right">staje się aktywnym współtwórcą systemu</span>
- <span class="fragment fade-right">co-design i scaffolding poznawczy wpływają na architekturę</span>

<p class="fragment highlight-current-green">Kryteria sukcesu powinny powstawać wspólnie z użytkownikami.</p>

---

<!-- .slide: data-transition="convex" data-background-gradient="linear-gradient(135deg, #0f2027, #2c5364)" -->

# Przykłady inkluzywnych architektur HRI

<div class="r-stack">

<div class="fragment current-visible">
### KASPAR
- minimalistyczny humanoid
- ograniczona ekspresja
- czytelne sygnały i user-driven design
</div>

<div class="fragment current-visible">
### (A)MICO
- system do przestrzeni pracy
- współprojektowany z pracownikami
- akustyczne zarządzanie przeciążeniem sensorycznym
</div>

<div class="fragment current-visible">
### JARI
- modułowy robot zoomorficzny
- komunikacja oparta na rytmie i presji
- ograniczona antropomorfizacja
</div>

<div class="fragment current-visible">
### EmoTrustBot
- adaptacja przez uczenie ze wzmocnieniem
- dopasowanie zachowań do konkretnego pacjenta
</div>

</div>

---

<!-- .slide: data-transition="concave" data-background-gradient="linear-gradient(135deg, #0b132b, #1c2541, #3a506b)" -->

# Wielowymiarowa ewaluacja

## Jak mierzyć sukces HRI?

- <span class="fragment fade-up"><strong>nie tylko</strong> accuracy i F1-score</span>
- <span class="fragment fade-up">bezpieczeństwo emocjonalne</span>
- <span class="fragment fade-up">jakość relacji i zaufania</span>
- <span class="fragment fade-up">zgodność z autonomią użytkownika</span>
- <span class="fragment fade-up">kalibracja niepewności</span>
- <span class="fragment fade-up">przewidywalność cyfrowej persony</span>

<p class="fragment highlight-red">Skuteczność robota nie może być oceniana wyłącznie wskaźnikami laboratoryjnymi.</p>

---

<!-- .slide: data-transition="zoom" data-background-gradient="linear-gradient(135deg, #0f0c29, #302b63, #24243e)" -->

# Inżynieria pokory epistemicznej

## Podsumowanie

1. <span class="fragment fade-right"><strong>Poza korelację</strong> — potrzebne jest wnioskowanie przyczynowe i kontekst</span>
2. <span class="fragment fade-right"><strong>Neuroróżnorodność jako fundament</strong> — różnica nie jest błędem danych</span>
3. <span class="fragment fade-right"><strong>Kalibracja niepewności</strong> — system powinien umieć komunikować, że nie wie</span>
4. <span class="fragment fade-right"><strong>Partycypacyjne projektowanie</strong> — wymagania współpowstają z użytkownikami</span>
5. <span class="fragment fade-right"><strong>Nowa funkcja celu</strong> — dobrostan i godność człowieka jako nadrzędna metryka sukcesu</span>

---

<!-- .slide: data-transition="fade" data-background-gradient="linear-gradient(135deg, #0f172a, #1e293b, #334155)" -->

# Dziękuję

### Pytania?

<p class="fragment fade-in">Dyskusja: jak projektować systemy, które wiedzą, kiedy nie wiedzą?</p>
