import random
import pygame
from pygame.locals import *


class FlyingShip:
	def __init__(self):
		self._running = True
		self.over = False
		self.window = None
		self.title = 'Flying Spaceship'
		self.header_size = 50
		self.size = self.width, self.height = 760, 480 + self.header_size
		self.frames_per_sec = 30
		self.bg_image_src = 'images/background.png'
		self.game_images = {}
		self.temp_height = 100

	def on_init(self):
		# Initializing the game
		pygame.init()
		self._running = True
		self.over = False
		self.over_reason = ''
		
		# Creating the window where everything will be displayed
		self.window = pygame.display.set_mode(self.size)
		self.clock = pygame.time.Clock()
		pygame.display.set_caption(self.title)
		self.bg_image = pygame.transform.scale(pygame.image.load(self.bg_image_src).convert_alpha(), (self.width, self.height-self.header_size ))
		
		self.player = Player(self.width, self.height)
		self.pipes = Pipes(self.width, self.height)
		
		self.pipes.get_first_pipes()
		self.on_render()

	
	def on_event(self, event):
		if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
			self._running = False
		
		space_pressed = event.type == KEYDOWN and event.key == K_SPACE
		key_up_pressed = event.type == KEYDOWN and event.key == K_UP
		
		# When any of these 2 keys are pressed, the player will move
		if space_pressed or key_up_pressed:
			if self.player.vertical > 0:
				self.player.velocity_y = self.player.flap_velocity
				self.player.flapped = True
		
		# When space is pressed, the game will restart
		if space_pressed and self.over:
			self.on_init()


	def on_loop(self):
		if self.over:
			return

		player_position = (self.player.get_x_position(), self.player.get_y_position())
		scored, crashed = self.pipes.check_pipe(player_position)
		
		if self.player.fallen:
			self.over_reason = 'You fell'
			self.game_over(self.over_reason)

		if crashed:
			self.over_reason = 'You crashed'
			self.game_over(self.over_reason)
		
		self.player.fly()
		self.pipes.move()

		if scored:
			self.player.score += 1
		
	def on_render(self):
		if self.over:
			self.game_over(self.over_reason)
			return
		
		self.window.blit(self.bg_image, (0, self.header_size))			
		self.window.blit(self.player.image, (self.player.horizontal, self.player.vertical))
		self.pipes.render_pipes(self.window)
		self.render_score()
		
		pygame.display.update()
		self.clock.tick(self.frames_per_sec)

	def on_cleanup(self):
		pygame.quit()

	def on_execute(self):
		if self.on_init() == False:
			self._running = False

		while self._running:
			for event in pygame.event.get():
				self.on_event(event)
			self.on_loop()
			self.on_render()
		self.on_cleanup()		
	
	
	def game_over(self, reason):
		self.over = True

		# Filling the screen white to remove previous content
		self.window.fill((255, 255 , 255))
		font = pygame.font.Font(pygame.font.get_default_font(), 32)
		
		# These will be the messages to be displayed in the game over screen
		game_over_text = font.render('{}, GAME OVER'.format(reason), True, (0,0,0))
		restart_text = font.render('Press SPACE to restart game!', True, (0,0,0))
		
		# This will render the text of the 2 previous variables
		padding = 60
		for index, text in enumerate([game_over_text, restart_text]):
			x_position = (self.width - text.get_width())/2
			y_position = (self.height-self.header_size-text.get_height())/2 + index * padding
			self.window.blit(text, (x_position, y_position))
		pygame.display.update()
	
	def render_score(self):
		# We are drawing first the header area where the score will be shown
		pygame.draw.rect(self.window, color=(255, 255, 255), rect=(0, 0, self.width, self.header_size))
		pygame.draw.lines(self.window, closed=True, color=(0, 0, 0), points=([0, 0], [self.width, 0]), width=4)
		pygame.draw.lines(self.window, closed=True, color=(0, 0, 0), points=([0, self.header_size], [self.width, self.header_size]), width=3)

		# This will display the score in the upper corner of the screen
		font = pygame.font.Font(pygame.font.get_default_font(), 32)
		text = font.render('Score: {}'.format(self.player.score), True, (0,0,0))
		self.window.blit(text, (10,10))

class Player():
	def __init__(self, width, height):
		self.window_width = width
		self.window_height = height
		self.size = 100
		self.velocity_y = -9
		self.max_vel_y = 10
		self.min_vel_y = -8
		self.acc_y = 1
		self.flap_velocity = -8
		self.flapped = False
		self.fallen = False
		self.score = 0
		self.horizontal = int(width/8)
		self.vertical = int(height/2)
		self.elevation = height * 1.2
		self.image_src = 'images/spaceship.png'
		self.image =  pygame.transform.scale(
					  	pygame.transform.rotate(
					  		pygame.image.load(self.image_src).convert_alpha(), 270), (self.size, self.size))
	
	def get_y_position(self):
		return self.vertical + self.image.get_height()/2
	
	def get_x_position(self):
		return self.horizontal + self.image.get_width()/2
	
	def fly(self):
		if self.velocity_y < self.max_vel_y and not self.flapped:
			self.velocity_y += self.acc_y
		
		if self.flapped:
			self.flapped = False
		
		self.vertical += min(
			self.velocity_y, 
			self.elevation - self.vertical - self.size)

		if self.get_y_position() > self.window_height:
			self.fallen = True

class Pipes():
	def __init__(self, width, height):
		self.window_width = width
		self.window_height = height
		self.pipes_list = []
		self.pipe_vel_x = -4
		self.scored = False
		self.crashed = False
		self.horizontal = self.window_width/3
		self.image_src = 'images/pipe.png'
		self.image_up = pygame.image.load(self.image_src).convert_alpha()
		self.image_down = pygame.transform.rotate(pygame.image.load(self.image_src).convert_alpha(), 180)
	
	def move(self):
		for pipe in self.pipes_list:
			pipe[0]['x'] += self.pipe_vel_x
			pipe[1]['x'] += self.pipe_vel_x
	
	def check_pipe(self, player_position):
		self.scored = False
		
		pipe_width = self.get_width()
		pipe_height = self.get_height()
		for pipe in self.pipes_list:
			pipe_x_pos = pipe[0]['x'] + pipe_width / 2
			pipe_up_y_range = [pipe[0]['y'], pipe[0]['y']+pipe_height]
			pipe_down_y_range = [pipe[1]['y'], pipe[1]['y']+pipe_height]

			# Creating variables to compare the player position with the pipes position
			same_x_position = pipe_x_pos <= player_position[0] < pipe_x_pos + 4
			same_y_position_up = pipe_up_y_range[0] < player_position[1] < pipe_up_y_range[1]
			same_y_position_down = pipe_down_y_range[0] < player_position[1] < pipe_down_y_range[1]
			
			# When the pipe is crossing the border of the screen, this will add a new pipe
			if 0 < pipe_x_pos < pipe_width:
				self.create_pipe()

			# When the pipe is out of the screen, we remove it from the pipe list
			if pipe_x_pos < pipe_width:
				self.pipes_list.pop(0)
				self.horizontal -= 250
			
			if (same_y_position_up or same_y_position_down) and same_x_position:
				self.crashed = True
			elif same_x_position:
				self.scored = True

		return (self.scored, self.crashed)
	
	def render_pipes(self, window):
		# This will display in the screen all the pipes in the pipe list
		for pipe in self.pipes_list:
			window.blit(self.image_up, (pipe[1]['x'], pipe[1]['y']))
			window.blit(self.image_down, (pipe[0]['x'], pipe[0]['y']))

	def get_first_pipes(self):
		[self.create_pipe() for i in range(3)]
	
	def create_pipe(self):
		offset = self.window_height/3
	
		y_down = offset + random.randrange(100, self.window_height - 1.5 * offset)
		pipeX = self.horizontal
		y_up = self.get_height() - y_down + offset

		pipe = [{'x': pipeX, 'y': -y_up}, {'x': pipeX, 'y': y_down}]
		self.horizontal += 250
		
		self.pipes_list.append(pipe)
	
	def get_x_position(self):
		return self.horizontal + self.image_up.get_width()/2

	def get_width(self):
		return self.image_up.get_width()

	def get_height(self):
		return self.image_up.get_height()
	
	

if __name__ == '__main__':
	app = FlyingShip()
	app.on_execute()
