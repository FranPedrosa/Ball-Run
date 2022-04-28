import math
import colors
import numpy as np

PI = 3.141592

#Devolve as coordenadas de um ponto em um círuculo, centrado na origem, de raio radius e ângulo theta
def circle_cord(theta, radius,center):
	x = radius*math.cos(theta) + center[0]
	y = radius*math.sin(theta) + center[1]
	return (x,y)

#Pega duas matrizes em forma de array(1,16), transforma em array(4,4), multiplica as matrizes e devolve o array resultante em formato (1,16)
def multiplica_matriz(a, b):
	m_a = a.reshape(4, 4)
	m_b = b.reshape(4, 4)
	m_c = np.dot(m_a, m_b)
	c = m_c.reshape(1, 16)
	return c

#Função que define um círculo centrado em zero, que tem raio radius e número de vértices igual a triangle_count
#Desenhamos vários triângulos adjacentes para criar um círculo
def circle_points(center,radius, triangle_count):
	angle = (2*PI)/triangle_count

	points = []
	for i in range(0, triangle_count):
		theta = angle*i
		theta_n = 0
		if i+1 == triangle_count:
			theta_n = 2*PI
		else:
			theta_n = (i+1)*angle

		vertex0 = circle_cord(theta, radius, center)
		vertex1 = circle_cord(theta_n, radius, center)
		points.append(center)
		points.append(vertex0)
		points.append(vertex1)

	return points

def bacteria_points():
	points = circle_points((0,0),0.07,50) 
	points += circle_points((0,0.07),0.06,50) 
	points += circle_points((-0.01,0.02),0.01,50) 
	points += circle_points((0.04,-0.01),0.01,50) 
	points += circle_points((-0.02,0.09),0.01,50) 
	points += circle_points((-0.03,-0.02),0.01,50) 
	points += circle_points((0.02,0.07),0.01,50) 
	return points

#Função que define um círculo centrado em zero, que tem raio radius e número de vértices igual a triangle_count
#Desenhamos vários triângulos adjacentes para criar um círculo
def virus_points(radius, triangle_count):
	angle = (2*PI)/triangle_count

	points = []
	for i in range(0, triangle_count):
		theta = angle*i
		theta_n = 0
		if i+1 == triangle_count:
			theta_n = 2*PI
		else:
			theta_n = (i+1)*angle

		virus_radius = 1*radius + 0.1*radius*math.sin(theta*20)
		virus_radius_n = 1*radius + 0.1*radius*math.sin(theta_n*20)
		vertex0 = circle_cord(theta, virus_radius,(0,0))
		vertex1 = circle_cord(theta_n, virus_radius_n,(0,0))
		points.append((0,0))
		points.append(vertex0)
		points.append(vertex1)

	return points

#class Cell, classe que cria um objeto em formato de círculo e tem suas funções relacionadas
class Cell:

	#criação do objeto círculo.
	def __init__(self,offset, x, y, tam, cell_type):
		self.x = x 
		self.y = y 
		self.tam = tam
		self.tam_base = tam
		self.tam_temp = 0
		self.dir_x = 0.02
		self.dir_y = 0.01
		self.angle = 0.0
		self.speed = 0.002
		self.cell_type = cell_type
		if cell_type == 'virus':
			self.points = virus_points(0.1,100)
			self.colors = [ colors.green for i in range(100)] 
		else:
			self.points = bacteria_points()
			self.colors = [ colors.pink for i in range(100)] + [colors.red for i in range(250)]
		self.offset = offset

	#atualiza a coordenada x,y para na próxima atualização, a bola esteja se movendo
	def move(self,scale):
		if self.cell_type == 'bacteria':
			self.move_bacteria(scale)
		else:
			self.move_virus(scale)


	#atualiza a coordenada x,y para na próxima atualização, a bola esteja se movendo
	def move_virus(self,scale):

		#Movimento reflexivos, se o obejto bate na parede da janela, ele não passa por ela e volta invertendo o sentido de movimento
		if self.x + 0.1 * self.tam * scale > 1:
			self.dir_x = -abs(self.dir_x) 
		if self.x - 0.1 * self.tam * scale < -1:
			self.dir_x = abs(self.dir_x) 
		if self.y + 0.1 * self.tam * scale > 1:
			self.dir_y = -abs(self.dir_y) 
		if self.y - 0.1 * self.tam * scale < -1:
			self.dir_y = abs(self.dir_y) 

		self.x += (0.5/self.tam)*self.dir_x
		self.y += (0.5/self.tam)*self.dir_y
		self.tam = self.tam_base* (1 + math.cos(self.tam_temp)/10)
		self.tam_temp += 0.1

	#atualiza a coordenada x,y para na próxima atualização, a bola esteja se movendo
	def move_bacteria(self,scale):

		self.dir_x = self.speed * math.sin(self.angle)
		self.dir_y = self.speed * math.cos(self.angle)

		#Movimento reflexivos, se o obejto bate na parede da janela, ele não passa por ela e volta invertendo o sentido de movimento
		if self.x + self.dir_x + 0.1*scale > 1 or self.x + self.dir_x - 0.1*scale < -1:
			self.dir_x = 0
		if self.y + self.dir_y + 0.1 * scale > 1 or self.y + self.dir_y - 0.1*scale < -1:
			self.dir_y = 0

		self.x += self.dir_x
		self.y += self.dir_y



	#verifica se duas bolas colidiram entre si
	def check_colision(self,b,scale):
		dist_2 = (self.x - b.x)**2 + (self.y - b.y)**2
		rads_2 = (0.1*self.tam*scale + 0.1 *b.tam*scale)**2
		return dist_2 < rads_2
	
	#Função que pega a matriz de transformação da bola.
	#É feito as operações de: 
	# 	rotação(a bola girando no próprio eixo)
	#	translação(o movimento da própria bola)
	#	escala(escala/tamanho dos objetos)
	def get_transformation(self):
		c = 1
		s = 0
		if self.cell_type == 'bacteria':
			c = math.cos(self.angle)
			s = math.sin(self.angle)

		mat_rotation = np.array([c, s, 0.0, 0.0,
								 -s, c, 0.0, 0.0,
								 0.0, 0.0, 1.0, 0.0,
								 0.0, 0.0, 0.0, 1.0], np.float32)
		
		mat_scale = np.array([self.tam, 0.0, 0.0, 0.0,
							  0.0, self.tam, 0.0, 0.0,
							  0.0, 0.0, 1.0, 0.0,
							  0.0, 0.0, 0.0, 1.0], np.float32)
		
		mat_translation = np.array([1.0, 0.0, 0.0, self.x,
									0.0, 1.0, 0.0, self.y,
									0.0, 0.0, 1.0, 0.0,
									0.0, 0.0, 0.0, 1.0], np.float32)
		
		mat_transform = multiplica_matriz(mat_translation, mat_scale)
		mat_transform = multiplica_matriz(mat_transform, mat_rotation)
		
		return mat_transform

