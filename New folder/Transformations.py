import numpy as np

class point:
	def __init__(self, RPos_x=0, RPos_y=0, RPos_z=0):
		self.RPos_x = RPos_x
		self.RPos_y = RPos_y
		self.RPos_z = RPos_z
	def Cvt2RPos(self, ImgPos_x, ImgPos_y, cam, size):
		if cam == 0:
			self.RPos_x = size - ImgPos_x
			self.RPos_y = ImgPos_y
		elif cam == 1:
			self.RPos_z = ImgPos_x
			self.RPos_y = ImgPos_y

class position:
	def __init__(self, Pos_x=0, Pos_y=0, Pos_z=0):
		self.Pos_x = Pos_x
		self.Pos_y = Pos_y
		self.Pos_z = Pos_z
	def relative_to(self, point1, point2, Scale):
		self.Pos_x = point1.RPos_x
		self.Pos_y = point1.RPos_y
		self.Pos_z = point2.RPos_z

class Vetor:
	def __init__(self):
		self.Vetor_x = 0
		self.Vetor_y = 0
		self.Vetor_z = 0
	def cvt2Vetor(self, point1, point2, Scale):
		self.Vetor_x = point2.Pos_x - point1.Pos_x
		self.Vetor_y = point2.Pos_y - point1.Pos_y
		self.Vetor_z = int(point2.Pos_z - point1.Pos_z) * Scale
	def Vector2Array(self):
		return [[self.Vetor_x], [self.Vetor_y], [self.Vetor_z]]
	def Array2Vector(self, array):
		self.Vetor_x = array[0]
		self.Vetor_y = array[1]
		self.Vetor_z = array[2]

'''
def rotation_matrix_x(alpha):
	c = cos(alpha * pi/180)
	s = sin(alpha * pi/180)
	matrix = np.array([[1, 0, 0],
					   [0, c,-s],
					   [0, s, c]])
	return matrix'''