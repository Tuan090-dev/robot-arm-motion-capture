
import time
import multiprocessing
import cv2
   
from math import cos, sin, pi, atan

import pygame
import serial
import numpy as np

import UI
from Transformations import *
from Detection import capture_frame, Hand_Detection
from arduino_comm import string_join
from RobotAngles import Get_Joint_Position,rotation_matrix_x,rotation_matrix_z,Get_Joint_Angles,Get_Joint_Angle, rotation_matrix_y, rotation_matrix

from math import cos, sin, pi, atan

def Rota_vector(Vetor, alpha, axis):
    array_vector = np.array(Vetor.Vector2Array()) 
    for i in range(len(alpha)):
        array_vector = rotation_matrix(alpha[i], axis[i]) @ array_vector 
    return array_vector.reshape(-1, 1)
 
def Draw_line(ImgPos_array_X,ImgPos_array_Y,frame):
    for i in range(0, len(ImgPos_array_X) - 1):
        cv2.line(frame, 
                 (int(ImgPos_array_X[i]), int(ImgPos_array_Y[i])), 
                 (int(ImgPos_array_X[i + 1]), int(ImgPos_array_Y[i + 1])), 
                 (255, 0, 255), 2)  

def main():
    # kết nối arduino
    arduino_port = "COM3"  
    baud_rate = 115200    
    ser = serial.Serial(arduino_port, baud_rate)
    time.sleep(1)
    ser.write('10100000'.encode())

    # khởi tạo UI pygame
    pygame.init()
    pygame.display.set_caption("ArmEcho")
    font = pygame.font.SysFont('sans', 60)

    SCREEN_WIDTH = 1450
    SCREEN_HEIGHT = 700 + 100
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # các biến lưu giá trị
    last_frame1 = None
    last_frame2 = None

    UI_frame_1 = None
    UI_frame_2 = None

    Positions = [[0],[0],[0],[0]]
    Scale = 1

    Positions_h = [[0],[0],[0]]

    # Khởi tạo Queue và các biến trung gian để truyền dữ liệu
    queue1 = multiprocessing.Queue(1)
    queue2 = multiprocessing.Queue(1)
    queue3 = multiprocessing.Queue(1)
    queue4 = multiprocessing.Queue(1)
    is_detect_1 = multiprocessing.Value('b', False)
    is_detect_2 = multiprocessing.Value('b', False)
    frame_count_1 = multiprocessing.Array('i', 2)
    frame_count_2 = multiprocessing.Array('i', 2)
    ImgPos_array_X1 = multiprocessing.Array('i', 6)
    ImgPos_array_Y1 = multiprocessing.Array('i', 6)
    ImgPos_array_X2 = multiprocessing.Array('i', 6)
    ImgPos_array_Y2 = multiprocessing.Array('i', 6)

    Hands_Pos_array_X1 = multiprocessing.Array('i', 4)
    Hands_Pos_array_Y1 = multiprocessing.Array('i', 4)
    Hands_Pos_array_X2 = multiprocessing.Array('i', 4)
    Hands_Pos_array_Y2 = multiprocessing.Array('i', 4)

    # Tạo và khởi động tiến trình cho mỗi camera
    p1 = multiprocessing.Process(target=capture_frame, args=(ImgPos_array_X1, ImgPos_array_Y1, 1, queue1, queue3, is_detect_1, frame_count_1))  # Camera 0
    p2 = multiprocessing.Process(target=capture_frame, args=(ImgPos_array_X2, ImgPos_array_Y2, 2, queue2, queue4, is_detect_2, frame_count_2))  # Camera 1
    p3 = multiprocessing.Process(target=Hand_Detection, args=(Hands_Pos_array_X1, Hands_Pos_array_Y1, queue3, 2))
    p4 = multiprocessing.Process(target=Hand_Detection, args=(Hands_Pos_array_X2, Hands_Pos_array_Y2, queue4, 2))
    p1.start()
    p2.start()
    p3.start()
    p4.start()

    running = True
    while running:
        clock.tick(60)
        UI.Draw_panel(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
#================ láy ảnh camera =====================================        
        if not queue1.empty(): 
            frame1 = queue1.get()
            last_frame1 = frame1.copy()

        if not queue2.empty():
            while queue2.qsize() > 1:
                queue2.get()
            frame2 = queue2.get()
            last_frame2 = frame2.copy()
#========================== tính toán ==========================
        Positions, Scale = Get_Joint_Position(ImgPos_array_X1, ImgPos_array_Y1, ImgPos_array_X2,ImgPos_array_Y2,640)

        if len(ImgPos_array_X1) == 6 and last_frame1 is not None:
            Draw_line(ImgPos_array_X1,ImgPos_array_Y1,last_frame1)

            V_x = frame_count_1[0]
            V_Y = frame_count_1[1]
            top_left = (V_x - 80, V_Y - 80) 
            bottom_right = (V_x + 80, V_Y + 80)
            cv2.rectangle(last_frame1, top_left, bottom_right, (0, 0, 255), 2)
            UI_frame_1 = cv2.getRectSubPix(frame1, (200, 200), (V_x, V_Y))
            Draw_line(Hands_Pos_array_X1, Hands_Pos_array_Y1,UI_frame_1)

        if len(ImgPos_array_X2) == 6 and last_frame2 is not None:
            Draw_line(ImgPos_array_X2,ImgPos_array_Y2,last_frame2)

            V_x = frame_count_2[0]
            V_Y = frame_count_2[1]
            top_left = (V_x - 80, V_Y - 80) 
            bottom_right = (V_x + 80, V_Y + 80)
            cv2.rectangle(last_frame2, top_left, bottom_right, (0, 0, 255), 2)
            UI_frame_2 = cv2.getRectSubPix(frame2, (200, 200), (V_x, V_Y))
            Draw_line(Hands_Pos_array_X2, Hands_Pos_array_Y2,UI_frame_2)

        #================ trục 1==================
        Vetor_Img0 = Vetor()
        Vetor_Img0.cvt2Vetor(Positions[1], Positions[2], Scale)
        alpha_0 = Get_Joint_Angle(Vetor_Img0.Vetor_z, Vetor_Img0.Vetor_y)

        #================ trục 2 ==================
        #gốc x tính ra dương nhương thu về cùng chiều kim đồng hồ nên là gốc âm
        Vetor_R1 = Vetor()
        Vetor_R1.Array2Vector(Rota_vector(Vetor_Img0, [-alpha_0], ['x']))
        alpha_1 = Get_Joint_Angle(Vetor_R1.Vetor_x, Vetor_R1.Vetor_y)

        #================ trục 3 ==================
        Vetor_Img1 = Vetor()
        Vetor_Img1.cvt2Vetor(Positions[2], Positions[3], Scale)
        #gốc x dương nhương thu về cùng chiều kim đồng hồ nên là gốc âm+
        #gốc z dương thu về cùng chiều kim đồng hộ nên gốc dương
        Vetor_R2 = Vetor()
        Vetor_R2.Array2Vector(Rota_vector(Vetor_Img1, [-alpha_0, alpha_1], ['x', 'z']))
        
        alpha_2 = 0
        if Vetor_R2.Vetor_x == 0:
            alpha_2 = 0
        elif Vetor_R2.Vetor_z <= 0 and Vetor_R2.Vetor_x > 0:
            alpha_2 = 90
        elif Vetor_R2.Vetor_z <= 0 and Vetor_R2.Vetor_x < 0:
            alpha_2 = -50
        else:
            alpha_2 = atan(Vetor_R2.Vetor_x/Vetor_R2.Vetor_z) * (180/pi)

        if alpha_2 <= -50:
            alpha_2 = -50

        #================ trục 4 ==================
        Vetor_R3 = Vetor()
        Vetor_R3.Array2Vector(Rota_vector(Vetor_Img1, [-alpha_0, alpha_1, -alpha_2], ['x','z','y']))
        alpha_3 = 0
        if Vetor_R3.Vetor_x == 0:
            alpha_3 = 0
        else:
            alpha_3 = atan(Vetor_R3.Vetor_y/Vetor_R3.Vetor_z) * (180/pi)

        if alpha_3 < -30:
            alpha_3 = -30

        #============= truc 5 ===================
        Positions_h, _ = Get_Joint_Position(Hands_Pos_array_X1, Hands_Pos_array_Y1, Hands_Pos_array_X2,Hands_Pos_array_Y2,200)
        Vetor_Img2 = Vetor()
        Vetor_Img2.cvt2Vetor(Positions_h[1], Positions_h[3], Scale)
        Vetor_R4 = Vetor()
        Vetor_R4.Array2Vector(Rota_vector(Vetor_Img2, [-alpha_0, alpha_1, -alpha_2, alpha_3], ['x','z','y','x']))

        alpha_4 = 0
        if Vetor_R4.Vetor_y == 0:
            alpha_4 = 0
        elif Vetor_R4.Vetor_y < 0 and Vetor_R4.Vetor_x < 0:
            alpha_4 = -90
        elif Vetor_R4.Vetor_y < 0 and Vetor_R4.Vetor_x > 0:
            alpha_4 = 90
        else:
            alpha_4 = atan(Vetor_R4.Vetor_x/Vetor_R4.Vetor_y) * (180/pi)

        #=============== truc 6 ====================
        Vetor_Img3 = Vetor()
        Vetor_Img3.cvt2Vetor(Positions_h[0], Positions_h[1], Scale)
        Vetor_R5 = Vetor()
        Vetor_R5.Array2Vector(Rota_vector(Vetor_Img3, [-alpha_0, alpha_1, -alpha_2, alpha_3, alpha_4], ['x','z','y','x','z']))

        alpha_5 = 0
        if Vetor_R5.Vetor_z == 0:
            alpha_5 = 0
        else:
            alpha_5 = atan(Vetor_R5.Vetor_x/Vetor_R5.Vetor_z) * (180/pi)

        #================ truc 7 ===================
        Vetor_Img4 = Vetor()
        Vetor_Img4.cvt2Vetor(Positions_h[1], Positions_h[2], Scale)
        Vetor_R6 = Vetor()
        Vetor_R6.Array2Vector(Rota_vector(Vetor_Img4, [-alpha_0, alpha_1, -alpha_2, alpha_3, alpha_4, alpha_5], ['x','z','y','x','z','y']))

        alpha_6 = 0
        if Vetor_R6.Vetor_x >= 0:
            alpha_6 = -90
        elif Vetor_R6.Vetor_z <0:
            alpha_6 = 0
        else:
            alpha_6 = atan(Vetor_R6.Vetor_z/Vetor_R6.Vetor_x) * (180/pi)
        alpha_6 = 90 - (- alpha_6)
#========================== UI ==============================
        text1 = f'screen : {str(round(Scale, 2))}'
        text2 = f'alpha_0 : {int(alpha_0)}'
        text3 = f'alpha_1 : {int(alpha_1)}'
        text4 = f'alpha_2 : {int(alpha_2)}'
        text5 = f'alpha_6 : {int(alpha_6)}'
        text6 = f'alpha_3 : {int(alpha_3)}'
        text7 = f'alpha_4 : {int(alpha_4)}'
        text8 = f'alpha_5 : {int(alpha_5)}'
        texts = [text1, text2, text3, text4, text5, text6, text7, text8]
        text_pos = [(1100, 550),(70, 550),(70, 610),(70, 670), (800,610),(500,550),(500,610) ,(500, 670)]

        UI.Put_texts(screen, font, texts, text_pos)
        if last_frame1 is not None:
            UI.Show_cam(screen, last_frame1, (55, 55))
            UI.Show_cam(screen, UI_frame_1, (55+440, 55))
        if last_frame2 is not None:
            UI.Show_cam(screen, last_frame2, (755, 55))
            UI.Show_cam(screen, UI_frame_2, (755+440, 55))

#===================== truyền dữ liệu cho arduino =============
        if is_detect_1.value and is_detect_2.value:
            data = string_join([alpha_0, alpha_1, alpha_2, alpha_3, alpha_4, alpha_5, alpha_6])
            ser.write(data.encode())  

#======================== End ==========================
        pygame.display.update()
        time.sleep(0.01)
        
#============== giải phóng các tiến trình ============
    p1.terminate()
    p2.terminate()
    p3.terminate()
    p4.terminate()

    p1.join()
    p2.join()
    p3.join()
    p4.join()

    pygame.quit()

if __name__ == '__main__':
    main()
