import pygame
from settings import *
from support import *
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)

        # ! IMPORTANT !
        self.import_assets()
        self.status = 'down_idle' # default_status_surface
        self.frame_index = 0
        
        # the image has to be some kind of surface
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
    
        # movement attributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

    def import_assets(self):
        self.animations = {'up': [],'down': [],'left': [],'right': [], 
                           'right_idle':[],'left_idle':[],'up_idle' :[],'down_idle':[],
                           'right_hoe':[], 'left_hoe' : [],'up_hoe' : [],'down_hoe':[],
                           'right_axe':[], 'left_axe': [],'up_axe' : [],'down_axe':[],
                           'right_water':[],'left_water':[],'up_water':[],'down_water':[]}
        for animation in self.animations.keys():
            full_path = '../graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)

        print(self.animations)


    def input(self):
        keys = pygame.key.get_pressed() # returns the list of pressed keys 
        
        # Vertical Movement
        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        # Horizontal Movement
        if keys[pygame.K_LEFT]:
            self.direction.x = -1
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
        else:
            self.direction.x=0

    def move(self, dt):
        # Normalize (to avoid be faster when going diagonal)
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        
        # horizontal movement
        self.pos.x += self.direction.x*self.speed*dt
        self.rect.centerx = self.pos.x
        
        # vertical movement
        self.pos.y += self.direction.y*self.speed*dt
        self.rect.centery = self.pos.y
        
    def update(self, dt):
        self.input()
        self.move(dt)
