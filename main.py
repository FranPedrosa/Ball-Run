import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import math
from numpy import random

import ball
import keys
import colors

# %%
glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
window = glfw.create_window(800, 800, "Transformação Geométrica", None, None)
glfw.make_context_current(window)
# %%
vertex_code = """
		attribute vec2 position;
		uniform mat4 mat;
		void main(){
			gl_Position = mat * vec4(position,0.0,1.0);
		}
		"""
fragment_code = """
		uniform vec4 color;
		void main(){
			gl_FragColor = color;
		}
		"""

program = glCreateProgram()
vertex = glCreateShader(GL_VERTEX_SHADER)
fragment = glCreateShader(GL_FRAGMENT_SHADER)
glShaderSource(vertex, vertex_code)
glShaderSource(fragment, fragment_code)
glCompileShader(vertex)
if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
	error = glGetShaderInfoLog(vertex).decode()
	print(error)
	raise RuntimeError("Erro de compilacao do Vertex Shader")
glCompileShader(fragment)
if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
	error = glGetShaderInfoLog(fragment).decode()
	print(error)
	raise RuntimeError("Erro de compilacao do Fragment Shader")
glAttachShader(program, vertex)
glAttachShader(program, fragment)
glLinkProgram(program)
if not glGetProgramiv(program, GL_LINK_STATUS):
	print(glGetProgramInfoLog(program))
	raise RuntimeError('Linking error')

glUseProgram(program)

angle = 0.0
colisions = 0
angle_speed = 0.0
scale = 1.0
all_points = []
balls = []

b1 = ball.Ball(len(all_points),0,0,1,colors.red,colors.blue)
all_points += b1.points
balls.append(b1)

for i in range(5):
	x = random.randint(-10,10) / 10
	y = random.randint(-10,10) / 10
	t = random.randint(2,10) / 10
	b = ball.Ball(len(all_points),x,y,t,colors.yellow,colors.black)
	all_points += b.points
	balls.append(b)

vertices = np.zeros(len(all_points), [("position", np.float32, 2)])
vertices['position'] = all_points
buffer = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, buffer)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)
glBindBuffer(GL_ARRAY_BUFFER, buffer)
stride = vertices.strides[0]
offset = ctypes.c_void_p(0)
loc = glGetAttribLocation(program, "position")
glEnableVertexAttribArray(loc)
glVertexAttribPointer(loc, 2, GL_FLOAT, False, stride, offset)


def key_event(window, key, scancode, action, mods):
	global angle_speed, scale
	if action == 1:
		if key == keys.right:
			balls[0].dir_x = 0.02
			balls[0].dir_y = 0.00
		if key == keys.up:
			balls[0].dir_x = 0.00
			balls[0].dir_y = 0.02
		if key == keys.left:
			balls[0].dir_x = -0.02
			balls[0].dir_y = 0.00
		if key == keys.down:
			balls[0].dir_x = 0.00
			balls[0].dir_y = -0.02
		if key == keys.w:
			scale += 0.1
		if key == keys.s and scale > 0.01:
			scale -= 0.1
		if key == keys.d:
			angle_speed += 0.1
		if key == keys.a:
			angle_speed -= 0.1


glfw.set_key_callback(window, key_event)
loc_color = glGetUniformLocation(program, "color")
glfw.show_window(window)

def draw(offset,colors, transf):
	loc1 = glGetUniformLocation(program, "mat")
	glUniformMatrix4fv(loc1, 1, GL_TRUE, transf)
	index = 0
	for c in colors:
		glUniform4f(loc_color, c['r'], c['g'], c['b'], 1.0)
		glDrawArrays(GL_TRIANGLES, offset + 3*index, 3)
		index += 1


def get_global_transformation(ang,scale):
	c = math.cos(math.radians(angle))
	s = math.sin(math.radians(angle))
	mat_rotation = np.array([c, -s, 0.0, 0.0,
							 s, c, 0.0, 0.0,
							 0.0, 0.0, 1.0, 0.0,
							 0.0, 0.0, 0.0, 1.0], np.float32)
	mat_scale = np.array([scale, 0.0, 0.0, 0.0,
						  0.0, scale, 0.0, 0.0,
						  0.0, 0.0, 1.0, 0.0,
						  0.0, 0.0, 0.0, 1.0], np.float32)
	mat_transform = ball.multiplica_matriz(mat_rotation, mat_scale)
	return mat_transform

while not glfw.window_should_close(window) and colisions < 20:
	glfw.poll_events()
	glClear(GL_COLOR_BUFFER_BIT)
	glClearColor(1.0, 1.0, 1.0, 1.0)
	angle += angle_speed
	
	gt = get_global_transformation(angle,scale) 

	for b in balls:
		b.move(scale)
		t = b.get_transformation(angle)
		t = ball.multiplica_matriz(t,gt)
		draw(b.offset,b.colors,t)

	for b in balls[1:]:
		if b.check_colision(balls[0],scale):
			colisions += 1
	print(colisions)
		
	glfw.swap_buffers(window)
glfw.terminate()
