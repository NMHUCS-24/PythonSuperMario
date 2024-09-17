__author__ = 'marble_xu'

"""
This module defines the `Menu` class, which represents the main menu screen in the game. 
The main menu allows players to select their character (Mario or Luigi) and start a new game.
"""

import pygame as pg
from .. import tools
from .. import setup
from .. import constants as c
from .. components import info

class Menu(tools.State):
    """
    Represents the main menu screen.

    Attributes:
        game_info (dict): A dictionary storing game information.
        overhead_info (Info): An `Info` object for displaying game information.
        background (pygame.Surface): The background image for the main menu.
        background_rect (pygame.Rect): The rectangle representing the background image's dimensions.
        viewport (pygame.Rect): The visible area of the game screen.
        image_dict (dict): A dictionary storing images used in the main menu.
        player_list (list): A list of player images.
        player_index (int): The current index of the selected player.
        cursor (pygame.sprite.Sprite): The cursor sprite.
    """
    def __init__(self):
        tools.State.__init__(self)
        persist = {c.COIN_TOTAL: 0,
                   c.SCORE: 0,
                   c.LIVES: 3,
                   c.TOP_SCORE: 0,
                   c.CURRENT_TIME: 0.0,
                   c.LEVEL_NUM: 1,
                   c.PLAYER_NAME: c.PLAYER_MARIO}
        self.startup(0.0, persist)
    
    def startup(self, current_time, persist):
        """
        Initializes the main menu.

        Args:
            current_time (float): The current game time.
            persist (dict): A dictionary containing persistent game data.
        """
        self.next = c.LOAD_SCREEN
        self.persist = persist
        self.game_info = persist
        self.overhead_info = info.Info(self.game_info, c.MAIN_MENU)

        self.setup_background()
        self.setup_player()
        self.setup_cursor()

        self.timer_start = current_time
        
    def setup_background(self):
        """Loads and scales the background image."""

        self.background = setup.GFX['level_1']
        self.background_rect = self.background.get_rect()
        self.background = pg.transform.scale(self.background,
                                    (int(self.background_rect.width*c.BACKGROUND_MULTIPLER),
                                    int(self.background_rect.height*c.BACKGROUND_MULTIPLER)))

        self.viewport = setup.SCREEN.get_rect(bottom=setup.SCREEN_RECT.bottom)
        self.image_dict = {}
        image = tools.get_image(setup.GFX['title_screen'], 1, 60, 176, 88,
                            (255, 0, 220), c.SIZE_MULTIPLIER)
        rect = image.get_rect()
        rect.x, rect.y = (170, 100)
        self.image_dict['GAME_NAME_BOX'] = (image, rect)

    def setup_player(self):
        """Sets up the player images and initial selection."""

        self.player_list = []
        player_rect_info = [(178, 32, 12, 16), (178, 128, 12, 16)]
        for rect in player_rect_info:
            image = tools.get_image(setup.GFX['mario_bros'],
                                *rect, c.BLACK, 2.9)
            rect = image.get_rect()
            rect.x, rect.bottom = 110, c.GROUND_HEIGHT
            self.player_list.append((image, rect))
        self.player_index = 0

    def setup_cursor(self):
        """Creates the cursor sprite and positions it."""

        self.cursor = pg.sprite.Sprite()
        self.cursor.image = tools.get_image(setup.GFX[c.ITEM_SHEET], 24, 160, 8, 8, c.BLACK, 3)
        rect = self.cursor.image.get_rect()
        rect.x, rect.y = (220, 358)
        self.cursor.rect = rect
        self.cursor.state = c.PLAYER1

    def update(self, surface, keys, current_time):
        """Updates the main menu.

        Args:
            surface (pygame.Surface): The game's surface.
            keys (list): A list of pressed keys.
            current_time (float): The current game time.
        """

        self.current_time = current_time
        self.game_info[c.CURRENT_TIME] = self.current_time
        self.player_image = self.player_list[self.player_index][0]
        self.player_rect = self.player_list[self.player_index][1]
        self.update_cursor(keys)
        self.overhead_info.update(self.game_info)

        surface.blit(self.background, self.viewport, self.viewport)
        surface.blit(self.image_dict['GAME_NAME_BOX'][0],
                     self.image_dict['GAME_NAME_BOX'][1])
        surface.blit(self.player_image, self.player_rect)
        surface.blit(self.cursor.image, self.cursor.rect)
        self.overhead_info.draw(surface)

        elapsed_time = current_time - self.timer_start
        if elapsed_time >= 1000:
            self.done = True
            self.next = c.LOAD_SCREEN

    def update_cursor(self, keys):
        """Updates the cursor position based on user input.

        Args:
            keys (list): A list of pressed keys.
        """

        if self.cursor.state == c.PLAYER1:
            self.cursor.rect.y = 358
            if keys[pg.K_DOWN]:
                self.cursor.state = c.PLAYER2
                self.player_index = 1
                self.game_info[c.PLAYER_NAME] = c.PLAYER_LUIGI
        elif self.cursor.state == c.PLAYER2:
            self.cursor.rect.y = 403
            if keys[pg.K_UP]:
                self.cursor.state = c.PLAYER1
                self.player_index = 0
                self.game_info[c.PLAYER_NAME] = c.PLAYER_MARIO
        if keys[pg.K_RETURN]:
            self.reset_game_info()
            self.done = True
    
    def reset_game_info(self):
        """Resets the game information to default values."""

        self.game_info[c.COIN_TOTAL] = 0
        self.game_info[c.SCORE] = 0
        self.game_info[c.LIVES] = 3
        self.game_info[c.CURRENT_TIME] = 0.0
        self.game_info[c.LEVEL_NUM] = 1
        
        self.persist = self.game_info
