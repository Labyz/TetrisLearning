import pygame
import numpy as np
from tetrisgame import TetrisApp
from pygame.constants import K_UP, K_LEFT, K_RIGHT, K_SPACE, K_DOWN

class Random_agent():
    def __init__(self):
        self.game = TetrisApp()
    def start(self):
        while self.game.perdu != True:
            self.game.run(1)
            pygame.event.post(self.on_event_get(0))
    def on_event_get(self, _, *args, **kwargs):
        keys = [K_LEFT, K_RIGHT, K_SPACE, K_UP]
        i = np.random.randint(0, 4)
        event = pygame.event.Event(pygame.KEYDOWN, {"key" : keys[i]})
        return (event)

player = Random_agent()
player.start()
