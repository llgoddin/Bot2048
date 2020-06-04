# Lucas Goddin
# testing
# Feb 24, 2020

import pygame
import time
import sys

print("PYTHON VER: " + sys.version)
print("PYGAME VER: " + pygame.ver)

pygame.init()
screen = pygame.display.set_mode((600, 800))
screen.fill((255, 0, 0))
pygame.display.flip()

gameRunning = True
screen.fill((255, 0, 0))

while gameRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameRunning = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                print('UP')
                pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(100, 100, 100, 100))
                pygame.display.flip()


    pygame.display.flip()

pygame.quit()
sys.exit()
