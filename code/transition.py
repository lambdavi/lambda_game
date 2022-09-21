import pygame
from settings import *

class Transition:
    def __init__(self, reset, player):
        
        # setup
        self.display_surface = pygame.display.get_surface()
        self.reset = reset
        self.player = player

        # overlay image
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color = 255
        self.speed = -2

    def play(self):
        # 1. call reset
		# 2. wake up the player
		# 3. set the speed to -2 at the end of the transition
		
        self.color += self.speed
        if self.color <= 0:
            self.color = 0
            self.speed *= -1
            self.reset()
        if self.color > 255:
            self.color = 255
            self.player.status = 'right_idle'
            self.player.sleep = False
            self.speed = -2
        self.image.fill((self.color, self.color, self.color))
        self.display_surface.blit(self.image, (0,0), special_flags = pygame.BLEND_RGB_MULT)

        
