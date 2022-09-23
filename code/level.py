import pygame
from support import import_folder 
from settings import *
from player import Player 
from overlay import Overlay
from sprites import Generic, Interaction, Water, WildFlower, Tree, Particle
from pytmx.util_pygame import load_pygame
from transition import Transition
from soil import SoilLayer
from sky import Rain, Sky
from random import randint
from menu import Menu
class Level:
	def __init__(self):
		# get the display surface, so we can draw directly on the main display
		self.display_surface = pygame.display.get_surface()

		# sprite groups ("all sprites" are all characters, objects etc)
		self.all_sprites = CameraGroup()
		self.collision_sprites = pygame.sprite.Group()
		self.tree_sprites = pygame.sprite.Group()
		self.interaction_sprites = pygame.sprite.Group()
		self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)

		self.setup()
		self.overlay = Overlay(self.player)
		self.transition = Transition(self.reset, self.player)

		# sky
		self.rain = Rain(self.all_sprites)
		self.raining = randint(0,10) > 7
		self.soil_layer.raining = self.raining
		self.sky = Sky()

		# shop
		self.shop_active = False
		self.menu=Menu(self.player, self.toggle_shop)

		
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
			Tree(
				pos = (obj.x, obj.y),
				surf = obj.image, 
				groups = [self.all_sprites, self.collision_sprites, self.tree_sprites], 
				name = obj.name,
				player_add = self.player_add)
		
		# wildflowers
		for obj in tmx_data.get_layer_by_name('Decoration'):
			WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])
		
		# Collision tiles
		for x,y, surf in tmx_data.get_layer_by_name('Collision').tiles():
			Generic((x*TILE_SIZE, y*TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)
		
		# Player stuff
		for obj in tmx_data.get_layer_by_name('Player'):
			if obj.name == 'Start':
				self.player = Player(
					pos = (obj.x, obj.y), 
					group = self.all_sprites, 
					collision_sprites = self.collision_sprites,
					tree_sprites = self.tree_sprites,
					interaction = self.interaction_sprites,
					soil_layer = self.soil_layer,
					toggle_shop = self.toggle_shop)
			if obj.name == 'Bed':
				Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)

			if obj.name == 'Trader':
				Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
		
		Generic(
			pos = (0,0),
			surf = pygame.image.load('../graphics/world/ground.png').convert_alpha(),
			groups = self.all_sprites,
			z = LAYERS['ground']
		)

	def plant_collision(self):
		if self.soil_layer.plant_sprites: # if there are plants
			for plant in self.soil_layer.plant_sprites.sprites():
				if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
					self.player_add(plant.plant_type)
					plant.kill()
					Particle(plant.rect.topleft, plant.image, self.all_sprites, z = LAYERS['main'])
					self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')

	def reset(self):

		# plants
		self.soil_layer.update_plants()

		
		# soil
		# remove water
		self.soil_layer.remove_water()
		self.raining = randint(0,10) > 7

		#randomize the rain
		self.soil_layer.raining = self.raining
		if self.raining:
			self.soil_layer.water_all()

		# apples on trees
		for tree in self.tree_sprites.sprites():
			for apple in tree.apple_sprites.sprites():
				apple.kill()
			tree.create_fruit()
		
	def player_add(self, item, qty = 1):
		self.player.item_inventory[item] += qty

	def toggle_shop(self):
		self.shop_active = not self.shop_active


	def run(self,dt):

		# drawing logic
		self.display_surface.fill('black')
		self.all_sprites.custom_draw(self.player)
		
		# updates
		if self.shop_active:
			self.menu.update()
		else:
			self.all_sprites.update(dt) # this method calls every update method on childs of the group
			self.plant_collision()
		
		self.overlay.display()
		
		# weather
		if self.raining and not self.shop_active:
			self.rain.update()
		self.sky.display(dt)

		# transition overlay
		if self.player.sleep:
			self.transition.play()

		# sky
		self.sky.start_color = 	[255, 255, 255]



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


