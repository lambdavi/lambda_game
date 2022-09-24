import os
import pygame
def import_folder(path):
    surface_list = [] # we are going to store all the surfaces (we are gonna return it)
    for _, _, img_files in os.walk(path):
        for image in img_files:
            image_surf = pygame.image.load(os.path.join(path, image)).convert_alpha()
            surface_list.append(image_surf)
    return surface_list

def import_folder_dictionary(path):
    surface_dict = {}
    for _, _, img_files in os.walk(path):
        for file in img_files:
            full_path = path + '/' + file
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_dict[file.split('.')[0]] = image_surf
    
    return surface_dict