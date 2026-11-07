"""
Conveyor Stream Orchestrator & Live MJPEG Stream Manager.
Integrates computer vision tracking with the EPA WARM v16 lifecycle engine.
"""

import asyncio
import time
from typing import List, Optional

from ..core.detector import SyntheticConveyorGenerator, WasteDetector
from ..core.tracker import ConveyorTripwireTracker
from ..schemas.metrics import ConveyorTelemetry
from ..schemas.waste_event import WasteDetectionEvent
from ..services.warm_calculator import EpawarmAccountingEngine


class ConveyorStreamManager:
    """Manages continuous conveyor processing, object tracking, and live video feeds."""

    def __init__(
        self, session_id: str = "conveyor-belt-primary", tripwire_y: float = 240.0
    ):
        self.session_id = session_id
        self.tripwire_y = tripwire_y
        self.tracker = ConveyorTripwireTracker(tripwire_y=tripwire_y)
        self.detector = WasteDetector(tripwire_y=tripwire_y)
        self.generator = SyntheticConveyorGenerator(width=640, height=480, speed=8.0)
        self.warm_engine = EpawarmAccountingEngine()

        self.recorded_events: List[WasteDetectionEvent] = []
        self.start_time: float = time.time()
        self.is_running: bool = True
        self._latest_jpeg: Optional[bytes] = None

    def reset(self):
        """Resets stream metrics and tracker."""
        self.tracker.reset()
        self.recorded_events.clear()
        self.start_time = time.time()

    def process_next_frame(self) -> bytes:
        """
        Advances one frame, performs tracking, updates EPA WARM accounting,
        and renders HUD annotations.
        """
        raw_img, detections = self.generator.step()

        # Update tracker
        active_tracks, crossing_events = self.tracker.update(detections)

        # Register crossing events into EPA WARM accounting
        if crossing_events:
            self.recorded_events.extend(crossing_events)

        # Compute current avoided GHG for HUD overlay
        elapsed = max(time.time() - self.start_time, 1.0)
        current_telemetry = self.warm_engine.compute_session_telemetry(
            session_id=self.session_id,
            events=self.recorded_events,
            elapsed_seconds=elapsed,
        )

        # Render HUD
        annotated_img = self.detector.draw_hud(
            image=raw_img,
            active_tracks=active_tracks,
            total_co2e=current_telemetry.total_avoided_co2e_kg,
            items_total=current_telemetry.items_total,
        )

        jpeg_bytes = self.detector.encode_jpeg(annotated_img, quality=80)
        self._latest_jpeg = jpeg_bytes
        return jpeg_bytes

    def get_current_telemetry(self) -> ConveyorTelemetry:
        """Retrieves real-time carbon, energy, and purity metrics."""
        elapsed = max(time.time() - self.start_time, 1.0)
        return self.warm_engine.compute_session_telemetry(
            session_id=self.session_id,
            events=self.recorded_events,
            elapsed_seconds=elapsed,
        )

    def get_latest_frame(self) -> bytes:
        """Returns the most recent annotated JPEG frame."""
        if self._latest_jpeg is None:
            return self.process_next_frame()
        return self._latest_jpeg

    async def generate_mjpeg_stream(self, fps: int = 24):
        """Yields continuous multipart MJPEG stream for live web video display."""
        delay = 1.0 / fps
        while self.is_running:
            frame_bytes = self.process_next_frame()
            yield (
                b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )
            await asyncio.sleep(delay)
