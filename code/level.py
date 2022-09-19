import pygame 
from settings import *
from player import Player 
from overlay import Overlay
class Level:
	def __init__(self):

		# get the display surface, so we can draw directly on the main display
		self.display_surface = pygame.display.get_surface()

		# sprite groups ("all sprites" are all characters, objects etc)
		self.all_sprites = pygame.sprite.Group()

		self.setup()
		self.overlay = Overlay(self.player)
	
	def setup(self):
		self.player = Player((640, 360), self.all_sprites)

	def run(self,dt):
		self.display_surface.fill('black')
		self.all_sprites.draw(self.display_surface)
		self.all_sprites.update(dt) # this method calls every update method on childs of the group
		
		self.overlay.display()