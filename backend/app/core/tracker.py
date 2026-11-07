"""
High-Speed ByteTrack-style Multi-Object Association & Virtual Tripwire Tracking.
Ensures zero double-counting on industrial conveyor belts.
Combines IoU matching with Centroid Distance association for high-speed tracking.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from ..schemas.waste_event import MaterialCategory, WasteDetectionEvent


def calculate_iou(boxA: List[float], boxB: List[float]) -> float:
    """Computes Intersection over Union (IoU) between two bounding boxes [x1, y1, x2, y2]."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0.0, xB - xA) * max(0.0, yB - yA)
    boxAArea = max(0.0, boxA[2] - boxA[0]) * max(0.0, boxA[3] - boxA[1])
    boxBArea = max(0.0, boxB[2] - boxB[0]) * max(0.0, boxB[3] - boxB[1])

    denom = boxAArea + boxBArea - interArea
    if denom <= 0:
        return 0.0
    return interArea / denom


def calculate_distance(ptA: Tuple[float, float], ptB: Tuple[float, float]) -> float:
    """Computes Euclidean distance between two 2D points."""
    return math.sqrt((ptA[0] - ptB[0]) ** 2 + (ptA[1] - ptB[1]) ** 2)


@dataclass
class TrackedItem:
    track_id: int
    material: MaterialCategory
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    centroid: Tuple[float, float]
    history: List[Tuple[float, float]] = field(default_factory=list)
    missed_frames: int = 0
    counted: bool = False
    estimated_mass_grams: float = 30.0

    def update(
        self, bbox: List[float], confidence: float, mass_grams: Optional[float] = None
    ):
        self.bbox = bbox
        self.confidence = confidence
        cx = (bbox[0] + bbox[2]) / 2.0
        cy = (bbox[1] + bbox[3]) / 2.0
        self.centroid = (cx, cy)
        self.history.append((cx, cy))
        if len(self.history) > 30:
            self.history.pop(0)
        self.missed_frames = 0
        if mass_grams is not None:
            self.estimated_mass_grams = mass_grams


class ConveyorTripwireTracker:
    """
    Multi-object tracker with a virtual tripwire boundary.
    Objects crossing the boundary trigger exactly one WasteDetectionEvent.
    """

    def __init__(
        self,
        tripwire_y: float = 240.0,
        iou_threshold: float = 0.20,
        max_distance: float = 120.0,
        max_missed_frames: int = 15,
        tripwire_direction: str = "top_to_bottom",  # or "bottom_to_top"
    ):
        self.tripwire_y = tripwire_y
        self.iou_threshold = iou_threshold
        self.max_distance = max_distance
        self.max_missed_frames = max_missed_frames
        self.tripwire_direction = tripwire_direction
        self.tracks: Dict[int, TrackedItem] = {}
        self._next_id: int = 1

    def update(
        self,
        detections: List[
            Dict
        ],  # List of {"bbox": [x1, y1, x2, y2], "material": MaterialCategory, "confidence": float, "mass_grams": float}
    ) -> Tuple[List[TrackedItem], List[WasteDetectionEvent]]:
        """
        Updates tracks with current frame detections.
        Returns:
            active_tracks: List of current active TrackedItem instances
            crossing_events: List of WasteDetectionEvent triggered on tripwire crossing
        """
        crossing_events: List[WasteDetectionEvent] = []

        # Age existing tracks
        for track in self.tracks.values():
            track.missed_frames += 1

        unmatched_detections = list(range(len(detections)))
        matched_track_ids = set()

        if self.tracks and detections:
            track_ids = list(self.tracks.keys())

            # Stage 1: Primary IoU Matching
            iou_matrix = []
            for tid in track_ids:
                row = [
                    calculate_iou(self.tracks[tid].bbox, det["bbox"])
                    for det in detections
                ]
                iou_matrix.append(row)

            while True:
                max_iou = 0.0
                best_pair = None
                for t_idx, row in enumerate(iou_matrix):
                    if track_ids[t_idx] in matched_track_ids:
                        continue
                    for d_idx, iou in enumerate(row):
                        if d_idx not in unmatched_detections:
                            continue
                        if iou > max_iou:
                            max_iou = iou
                            best_pair = (t_idx, d_idx)

                if best_pair is None or max_iou < self.iou_threshold:
                    break

                t_idx, d_idx = best_pair
                tid = track_ids[t_idx]
                matched_track_ids.add(tid)
                unmatched_detections.remove(d_idx)
                self._apply_match(tid, detections[d_idx], crossing_events)

            # Stage 2: Secondary Centroid Distance Matching (Handles fast-moving objects)
            unmatched_tracks = [
                tid for tid in track_ids if tid not in matched_track_ids
            ]
            if unmatched_tracks and unmatched_detections:
                dist_pairs = []
                for tid in unmatched_tracks:
                    track_centroid = self.tracks[tid].centroid
                    for d_idx in unmatched_detections:
                        det = detections[d_idx]
                        det_centroid = (
                            (det["bbox"][0] + det["bbox"][2]) / 2.0,
                            (det["bbox"][1] + det["bbox"][3]) / 2.0,
                        )
                        dist = calculate_distance(track_centroid, det_centroid)
                        # Ensure category matches and within max distance
                        if (
                            dist <= self.max_distance
                            and self.tracks[tid].material == det["material"]
                        ):
                            dist_pairs.append((dist, tid, d_idx))

                dist_pairs.sort(key=lambda x: x[0])
                for dist, tid, d_idx in dist_pairs:
                    if tid in matched_track_ids or d_idx not in unmatched_detections:
                        continue
                    matched_track_ids.add(tid)
                    unmatched_detections.remove(d_idx)
                    self._apply_match(tid, detections[d_idx], crossing_events)

        # Create new tracks for remaining unmatched detections
        for d_idx in unmatched_detections:
            det = detections[d_idx]
            new_id = self._next_id
            self._next_id += 1
            cx = (det["bbox"][0] + det["bbox"][2]) / 2.0
            cy = (det["bbox"][1] + det["bbox"][3]) / 2.0

            new_track = TrackedItem(
                track_id=new_id,
                material=det["material"],
                confidence=det["confidence"],
                bbox=det["bbox"],
                centroid=(cx, cy),
                history=[(cx, cy)],
                estimated_mass_grams=det.get("mass_grams", 30.0),
                counted=False,
            )
            self.tracks[new_id] = new_track

        # Remove dead tracks (beyond max_missed_frames)
        dead_ids = [
            tid
            for tid, track in self.tracks.items()
            if track.missed_frames > self.max_missed_frames
        ]
        for tid in dead_ids:
            del self.tracks[tid]

        # Return only active (not missed in current frame) or recent tracks
        active_tracks = [t for t in self.tracks.values() if t.missed_frames == 0]
        return active_tracks, crossing_events

    def _apply_match(
        self, tid: int, det: Dict, crossing_events: List[WasteDetectionEvent]
    ):
        """Updates matched track and detects virtual tripwire crossing."""
        prev_y = self.tracks[tid].centroid[1]
        curr_y = (det["bbox"][1] + det["bbox"][3]) / 2.0

        self.tracks[tid].update(
            bbox=det["bbox"],
            confidence=det["confidence"],
            mass_grams=det.get("mass_grams"),
        )

        if not self.tracks[tid].counted:
            crossed = False
            if (
                self.tripwire_direction == "top_to_bottom"
                and prev_y < self.tripwire_y <= curr_y
            ):
                crossed = True
            elif (
                self.tripwire_direction == "bottom_to_top"
                and prev_y > self.tripwire_y >= curr_y
            ):
                crossed = True
            elif prev_y <= self.tripwire_y and curr_y >= self.tripwire_y:
                crossed = True

            if crossed:
                self.tracks[tid].counted = True
                crossing_events.append(
                    WasteDetectionEvent(
                        track_id=tid,
                        material=self.tracks[tid].material,
                        confidence=self.tracks[tid].confidence,
                        bounding_box=self.tracks[tid].bbox,
                        estimated_mass_grams=self.tracks[tid].estimated_mass_grams,
                        is_sorted=True,
                    )
                )

    def reset(self):
        """Resets tracker state."""
        self.tracks.clear()
        self._next_id = 1
