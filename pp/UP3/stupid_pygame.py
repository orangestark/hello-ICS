import pygame
from pygame.locals import *
import sys
import json
import threading
from chat_utils import *

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREY = (92, 92, 92)




class App:
    def __init__(self,s=None, me='', peer=''):
        self._running = False
        self.screen = None
        self.size = self.weight, self.height = 640, 400

        self.POS_moving = False
        self.position = (0,0)
        self.clock = pygame.time.Clock()

 
    def on_init(self):
        print("initializing..")
        pygame.init()
        self.screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.screen.fill(GREY)
        self._running = True
 
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

        elif event.type == pygame.KEYDOWN:
            #press q to quit
            if event.key == pygame.K_q:
                self._running = False
        
        #mouse down
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.POS_moving = True
        #mouse up
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.POS_moving = False
        
    
    def on_loop(self):
        if self.POS_moving:
            self.position = pygame.mouse.get_pos()
    
    def on_render(self):
        pygame.draw.circle(self.screen, GREEN, self.position, 25, 1)
        pygame.draw.circle(self.screen, BLUE, self.position, 75, 1)
        pygame.draw.circle(self.screen, RED, self.position, 125, 1)

    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)

            self.on_loop()
            self.on_render()
            pygame.display.flip()
        self.on_cleanup()

 
if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()

