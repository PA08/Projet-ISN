import pygame
from pygame.locals import *
from game import *
from graphics import background, icon, size

pygame.init()

game = Game(size, "Cave Battle", icon, background)

game.start()
