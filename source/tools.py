__author__ = 'marble_xu'

import os
import pygame as pg
from abc import ABC, abstractmethod

keybinding = {
    'action':pg.K_s,
    'jump':pg.K_a,
    'left':pg.K_LEFT,
    'right':pg.K_RIGHT,
    'down':pg.K_DOWN
}

class State():
    """
    This class represents a generic game state. A game state is a specific situation or screen 
    in the game (e.g., main menu, level, game over). Different states can handle their own 
    logic, update visuals, and respond to user input.

    Attributes:
        start_time (float): The time the state was entered.
        current_time (float): The current game time.
        done (bool): Flag indicating if the state is finished and needs to be transitioned from.
        next (str or State): The next state to transition to after the current state is finished.
        persist (dict): A dictionary storing persistent data that can be carried across states.
    """

    def __init__(self):
        """
        Initializes the state with default values.
        """

        self.start_time = 0.0
        self.current_time = 0.0
        self.done = False
        self.next = None
        self.persist = {}
    
    @abstractmethod
    def startup(self, current_time, persist):
        """
        This is an abstract method that must be implemented by subclasses. 
        The `startup` method is called when the state is first entered. 
        It is responsible for initializing the state's specific logic and data.

        Args:
            current_time (float): The current game time.
            persist (dict): A dictionary containing persistent data from previous states.
        """

    def cleanup(self):
        """
        This method is called when the state is transitioned from. 
        It can be used to clean up any resources or perform final actions for the state.

        Returns:
            dict: The persistent data that should be carried over to the next state.
        """

        self.done = False
        return self.persist
    
    @abstractmethod
    def update(sefl, surface, keys, current_time):
        """
        This is an abstract method that must be implemented by subclasses. 
        The `update` method is called on every game loop iteration. 
        It is responsible for handling the state's logic, updating visuals on the screen, 
        and responding to user input (keys).

        Args:
            surface (pygame.Surface): The game's surface to draw on.
            keys (list): A list of currently pressed keys.
            current_time (float): The current game time.
        """


class Control():
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.done = False
        self.clock = pg.time.Clock()
        self.fps = 60
        self.current_time = 0.0
        self.keys = pg.key.get_pressed()
        self.state_dict = {}
        self.state_name = None
        self.state = None
    
    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]
    
    def update(self):
        self.current_time = pg.time.get_ticks()
        if self.state.done:
            self.flip_state()
        self.state.update(self.screen, self.keys, self.current_time)
    
    def flip_state(self):
        previous, self.state_name = self.state_name, self.state.next
        persist = self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.current_time, persist)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()
    
    def main(self):
        while not self.done:
            self.event_loop()
            self.update()
            pg.display.update()
            self.clock.tick(self.fps)

def get_image(sheet, x, y, width, height, colorkey, scale):
        image = pg.Surface([width, height])
        rect = image.get_rect()

        image.blit(sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(colorkey)
        image = pg.transform.scale(image,
                                   (int(rect.width*scale),
                                    int(rect.height*scale)))
        return image

def load_all_gfx(directory, colorkey=(255,0,255), accept=('.png', '.jpg', '.bmp', '.gif')):
    graphics = {}
    for pic in os.listdir(directory):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pg.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey(colorkey)
            graphics[name] = img
    return graphics
