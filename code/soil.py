import pygame
from settings import *
from pytmx.util_pygame import load_pygame
from support import *

class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil']

class SoilLayer:
    def __init__(self, all_sprites):
        
        # sprite groups
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()

        # graphics
        self.soil_surf = pygame.image.load('../graphics/soil/o.png')
        self.soil_surfs = import_folder_dictionary('../graphics/soil/')
        self.create_soil_grid()
        self.create_hit_rects()
    
    def create_soil_grid(self):
        ground = pygame.image.load('../graphics/world/ground.png')
        # getting the total number of tiles
        h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE

        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        for x, y, _ in load_pygame('../data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F') # Y=ROW, X=COL
        
    def create_hit_rects(self):
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'F' in cell:
                    x = TILE_SIZE * index_col
                    y = TILE_SIZE * index_row
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE
                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()
    
    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell:

                    # tile options
                    t = 'X' in self.grid[index_row -1][index_col]
                    b = 'X' in self.grid[index_row +1][index_col] 
                    r = 'X' in row[index_col +1]
                    l = 'X' in row[index_col-1]

                    tile_type = 'o'

                    # all sides
                    if all((t,r,b,l)): tile_type = 'x'

                    # horizontal tiles only
                    if l and not any((t,r,b)): tile_type = 'r'
                    if l and r and not b and not t: tile_type = 'lr'
                    if r and not any((l,t,b)): tile_type = 'l'
                    
                    # vertical tiles only
                    if t and not any((l,r,b)): tile_type = 'b'
                    if t and b and not l and not r: tile_type = 'tb'
                    if b and not any((l,t,r)): tile_type = 't'

                    # corners
                    if l and b and not t and not r: tile_type = 'tr'
                    if r and b and not t and not l: tile_type = 'tl'
                    if l and t and not b and not r: tile_type = 'br'
                    if r and t and not b and not l: tile_type = 'bl'

                    # t-shapes
                    if all((t,b,r)) and not l: tile_type='tbr'
                    if all((t,b,l)) and not r: tile_type='tbl'
                    if all((l,r,t)) and not b: tile_type='lrb'
                    if all((l,r,b)) and not t: tile_type='lrt'




                    SoilTile(
                        pos = (TILE_SIZE * index_col, TILE_SIZE * index_row),
                        surf = self.soil_surfs[tile_type],
                        groups = [self.all_sprites, self.soil_sprites])

                    

