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
BLACK = (0,0,0)
WOOD = (193,154,107)




class App:
    def __init__(self,s=None, me='', peer='',color=BLUE, peer_color=BLUE):
        self._running = True
        self.screen = None
        self.size = self.weight, self.height = 825, 825
        #---------
        self.s = s
        self.me = me
        self.peer = peer
        
        self.lock = threading.Lock()

        self.receive_thread = threading.Thread(target=self.get_msg)
        self.receive_thread.daemon = True
        
        self.looping_thread = threading.Thread(target=self.running)
        self.looping_thread.daemon = True
        #---------------
        self.POS_moving = False
        self.position = (0,0)
        # self.clock = pygame.time.Clock()
        self.color = color
        self.peer_color = peer_color
        self.peer_pos = False
        self.start =False
        if self.color == BLACK:
            self.my_turn = True
        else:
            self.my_turn = False
        self.all_chess={BLACK: [], WHITE: [], 'rest': []}
        for x in range(0,15):
            for y in range(0,15):
                self.all_chess['rest'].append((x,y))

         
    def on_init(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.screen.fill(WOOD)
        self._running = True
        #draw the board
        for i in range(0,15):
            pygame.draw.line(self.screen, BLACK, (0,i*55+27), (825,i*55+27), 1)
        for i in range(0,15):
            pygame.draw.line(self.screen, BLACK, (i*55+27,0), (i*55+27,825), 1)
        pygame.display.flip()

        fontObj = pygame.font.Font('comicbd.ttf', 48)

        self.win = fontObj.render('You Win!', True, RED)
        self.lose = fontObj.render('You Lose!', True, RED)

        self.win_rect = self.win.get_rect()
        self.lose_rect = self.lose.get_rect()

        self.win_rect.center = (412, 412)
        self.lose_rect.center = (412, 412)


    def on_event(self, event):
        if event.type == pygame.QUIT:
            #--------
            mysend(self.s, json.dumps({"action":"quit_game"}))
            #--------
            self._running = False

        elif event.type == pygame.KEYDOWN:
            #press q to quit
            if event.key == pygame.K_q:
                #--------
                mysend(self.s, json.dumps({"action":"quit_game"}))
                #--------
                self._running = False
        
        #mouse down

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.POS_moving = True

        #mouse up
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.POS_moving = False
            

    def get_msg(self):
        # self.lock.acquire()
        try:
            while self.running:
                peer_msg = myrecv(self.s)
                #if peer_msg != msg:
                #    peer_msg = msg
                if len(peer_msg) > 0:
                    peer_msg = json.loads(peer_msg)
                    if peer_msg["action"] == "quit_game":
                        self._running = False
                    elif peer_msg["action"] == "new_pos":
                        self.start = True
                        self.peer_pos = True
                        self.position = peer_msg["position"]
                        self.my_turn = True
        except:
            print("not Recieving!")
        # finally:
        #     self.lock.release()
    def on_loop(self):
        if self.POS_moving:
            self.position = pygame.mouse.get_pos()
            self.peer_pos = False
            self.start =True
            mysend(self.s, json.dumps({"action":"new_pos", "position":self.position}))
    
    def on_render(self, color=WOOD):
        x, y = self.position
        x = x//55
        y = y//55
        if x == 15:
            x = 14
        if y == 15:
            y = 14
        pygame.draw.circle(self.screen, color, (x*55+27, y*55+27), 22, 0)
        pygame.display.flip()
        if (x,y) in self.all_chess['rest']:
            self.all_chess[color].append((x,y))
            self.all_chess['rest'].remove((x,y))
        # self.clock.tick(60)

    def on_cleanup(self):
        # self.looping_thread.join(5)
        # self.receive_thread.join(5)
        pygame.quit()

 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        # start two seperate thread, one for recieving message, one for game loop

        self.receive_thread.start()
        self.looping_thread.start()

        self.running()

        self.on_cleanup()

    def running(self):
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            if self.my_turn:
                self.on_loop()
                if self.start:
                    if self.peer_pos:
                        self.on_render(self.peer_color)
                    else:
                        self.on_render(self.color)
                        self.my_turn = False
            else:
                if self.start:
                    if self.peer_pos:
                        self.on_render(self.peer_color)
                    else:
                        self.on_render(self.color)
                    
            self.detect_win()
            
        
    def detect_win(self):
        for chess in self.all_chess[self.color]:
            if self.detect_horizontal(chess, self.color) or self.detect_vertical(chess, self.color) or \
               self.detect_diagonal(chess, self.color):
                self.screen.blit(self.win, self.win_rect)
                pygame.display.update()
                return
        for chess in self.all_chess[self.peer_color]:
            if self.detect_horizontal(chess, self.peer_color) or self.detect_vertical(chess, self.peer_color) or \
               self.detect_diagonal(chess, self.peer_color):
                self.screen.blit(self.lose, self.lose_rect)
                pygame.display.update()
                return
    
    def detect_horizontal(self, chess, color, times = 1):
        if times == 5:
            return True
        next_chess = (chess[0]+1,chess[1])
        if next_chess in self.all_chess[color]:
            return True and self.detect_horizontal(next_chess, color, times+1)
                
    def detect_vertical(self, chess, color, times = 1):
        if times == 5:
            return True
        next_chess = (chess[0],chess[1]+1)
        if next_chess in self.all_chess[color]:
            return True and self.detect_vertical(next_chess, color, times+1)
                
    def detect_diagonal(self, chess, color, times = 1):
        if times == 5:
            return True
        next_chess = (chess[0]+1,chess[1]+1)
        if next_chess in self.all_chess[color]:
            return True and self.detect_diagonal(next_chess, color, times+1)
                

'''
if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()
'''
