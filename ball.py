import math
import numpy as np

PI = 3.141592

#Devolve as coordenadas de um ponto em um círuculo, centrado na origem, de raio radius e ângulo theta
def circle_cord(theta, radius):
	x = radius*math.cos(theta)
	y = radius*math.sin(theta)
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
def circle_points(radius, triangle_count):
	angle = (2*PI)/triangle_count

	points = []
	for i in range(0, triangle_count):
		theta = angle*i
		theta_n = 0
		if i+1 == triangle_count:
			theta_n = 2*PI
		else:
			theta_n = (i+1)*angle

		vertex0 = circle_cord(theta, radius)
		vertex1 = circle_cord(theta_n, radius)
		points.append((0,0))
		points.append(vertex0)
		points.append(vertex1)

	return points

#class Ball, classe que cria um objeto em formato de círculo e tem suas funções relacionadas
class Ball:

	#criação do objeto círculo.
	def __init__(self,offset, x, y, tam, color_a, color_b):
		self.x = x 
		self.y = y 
		self.tam = tam
		self.dir_x = 0.02
		self.dir_y = 0.01
		self.points = circle_points(0.1,20)
		self.colors = [ color_a if i % 4 < 2  else color_b for i in range(20)] 
		self.offset = offset

	#atualiza a coordenada x,y para na próxima atualização, a bola esteja se movendo
	def move(self,scale):
		self.x += (0.5/self.tam)*self.dir_x
		self.y += (0.5/self.tam)*self.dir_y

		#Movimento reflexivos, se o obejto bate na parede da janela, ele não passa por ela e volta invertendo o sentido de movimento
		if self.x + 0.1 * self.tam * scale > 1:
			self.dir_x = -abs(self.dir_x) 
		if self.x - 0.1 * self.tam * scale < -1:
			self.dir_x = abs(self.dir_x) 
		if self.y + 0.1 * self.tam * scale > 1:
			self.dir_y = -abs(self.dir_y) 
		if self.y - 0.1 * self.tam * scale < -1:
			self.dir_y = abs(self.dir_y) 

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
	def get_transformation(self,angulo):
		c = math.cos(math.radians(angulo))
		s = math.sin(math.radians(angulo))
		
		mat_rotation = np.array([c, -s, 0.0, 0.0,
								 s, c, 0.0, 0.0,
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
		
		mat_transform = multiplica_matriz(mat_translation, mat_rotation)
		mat_transform = multiplica_matriz(mat_transform, mat_scale)
		
		return mat_transform