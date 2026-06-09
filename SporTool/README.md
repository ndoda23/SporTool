--Overview--
This project is a video processing and tracking tool for tennis or padel matches. It detects players, tracks the ball, estimates rallies, and generates processed videos with statistics.

--Features--
1.Player Detection
   -Detects players in each video frame using YOLOv8.

   -Draws bounding boxes around detected players.

   -Assigns unique IDs to players and tracks them across frames.

   -Shows player IDs on the output video.
2.Ball Detection and Tracking

   -Detects tennis/padel balls in each frame.

   -Draws circles around detected balls.

   -Tracks ball position across frames.

   -Detects ball hits using a velocity threshold (fast movements of the ball are counted as hits).

3.Player Movement Tracking

   -Tracks player movement distances in meters based on court dimensions.

   -Accumulates total distance moved for each player across frames.

   -Converts pixel movement into real-world meters using court size.

4.Rally Duration Estimation

   -Counts frames where the ball is detected.

   -Estimates rally duration in seconds.

5.Per-Frame Statistics

   -Tracks how many players are detected per frame.

   -Counts total frames processed.

   -Keeps a list of player positions (player_positions) and ball positions (ball_positions).

6.Video Output

   -Creates a processed video with:

     -Player bounding boxes

     -Player IDs

     -Ball positions

     -Overlayed statistics (frame number, players, ball hits)

7.Quick Processing Options

   -max_frames parameter lets you process only a subset of frames (useful for testing).

8.Error Handling

   -Skips frames if detection fails, logs errors without stopping the processing.


--API Endpoints--

Endpoin             

1./health -> Returns 200 if API is up
2./upload -> Upload a video for processing. Use form-data, key=video. Returns job_id.
3./process/<job_id> -> Process the uploaded video with the given job_id. Returns JSON statistics + download link.
4./download/<job_id> -> Download processed video using job_id.

------------------------------
Uploaded videos → uploads/
Processed videos → outputs/
------------------------------