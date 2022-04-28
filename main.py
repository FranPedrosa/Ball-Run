'''
Nomes:							Nusi
Bruno Fernandes Moreira  		11218712
Francisco de Freitas Pedrosa  	11215699
Luis Otávio Machado Ferreira	 8988296
Savio Duarte Fontes				10737251
Thales Willian Dalvi da Silva   11219196

Trabalho 1 - SCC0250-2022

Nosso trabalho tem o cenário aonde nosso objetivo é testar o reflexo do usuário.

O usuário controla uma "bactéria" e deve desviar dos "vírus".
Caso ele ache que o jogo está muito díficil ou fácil, ele pode alterar o tamanho dos objetos na janela.

Comandos:
	Setas esquerda e direita controlam a direção do movimento do objeto controlável.
	Seta Cima e Baixo controlam a velocidade do movimento do objeto controlável
	Teclas W e S para alterar a escala dos obejtos do jogo.
'''


#----------------------------------------------------------------#

#Importação dos pacotes
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import math
import time
from numpy import random

#Importando os outros arquivos
import cell
import keys
import colors

#----------------------------------------------------------------#

# Inicializando a Janela
glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
window = glfw.create_window(800, 800, "Transformação Geométrica", None, None)
glfw.make_context_current(window)

#Definição do vertex code
vertex_code = """
		attribute vec2 position;
		uniform mat4 mat;
		void main(){
			gl_Position = mat * vec4(position,0.0,1.0);
		}
		"""

#Definição do Fragment code
fragment_code = """
		uniform vec4 color;
		void main(){
			gl_FragColor = color;
		}
		"""

#Requisitando slot para a GPU para nossos programas Vertex e Fragment Shaders
program = glCreateProgram()
vertex = glCreateShader(GL_VERTEX_SHADER)
fragment = glCreateShader(GL_FRAGMENT_SHADER)

#Associando nosso código-fonte aos slots solicitados
glShaderSource(vertex, vertex_code)
glShaderSource(fragment, fragment_code)

#Compilando o Vertex Shader
glCompileShader(vertex)
if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
	error = glGetShaderInfoLog(vertex).decode()
	print(error)
	raise RuntimeError("Erro de compilacao do Vertex Shader")

#Compilando o Fragment Shader
glCompileShader(fragment)
if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
	error = glGetShaderInfoLog(fragment).decode()
	print(error)
	raise RuntimeError("Erro de compilacao do Fragment Shader")

#Associando os programas compilados aos programas principais
glAttachShader(program, vertex)
glAttachShader(program, fragment)

#Linkagem do programa
glLinkProgram(program)
if not glGetProgramiv(program, GL_LINK_STATUS):
	print(glGetProgramInfoLog(program))
	raise RuntimeError('Linking error')

#Fazendo program o programa padrão
glUseProgram(program)

#----------------------------------------------------------------#

#Criação dos objetos
#Todos os objetos serão colocados no mesmo Buffer, assim, utilizaremos a variável offset para definirmos a posição de cada um no array passado para o Buffer

colisions = 0			#Número de colisões entre a bola controlável e a bolas não controláveis
scale = 1.0				#escala que é aplicada em todos os objetos
all_points = []			#array que armazena todos os pontos de todos os objetos
cells = []				#array que armazena todos os objetos(células - bactéria e vírus) do programa

#Criação da "Célula" (Bactéria) controlável pelo jogador
b1 = cell.Cell(len(all_points),-0.9,-0.9,1,'bacteria')
all_points += b1.points
cells.append(b1)

#Criação das "células" inimigas (vírus) não controláveis pelo jogador, sua posição inicial é escolhida aleatóriamente
for i in range(5):
	x = random.randint(-10,10) / 10
	y = random.randint(-10,10) / 10
	t = random.randint(4,15) / 10
	b = cell.Cell(len(all_points),x,y,t,'virus')
	all_points += b.points
	cells.append(b)

#Preparando o espaço para todos os vértices de todas os objetos
vertices = np.zeros(len(all_points), [("position", np.float32, 2)])

#Passando todos os vértices
vertices['position'] = all_points

#Requesitando um Buffer slot da GPU
buffer = glGenBuffers(1)
#Fazendo esse Buffer o padrão
glBindBuffer(GL_ARRAY_BUFFER, buffer)
#Carregando os dados
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)
glBindBuffer(GL_ARRAY_BUFFER, buffer)
#Definindo o Byte inicial e offset dos dados
stride = vertices.strides[0]
offset = ctypes.c_void_p(0)

#Pegamos a localização da variável position e indicamos a GPU onde está o conteúdo para esta variável
loc = glGetAttribLocation(program, "position")
glEnableVertexAttribArray(loc)
glVertexAttribPointer(loc, 2, GL_FLOAT, False, stride, offset)

#----------------------------------------------------------------#

#Função que pega os eventos do teclado e a partir deles, modifica as variáveis relacionadas as transformações
def key_event(window, key, scancode, action, mods):
	global scale
		
	if action == 1:

		#As setas do teclado definem a direção da Bola Controlável
		if key == keys.up and cells[0].speed < 0.006:
			cells[0].speed += 0.002
		if key == keys.down and cells[0].speed > 0.002:
			cells[0].speed -= 0.002
		if key == keys.left:
			cells[0].angle -= math.pi / 4
		if key == keys.right:
			cells[0].angle += math.pi / 4
		#Teclas W e S definem o aumento ou diminuição da escala dos obejtos
		if key == keys.w:
			scale += 0.1
		if key == keys.s and scale > 0.01:
			scale -= 0.1

#pega os eventos do teclado
glfw.set_key_callback(window, key_event)

#pegamos a localização da variável color (uniform) do Fragment Shader para podermos alterá-la durante nosso laço de janela
loc_color = glGetUniformLocation(program, "color")

#Exibimos a janela
glfw.show_window(window)

#Função para desenhar o objeto na janela de acordo com o offset (vários objetos no mesmo Buffer)
def draw(offset,colors, transf):
	loc1 = glGetUniformLocation(program, "mat")
	glUniformMatrix4fv(loc1, 1, GL_TRUE, transf)
	index = 0
	for c in colors:
		glUniform4f(loc_color, c['r'], c['g'], c['b'], 1.0)
		glDrawArrays(GL_TRIANGLES, offset + 3*index, 3)
		index += 1


#Transformação que faz a operação de escala para aplicar em todos os objetos
def get_global_scale():
	mat_scale = np.array([scale, 0.0, 0.0, 0.0,
		  0.0, scale, 0.0, 0.0,
		  0.0, 0.0, 1.0, 0.0,
		  0.0, 0.0, 0.0, 1.0], np.float32)
	return mat_scale

#----------------------------------------------------------------#

#Loop principal enquanto a janela está aberta
while not glfw.window_should_close(window) and colisions < 100:
	glfw.poll_events()
	glClear(GL_COLOR_BUFFER_BIT)
	glClearColor(0.0, 1.0, 1.0, 1.0)
	

	#Fazendo a transformação para cada bola e desenhando ela
	for b in cells:
		b.move(scale)
		gt = get_global_scale()	
		t = b.get_transformation()
		t = cell.multiplica_matriz(t,gt)
		draw(b.offset,b.colors,t)

	#verifica se está havendo colisão entre a bacteria e os virus
	for b in cells[1:]:
		if b.check_colision(cells[0],scale):
			colisions += 1
	print(colisions)
	time.sleep(0.01)
		
	glfw.swap_buffers(window)
glfw.terminate()
