import pygame
from settings import *
from support import *
from timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites, tree_sprites, interaction):
        super().__init__(group)

        # ! IMPORTANT !
        self.import_assets()
        self.status = 'down_idle' # default_status_surface
        self.frame_index = 0

        # general attributes
        self.image = self.animations[self.status][self.frame_index] # the image is a surface
        self.rect = self.image.get_rect(center=pos)
        self.z = LAYERS['main']
        
        # movement attributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        #collision
        self.hitbox = self.rect.copy().inflate((-126, -70))
        self.collision_sprites = collision_sprites
        
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

        # inventory
        self.item_inventory = {
            'wood':   0,
            'apple':  0,
            'corn':   0,
            'tomato': 0
        }

        # interaction
        self.tree_sprites = tree_sprites
        self.interaction = interaction
        self.sleep = False

    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]
    
    def use_tool(self):
        if self.selected_tool == 'hoe' or self.selected_tool == 'water':
            pass
        
        if self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()

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
        
        if not self.timers['tool use'].active and not self.sleep: # to prevent moving while using tools
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
            
            # INTERACTIONS
            if keys[pygame.K_RETURN]:
                collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction, False)
                if collided_interaction_sprite:
                    if collided_interaction_sprite[0].name == 'Trader':
                        pass
                    else:
                        self.status = 'left_idle'
                        self.sleep = True
               
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
    
    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0: # moving right
                            self.hitbox.right = sprite.hitbox.left # move back to left (the hitbox)
                        if self.direction.x < 0: # moving left
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx # this move also the rect
                        self.pos.x = self.hitbox.centerx
                    else:
                        if self.direction.y > 0: # moving down
                            self.hitbox.bottom = sprite.hitbox.top 
                        if self.direction.y < 0: # moving up
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery # this move also the rect
                        self.pos.y = self.hitbox.centery
    
    def move(self, dt):
        # Normalize (to avoid be faster when going diagonal)
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        
        # horizontal movement
        self.pos.x += self.direction.x*self.speed*dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')
        
        # vertical movement
        self.pos.y += self.direction.y*self.speed*dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    
    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        self.move(dt)
        self.animate(dt)
