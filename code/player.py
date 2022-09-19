from json import tool
import pygame
from settings import *
from support import *
from timer import Timer

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

        # timers
        self.timers = {
            'tool use': Timer(350, self.use_tool),
            'tool switch': Timer(200),
            'seed use': Timer(350, self.use_seed),
            'seed switch': Timer(200)
        }

        # tools 
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        # seeds
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]


    def use_tool(self):
        pass

    def use_seed(self):
        pass

    def import_assets(self):
        self.animations = {'up': [],'down': [],'left': [],'right': [], 
                           'right_idle':[],'left_idle':[],'up_idle' :[],'down_idle':[],
                           'right_hoe':[], 'left_hoe' : [],'up_hoe' : [],'down_hoe':[],
                           'right_axe':[], 'left_axe': [],'up_axe' : [],'down_axe':[],
                           'right_water':[],'left_water':[],'up_water':[],'down_water':[]}
        for animation in self.animations.keys():
            full_path = '../graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
        # This iterate images in folder to animate the status
        self.frame_index += 4*dt 

        # If we finish the images we re-iterate from zero
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        
        self.image = self.animations[self.status][int(self.frame_index)]
    
    def input(self):
        keys = pygame.key.get_pressed() # returns the list of pressed keys 
        
        if not self.timers['tool use'].active: # to prevent moving while using tools
            # DIRECTIONS
            # Vertical Movement
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status='up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status='down'
            else:
                self.direction.y = 0

            # Horizontal Movement
            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status='left'
            elif keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status='right'
            else:
                self.direction.x=0

            # TOOL USE
            if keys[pygame.K_SPACE]:
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2() # to stop the player (previously moving) while using 
                self.frame_index = 0
            
            # CHANGE TOOL
            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                self.tool_index += 1
                self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
                self.selected_tool = self.tools[self.tool_index]

            # SEED USE
            if keys[pygame.K_LCTRL]:
                self.timers['seed use'].activate()
                self.direction = pygame.math.Vector2() # to stop the player (previously moving) while using 
                self.frame_index = 0
            
            # CHANGE SEED
            if keys[pygame.K_e] and not self.timers['seed switch'].active:
                self.timers['seed switch'].activate()
                self.seed_index += 1
                self.seed_index = self.seed_index if self.seed_index < len(self.seeds) else 0
                self.selected_seed = self.seeds[self.seed_index]
                
    def get_status(self):
        # IDLE MANAGEMENT
        # If the player is not moving -> add_idle to status
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle' # to prevent: down_idle_idle_...

        # TOOL USE MANAGEMENT (AXE, ECC)
        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool
    
    def update_timers(self): # this prevents infinite loop of timers
        for timer in self.timers.values():
            timer.update()
    
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
        self.get_status()
        self.update_timers()
        self.move(dt)
        self.animate(dt)
