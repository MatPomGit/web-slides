#!/usr/bin/env python3
"""
Hand-wave slide controller.

Wykrywa machnięcie dłonią przed kamerą i wysyła klawisze sterujące prezentacją:
- machnięcie w prawo -> SPACE (następny slajd)
- machnięcie w lewo  -> LEFT  (poprzedni slajd)
"""

from __future__ import annotations

import argparse
import collections
import dataclasses
import importlib
import logging
import os
import signal
import time
import warnings
from pathlib import Path
from typing import Deque, Dict, List, Optional, Tuple

import cv2
import yaml
from run_logger import configure_run_logging


def configure_third_party_runtime(quiet: bool, hide_protobuf_deprecation: bool) -> None:
    """Konfiguruje poziomy logów z bibliotek zewnętrznych, aby ograniczyć szum na STDERR."""
    if quiet:
        # TensorFlow Lite i MediaPipe emitują wiele logów native; poziom "2"
        # zostawia tylko ostrzeżenia i błędy.
        os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
        os.environ.setdefault("GLOG_minloglevel", "2")

        # Ograniczamy też logowanie po stronie Pythona.
        logging.getLogger("absl").setLevel(logging.ERROR)
        logging.getLogger("tensorflow").setLevel(logging.ERROR)
        logging.getLogger("mediapipe").setLevel(logging.ERROR)

    if hide_protobuf_deprecation:
        # Filtrujemy konkretne ostrzeżenie deprecacyjne z protobuf, które nie
        # wpływa na działanie aplikacji i zaszumia konsolę.
        warnings.filterwarnings(
            "ignore",
            message=r"SymbolDatabase\.GetPrototype\(\) is deprecated\..*",
            category=UserWarning,
        )


def _import_first_available_module(module_names: Tuple[str, ...]):
    """Importuje pierwszy dostępny moduł z listy kandydatów."""
    for module_name in module_names:
        try:
            return importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
    return None


def _import_mediapipe_top_level():
    """Importuje top-level `mediapipe` i mapuje najczęstsze błędy ABI na czytelny komunikat."""
    try:
        return importlib.import_module("mediapipe")
    except Exception as exc:
        # Przy mieszaniu binarek budowanych pod NumPy 1.x z NumPy 2.x
        # import MediaPipe potrafi kończyć się długim tracebackiem z matplotlib.
        # Podmieniamy go na krótką diagnozę z konkretną sugestią naprawy.
        message = str(exc)
        if "A module that was compiled using NumPy 1.x cannot be run in NumPy 2" in message:
            raise RuntimeError(
                "Wykryto konflikt ABI NumPy (moduły zbudowane dla NumPy 1.x uruchamiane z NumPy 2.x). "
                "Uruchom aplikację przez `./run_hand_wave_conda.sh --create-env -- --debug` "
                "albo przypnij `numpy<2` w aktualnym środowisku."
            ) from exc
        raise RuntimeError(
            "Nie udało się zaimportować `mediapipe`. "
            "Sprawdź zależności środowiska i uruchomienie przez launcher Conda."
        ) from exc


def resolve_mediapipe_hands():
    """Zwraca moduł MediaPipe Hands zgodny z różnymi wariantami instalacji."""
    mp = _import_mediapipe_top_level()
    # W pierwszej kolejności próbujemy klasycznej ścieżki API.
    solutions = getattr(mp, "solutions", None)
    if solutions is not None and hasattr(solutions, "hands"):
        return solutions.hands

    # Niektóre buildy udostępniają tylko pakiet `solutions` (bez bezpośredniego
    # importu podmodułu `hands`). Wtedy pobieramy atrybut z pakietu nadrzędnego.
    solutions_module = _import_first_available_module(
        (
            "mediapipe.python.solutions",
            "mediapipe.solutions",
        )
    )
    if solutions_module is not None and hasattr(solutions_module, "hands"):
        return solutions_module.hands

    # Fallback dla buildów, gdzie `solutions` nie jest wystawione na top-level.
    hands_module = _import_first_available_module(
        (
            "mediapipe.python.solutions.hands",
            "mediapipe.solutions.hands",
        )
    )
    if hands_module is None:
        # W nowszych wydaniach MediaPipe gałąź `solutions` bywa niewystawiona.
        # Aplikacja korzysta z legacy API (`mp.solutions.hands`), więc podajemy
        # użytkownikowi konkretną, sprawdzoną wersję pakietu.
        raise RuntimeError(
            "Nie znaleziono modułu MediaPipe Hands (`solutions.hands`). "
            "Ta aplikacja wymaga wariantu `mediapipe` z legacy API, np. "
            "`mediapipe==0.10.14`."
        )
    return hands_module


def resolve_mediapipe_drawing_utils_module():
    """Zwraca moduł `drawing_utils` zgodny z różnymi wariantami MediaPipe."""
    mp = _import_mediapipe_top_level()
    # Klasyczna ścieżka przez top-level `mediapipe.solutions`.
    solutions = getattr(mp, "solutions", None)
    if solutions is not None and hasattr(solutions, "drawing_utils"):
        return solutions.drawing_utils

    # Analogiczny fallback jak dla `hands`: najpierw próbujemy pakietu
    # nadrzędnego `solutions`, który może eksportować `drawing_utils`.
    solutions_module = _import_first_available_module(
        (
            "mediapipe.python.solutions",
            "mediapipe.solutions",
        )
    )
    if solutions_module is not None and hasattr(solutions_module, "drawing_utils"):
        return solutions_module.drawing_utils

    # Fallback dla buildów, które trzymają `drawing_utils` pod `mediapipe.python`.
    drawing_utils_module = _import_first_available_module(
        (
            "mediapipe.python.solutions.drawing_utils",
            "mediapipe.solutions.drawing_utils",
        )
    )
    if drawing_utils_module is None:
        raise RuntimeError(
            "Nie znaleziono modułu MediaPipe `drawing_utils`. "
            "Sprawdź instalację pakietu `mediapipe`."
        )
    return drawing_utils_module




def _load_yaml_config(config_path: str) -> Dict[str, float]:
    """Wczytuje konfigurację YAML i zwraca słownik z parametrami detekcji gestów."""
    # Ścieżkę relatywną interpretujemy względem katalogu `desktop`,
    # aby uruchomienie z innego CWD nadal używało poprawnego pliku.
    resolved_path = Path(config_path)
    if not resolved_path.is_absolute():
        resolved_path = Path(__file__).resolve().parent / resolved_path

    if not resolved_path.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku konfiguracji YAML: {resolved_path}")

    with resolved_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    gesture = data.get("gesture_detection", {})
    if not isinstance(gesture, dict):
        raise ValueError("Sekcja `gesture_detection` w YAML musi być mapą klucz-wartość.")

    return gesture


class KeyboardBackend:
    """Abstrakcja wysyłania klawiszy do sterowania slajdami."""
    def press_next(self) -> None:
        raise NotImplementedError

    def press_previous(self) -> None:
        raise NotImplementedError


class PyAutoGUIBackend(KeyboardBackend):
    """Backend oparty o bibliotekę pyautogui."""
    def __init__(self) -> None:
        import pyautogui
        pyautogui.FAILSAFE = False
        self._pyautogui = pyautogui

    def press_next(self) -> None:
        self._pyautogui.press("space")

    def press_previous(self) -> None:
        self._pyautogui.press("left")


class PynputBackend(KeyboardBackend):
    """Backend oparty o bibliotekę pynput."""
    def __init__(self) -> None:
        from pynput.keyboard import Controller, Key
        self._controller = Controller()
        self._space = Key.space
        self._left = Key.left

    def press_next(self) -> None:
        self._controller.press(self._space)
        self._controller.release(self._space)

    def press_previous(self) -> None:
        self._controller.press(self._left)
        self._controller.release(self._left)


@dataclasses.dataclass
class Config:
    camera_id: int = 0
    frame_width: int = 320
    frame_height: int = 240
    process_every_n_frames: int = 2

    max_num_hands: int = 1
    detection_confidence: float = 0.65
    tracking_confidence: float = 0.65
    model_complexity: int = 0

    roi: Tuple[float, float, float, float] = (0.20, 0.15, 0.80, 0.85)

    wave_window_sec: float = 0.45
    wave_min_delta_x_px: int = 90
    wave_max_delta_y_px: int = 110
    min_samples_in_window: int = 5
    cooldown_sec: float = 1.20

    arm_hold_sec: float = 0.12
    require_open_hand: bool = True
    min_extended_fingers: int = 3
    min_horizontal_velocity_px_s: float = 220.0

    backend: str = "pyautogui"
    debug: bool = False
    headless: bool = False
    mirror: bool = True
    exit_key: str = "esc"
    debug_action_flash_duration_sec: float = 3.0


@dataclasses.dataclass
class Sample:
    timestamp: float
    x: float
    y: float


@dataclasses.dataclass
class DetectionState:
    armed_since: Optional[float] = None
    last_trigger_time: float = 0.0


class WaveDetector:
    """Detektor machnięcia analizujący ruch dłoni w krótkim oknie czasowym."""
    def __init__(self, config: Config) -> None:
        self.cfg = config
        self.samples: Deque[Sample] = collections.deque()
        self.state = DetectionState()

    def reset_samples(self) -> None:
        self.samples.clear()

    def on_hand_lost(self) -> None:
        self.state.armed_since = None
        self.reset_samples()

    def add_sample(self, sample: Sample) -> None:
        self.samples.append(sample)
        while self.samples and (sample.timestamp - self.samples[0].timestamp) > self.cfg.wave_window_sec:
            self.samples.popleft()

    def _is_in_cooldown(self, now: float) -> bool:
        return (now - self.state.last_trigger_time) < self.cfg.cooldown_sec

    def update_arming(self, now: float, hand_is_ready: bool) -> bool:
        if not hand_is_ready:
            self.state.armed_since = None
            return False
        if self.state.armed_since is None:
            self.state.armed_since = now
            return False
        return (now - self.state.armed_since) >= self.cfg.arm_hold_sec

    def classify_wave(self, now: float) -> Optional[str]:
        if self._is_in_cooldown(now):
            return None
        if len(self.samples) < self.cfg.min_samples_in_window:
            return None

        xs = [s.x for s in self.samples]
        ys = [s.y for s in self.samples]
        ts = [s.timestamp for s in self.samples]

        delta_x = max(xs) - min(xs)
        delta_y = max(ys) - min(ys)
        duration = max(ts) - min(ts)
        if duration <= 0:
            return None

        velocity = delta_x / duration
        if delta_x < self.cfg.wave_min_delta_x_px:
            return None
        if delta_y > self.cfg.wave_max_delta_y_px:
            return None
        if velocity < self.cfg.min_horizontal_velocity_px_s:
            return None

        net_dx = xs[-1] - xs[0]
        if abs(net_dx) < self.cfg.wave_min_delta_x_px * 0.45:
            return None

        return "right" if net_dx > 0 else "left"

    def mark_triggered(self, now: float) -> None:
        self.state.last_trigger_time = now
        self.state.armed_since = None
        self.reset_samples()


class HandTracker:
    """Warstwa odpowiedzialna za wykrywanie dłoni i wyznaczanie cech ruchu."""
    def __init__(self, config: Config) -> None:
        self.cfg = config
        # Rozwiązujemy moduł Hands w sposób odporny na różnice między wydaniami MediaPipe.
        self.mp_hands = resolve_mediapipe_hands()
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=self.cfg.max_num_hands,
            model_complexity=self.cfg.model_complexity,
            min_detection_confidence=self.cfg.detection_confidence,
            min_tracking_confidence=self.cfg.tracking_confidence,
        )

    def process(self, frame_bgr):
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        return self.hands.process(rgb)

    def close(self) -> None:
        """Zamyka zasoby MediaPipe, aby proces nie trzymał urządzeń po wyjściu."""
        # MediaPipe Hands udostępnia metodę `close`, która zwalnia zasoby
        # natywne oraz wątki uruchomione przez runtime.
        close_fn = getattr(self.hands, "close", None)
        if callable(close_fn):
            close_fn()

    @staticmethod
    def palm_center_px(hand_landmarks, width: int, height: int) -> Tuple[float, float]:
        ids = [0, 5, 9, 13, 17]
        xs = [hand_landmarks.landmark[i].x * width for i in ids]
        ys = [hand_landmarks.landmark[i].y * height for i in ids]
        return sum(xs) / len(xs), sum(ys) / len(ys)

    @staticmethod
    def count_extended_fingers(hand_landmarks) -> int:
        landmarks = hand_landmarks.landmark
        tip_pip_pairs = [(8, 6), (12, 10), (16, 14), (20, 18)]
        count = sum(1 for tip, pip in tip_pip_pairs if landmarks[tip].y < landmarks[pip].y)
        thumb_extended = abs(landmarks[4].x - landmarks[3].x) > 0.03
        if thumb_extended:
            count += 1
        return count


class SlideWaveApp:
    """Główna pętla aplikacji desktopowej."""
    def __init__(self, config: Config) -> None:
        self.cfg = config
        self.detector = WaveDetector(config)
        self.tracker = HandTracker(config)
        # Rysowanie landmarków może być dostępne inną ścieżką niż `mp.solutions`.
        self.mp_drawing_utils = self._resolve_drawing_utils()
        self.keyboard = self._make_keyboard_backend(config.backend)
        self.running = True
        self.frame_index = 0
        self.last_action = "none"
        self.frames_read = 0
        self.frames_dropped = 0
        self.hand_detections = 0
        self.gestures_next = 0
        self.gestures_previous = 0
        self.debug_action_flash_until = 0.0
        self.debug_action_color = (0, 255, 0)

    @staticmethod
    def _resolve_drawing_utils():
        """Zwraca narzędzia do rysowania MediaPipe kompatybilne z bieżącą instalacją."""
        return resolve_mediapipe_drawing_utils_module()

    @staticmethod
    def _make_keyboard_backend(name: str) -> KeyboardBackend:
        if name == "pyautogui":
            return PyAutoGUIBackend()
        if name == "pynput":
            return PynputBackend()
        raise ValueError(f"Unsupported backend: {name}")

    def _roi_pixels(self, width: int, height: int) -> Tuple[int, int, int, int]:
        x1, y1, x2, y2 = self.cfg.roi
        return int(x1 * width), int(y1 * height), int(x2 * width), int(y2 * height)

    def _point_in_roi(self, x: float, y: float, width: int, height: int) -> bool:
        x1, y1, x2, y2 = self._roi_pixels(width, height)
        return x1 <= x <= x2 and y1 <= y <= y2


    def _mark_debug_action(self, direction: str, now: float) -> None:
        """Ustawia kolor komunikatów debugowych po wykryciu gestu na ograniczony czas."""
        self.debug_action_flash_until = now + self.cfg.debug_action_flash_duration_sec
        if direction == "right":
            # OpenCV używa przestrzeni BGR, więc niebieski to (255, 0, 0).
            self.debug_action_color = (255, 0, 0)
        else:
            # Czerwony w przestrzeni BGR to (0, 0, 255).
            self.debug_action_color = (0, 0, 255)

    def _debug_text_color(self, now: float) -> Tuple[int, int, int]:
        """Zwraca kolor tekstu debugowego zależnie od aktywnej animacji po geście."""
        if now <= self.debug_action_flash_until:
            return self.debug_action_color
        return (0, 255, 0)

    def _draw_debug(self, frame, hand_landmarks, cx: Optional[float], cy: Optional[float], ready: bool) -> None:
        h, w = frame.shape[:2]
        x1, y1, x2, y2 = self._roi_pixels(w, h)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (80, 200, 80), 2)

        if hand_landmarks is not None:
            self.mp_drawing_utils.draw_landmarks(
                frame, hand_landmarks, self.tracker.mp_hands.HAND_CONNECTIONS
            )

        if cx is not None and cy is not None:
            cv2.circle(frame, (int(cx), int(cy)), 6, (0, 255, 255), -1)

        status = "ARMED" if ready else "WAIT"
        cooldown_left = max(0.0, self.cfg.cooldown_sec - (time.time() - self.detector.state.last_trigger_time))
        lines = [
            f"Status: {status}",
            f"Cooldown: {cooldown_left:.2f}s",
            f"Samples: {len(self.detector.samples)}",
            f"Last action: {self.last_action}",
            f"Press {self.cfg.exit_key.upper()} to quit",
        ]
        lines.extend(self._build_detection_params_lines())

        y = 20
        text_color = self._debug_text_color(time.time())
        for line in lines:
            cv2.putText(frame, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, text_color, 1, cv2.LINE_AA)
            y += 22

    def _build_detection_params_lines(self) -> List[str]:
        """Buduje listę linii z aktywnymi parametrami detekcji do wyświetlenia w podglądzie."""
        # Grupujemy parametry tematycznie, żeby użytkownik mógł szybciej diagnozować
        # problematyczną konfigurację bez zaglądania do argumentów startowych.
        roi_x1, roi_y1, roi_x2, roi_y2 = self.cfg.roi
        return [
            "Detection params:",
            (
                "  conf(det/track)="
                f"{self.cfg.detection_confidence:.2f}/{self.cfg.tracking_confidence:.2f}, "
                f"model={self.cfg.model_complexity}, hands={self.cfg.max_num_hands}"
            ),
            (
                "  wave(win/dx/dy/vel)="
                f"{self.cfg.wave_window_sec:.2f}s/{self.cfg.wave_min_delta_x_px}px/"
                f"{self.cfg.wave_max_delta_y_px}px/{self.cfg.min_horizontal_velocity_px_s:.1f}px/s"
            ),
            (
                "  arm(hold/open/fingers/samples)="
                f"{self.cfg.arm_hold_sec:.2f}s/{self.cfg.require_open_hand}/"
                f"{self.cfg.min_extended_fingers}/{self.cfg.min_samples_in_window}"
            ),
            (
                "  roi="
                f"({roi_x1:.2f}, {roi_y1:.2f}, {roi_x2:.2f}, {roi_y2:.2f}), "
                f"cooldown={self.cfg.cooldown_sec:.2f}s"
            ),
        ]

    def stop(self, *_args) -> None:
        self.running = False

    def run(self) -> int:
        cap = cv2.VideoCapture(self.cfg.camera_id)
        if not cap.isOpened():
            logging.error("Nie udało się otworzyć kamery: %s", self.cfg.camera_id)
            return 2

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cfg.frame_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cfg.frame_height)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        signal.signal(signal.SIGINT, self.stop)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, self.stop)

        logging.info(
            "Start. Kamera=%s, rozdzielczość=%sx%s, backend=%s",
            self.cfg.camera_id, self.cfg.frame_width, self.cfg.frame_height, self.cfg.backend
        )

        try:
            while self.running:
                ok, frame = cap.read()
                if not ok:
                    logging.warning("Pominięto klatkę: błąd odczytu z kamery")
                    self.frames_dropped += 1
                    continue
                self.frames_read += 1

                if self.cfg.mirror:
                    frame = cv2.flip(frame, 1)

                self.frame_index += 1
                if self.frame_index % self.cfg.process_every_n_frames != 0:
                    if self.cfg.debug and not self.cfg.headless:
                        cv2.imshow("Hand Wave Slide Controller", frame)
                        if self._check_exit_key():
                            break
                    continue

                # Analiza dłoni odbywa się tylko na wybranych klatkach dla niższego opóźnienia.
                h, w = frame.shape[:2]
                result = self.tracker.process(frame)
                now = time.time()

                hand_landmarks = None
                cx = cy = None
                ready = False

                if result.multi_hand_landmarks:
                    self.hand_detections += 1
                    hand_landmarks = result.multi_hand_landmarks[0]
                    cx, cy = self.tracker.palm_center_px(hand_landmarks, w, h)

                    in_roi = self._point_in_roi(cx, cy, w, h)
                    extended_fingers = self.tracker.count_extended_fingers(hand_landmarks)
                    hand_is_open_enough = extended_fingers >= self.cfg.min_extended_fingers
                    hand_is_ready = in_roi and (hand_is_open_enough or not self.cfg.require_open_hand)

                    ready = self.detector.update_arming(now, hand_is_ready)
                    if ready:
                        self.detector.add_sample(Sample(timestamp=now, x=cx, y=cy))
                        direction = self.detector.classify_wave(now)
                        if direction == "right":
                            logging.info("Wykryto gest w prawo -> NEXT")
                            self.keyboard.press_next()
                            self.last_action = "next"
                            self.gestures_next += 1
                            self._mark_debug_action("right", now)
                            self.detector.mark_triggered(now)
                        elif direction == "left":
                            logging.info("Wykryto gest w lewo -> PREVIOUS")
                            self.keyboard.press_previous()
                            self.last_action = "previous"
                            self.gestures_previous += 1
                            self._mark_debug_action("left", now)
                            self.detector.mark_triggered(now)
                    else:
                        self.detector.reset_samples()
                else:
                    self.detector.on_hand_lost()

                if self.cfg.debug and not self.cfg.headless:
                    self._draw_debug(frame, hand_landmarks, cx, cy, ready)
                    cv2.imshow("Hand Wave Slide Controller", frame)
                    if self._check_exit_key():
                        break
                elif not self.cfg.headless:
                    if cv2.waitKey(1) & 0xFF == 27:
                        break

        finally:
            # Zawsze zwalniamy kamerę, nawet jeśli pętla zakończyła się wyjątkiem.
            cap.release()
            # Zwolnienie zasobów MediaPipe zapobiega pozostawieniu aktywnych
            # uchwytów/wątków, które mogły blokować ponowny start aplikacji.
            self.tracker.close()
            # W środowiskach headless `destroyAllWindows` może zgłaszać błąd.
            try:
                cv2.destroyAllWindows()
            except cv2.error:
                logging.debug("cv2.destroyAllWindows() pominięte (brak GUI).")
            logging.info(
                "Podsumowanie uruchomienia: frames_read=%s, frames_dropped=%s, hand_detections=%s, gestures_next=%s, gestures_previous=%s",
                self.frames_read,
                self.frames_dropped,
                self.hand_detections,
                self.gestures_next,
                self.gestures_previous,
            )
            logging.info("Zatrzymano program")

        return 0

    def _check_exit_key(self) -> bool:
        key = cv2.waitKey(1) & 0xFF
        if self.cfg.exit_key == "esc":
            return key == 27
        if len(self.cfg.exit_key) == 1:
            return key == ord(self.cfg.exit_key)
        return False


def parse_args(argv: Optional[List[str]] = None) -> Config:
    parser = argparse.ArgumentParser(description="Sterowanie slajdami machnięciem dłoni")
    parser.add_argument("--camera-id", type=int, default=0)
    parser.add_argument("--frame-width", type=int, default=320)
    parser.add_argument("--frame-height", type=int, default=240)
    parser.add_argument("--process-every-n-frames", type=int, default=2)

    parser.add_argument("--detection-confidence", type=float, default=0.65)
    parser.add_argument("--tracking-confidence", type=float, default=0.65)
    parser.add_argument("--model-complexity", type=int, choices=[0, 1], default=0)

    parser.add_argument("--wave-window-sec", type=float, default=0.45)
    parser.add_argument("--wave-min-delta-x-px", type=int, default=90)
    parser.add_argument("--wave-max-delta-y-px", type=int, default=110)
    parser.add_argument("--min-samples-in-window", type=int, default=5)
    parser.add_argument("--min-horizontal-velocity-px-s", type=float, default=220.0)
    parser.add_argument("--cooldown-sec", type=float, default=1.2)

    parser.add_argument("--arm-hold-sec", type=float, default=0.12)
    parser.add_argument("--require-open-hand", action="store_true", default=True)
    parser.add_argument("--no-require-open-hand", action="store_false", dest="require_open_hand")
    parser.add_argument("--min-extended-fingers", type=int, default=3)

    parser.add_argument("--roi", type=float, nargs=4, metavar=("X1", "Y1", "X2", "Y2"),
                        default=(0.20, 0.15, 0.80, 0.85),
                        help="ROI jako proporcje kadru, np. 0.2 0.15 0.8 0.85")

    parser.add_argument("--backend", choices=["pyautogui", "pynput"], default="pyautogui")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--no-mirror", action="store_true")
    parser.add_argument("--exit-key", type=str, default="esc")
    parser.add_argument("--gesture-config", type=str, default="gesture_config.yaml")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")
    parser.add_argument("--log-dir", type=str, default="logs/hand_wave")
    parser.add_argument(
        "--quiet-third-party-logs",
        action="store_true",
        default=True,
        help="Wycisza logi bibliotek zewnętrznych (TensorFlow/MediaPipe/absl).",
    )
    parser.add_argument(
        "--no-quiet-third-party-logs",
        action="store_false",
        dest="quiet_third_party_logs",
        help="Nie wycisza logów bibliotek zewnętrznych.",
    )
    parser.add_argument(
        "--hide-protobuf-deprecation-warning",
        action="store_true",
        default=True,
        help="Ukrywa znane ostrzeżenie deprecacyjne protobuf.",
    )
    parser.add_argument(
        "--show-protobuf-deprecation-warning",
        action="store_false",
        dest="hide_protobuf_deprecation_warning",
        help="Pokazuje ostrzeżenie deprecacyjne protobuf.",
    )

    args = parser.parse_args(argv)
    configure_third_party_runtime(
        quiet=args.quiet_third_party_logs,
        hide_protobuf_deprecation=args.hide_protobuf_deprecation_warning,
    )
    run_log_path = configure_run_logging(log_level=args.log_level, log_dir=args.log_dir)
    logging.info("Konfiguracja logowania aktywna. Bieżący plik: %s", run_log_path)

    # Walidacja ROI zapobiega konfiguracjom powodującym błędną detekcję.
    x1, y1, x2, y2 = args.roi
    if not (0.0 <= x1 < x2 <= 1.0 and 0.0 <= y1 < y2 <= 1.0):
        parser.error("ROI musi być w zakresie 0..1 i spełniać x1 < x2, y1 < y2")

    yaml_config = _load_yaml_config(args.gesture_config)

    # Parametry z YAML traktujemy jako źródło domyślne dla czułości detekcji.
    # CLI nadal może je nadpisać, jeśli użytkownik poda jawnie flagi.
    args.wave_window_sec = yaml_config.get("wave_window_sec", args.wave_window_sec)
    args.wave_min_delta_x_px = yaml_config.get("wave_min_delta_x_px", args.wave_min_delta_x_px)
    args.wave_max_delta_y_px = yaml_config.get("wave_max_delta_y_px", args.wave_max_delta_y_px)
    args.min_samples_in_window = yaml_config.get("min_samples_in_window", args.min_samples_in_window)
    args.min_horizontal_velocity_px_s = yaml_config.get("min_horizontal_velocity_px_s", args.min_horizontal_velocity_px_s)
    args.cooldown_sec = yaml_config.get("cooldown_sec", args.cooldown_sec)
    args.arm_hold_sec = yaml_config.get("arm_hold_sec", args.arm_hold_sec)
    args.min_extended_fingers = yaml_config.get("min_extended_fingers", args.min_extended_fingers)
    args.detection_confidence = yaml_config.get("detection_confidence", args.detection_confidence)
    args.tracking_confidence = yaml_config.get("tracking_confidence", args.tracking_confidence)
    args.debug_action_flash_duration_sec = yaml_config.get("debug_action_flash_duration_sec", 3.0)

    return Config(
        camera_id=args.camera_id,
        frame_width=args.frame_width,
        frame_height=args.frame_height,
        process_every_n_frames=args.process_every_n_frames,
        detection_confidence=args.detection_confidence,
        tracking_confidence=args.tracking_confidence,
        model_complexity=args.model_complexity,
        roi=tuple(args.roi),
        wave_window_sec=args.wave_window_sec,
        wave_min_delta_x_px=args.wave_min_delta_x_px,
        wave_max_delta_y_px=args.wave_max_delta_y_px,
        min_samples_in_window=args.min_samples_in_window,
        cooldown_sec=args.cooldown_sec,
        arm_hold_sec=args.arm_hold_sec,
        require_open_hand=args.require_open_hand,
        min_extended_fingers=args.min_extended_fingers,
        min_horizontal_velocity_px_s=args.min_horizontal_velocity_px_s,
        backend=args.backend,
        debug=args.debug,
        headless=args.headless,
        mirror=not args.no_mirror,
        exit_key=args.exit_key.lower(),
        debug_action_flash_duration_sec=args.debug_action_flash_duration_sec,
    )


def main(argv: Optional[List[str]] = None) -> int:
    config = parse_args(argv)
    app = SlideWaveApp(config)
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
