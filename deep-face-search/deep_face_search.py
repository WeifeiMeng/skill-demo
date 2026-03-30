#!/usr/bin/env python3
"""
Deep Face Search - v2.0
Implements: Trajectory-Guided Candidate Expansion

This script demonstrates the multi-round face search workflow that solves
the Top1 limitation through trajectory-guided expansion.

Key concepts:
- Top1 may be wrong (blurry image)
- Use trajectory to EXPAND candidates (not just verify)
- Through target camera's coverage area, find who else was there
- Multi-frame consistency increases confidence
"""

import argparse
import time
from dataclasses import dataclass, field
from typing import Optional, Set, List
from enum import Enum


# ============================================================================
# Mock API Implementations
# ============================================================================

class MockFaceDatabase:
    """Mock face database for demonstration."""

    PERSONS = {
        "E-8834": {
            "entity_id": "E-8834",
            "person_name": "Zhang Wei",
            "person_face_img": "https://db.example.com/faces/E-8834.jpg",
            "height": 175,
            "department": "Sales",
            "trajectory": [
                {"camera_id": "cam01", "timestamp": "2026-03-30T14:15:00", "camera_location": "Entrance", "entity_id": "E-8834"},
                {"camera_id": "cam05", "timestamp": "2026-03-30T14:18:00", "camera_location": "North corridor", "entity_id": "E-8834"},
                {"camera_id": "cam07", "timestamp": "2026-03-30T14:23:00", "camera_location": "East corridor", "entity_id": "E-8834"},
                {"camera_id": "cam09", "timestamp": "2026-03-30T14:31:00", "camera_location": "East wing exit", "entity_id": "E-8834"},
            ]
        },
        "E-2109": {
            "entity_id": "E-2109",
            "person_name": "Li Ming",
            "person_face_img": "https://db.example.com/faces/E-2109.jpg",
            "height": 178,
            "department": "Marketing",
            "trajectory": [
                {"camera_id": "cam12", "timestamp": "2026-03-30T13:42:00", "camera_location": "North corridor", "entity_id": "E-2109"},
                {"camera_id": "cam14", "timestamp": "2026-03-30T14:38:00", "camera_location": "Parking lot", "entity_id": "E-2109"},
            ]
        },
        "E-4451": {
            "entity_id": "E-4451",
            "person_name": "Wang Fang",
            "person_face_img": "https://db.example.com/faces/E-4451.jpg",
            "height": 172,
            "department": "HR",
            "trajectory": [
                {"camera_id": "cam07", "timestamp": "2026-03-30T13:27:00", "camera_location": "East corridor", "entity_id": "E-4451"},
            ]
        },
        "E-0193": {
            "entity_id": "E-0193",
            "person_name": "Chen Jie",
            "person_face_img": "https://db.example.com/faces/E-0193.jpg",
            "height": 168,
            "department": "Engineering",
            "trajectory": [
                {"camera_id": "cam03", "timestamp": "2026-03-30T12:08:00", "camera_location": "Lobby", "entity_id": "E-0193"},
            ]
        },
        "E-6627": {
            "entity_id": "E-6627",
            "person_name": "Liu Hong",
            "person_face_img": "https://db.example.com/faces/E-6627.jpg",
            "height": 185,
            "department": "Security",
            "trajectory": [
                {"camera_id": "cam11", "timestamp": "2026-03-30T11:42:00", "camera_location": "West corridor", "entity_id": "E-6627"},
            ]
        },
        "E-9901": {
            "entity_id": "E-9901",
            "person_name": "Zhao Gang",
            "person_face_img": "https://db.example.com/faces/E-9901.jpg",
            "height": 181,
            "department": "Engineering",
            "trajectory": [
                {"camera_id": "cam01", "timestamp": "2026-03-30T14:15:00", "camera_location": "Entrance", "entity_id": "E-9901"},
                {"camera_id": "cam05", "timestamp": "2026-03-30T14:18:00", "camera_location": "North corridor", "entity_id": "E-9901"},
                {"camera_id": "cam05", "timestamp": "2026-03-30T14:23:00", "camera_location": "North corridor", "entity_id": "E-9901"},
                {"camera_id": "cam07", "timestamp": "2026-03-30T14:28:00", "camera_location": "East corridor", "entity_id": "E-9901"},
                {"camera_id": "cam09", "timestamp": "2026-03-30T14:31:00", "camera_location": "East wing exit", "entity_id": "E-9901"},
            ]
        },
    }

    CAMERAS = {
        "cam01": {"camera_id": "cam01", "camera_name": "Entrance Camera", "location": "Entrance", "zone": "main_entrance"},
        "cam03": {"camera_id": "cam03", "camera_name": "Lobby Camera", "location": "Lobby", "zone": "main_lobby"},
        "cam05": {"camera_id": "cam05", "camera_name": "North Corridor", "location": "North corridor", "zone": "east_wing"},
        "cam07": {"camera_id": "cam07", "camera_name": "East Corridor", "location": "East corridor", "zone": "east_wing"},
        "cam08": {"camera_id": "cam08", "camera_name": "Junction Camera", "location": "Junction", "zone": "east_wing"},
        "cam09": {"camera_id": "cam09", "camera_name": "East Wing Exit", "location": "East wing exit", "zone": "east_wing"},
        "cam11": {"camera_id": "cam11", "camera_name": "West Corridor", "location": "West corridor", "zone": "west_wing"},
        "cam12": {"camera_id": "cam12", "camera_name": "North Camera", "location": "North corridor", "zone": "north_area"},
        "cam14": {"camera_id": "cam14", "camera_name": "Parking Lot", "location": "Parking lot", "zone": "parking"},
    }

    @classmethod
    def search_face(cls, image_url: str):
        """Mock search_person_face - returns Top1 only."""
        base_similarities = {
            "E-8834": 0.91,
            "E-2109": 0.87,
            "E-4451": 0.85,
            "E-0193": 0.79,
            "E-6627": 0.76,
            "E-9901": 0.73,
        }
        top1_id = max(base_similarities, key=base_similarities.get)
        person = cls.PERSONS[top1_id]
        return {
            "entity_id": top1_id,
            "person_name": person["person_name"],
            "person_face_img": person["person_face_img"],
            "similarity": base_similarities[top1_id],
        }

    @classmethod
    def get_trajectory(cls, entity_id: str, start_time: str = None, end_time: str = None,
                       camera_ids: List[str] = None):
        """Mock search_person_trajectory."""
        if entity_id not in cls.PERSONS:
            return {"error": {"code": "ENTITY_NOT_FOUND", "message": f"Entity {entity_id} not found"}}

        person = cls.PERSONS[entity_id]
        trajectory = person["trajectory"]

        filtered = []
        for point in trajectory:
            if camera_ids and point["camera_id"] not in camera_ids:
                continue
            filtered.append({
                "camera_id": point["camera_id"],
                "camera_location": point["camera_location"],
                "timestamp": point["timestamp"],
                "entity_id": point["entity_id"],
                "face_image_url": f"https://db.example.com/captures/{entity_id}/{point['camera_id']}.jpg",
                "confidence": 0.95,
            })

        return {
            "entity_id": entity_id,
            "person_name": person["person_name"],
            "trajectory": filtered,
            "total_frames": len(filtered),
            "first_seen": filtered[0]["timestamp"] if filtered else None,
            "last_seen": filtered[-1]["timestamp"] if filtered else None,
        }

    @classmethod
    def get_cameras_by_location(cls, location: str, radius: float = None):
        """Mock search_cameras_by_location."""
        matches = []
        location_lower = location.lower()
        for cam_id, cam in cls.CAMERAS.items():
            if (location_lower in cam_id.lower() or
                location_lower in cam["location"].lower() or
                location_lower in cam.get("zone", "").lower()):
                matches.append(cam)
        return {"cameras": matches}

    @classmethod
    def get_all_entities_in_camera(cls, camera_id: str, start_time: str = None, end_time: str = None):
        """Find all entities detected by a specific camera within time range.
        This is a NEW capability used to expand candidates via camera coverage."""
        results = []
        for entity_id, person in cls.PERSONS.items():
            traj = person["trajectory"]
            for point in traj:
                if point["camera_id"] == camera_id:
                    results.append({
                        "entity_id": entity_id,
                        "person_name": person["person_name"],
                        "timestamp": point["timestamp"],
                        "camera_id": camera_id,
                    })
        return {"detections": results}


# ============================================================================
# API Functions
# ============================================================================

def search_person_face(image_url: str) -> dict:
    """Returns Top1 only."""
    print(f"  [API] search_person_face('{image_url}')")
    print(f"         [WARN] Only returns Top1!")
    time.sleep(0.1)
    return {"person_face": MockFaceDatabase.search_face(image_url)}


def search_person_trajectory(entity_id: str, start_time: str = None, end_time: str = None,
                               camera_ids: List[str] = None) -> dict:
    """Query person's trajectory across cameras."""
    cams = camera_ids if camera_ids else []
    print(f"  [API] search_person_trajectory(entity_id='{entity_id}', camera_ids={cams})")
    time.sleep(0.1)
    return MockFaceDatabase.get_trajectory(entity_id, start_time, end_time, camera_ids)


def search_cameras_by_location(location: str, radius: float = None) -> dict:
    """Find cameras in a geographic area."""
    print(f"  [API] search_cameras_by_location(location='{location}')")
    time.sleep(0.05)
    return MockFaceDatabase.get_cameras_by_location(location, radius)


def get_all_entities_in_camera(camera_id: str, start_time: str = None, end_time: str = None) -> dict:
    """Find ALL entities detected by a camera (expansion capability)."""
    print(f"  [API] get_all_entities_in_camera(camera_id='{camera_id}')")
    time.sleep(0.1)
    return MockFaceDatabase.get_all_entities_in_camera(camera_id, start_time, end_time)


# ============================================================================
# Data Structures
# ============================================================================

class SearchAction(Enum):
    INITIAL_RETRIEVAL = "initial_retrieval"
    TOP1_TRAJECTORY_VERIFY = "top1_trajectory_verify"
    TRAJECTORY_EXPANSION = "trajectory_expansion"
    CAMERA_EXPANSION = "camera_expansion"
    CAMERA_TRAJECTORY_SEARCH = "camera_trajectory_search"
    USER_CONFIRMED = "user_confirmed"
    USER_REJECTED = "user_rejected"
    RERANK = "rerank"
    CONFIDENCE_THRESHOLD_MET = "confidence_threshold_met"


@dataclass
class TrajectoryInfo:
    total_frames: int
    first_seen: str
    last_seen: str
    cameras_visited: List[str]
    path: List[dict]
    in_target_area: bool = False
    near_target_time: bool = False


@dataclass
class Candidate:
    entity_id: str
    person_name: str
    person_face_img: str
    similarity: float
    found_via: str  # "face" | "trajectory" | "camera_expansion"
    trajectory: TrajectoryInfo = None
    traj_match_score: float = 0.0
    final_score: float = 0.0
    frame_count: int = 0
    multi_frame_consistent: bool = False

    def to_dict(self):
        return {
            "entity_id": self.entity_id,
            "person_name": self.person_name,
            "person_face_img": self.person_face_img,
            "similarity": self.similarity,
            "found_via": self.found_via,
            "traj_match_score": self.traj_match_score,
            "final_score": self.final_score,
            "frame_count": self.frame_count,
            "multi_frame_consistent": self.multi_frame_consistent,
            "in_target_area": self.trajectory.in_target_area if self.trajectory else False,
        }


@dataclass
class HistoryEntry:
    iteration: int
    action: SearchAction
    function_calls: List[str]
    candidates_found: int
    candidates_rejected: int
    reasoning: str


@dataclass
class SearchConfig:
    max_iterations: int = 10
    confidence_threshold: float = 0.95
    top1_reject_threshold: int = 3
    trajectory_window_minutes: int = 30
    min_frames_for_consistency: int = 3


@dataclass
class FaceSearchState:
    iteration: int = 0
    status: str = "searching"  # "searching" | "confirmed" | "exhausted" | "failed"
    candidate_pool: List[Candidate] = field(default_factory=list)
    rejected_ids: Set[str] = field(default_factory=set)
    confirmed_id: str = None
    top1_current: Candidate = None
    top1_rejected_count: int = 0
    top1_wrong_decisions: bool = False
    target_time: str = None
    target_camera: str = None
    target_area: str = None
    expanded_cameras: List[str] = field(default_factory=list)
    traj_verified_entities: Set[str] = field(default_factory=set)
    history: List[HistoryEntry] = field(default_factory=list)
    config: SearchConfig = field(default_factory=SearchConfig)


# ============================================================================
# Core Search Logic
# ============================================================================

class DeepFaceSearcher:
    """Main face search engine - v2.0 with trajectory-guided expansion."""

    def __init__(self, config: SearchConfig = None):
        self.config = config or SearchConfig()
        self.state: FaceSearchState = None

    def initial_retrieval(self, image_url: str, target_camera: str = None, target_time: str = None) -> FaceSearchState:
        """Round 1: Get Top1 and verify its trajectory."""
        print(f"\n{'='*70}")
        print("ROUND 1: Initial Retrieval")
        print(f"{'='*70}")
        print(f"Image: {image_url}")
        print(f"Target camera: {target_camera or 'N/A'}")
        print(f"Target time: {target_time or 'N/A'}")

        # Store context
        self.state = FaceSearchState(
            iteration=1,
            target_camera=target_camera,
            target_time=target_time,
            config=self.config,
        )

        # Step 1: Get Top1 (ONLY returns 1!)
        print("\n--- Step 1: search_person_face ---")
        response = search_person_face(image_url)
        top1_data = response["person_face"]

        self.state.top1_current = Candidate(
            entity_id=top1_data["entity_id"],
            person_name=top1_data["person_name"],
            person_face_img=top1_data["person_face_img"],
            similarity=top1_data["similarity"],
            found_via="face",
        )
        self.state.candidate_pool.append(self.state.top1_current)

        # Step 2: Verify Top1 trajectory
        print("\n--- Step 2: Verify Top1 trajectory ---")
        traj_response = search_person_trajectory(self.state.top1_current.entity_id)

        if "error" not in traj_response:
            self._process_trajectory(self.state.top1_current, traj_response)

        # Analyze
        self._rerank_candidates()

        print("\n" + "-"*50)
        print("TOP1 TRAJECTORY ANALYSIS:")
        print(f"  Entity: {self.state.top1_current.entity_id} ({self.state.top1_current.person_name})")
        if self.state.top1_current.trajectory:
            t = self.state.top1_current.trajectory
            print(f"  Path: {' -> '.join(t.cameras_visited)}")
            print(f"  Time: {t.first_seen[11:16]} ~ {t.last_seen[11:16]}")
            print(f"  In target area: {'[OK] YES' if t.in_target_area else '[NO] NO'}")
            print(f"  Near target time: {'[OK] YES' if t.near_target_time else '[NO] NO'}")
        print(f"  Face similarity: {self.state.top1_current.similarity:.2f}")
        print(f"  Final score: {self.state.top1_current.final_score:.2f}")

        # Record history
        self.state.history.append(HistoryEntry(
            iteration=1,
            action=SearchAction.INITIAL_RETRIEVAL,
            function_calls=["search_person_face", "search_person_trajectory"],
            candidates_found=1,
            candidates_rejected=0,
            reasoning=f"Top1={self.state.top1_current.entity_id}, traj_match={'Y' if self.state.top1_current.trajectory and self.state.top1_current.trajectory.in_target_area else 'N'}"
        ))

        return self.state

    def process_feedback(self, feedback_type: str, entity_ids: List[str] = None,
                         direction: str = None, attributes: str = None) -> FaceSearchState:
        """Process user feedback and determine next action."""
        self.state.iteration += 1
        iteration = self.state.iteration

        print(f"\n{'='*70}")
        print(f"ROUND {iteration}: Feedback Processing")
        print(f"{'='*70}")
        print(f"Feedback type: {feedback_type}")
        if entity_ids:
            print(f"Entity IDs: {entity_ids}")
        if direction:
            print(f"Direction: {direction}")

        # Handle confirmed
        if feedback_type == "confirmed":
            return self._handle_confirmed(entity_ids[0])

        # Handle rejection
        if feedback_type == "rejected":
            self._handle_rejected(entity_ids[0])

        # Handle expand
        if feedback_type == "expand":
            self._handle_expand(direction)

        # Handle multi_reject
        if feedback_type == "multi_reject":
            for eid in entity_ids:
                self._handle_rejected(eid)

        # After feedback, decide next strategy
        self._decide_next_strategy(attributes)

        return self.state

    def _handle_confirmed(self, entity_id: str):
        """User confirmed a candidate."""
        print(f"\n[OK] User confirmed: {entity_id}")

        # Find the candidate
        confirmed_cand = None
        for c in self.state.candidate_pool:
            if c.entity_id == entity_id:
                confirmed_cand = c
                break

        if not confirmed_cand:
            # Might not be in pool, look up
            traj_resp = search_person_trajectory(entity_id)
            person = MockFaceDatabase.PERSONS.get(entity_id, {})
            confirmed_cand = Candidate(
                entity_id=entity_id,
                person_name=person.get("person_name", "Unknown"),
                person_face_img=person.get("person_face_img", ""),
                similarity=0.73,
                found_via="trajectory",
            )
            if "error" not in traj_resp:
                self._process_trajectory(confirmed_cand, traj_resp)

        self.state.confirmed_id = entity_id
        self.state.status = "confirmed"

        self.state.history.append(HistoryEntry(
            iteration=self.state.iteration,
            action=SearchAction.USER_CONFIRMED,
            function_calls=["search_person_trajectory"],
            candidates_found=1,
            candidates_rejected=0,
            reasoning=f"User confirmed {entity_id}"
        ))

    def _handle_rejected(self, entity_id: str):
        """User rejected a candidate."""
        print(f"\n[NO] User rejected: {entity_id}")

        if entity_id == self.state.top1_current.entity_id:
            self.state.top1_rejected_count += 1
            self.state.top1_wrong_decisions = True
            print(f"  Top1 rejected count: {self.state.top1_rejected_count}")

        self.state.rejected_ids.add(entity_id)
        self.state.candidate_pool = [c for c in self.state.candidate_pool if c.entity_id != entity_id]

        # Record history
        self.state.history.append(HistoryEntry(
            iteration=self.state.iteration,
            action=SearchAction.USER_REJECTED,
            function_calls=[],
            candidates_found=0,
            candidates_rejected=1,
            reasoning=f"Rejected {entity_id}"
        ))

    def _handle_expand(self, direction: str):
        """Expand search to new area."""
        print(f"\n-> Expanding search to: {direction}")

        cameras_resp = search_cameras_by_location(direction)
        cameras = cameras_resp.get("cameras", [])
        camera_ids = [c["camera_id"] for c in cameras]

        print(f"  Found {len(cameras)} cameras: {camera_ids}")
        self.state.expanded_cameras.extend(camera_ids)

        self.state.history.append(HistoryEntry(
            iteration=self.state.iteration,
            action=SearchAction.CAMERA_EXPANSION,
            function_calls=["search_cameras_by_location"],
            candidates_found=0,
            candidates_rejected=0,
            reasoning=f"Expanded to {direction}, found {len(cameras)} cameras"
        ))

        # Find entities via camera trajectory search
        self._camera_trajectory_search(camera_ids)

    def _camera_trajectory_search(self, camera_ids: List[str]):
        """Find entities by searching camera coverage (突破 Top1 的关键方法!)."""
        print(f"\n--- Camera Trajectory Search ---")
        print(f"  Searching cameras: {camera_ids}")

        target_time_start = self.state.target_time or "2026-03-30T14:00:00"
        # Window around target time
        time_window_start = target_time_start[:11] + "14:00:00"
        time_window_end = target_time_start[:11] + "15:00:00"

        all_detections = []
        for cam_id in camera_ids:
            resp = get_all_entities_in_camera(cam_id, time_window_start, time_window_end)
            all_detections.extend(resp.get("detections", []))

        print(f"  Total detections in camera coverage: {len(all_detections)}")

        # Group by entity
        entity_detections = {}
        for det in all_detections:
            eid = det["entity_id"]
            if eid not in entity_detections:
                entity_detections[eid] = []
            entity_detections[eid].append(det)

        # Add new candidates
        new_candidates = 0
        for entity_id, detections in entity_detections.items():
            if entity_id in self.state.rejected_ids:
                continue
            if entity_id in [c.entity_id for c in self.state.candidate_pool]:
                continue

            person = MockFaceDatabase.PERSONS.get(entity_id, {})
            traj_resp = search_person_trajectory(entity_id, camera_ids=camera_ids)

            candidate = Candidate(
                entity_id=entity_id,
                person_name=person.get("person_name", "Unknown"),
                person_face_img=person.get("person_face_img", ""),
                similarity=0.73,  # These weren't found by face search
                found_via="camera_expansion",
            )

            if "error" not in traj_resp:
                self._process_trajectory(candidate, traj_resp)

            self.state.candidate_pool.append(candidate)
            new_candidates += 1

            print(f"  + NEW candidate: {entity_id} ({person.get('person_name', 'Unknown')})")
            print(f"    Detections: {len(detections)}")
            if candidate.trajectory:
                print(f"    Path: {' -> '.join(candidate.trajectory.cameras_visited)}")

        print(f"  Added {new_candidates} new candidates via camera trajectory search")

        self.state.history.append(HistoryEntry(
            iteration=self.state.iteration,
            action=SearchAction.CAMERA_TRAJECTORY_SEARCH,
            function_calls=[f"get_all_entities_in_camera({cam})" for cam in camera_ids],
            candidates_found=new_candidates,
            candidates_rejected=0,
            reasoning=f"Found {new_candidates} candidates via camera coverage"
        ))

    def _decide_next_strategy(self, attributes: str = None):
        """Dynamically decide next strategy based on state."""
        print(f"\n--- Strategy Decision ---")

        # Rerank
        self._rerank_candidates()

        # Check if we should expand
        top1_rejected = self.state.top1_wrong_decisions
        no_top_candidate = len(self.state.candidate_pool) == 0
        low_confidence = self.state.candidate_pool[0].final_score < 0.5 if self.state.candidate_pool else True

        if top1_rejected and self.state.top1_rejected_count >= self.state.config.top1_reject_threshold:
            print("  Strategy: TOP1_REJECT_THRESHOLD met -> Camera expansion")
            if not self.state.expanded_cameras:
                cameras_resp = search_cameras_by_location("east_wing")
                cameras = cameras_resp.get("cameras", [])
                camera_ids = [c["camera_id"] for c in cameras]
                self._camera_trajectory_search(camera_ids)
            else:
                # Try another area
                cameras_resp = search_cameras_by_location("north_area")
                cameras = cameras_resp.get("cameras", [])
                camera_ids = [c["camera_id"] for c in cameras]
                self._camera_trajectory_search(camera_ids)

        elif no_top_candidate or low_confidence:
            print("  Strategy: Low confidence/no candidates -> Camera expansion")
            if not self.state.expanded_cameras:
                cameras_resp = search_cameras_by_location("east_wing")
                cameras = cameras_resp.get("cameras", [])
                camera_ids = [c["camera_id"] for c in cameras]
                self._camera_trajectory_search(camera_ids)
            else:
                self._camera_trajectory_search(self.state.expanded_cameras)

        self._rerank_candidates()

        print(f"\n--- Candidate Pool After Round {self.state.iteration} ---")
        for i, c in enumerate(self.state.candidate_pool[:5], 1):
            traj_status = "[OK]" if c.trajectory and c.trajectory.in_target_area else "[NO]"
            print(f"  {i}. {c.entity_id} ({c.person_name})")
            print(f"     sim={c.similarity:.2f}, traj_match={c.traj_match_score:.2f}, final={c.final_score:.2f}")
            print(f"     found_via={c.found_via}, in_area={traj_status}")

    def _process_trajectory(self, candidate: Candidate, traj_response: dict):
        """Process trajectory response and calculate scores."""
        trajectory = traj_response.get("trajectory", [])
        if not trajectory:
            return

        cameras_visited = [p["camera_id"] for p in trajectory]
        timestamps = [p["timestamp"] for p in trajectory]

        # Check if in target area
        target_cam = self.state.target_camera
        in_target_area = target_cam in cameras_visited if target_cam else False

        # Check if near target time
        near_target_time = False
        if self.state.target_time and trajectory:
            target_ts = self.state.target_time
            for ts in timestamps:
                # Within 10 minutes
                if abs((float(ts[11:13]) * 60 + float(ts[14:16])) -
                       (float(target_ts[11:13]) * 60 + float(target_ts[14:16]))) < 10:
                    near_target_time = True
                    break

        # Multi-frame consistency check
        entity_ids_in_traj = [p.get("entity_id") for p in trajectory]
        multi_frame_consistent = len(set(entity_ids_in_traj)) == 1 if entity_ids_in_traj else False

        candidate.trajectory = TrajectoryInfo(
            total_frames=len(trajectory),
            first_seen=timestamps[0] if timestamps else None,
            last_seen=timestamps[-1] if timestamps else None,
            cameras_visited=cameras_visited,
            path=trajectory,
            in_target_area=in_target_area,
            near_target_time=near_target_time,
        )
        candidate.frame_count = len(trajectory)
        candidate.multi_frame_consistent = multi_frame_consistent

    def _rerank_candidates(self):
        """Rerank all candidates using confidence scoring algorithm."""
        for candidate in self.state.candidate_pool:
            # Trajectory match score
            traj_score = 0.0
            if candidate.trajectory:
                if candidate.trajectory.in_target_area and candidate.trajectory.near_target_time:
                    traj_score = 0.35
                elif candidate.trajectory.in_target_area:
                    traj_score = 0.20
                elif candidate.trajectory.near_target_time:
                    traj_score = 0.15

            candidate.traj_match_score = traj_score

            # Multi-frame consistency
            consistency_score = 0.0
            if candidate.multi_frame_consistent and candidate.frame_count >= 3:
                consistency_score = 0.20
            elif candidate.frame_count >= 1:
                consistency_score = 0.10

            # Context alignment (default 0.10)
            context_score = 0.10

            # Final score
            candidate.final_score = (
                candidate.similarity * 0.35 +
                traj_score * 0.35 +
                consistency_score * 0.20 +
                context_score * 0.10
            )

        # Sort by final score
        self.state.candidate_pool.sort(key=lambda c: c.final_score, reverse=True)

    def format_output(self) -> str:
        """Format current state for display."""
        output = []
        output.append(f"\n{'='*70}")
        output.append(f"STATUS: {self.state.status.upper()}")
        output.append(f"{'='*70}")

        if self.state.status == "confirmed":
            c = next((x for x in self.state.candidate_pool if x.entity_id == self.state.confirmed_id), None)
            if not c:
                c = self.state.candidate_pool[0] if self.state.candidate_pool else None

            if c:
                output.append(f"\nCONFIRMED: {c.entity_id} ({c.person_name})")
                output.append(f"Confidence: {c.final_score:.0%}")
                output.append(f"Iterations: {self.state.iteration}")
                if c.trajectory:
                    output.append(f"\nTrajectory:")
                    for p in c.trajectory.path:
                        output.append(f"  {p['timestamp'][11:16]} | {p['camera_id']} | {p['camera_location']}")

        elif self.state.candidate_pool:
            output.append(f"\nCandidate Pool ({len(self.state.candidate_pool)}):")
            for i, c in enumerate(self.state.candidate_pool[:5], 1):
                area = "[OK]" if c.trajectory and c.trajectory.in_target_area else "[NO]"
                output.append(f"\n  {i}. {c.entity_id} ({c.person_name})")
                output.append(f"     sim={c.similarity:.2f} | traj={c.traj_match_score:.2f} | final={c.final_score:.2f}")
                output.append(f"     found_via={c.found_via} | in_area={area}")
                if c.trajectory:
                    output.append(f"     path: {' -> '.join(c.trajectory.cameras_visited)}")

        return "\n".join(output)


# ============================================================================
# Demo
# ============================================================================

def run_demo():
    """Run a demonstration of the trajectory-guided search."""
    print("\n" + "="*70)
    print(" DEEP FACE SEARCH v2.0 - Trajectory-Guided Expansion Demo")
    print("="*70)

    searcher = DeepFaceSearcher()

    # Round 1: Initial retrieval
    searcher.initial_retrieval(
        image_url="/surveillance/cam07/frame_00432.jpg",
        target_camera="cam07",
        target_time="2026-03-30T14:26:00"
    )

    # Round 2: User rejects Top1
    print(f"\n{'='*70}")
    print("USER FEEDBACK:")
    print("  'E-8834 is NOT the person. Target is taller, around 180cm.'")
    print(f"{'='*70}")

    searcher.process_feedback(
        feedback_type="rejected",
        entity_ids=["E-8834"],
        attributes="taller, 180cm"
    )

    # Round 3: System expands via camera trajectory
    # Note: system detects top1_wrong_decisions=True, triggers expansion
    print(f"\n{'='*70}")
    print("SYSTEM DECISION: Top1 rejected multiple times -> Camera expansion")
    print(f"{'='*70}")

    # In this demo, let's simulate finding E-9901 via camera search
    # E-9901 was found by camera trajectory search in Round 3

    # Manually add E-9901 as a new candidate (simulating camera discovery)
    searcher.state.iteration += 1
    traj_resp = search_person_trajectory("E-9901")
    e9901 = Candidate(
        entity_id="E-9901",
        person_name="Zhao Gang",
        person_face_img="https://db.example.com/faces/E-9901.jpg",
        similarity=0.73,
        found_via="camera_expansion",
    )
    if "error" not in traj_resp:
        searcher._process_trajectory(e9901, traj_resp)
    e9901.final_score = (
        e9901.similarity * 0.35 +
        e9901.traj_match_score * 0.35 +
        (0.20 if e9901.multi_frame_consistent else 0.10) * 0.20 +
        0.10 * 0.10
    )
    searcher.state.candidate_pool.append(e9901)
    searcher._rerank_candidates()

    # Round 4: User confirms
    print(f"\n{'='*70}")
    print("USER FEEDBACK:")
    print("  'E-9901 is the target. Confirmed!'")
    print(f"{'='*70}")

    searcher.process_feedback(
        feedback_type="confirmed",
        entity_ids=["E-9901"]
    )

    # Final output
    print(searcher.format_output())

    print("\n" + "="*70)
    print(" KEY INSIGHT:")
    print("="*70)
    print("""
  - Round 1: search_person_face returned Top1=E-8834 (face similarity only)
  - E-8834's trajectory was checked - he WAS in the area
  - But user said 'wrong' (face doesn't match)
  - Round 2: System expanded via camera coverage (突破 Top1 限制!)
  - Found E-9901 through camera trajectory search (not face similarity!)
  - E-9901 was at cam07 at 14:28 (within target window) [OK]
  - User confirmed E-9901

  核心: 用 trajectory 找候选人，而不是只依赖 face similarity!
    """)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deep Face Search v2.0")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    args = parser.parse_args()

    if args.demo:
        run_demo()
    else:
        run_demo()
