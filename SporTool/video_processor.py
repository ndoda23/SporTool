import cv2
from ultralytics import YOLO
import numpy as np
from collections import defaultdict

class VideoProcessor:
    def __init__(self, court_length_m=23.77, court_width_m=8.23):
        """Initialize YOLOv8 model"""
        print("Loading YOLOv8 model...")
        self.model = YOLO('yolov8m.pt')  # medium model
        print("Model loaded successfully!")
        self.court_length_m = court_length_m
        self.court_width_m = court_width_m
    
    def process_video(self, input_path, output_path, max_frames=None):
        print(f"Processing video: {input_path}")
        cap = cv2.VideoCapture(input_path)
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"Video properties: {width}x{height} @ {fps}fps, {total_frames} frames")
        
        # Convert pixels to meters
        pixel_to_meter_x = self.court_length_m / width
        pixel_to_meter_y = self.court_width_m / height
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Stats
        stats = {
            "total_frames": 0,
            "players_detected": 0,
            "unique_players": 0,
            "ball_detections": 0,
            "player_positions": [],
            "ball_positions": [],
            "average_players_per_frame": 0,
            "ball_hit_count": 0,
            "rally_duration_seconds": 0,
            "player_distances_m": defaultdict(float)
        }
        
        prev_players = {}  # key: player_id, value: (x, y)
        next_player_id = 1
        frame_count = 0
        player_counts = []
        ball_detected_frames = []
        prev_ball_pos = None
        ball_velocity_threshold = 50  # pixels/frame

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            if max_frames and frame_count > max_frames:
                break
            if frame_count % 2 != 0:
                out.write(frame)
                continue

            try:
                results = self.model(frame, verbose=False)
                people_count = 0
                ball_detected = False
                current_ball_pos = None
                current_players = []
                
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        
                        if cls == 0 and conf > 0.5:  # Person
                            people_count += 1
                            center_x = int((x1 + x2) / 2)
                            center_y = int((y1 + y2) / 2)
                            current_players.append((center_x, center_y))
                            stats["player_positions"].append((center_x, center_y))
                            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                        
                        elif cls == 32 and conf > 0.1:  # Ball
                            ball_detected = True
                            center_x = int((x1 + x2) / 2)
                            center_y = int((y1 + y2) / 2)
                            current_ball_pos = (center_x, center_y)
                            stats["ball_positions"].append((center_x, center_y))
                            cv2.circle(frame, (center_x, center_y), 10, (0, 0, 255), -1)
                            if prev_ball_pos:
                                dx = current_ball_pos[0] - prev_ball_pos[0]
                                dy = current_ball_pos[1] - prev_ball_pos[1]
                                velocity = np.sqrt(dx**2 + dy**2)
                                if velocity > ball_velocity_threshold:
                                    stats["ball_hit_count"] += 1

                # Track player distances
                frame_player_ids = []
                for cx, cy in current_players:
                    min_dist = float('inf')
                    matched_id = None
                    for pid, (px, py) in prev_players.items():
                        dist = np.sqrt((cx - px)**2 + (cy - py)**2)
                        if dist < min_dist and dist < 100:
                            min_dist = dist
                            matched_id = pid
                    if matched_id is None:
                        matched_id = next_player_id
                        next_player_id += 1
                    if matched_id in prev_players:
                        px, py = prev_players[matched_id]
                        dx_m = abs(cx - px) * pixel_to_meter_x
                        dy_m = abs(cy - py) * pixel_to_meter_y
                        distance_m = np.sqrt(dx_m**2 + dy_m**2)
                        stats["player_distances_m"][matched_id] += distance_m
                    prev_players[matched_id] = (cx, cy)
                    frame_player_ids.append(matched_id)

                # Draw player IDs
                for idx, (cx, cy) in zip(frame_player_ids, current_players):
                    cv2.putText(frame, f"P{idx}", (cx-10, cy-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

                player_counts.append(people_count)
                if ball_detected:
                    ball_detected_frames.append(frame_count)
                    stats["ball_detections"] += 1
                prev_ball_pos = current_ball_pos

                info_text = f"Frame: {frame_count} | Players: {people_count} | Ball Hits: {stats['ball_hit_count']}"
                cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
                out.write(frame)

                if frame_count % 30 == 0:
                    print(f"Processed {frame_count}/{total_frames} frames...")

            except Exception as e:
                print(f"Error processing frame {frame_count}: {e}")
                out.write(frame)
                continue

        cap.release()
        out.release()

        stats["total_frames"] = frame_count
        stats["players_detected"] = sum(player_counts)
        stats["unique_players"] = next_player_id - 1
        stats["average_players_per_frame"] = np.mean(player_counts) if player_counts else 0
        if ball_detected_frames:
            stats["rally_duration_seconds"] = round(len(ball_detected_frames)/fps, 2)

        # Convert defaultdict to normal dict
        stats["player_distances_m"] = dict(stats["player_distances_m"])

        print(f"Processing complete! Output saved to: {output_path}")
        print(f"Statistics: {stats}")
        return stats
