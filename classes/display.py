


import pygame
from pygame.locals import *

class Display:
    def __init__(self):
        pygame.init()
        self.__defWindowSize=[800,600]
        self.__margins=[30,30]

        self.__screen=pygame.display.set_mode(self.__defWindowSize,flags=(pygame.NOFRAME | pygame.RESIZABLE),vsync=1)
        self.__pygameEvents=[]

        
    def getEvents(self):
        return self.__pygameEvents

    def tick(self,texts,boldFirst:bool=False):
        self.__pygameEvents=pygame.event.get()
        for e in self.__pygameEvents:
            if e.type == QUIT:
                return False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return False

        self.__drawScreen(texts,boldFirst)
        pygame.display.update()
        return True

    
    def __drawScreen(self,text,boldFirst:bool=False):
        self.__screen.fill((40,40,40))

        font = pygame.font.Font(None, 30)
        font_bold = pygame.font.Font(None, 30)
        font_bold.set_bold(True)

        line_height = font.get_linesize()

        screen_width, screen_height = self.__screen.get_size()

        # Start at the bottom of the screen
        y = screen_height - line_height

        alphas=[]
        if isinstance(text,dict):
            alphas=list(text.items())
            text=list(text.keys())
        else:
            for i in text:
                alphas.append(1.0)
        
        for i in range(len(text)):
            line=text[i]
            if y < 0:
                break

            if i==1 and boldFirst:
                rendered_text = font_bold.render(str(line), True, (255, 255, 255))
            else:
                rendered_text = font.render(str(line), True, (255, 255, 255))

            # Set transparency (0 = invisible, 255 = fully visible)
            rendered_text.set_alpha(int(min(1.0,alphas[i]) * 255))

            # Draw from the left edge
            self.__screen.blit(rendered_text, (self.__margins[0], y-self.__margins[0]))

            # Move upwards
            y -= line_height