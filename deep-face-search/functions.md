# Face Search Function API Reference

---

## 1. search_person_face

**Description**: Search for person archive information using a face image. Retrieves the most similar persons from the face database based on embedding similarity.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `image_url` | `str` | Yes | URL or path to the query face image |

**Response**:
```json
{
  "person_face": {
    "entity_id": "string",      // Unique person identifier
    "person_name": "string",    // Person's display name
    "person_face_img": "string" // URL to person's registered face image
  }
}
```

**Notes**:
- Uses face embedding similarity for matching
- Returns top match by default
- Input image should contain a single clear face for best results

---

## 2. search_cameras_by_location

**Description**: Find all cameras within a specified geographic area or zone. Useful for expanding search scope to nearby cameras when tracking a target.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `location` | `str` | Yes | Location name, zone ID, or area description (e.g., "east_wing", "building_a_floor_2", "parking_lot") |
| `radius` | `float` | No | Search radius in meters (if location is coordinates-based) |

**Response**:
```json
{
  "cameras": [
    {
      "camera_id": "string",      // Unique camera identifier
      "camera_name": "string",    // Human-readable camera name
      "location": "string",       // Physical location/zone
      "position": {               // Geographic coordinates (if available)
        "latitude": "float",
        "longitude": "float",
        "altitude": "float"        // Optional, elevation
      },
      "direction": "string",      // Camera facing direction (e.g., "north", "northeast")
      "coverage_area": "string",  // Description of coverage zone
      "status": "string",          // "online" | "offline" | "maintenance"
      "last_active": "string"     // ISO timestamp of last frame captured
    }
  ]
}
```

**Notes**:
- If `location` is a zone name, returns all cameras in that zone
- If `location` is coordinates, returns cameras within `radius` meters
- `coverage_area` helps identify which cameras overlap or face each other

---

## 3. search_person_trajectory

**Description**: Retrieve a person's movement trajectory across multiple cameras and time. Returns the chronological path of a person through the surveillance network.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `entity_id` | `str` | Yes | Unique person identifier |
| `start_time` | `str` | No | ISO 8601 timestamp — start of search window (default: 24h ago) |
| `end_time` | `str` | No | ISO 8601 timestamp — end of search window (default: now) |
| `camera_ids` | `list[str]` | No | Filter to specific cameras only |

**Response**:
```json
{
  "entity_id": "string",
  "person_name": "string",
  "trajectory": [
    {
      "camera_id": "string",      // Camera that captured this frame
      "camera_location": "string", // Camera's zone/area name
      "timestamp": "string",        // ISO 8601 when person was detected
      "face_image_url": "string",  // URL to captured face frame
      "body_image_url": "string",   // URL to full body frame (if available)
      "confidence": "float",        // Detection confidence (0.0-1.0)
      "position_estimate": {       // Estimated position within frame
        "x": "float",               // Normalized 0-1
        "y": "float"
      }
    }
  ],
  "total_frames": "int",           // Number of detection points
  "first_seen": "string",          // ISO timestamp of first detection
  "last_seen": "string"            // ISO timestamp of last detection
}
```

**Trajectory Analysis Fields**:
| Field | Description |
|-------|-------------|
| `total_frames` | Count of detection points — more frames = more confident track |
| `first_seen` / `last_seen` | Time window of person's presence |
| `camera_transitions` | List of (from_camera → to_camera, time_gap) pairs |

**Notes**:
- Trajectory is sorted chronologically
- Gaps between detections may indicate person was off-camera or in non-covered area
- Use `camera_ids` filter to focus on specific area of interest
- Trajectory can be used to extrapolate probable location at a given time

---

## Usage in Deep Face Search Workflow

### Cross-Reference Pattern

```python
# Example: Using trajectory to verify candidate
# Step 1: Get initial face match
face_result = search_person_face(image_url="...")

# Step 2: Get person's trajectory
traj_result = search_person_trajectory(entity_id=face_result["person_face"]["entity_id"])

# Step 3: Check if trajectory passes through target camera/time
#   - If target camera_id appears in trajectory AND timestamp overlaps → HIGH confidence
#   - If target camera_id is nearby cameras in trajectory time window → MEDIUM confidence
#   - If trajectory is far from target area/time → LOW confidence
```

### Multi-Camera Expansion Pattern

```python
# Example: Expanding search to nearby cameras
# Step 1: Find cameras in target area
cameras = search_cameras_by_location(location="east_wing")

# Step 2: For each camera in area, check trajectory
for cam in cameras["cameras"]:
    traj = search_person_trajectory(
        entity_id=candidate_id,
        camera_ids=[cam["camera_id"]]
    )
    # If trajectory overlaps with camera AND time window → boost similarity score
```

---

## Error Responses

All functions return errors in this format:

```json
{
  "error": {
    "code": "string",      // Error code (e.g., "NO_FACE_DETECTED", "ENTITY_NOT_FOUND")
    "message": "string"    // Human-readable error description
  }
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `NO_FACE_DETECTED` | Input image contains no detectable face |
| `MULTIPLE_FACES_DETECTED` | Input image contains multiple faces — please crop to single face |
| `ENTITY_NOT_FOUND` | Requested person/entity ID does not exist in database |
| `CAMERA_NOT_FOUND` | Requested camera ID does not exist |
| `DATABASE_ERROR` | Backend database connection failed |
| `TIMEOUT` | Search operation timed out |
| `INVALID_IMAGE` | Image format not supported or file corrupted |

---

## Rate Limits

| Function | Limit |
|----------|-------|
| `search_person_face` | 100 requests/minute |
| `search_cameras_by_location` | 200 requests/minute |
| `search_person_trajectory` | 50 requests/minute |

---

## Future Functions (Planned)

| Function | Description |
|----------|-------------|
| `search_person_by_attributes` | Search by non-face attributes (height, clothing color, accessories) |
| `search_similar_faces` | Find visually similar faces to input |
| `compare_face_pair` | Compare two face images and return similarity score |
| `search_multi_frame_consistency` | Verify identity across multiple frames |
| `get_person_attributes` | Get physical attributes estimate from face embedding |
