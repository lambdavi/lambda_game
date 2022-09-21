import pygame
from support import import_folder 
from settings import *
from player import Player 
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree
from pytmx.util_pygame import load_pygame

class Level:
	def __init__(self):

		# get the display surface, so we can draw directly on the main display
		self.display_surface = pygame.display.get_surface()

		# sprite groups ("all sprites" are all characters, objects etc)
		self.all_sprites = CameraGroup()
		self.collision_sprites = pygame.sprite.Group()
		self.tree_sprites = pygame.sprite.Group()

		self.setup()
		self.overlay = Overlay(self.player)
	
	def setup(self):
		tmx_data = load_pygame("../data/map.tmx")

		# house
		for layer in ['HouseFloor', 'HouseFurnitureBottom']:
			for x,y, surf in tmx_data.get_layer_by_name(layer).tiles():
				Generic((x*TILE_SIZE, y*TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])
		for layer in ['HouseWalls', 'HouseFurnitureTop']:
			for x,y, surf in tmx_data.get_layer_by_name(layer).tiles():
				Generic((x*TILE_SIZE, y*TILE_SIZE), surf, self.all_sprites)

		# fence
		for x,y, surf in tmx_data.get_layer_by_name('Fence').tiles():
			Generic((x*TILE_SIZE, y*TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])

		# water
		water_frames = import_folder("../graphics/water")
		for x,y, surf in tmx_data.get_layer_by_name('Water').tiles():
			Water((x*TILE_SIZE, y*TILE_SIZE), water_frames, self.all_sprites)
		
		# trees
		for obj in tmx_data.get_layer_by_name('Trees'):
			Tree((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites, self.tree_sprites], obj.name)
		
		# wildflowers
		for obj in tmx_data.get_layer_by_name('Decoration'):
			WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])
		
		# Collision tiles
		for x,y, surf in tmx_data.get_layer_by_name('Collision').tiles():
			Generic((x*TILE_SIZE, y*TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)
		
		# Player spawn
		for obj in tmx_data.get_layer_by_name('Player'):
			if obj.name == 'Start':
				self.player = Player(
					pos = (obj.x, obj.y), 
					group = self.all_sprites, 
					collision_sprites = self.collision_sprites,
					tree_sprites = self.tree_sprites)
		
		Generic(
			pos = (0,0),
			surf = pygame.image.load('../graphics/world/ground.png').convert_alpha(),
			groups = self.all_sprites,
			z = LAYERS['ground']
		)

	def run(self,dt):
		self.display_surface.fill('black')
		self.all_sprites.custom_draw(self.player)
		self.all_sprites.update(dt) # this method calls every update method on childs of the group
		
		self.overlay.display()

class CameraGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.offset = pygame.math.Vector2()

	def custom_draw(self, player): # camera mechanism
		self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
		self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2
		for layer in LAYERS.values():
			for sprite in sorted(self.sprites(), key= lambda sprite: sprite.rect.centery):
				if sprite.z == layer:
					offset_rect = sprite.rect.copy()
					offset_rect.center -= self.offset
					self.display_surface.blit(sprite.image, offset_rect)

