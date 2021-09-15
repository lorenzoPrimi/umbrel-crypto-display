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
    ball_rect: Optional[RectType] = None

    def init(self):
        super(Script, self).init()
        self.ball = pygame.image.load("images/intro_ball.gif")
        self.ball_rect = self.ball.get_rect()

    def step(self):
        self.ball_rect = self.ball_rect.move(*self.speed)
        if self.ball_rect.left < 0 or self.ball_rect.right > self.size[0]:
            self.speed[0] = -self.speed[0]
        if self.ball_rect.top < 0 or self.ball_rect.bottom > self.size[1]:
            self.speed[1] = -self.speed[1]

        self.screen.fill(self.red)
        self.screen.blit(self.ball, self.ball_rect)
