from typing import Optional

import pygame
from pygame import Surface
from pygame.rect import RectType

try:
    from libs import *
except ImportError as e:
    from ..libs import *


class Script(iPygameScript):
    speed = [2, 2]
    black = 0, 0, 0
    white = 255, 255, 255
    red = 255, 0, 0
    mult = 3
    ball: Optional[Surface] = None
    ballrect: Optional[RectType] = None

    def init(self):
        super(Script, self).init()
        self.ball = pygame.image.load("images/intro_ball.gif")
        self.ballrect = self.ball.get_rect()

    def step(self):
        self.ballrect = self.ballrect.move(*self.speed)
        if self.ballrect.left < 0 or self.ballrect.right > self.size[0]:
            self.speed[0] = -self.speed[0]
        if self.ballrect.top < 0 or self.ballrect.bottom > self.size[1]:
            self.speed[1] = -self.speed[1]

        self.screen.fill(self.red)
        self.screen.blit(self.ball, self.ballrect)
