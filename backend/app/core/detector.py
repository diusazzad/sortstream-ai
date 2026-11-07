"""
Computer Vision Waste Detector and Conveyor Simulation Engine.
Detects industrial recyclable items and renders real-time HUD annotations.
"""

import io
import math
import random
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw

from ..schemas.waste_event import MaterialCategory
from .tracker import TrackedItem

# Standard Color Mapping per Material Class
MATERIAL_PALETTE = {
    MaterialCategory.ALUMINUM_CAN: (56, 189, 248),  # Sky Blue
    MaterialCategory.PET_PLASTIC: (52, 211, 153),  # Emerald
    MaterialCategory.HDPE_PLASTIC: (251, 191, 36),  # Amber
    MaterialCategory.CORRUGATED_CARDBOARD: (251, 146, 60),  # Orange
    MaterialCategory.E_WASTE: (248, 113, 113),  # Red
    MaterialCategory.UNKNOWN: (156, 163, 175),  # Gray
}


class SyntheticConveyorGenerator:
    """Generates synthetic conveyor frames with traversing recyclable waste items."""

    def __init__(self, width: int = 640, height: int = 480, speed: float = 8.0):
        self.width = width
        self.height = height
        self.speed = speed
        self.active_items: List[Dict] = []
        self.frame_count = 0
        self.belt_offset = 0.0

    def spawn_item(self):
        """Randomly spawns a recyclable item at top of the conveyor."""
        categories = [
            (MaterialCategory.ALUMINUM_CAN, 14.2, 50, 80),
            (MaterialCategory.PET_PLASTIC, 23.8, 60, 110),
            (MaterialCategory.HDPE_PLASTIC, 35.0, 75, 120),
            (MaterialCategory.CORRUGATED_CARDBOARD, 65.0, 100, 90),
            (MaterialCategory.E_WASTE, 80.0, 70, 70),
        ]
        cat, mass, w, h = random.choice(categories)
        x = random.uniform(80.0, self.width - 80.0 - w)
        y = -float(h) - random.uniform(10.0, 40.0)

        self.active_items.append(
            {
                "material": cat,
                "mass_grams": mass,
                "w": w,
                "h": h,
                "x": x,
                "y": y,
                "speed": self.speed + random.uniform(-1.0, 1.5),
                "confidence": round(random.uniform(0.88, 0.98), 2),
            }
        )

    def step(self) -> Tuple[Image.Image, List[Dict]]:
        """Advances conveyor simulation by one frame and returns raw frame and ground-truth detections."""
        self.frame_count += 1
        self.belt_offset = (self.belt_offset + self.speed) % 40.0

        # Spawn new items periodically
        if len(self.active_items) < 5 and (
            self.frame_count % 35 == 0 or not self.active_items
        ):
            self.spawn_item()

        # Update item positions
        surviving_items = []
        detections = []
        for item in self.active_items:
            item["y"] += item["speed"]
            x1 = item["x"]
            y1 = item["y"]
            x2 = x1 + item["w"]
            y2 = y1 + item["h"]

            # Keep items on screen or slightly above
            if y1 < self.height + 20:
                surviving_items.append(item)
                # Visible detections
                if y2 > 0 and y1 < self.height:
                    detections.append(
                        {
                            "bbox": [x1, max(0.0, y1), x2, min(float(self.height), y2)],
                            "material": item["material"],
                            "confidence": item["confidence"],
                            "mass_grams": item["mass_grams"],
                        }
                    )

        self.active_items = surviving_items

        # Render base conveyor image
        img = Image.new(
            "RGB", (self.width, self.height), color=(24, 24, 27)
        )  # Dark Slate industrial background
        draw = ImageDraw.Draw(img)

        # Draw conveyor belt surface (textured stripes)
        belt_x1, belt_x2 = 60, self.width - 60
        draw.rectangle([belt_x1, 0, belt_x2, self.height], fill=(39, 39, 42))

        # Belt rollers / slats
        for y_line in range(int(self.belt_offset) - 40, self.height + 40, 40):
            draw.line(
                [(belt_x1, y_line), (belt_x2, y_line)], fill=(55, 55, 60), width=2
            )

        # Draw waste items on the belt
        for item in self.active_items:
            ix1, iy1, ix2, iy2 = (
                item["x"],
                item["y"],
                item["x"] + item["w"],
                item["y"] + item["h"],
            )
            color = MATERIAL_PALETTE.get(item["material"], (150, 150, 150))
            darker_color = tuple(max(0, c - 40) for c in color)
            # Item shadow
            draw.rectangle([ix1 + 4, iy1 + 4, ix2 + 4, iy2 + 4], fill=(15, 15, 18))
            # Item body
            draw.rounded_rectangle(
                [ix1, iy1, ix2, iy2],
                radius=8,
                fill=darker_color,
                outline=color,
                width=2,
            )

        return img, detections


class WasteDetector:
    """Detection pipeline with overlay rendering for live stream feeds."""

    def __init__(self, tripwire_y: float = 240.0):
        self.tripwire_y = tripwire_y

    def draw_hud(
        self,
        image: Image.Image,
        active_tracks: List[TrackedItem],
        total_co2e: float = 0.0,
        items_total: int = 0,
    ) -> Image.Image:
        """Overlays bounding boxes, labels, tracking lines, and tripwire HUD on image."""
        hud_img = image.copy()
        draw = ImageDraw.Draw(hud_img)
        w, h = hud_img.size

        # 1. Draw glowing Tripwire Boundary Line
        trip_y = int(self.tripwire_y)
        draw.line(
            [(0, trip_y), (w, trip_y)], fill=(16, 185, 129), width=3
        )  # Glowing Green
        draw.text(
            (20, trip_y - 18),
            "▲ SORTSTREAM VIRTUAL TRIPWIRE (EPA WARM COUNTING ZONE)",
            fill=(52, 211, 153),
        )

        # 2. Draw Active Tracks & Bounding Boxes
        for track in active_tracks:
            x1, y1, x2, y2 = track.bbox
            color = MATERIAL_PALETTE.get(track.material, (200, 200, 200))

            # Bounding Box
            draw.rectangle([x1, y1, x2, y2], outline=color, width=3)

            # Header Badge
            label = f"ID #{track.track_id} | {track.material.value.upper()} ({int(track.confidence * 100)}%)"
            if track.counted:
                label += " [COUNTED]"
            badge_h = 16
            draw.rectangle(
                [x1, max(0, y1 - badge_h), x1 + len(label) * 7.5, max(badge_h, y1)],
                fill=color,
            )
            draw.text((x1 + 4, max(0, y1 - badge_h) + 2), label, fill=(10, 10, 10))

            # Center tracking dot
            cx, cy = track.centroid
            draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 255, 255))

        # 3. Industrial Telemetry Overlay at top
        banner_h = 32
        draw.rectangle([0, 0, w, banner_h], fill=(10, 10, 12))
        info_text = f"CONVEYOR 01 • ACTIVE ITEMS: {len(active_tracks)} • TOTAL COUNTED: {items_total} • AVOIDED GHG: {total_co2e:.4f} kg CO2e"
        draw.text((15, 8), info_text, fill=(228, 228, 231))

        return hud_img

    @staticmethod
    def encode_jpeg(image: Image.Image, quality: int = 80) -> bytes:
        """Encodes PIL Image to JPEG bytes."""
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=quality)
        return buf.getvalue()
