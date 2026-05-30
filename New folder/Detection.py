import cv2
import mediapipe as mp
import time
from sklearn.linear_model import LinearRegression  # Nhập khẩu LinearRegression
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf.symbol_database")


print('Detection running')

window_size = 10

def linear_regression(x, y):
    """Tính hồi quy tuyến tính sử dụng sklearn"""
    x = x.reshape(-1, 1)  # Định hình lại x để phù hợp với yêu cầu của sklearn
    model = LinearRegression()
    model.fit(x, y)
    return model.coef_[0], model.intercept_

def Abc(abc_x, abc_y):
    x = np.arange(len(abc_x[-window_size:]))
    y_x = np.array(abc_x[-window_size:])
    y_y = np.array(abc_y[-window_size:])
    
    m_x, c_x = linear_regression(x, y_x)
    m_y, c_y = linear_regression(x, y_y)
    
    regression_line_x = m_x * x + c_x
    regression_line_y = m_y * x + c_y

    return regression_line_x[int(window_size/2)], regression_line_y[int(window_size/2)]

def capture_frame(ImgPos_array_X, ImgPos_array_Y, camera_index, queue, queue_h, is_detect, frame_count):
    # Khởi tạo MediaPipe Pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False,          # Đặt False để xử lý video (tăng tốc độ xử lý)
                        model_complexity=0,             # Độ phức tạp của mô hình (0, 1, 2: thấp -> cao)
                        enable_segmentation=False,      # Không sử dụng phân đoạn để tăng tốc độ
                        min_detection_confidence=0.9,   # Độ tin cậy tối thiểu để phát hiện
                        min_tracking_confidence=0.5)    # Độ tin cậy tối thiểu để theo dõi
    #mp_drawing = mp.solutions.drawing_utils

    RAW_X = [[], [], [], [], [], []]  # Sửa tên biến cho thống nhất
    RAW_Y = [[], [], [], [], [], []]  # Sửa tên biến cho thống nhất

    point_18 = [0,0]

    cap = None
    prev_time = 0
    try:
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            raise Exception(f"Không thể mở camera {camera_index}")
        
        print(f"Đang lấy dữ liệu từ camera {camera_index}")
        
        while True:
            ret, frame = cap.read()
            frame = cv2.bilateralFilter(frame, 9, 75, 75)

            if not ret:
                print(f"Lỗi khi đọc từ camera {camera_index}. Đang thử lại...")
                time.sleep(1)
                continue
            frame = cv2.resize(frame, (640, 480))

            frame_dt = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_dt.flags.writeable = False
            results = pose.process(frame_dt)
            frame_dt.flags.writeable = True

            if results.pose_landmarks:
                # Lấy tọa độ các điểm 12, 14, 16, 24
                landmarks = results.pose_landmarks.landmark
                points_of_interest = [24, 12, 14, 16, 18, 22]
                points = []

                for idx in points_of_interest:
                    x = int(landmarks[idx].x * frame.shape[1])
                    y = int(landmarks[idx].y * frame.shape[0])
                    if idx == 18:         
                        frame_count[0] = x
                        frame_count[1] = y
                        point_18[0] = x
                        point_18[1] = y
                    
                    RAW_X[points_of_interest.index(idx)].append(x)
                    RAW_Y[points_of_interest.index(idx)].append(y)
                    if len(RAW_X[points_of_interest.index(idx)]) > window_size:  # Giới hạn điểm trên đồ thị
                        RAW_X[points_of_interest.index(idx)].pop(0)
                        RAW_Y[points_of_interest.index(idx)].pop(0)

                    if len(RAW_X[points_of_interest.index(idx)]) >= window_size:
                        smoothed_x, smoothed_y = Abc(RAW_X[points_of_interest.index(idx)], RAW_Y[points_of_interest.index(idx)])
                        points.append((int(smoothed_x), int(smoothed_y)))
                    else:
                        points.append((int(x), int(y)))  # Sử dụng giá trị chưa xử lý nếu dữ liệu chưa đủ


                #for i in range(len(points) - 1):
                    #cv2.line(frame_dt, points[i], points[i + 1], (0, 255, 0), 2)

                if len(points) >= 6:
                    for i in range(6):
                        ImgPos_array_X[i] = points[i][0]
                        ImgPos_array_Y[i] = points[i][1]
                    is_detect.value = True
            else:
                is_detect.value = False

            curr_time = time.time()
            fps = 1 / (curr_time - prev_time)
            prev_time = curr_time
            cv2.putText(frame_dt, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            frame_dt = cv2.resize(frame_dt, (640, 480))
            queue.put(frame_dt)

            V_x = point_18[0]
            V_Y = point_18[1]
            UI_frame_1 = cv2.getRectSubPix(frame_dt, (200, 200), (V_x, V_Y))
            queue_h.put(UI_frame_1)

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
    finally:
        if cap:
            cap.release()  # Giải phóng tài nguyên camera
        cv2.destroyAllWindows()  # Đóng tất cả cửa sổ OpenCV

def Hand_Detection(ImgPos_array_X, ImgPos_array_Y, queue, Pos):
    # Khởi tạo Mediapipe Hands
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils

    # Khởi tạo bộ nhận diện bàn tay
    hands = mp_hands.Hands(
        max_num_hands=2, 
        min_detection_confidence=0.5, 
        model_complexity=0  # Giảm độ phức tạp để tăng tốc
    )

    # Khởi tạo biến lưu trữ dữ liệu tọa độ
    RAW_X = [[], [], [], []]  # Lưu trữ tọa độ X của các điểm 0, 5, 8, 17
    RAW_Y = [[], [], [], []]  # Lưu trữ tọa độ Y của các điểm 0, 5, 8, 17

    while True:
        if not queue.empty():  # Kiểm tra queue có dữ liệu không
            frame = queue.get()  # Ảnh đã ở định dạng RGB từ main

            # Xử lý ảnh
            result = hands.process(frame)

            if result.multi_hand_landmarks and result.multi_handedness:
                for hand_landmarks in result.multi_hand_landmarks:
                    # Vẽ khung bàn tay lên ảnh
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Lấy bàn tay đầu tiên
                hand_landmarks = result.multi_hand_landmarks[0]

                # Lấy tọa độ các điểm 0, 5, 8, 17
                points = [hand_landmarks.landmark[i] for i in [0, 5, 8, 17]]
                h, w, _ = frame.shape

                # Lưu tọa độ vào mảng RAW_X và RAW_Y
                for i in range(4):
                    x = int(points[i].x * w)
                    y = int(points[i].y * h)
                    RAW_X[i].append(x)
                    RAW_Y[i].append(y)
                    if len(RAW_X[i]) > window_size:  # Giới hạn số lượng điểm lưu trữ
                        RAW_X[i].pop(0)
                        RAW_Y[i].pop(0)

                # Làm mượt tọa độ sử dụng hàm Abc
                smoothed_points = []
                for i in range(4):
                    if len(RAW_X[i]) >= window_size:
                        smoothed_x, smoothed_y = Abc(RAW_X[i], RAW_Y[i])
                        smoothed_points.append((int(smoothed_x), int(smoothed_y)))
                    else:
                        smoothed_points.append((int(points[i].x * w), int(points[i].y * h)))

                # Cập nhật tọa độ sau khi làm mượt
                for i in range(4):
                    ImgPos_array_X[i] = smoothed_points[i][0]
                    ImgPos_array_Y[i] = smoothed_points[i][1]

            #cv2.imshow('Right Arm Pose ' + str(Pos), frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break