# SporTool 

> **🏆 Ranked in the Top 20 out of 108 projects at Hacktoberfest Tbilisi! Built from scratch in just 24 hours.**

This project is a video processing and tracking tool for tennis or padel matches. It detects players, tracks the ball, estimates rallies, and generates processed videos with statistics.

---

## Features

### 1. Player Detection & Tracking
* **YOLOv8 Powered:** Detects players in each video frame.
* **Bounding Boxes:** Draws bounding boxes around detected players.
* **Identity Tracking:** Assigns unique IDs to players and tracks them across frames, showing player IDs on the output video.

### 2. Ball Detection and Tracking
* **Ball Localization:** Detects tennis/padel balls in each frame and draws circles around them.
* **Trajectory Tracking:** Tracks ball position across frames.
* **Hit Detection:** Detects ball hits using a velocity threshold (fast movements of the ball are counted as hits).

### 3. Player Movement Tracking
* **Pixel-to-Meter Conversion:** Converts pixel movement into real-world meters using court size.
* **Distance Accumulation:** Tracks total distance moved for each player across frames.

### 4. Rally Duration Estimation
* **Rally Calculation:** Counts frames where the ball is detected and estimates rally duration in seconds.

### 5. Per-Frame Statistics & Video Output
* **Analytics Logging:** Tracks how many players are detected per frame, counts total frames processed, and keeps a list of player and ball positions (`player_positions`, `ball_positions`).
* **Visual Overlay:** Creates a processed video overlayed with player bounding boxes, player IDs, ball positions, and statistics (frame number, players, ball hits).
* **Optimization & Safety:** The `max_frames` parameter lets you process only a subset of frames for quick testing. Skips frames if detection fails and logs errors without stopping.

---

## 🔌 API Endpoints

The system is exposed via the following REST API endpoints:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/health` | `GET` | Returns 200 if API is up and running. |
| `/upload` | `POST` | Upload a video for processing. Use form-data, key=`video`. Returns `job_id`. |
| `/process/<job_id>` | `POST` | Process the uploaded video with the given `job_id`. Returns JSON statistics + download link. |
| `/download/<job_id>` | `GET` | Download processed video using `job_id`. |

### 📂 Directory Structure
* Uploaded videos → `uploads/`
* Processed videos → `outputs/`
