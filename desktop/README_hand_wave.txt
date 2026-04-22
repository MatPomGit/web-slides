Hand Wave Slide

Gesty:
- machnięcie w prawo -> następny slajd (SPACE)
- machnięcie w lewo  -> poprzedni slajd (LEFT)

Uruchomienie przez Condę:
    conda env create -f environment.yml
    conda activate hand-wave
    python hand_wave.py --debug

Alternatywnie przez pip:
    pip install -r requirements.txt

Uruchomienie w tle:
    conda activate hand-wave
    python hand_wave.py --headless

Dobre ustawienia startowe:
    python hand_wave.py --debug --roi 0.25 0.20 0.75 0.80

Jeśli wykrywa za dużo:
- zwiększ --wave-min-delta-x-px
- zwiększ --cooldown-sec
- zwiększ --min-extended-fingers

Jeśli wykrywa za rzadko:
- zmniejsz --wave-min-delta-x-px
- zmniejsz --min-horizontal-velocity-px-s
- ustaw --process-every-n-frames 1
