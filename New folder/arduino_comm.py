print('ok')

def up_0(alpha,ind):
    while len(alpha) <= ind:
        alpha = '0'+alpha
    return alpha

def convert_to_data(alpha,a):
    return up_0(str(int(alpha)), a)

def convert_angles_to_data(angles):
    """
    Chuyển đổi danh sách các góc thành chuỗi dữ liệu.
    Mỗi góc được chuyển thành chuỗi, sau đó nối lại thành một chuỗi duy nhất.
    """
    ind = [1, 1, 2, 2, 2, 2, 1]    
    data = ''
    for i in range(len(angles)):
        data += ''.join(convert_to_data(angles[i], ind[i]))
    return data + "\n"

def string_join(angles):
    """
    Gửi dữ liệu góc dưới dạng chuỗi đến Arduino qua cổng serial.
    """
    data = convert_angles_to_data(angles)
    return data

#print(serial_write([8,9, 0]))