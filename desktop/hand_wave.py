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
import signal
import time
from typing import Deque, List, Optional, Tuple

import cv2
import mediapipe as mp


def _import_first_available_module(module_names: Tuple[str, ...]):
    """Importuje pierwszy dostępny moduł z listy kandydatów."""
    for module_name in module_names:
        try:
            return importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
    return None


def resolve_mediapipe_hands():
    """Zwraca moduł MediaPipe Hands zgodny z różnymi wariantami instalacji."""
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

        y = 20
        for line in lines:
            cv2.putText(frame, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 1, cv2.LINE_AA)
            y += 22

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
                    continue

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
                            self.detector.mark_triggered(now)
                        elif direction == "left":
                            logging.info("Wykryto gest w lewo -> PREVIOUS")
                            self.keyboard.press_previous()
                            self.last_action = "previous"
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
            cap.release()
            cv2.destroyAllWindows()
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
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")

    args = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(asctime)s %(levelname)s %(message)s")

    # Walidacja ROI zapobiega konfiguracjom powodującym błędną detekcję.
    x1, y1, x2, y2 = args.roi
    if not (0.0 <= x1 < x2 <= 1.0 and 0.0 <= y1 < y2 <= 1.0):
        parser.error("ROI musi być w zakresie 0..1 i spełniać x1 < x2, y1 < y2")

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
    )


def main(argv: Optional[List[str]] = None) -> int:
    config = parse_args(argv)
    app = SlideWaveApp(config)
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
