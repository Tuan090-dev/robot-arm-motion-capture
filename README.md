# 🦾 Robot Arm Motion Capture

A 6-DOF robotic arm that mirrors human arm movement in real-time using dual-camera stereo vision.

## Demo
[▶ Watch on YouTube](https://youtube.com/@gavip6892)

## How it works
- Dual cameras capture arm position from 2 angles
- MediaPipe detects body and hand keypoints
- Stereo vision reconstructs 3D joint positions
- Rotation matrices compute 7 joint angles in real-time
- Arduino receives angle data via serial and drives servos

## Tech Stack
- Python, OpenCV, MediaPipe, NumPy, PyGame
- Arduino C++, ESP32
- SolidWorks, 3D Printing (custom servo mounts)

## Files
- `test10.py` — main entry point
- `Detection.py` — camera capture and pose detection
- `Transformations.py` — 3D coordinate transforms
- `RobotAngles.py` — joint angle computation
- `arduino_comm.py` — serial communication
- `UI.py` — display interface
