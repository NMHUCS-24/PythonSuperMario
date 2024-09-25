__author__ = 'marble_xu'

import math
import pygame as pg
from .. import setup, tools  # Importing setup and utility tools from parent modules
from .. import constants as c  # Importing constants for enemy configurations

ENEMY_SPEED = 1  # Defining the base speed for all enemies

def draw_spawn_box(surface, x, y, size=20, color=(255, 0, 0)):
    # Draw a box or cross at the spawn location for visual debugging
    pygame.draw.rect(surface, color, (x - size//2, y - size//2, size, size), 2)  # Draw box

# Function to create and initialize an enemy based on item data and the level context
def create_enemy(item, level, surface):
    # Determine the direction of the enemy (left or right)
    dir = c.LEFT if item['direction'] == 0 else c.RIGHT
    color = item[c.COLOR]  # Get the color of the enemy from the item dictionary
    
    # Check if the enemy has a movement range defined
    if c.ENEMY_RANGE in item:
        in_range = item[c.ENEMY_RANGE]
        range_start = item['range_start']
        range_end = item['range_end']
    else:
        in_range = False
        range_start = range_end = 0

    # Instantiate the correct enemy type based on the 'type' key in the item dictionary
    if item['type'] == c.ENEMY_TYPE_GOOMBA:
        sprite = Goomba(item['x'], item['y'], dir, color, in_range, range_start, range_end)
    elif item['type'] == c.ENEMY_TYPE_KOOPA:
        sprite = Koopa(item['x'], item['y'], dir, color, in_range, range_start, range_end)
    elif item['type'] == c.ENEMY_TYPE_FLY_KOOPA:
        isVertical = False if item['is_vertical'] == 0 else True
        sprite = FlyKoopa(item['x'], item['y'], dir, color, in_range, range_start, range_end, isVertical)
    elif item['type'] == c.ENEMY_TYPE_PIRANHA:
        sprite = Piranha(item['x'], item['y'], dir, color, in_range, range_start, range_end)
    elif item['type'] == c.ENEMY_TYPE_FIRE_KOOPA:
        sprite = FireKoopa(item['x'], item['y'], dir, color, in_range, range_start, range_end, level)
    elif item['type'] == c.ENEMY_TYPE_FIRESTICK:
        sprite = []
        num = item['num']  # Number of fireballs in the firestick
        center_x, center_y = item['x'], item['y']  # Central point of rotation
        for i in range(num):
            radius = i * 21
            sprite.append(FireStick(center_x, center_y, dir, color, radius))
    
    # Visualize the spawn point
    draw_spawn_box(surface, item['x'], item['y'])

    return sprite

# Base class for all enemy types, inheriting from pygame's Sprite class
class Enemy(pg.sprite.Sprite):
    def __init__(self):
        # Initialize the pygame sprite
        pg.sprite.Sprite.__init__(self)
    
    # General setup function for initializing the enemy's position, appearance, and state
    def setup_enemy(self, x, y, direction, name, sheet, frame_rect_list,
                    in_range, range_start, range_end, isVertical=False):
        self.frames = []  # List of frames for enemy animation
        self.frame_index = 0  # Current frame index for animation
        self.animate_timer = 0  # Timer to control animation speed
        self.gravity = 1.5  # Gravity effect on enemy
        self.state = c.WALK  # Initial state is walking
        
        # Set enemy attributes
        self.name = name
        self.direction = direction
        self.load_frames(sheet, frame_rect_list)  # Load animation frames from sprite sheet
        self.image = self.frames[self.frame_index]  # Set initial frame as image
        self.rect = self.image.get_rect()  # Get rectangle for positioning
        self.rect.x = x  # Set x position of the enemy
        self.rect.bottom = y  # Set y position (bottom of the enemy)
        self.in_range = in_range  # Whether the enemy is restricted to a movement range
        self.range_start = range_start  # Start of movement range
        self.range_end = range_end  # End of movement range
        self.isVertical = isVertical  # If the enemy moves vertically
        self.set_velocity()  # Set initial velocity based on movement type
        self.death_timer = 0  # Timer for death-related events
    
    # Load animation frames from a sprite sheet, using coordinates and size multipliers
    def load_frames(self, sheet, frame_rect_list):
        for frame_rect in frame_rect_list:
            # Extract and append frames from the sprite sheet using utility function
            self.frames.append(tools.get_image(sheet, *frame_rect, 
                                               c.BLACK, c.SIZE_MULTIPLIER))

    # Set the velocity of the enemy, either vertical or horizontal depending on its type
    def set_velocity(self):
        if self.isVertical:
            # Vertical movement (e.g., for flying Koopa)
            self.x_vel = 0  # No horizontal movement
            self.y_vel = ENEMY_SPEED  # Vertical speed
        else:
            # Horizontal movement
            self.x_vel = ENEMY_SPEED * -1 if self.direction == c.LEFT else ENEMY_SPEED
            self.y_vel = 0  # No vertical movement
    
    # Update the enemy's position and behavior every frame
    def update(self, game_info, level):
        self.current_time = game_info[c.CURRENT_TIME]  # Get current game time
        self.handle_state()  # Manage the enemy's current state (walking, jumping, etc.)
        self.animation()  # Update animation based on state and timer
        self.update_position(level)  # Update enemy's position based on velocity

    # Handle the enemy's behavior based on its state
    def handle_state(self):
        if self.state == c.WALK or self.state == c.FLY:
            # Handle walking or flying behavior
            self.walking()
        elif self.state == c.FALL:
            # Handle falling behavior (e.g., after being knocked off a platform)
            self.falling()
        elif self.state == c.JUMPED_ON:
            # Handle behavior when the enemy is jumped on by the player
            self.jumped_on()
        elif self.state == c.DEATH_JUMP:
            # Handle the death jump animation (e.g., after being defeated)
            self.death_jumping()
        elif self.state == c.SHELL_SLIDE:
            # Handle Koopa shell sliding behavior
            self.shell_sliding()
        elif self.state == c.REVEAL:
            # Handle reveal animation or behavior (e.g., for hidden enemies)
            self.revealing()
    
def walking(self):
    # Controls the walking animation of the enemy
    # Switches between different frames every 125 milliseconds
    if (self.current_time - self.animate_timer) > 125:
        if self.direction == c.RIGHT:
            # When walking to the right, toggle between frames 4 and 5
            if self.frame_index == 4:
                self.frame_index += 1
            elif self.frame_index == 5:
                self.frame_index = 4
        else:
            # When walking to the left, toggle between frames 0 and 1
            if self.frame_index == 0:
                self.frame_index += 1
            elif self.frame_index == 1:
                self.frame_index = 0
        # Reset the animation timer to current time after changing frame
        self.animate_timer = self.current_time

def falling(self):
    # Simulate gravity when the enemy is falling
    # Increment vertical velocity by gravity, but limit it to a maximum of 10
    if self.y_vel < 10:
        self.y_vel += self.gravity

def jumped_on(self):
    # This is a placeholder method for when an enemy is jumped on by the player.
    # Actual behavior will be implemented based on specific enemy types
    pass

def death_jumping(self):
    # Handles the movement of the enemy when it is in a death jump state
    # Update both x and y positions based on the velocities
    self.rect.y += self.y_vel
    self.rect.x += self.x_vel
    # Apply gravity to y velocity for a falling effect
    self.y_vel += self.gravity
    # If the enemy goes off-screen (past the screen height), remove it
    if self.rect.y > c.SCREEN_HEIGHT:
        self.kill()

def shell_sliding(self):
    # Sets the speed of the Koopa shell when sliding
    if self.direction == c.RIGHT:
        self.x_vel = 10  # Move quickly to the right
    else:
        self.x_vel = -10  # Move quickly to the left

def revealing(self):
    # Placeholder function for when an enemy is revealed (such as in hidden blocks)
    pass

def start_death_jump(self, direction):
    # Initiates the death jump with an initial upward velocity
    self.y_vel = -8  # Jump upward initially
    self.x_vel = 2 if direction == c.RIGHT else -2  # Move slightly in the given direction
    self.gravity = .5  # Set gravity lower for a slow fall
    self.frame_index = 3  # Set death frame for the animation
    self.state = c.DEATH_JUMP  # Set enemy state to death jump

def animation(self):
    # Update the enemy's image to the current animation frame
    self.image = self.frames[self.frame_index]

def update_position(self, level):
    # Update the enemy's x and y positions based on velocity
    self.rect.x += self.x_vel
    self.check_x_collisions(level)  # Check for collisions along the x-axis

    # Check for vertical movement range (for vertically moving enemies)
    if self.in_range and self.isVertical:
        if self.rect.y < self.range_start:
            # Restrict movement within the range by adjusting the y position and reversing velocity
            self.rect.y = self.range_start
            self.y_vel = ENEMY_SPEED
        elif self.rect.bottom > self.range_end:
            self.rect.bottom = self.range_end
            self.y_vel = -1 * ENEMY_SPEED  # Reverse vertical direction

    # Update y position based on vertical velocity
    self.rect.y += self.y_vel

    # Check for collisions along the y-axis unless in a death jump or flying
    if self.state != c.DEATH_JUMP and self.state != c.FLY:
        self.check_y_collisions(level)

    # If the enemy moves out of bounds (x <= 0), remove it from the game
    if self.rect.x <= 0:
        self.kill()
    # Remove the enemy if it falls below the current level's bottom viewport
    elif self.rect.y > (level.viewport.bottom):
        self.kill()

def check_x_collisions(self, level):
    # Check for horizontal collisions with level objects and change direction if necessary
    if self.in_range and not self.isVertical:
        # If the enemy is restricted to a movement range, adjust position and direction when reaching the range limit
        if self.rect.x < self.range_start:
            self.rect.x = self.range_start
            self.change_direction(c.RIGHT)  # Change direction to the right
        elif self.rect.right > self.range_end:
            self.rect.right = self.range_end
            self.change_direction(c.LEFT)  # Change direction to the left
    else:
        # Check for collisions with ground, steps, or pipes in the level
        collider = pg.sprite.spritecollideany(self, level.ground_step_pipe_group)
        if collider:
            # If there's a collision, change direction based on the current movement
            if self.direction == c.RIGHT:
                self.rect.right = collider.rect.left
                self.change_direction(c.LEFT)
            elif self.direction == c.LEFT:
                self.rect.left = collider.rect.right
                self.change_direction(c.RIGHT)

    # Special case: When the enemy is in shell slide state, check for collisions with other enemies
    if self.state == c.SHELL_SLIDE:
        enemy = pg.sprite.spritecollideany(self, level.enemy_group)
        if enemy:
            # If another enemy is hit, update score and move the enemy to the dying group
            level.update_score(100, enemy, 0)  # Award points for defeating the enemy
            level.move_to_dying_group(level.enemy_group, enemy)
            enemy.start_death_jump(self.direction)  # Start the death jump animation for the enemy

def change_direction(self, direction):
    """
    Change the enemy's direction and update velocity and frame index.
    This controls which way the enemy is moving.
    """
    self.direction = direction
    if self.direction == c.RIGHT:
        self.x_vel = ENEMY_SPEED  # Move to the right
        if self.state == c.WALK or self.state == c.FLY:
            self.frame_index = 4  # Set right-facing walking or flying frame
    else:
        self.x_vel = ENEMY_SPEED * -1  # Move to the left
        if self.state == c.WALK or self.state == c.FLY:
            self.frame_index = 0  # Set left-facing walking or flying frame

def check_y_collisions(self, level):
    """
    Check for collisions with the ground, bricks, or boxes.
    Optimized to avoid checking bricks/boxes when the enemy is already on the ground.
    """
    # If enemy is on the ground, only check ground/steps/pipes collisions
    if self.rect.bottom >= c.GROUND_HEIGHT:
        sprite_group = level.ground_step_pipe_group
    else:
        # Otherwise, check for collisions with ground, bricks, and boxes
        sprite_group = pg.sprite.Group(level.ground_step_pipe_group,
                                       level.brick_group, level.box_group)
    
    # Detect collision with any sprite in the group
    sprite = pg.sprite.spritecollideany(self, sprite_group)
    if sprite and sprite.name != c.MAP_SLIDER:
        # If collision occurs with the top of the sprite, stop vertical velocity
        if self.rect.top <= sprite.rect.top:
            self.rect.bottom = sprite.rect.y  # Set the bottom to sprite's top
            self.y_vel = 0  # Stop vertical movement
            self.state = c.WALK  # Set state to walking
    level.check_is_falling(self)  # Check if enemy is falling

class Goomba(Enemy):
    def __init__(self, x, y, direction, color, in_range, range_start, range_end, name=c.GOOMBA):
        """
        Initialize a Goomba enemy with specified parameters.
        Load frames for walking and flipped (dead) images.
        """
        Enemy.__init__(self)
        frame_rect_list = self.get_frame_rect(color)
        self.setup_enemy(x, y, direction, name, setup.GFX[c.ENEMY_SHEET],
                         frame_rect_list, in_range, range_start, range_end)
        # Add dead jump frame (flipped)
        self.frames.append(pg.transform.flip(self.frames[2], False, True))
        # Add right-facing walking frames
        self.frames.append(pg.transform.flip(self.frames[0], True, False))
        self.frames.append(pg.transform.flip(self.frames[1], True, False))

    def get_frame_rect(self, color):
        """
        Return the frame rectangle list for Goomba based on its color.
        This defines how Goomba's sprite is displayed.
        """
        if color == c.COLOR_TYPE_GREEN:
            frame_rect_list = [(0, 34, 16, 16), (30, 34, 16, 16), 
                               (61, 30, 16, 16)]  # Green Goomba frames
        else:
            frame_rect_list = [(0, 4, 16, 16), (30, 4, 16, 16), 
                               (61, 0, 16, 16)]  # Default Goomba frames
        return frame_rect_list

    def jumped_on(self):
        """
        Handle Goomba being jumped on by the player.
        Stops horizontal movement, displays dead frame, and removes Goomba after a delay.
        """
        self.x_vel = 0  # Stop movement
        self.frame_index = 2  # Set frame to the dead frame
        if self.death_timer == 0:
            self.death_timer = self.current_time  # Start death timer
        elif (self.current_time - self.death_timer) > 500:
            self.kill()  # Remove Goomba after 500 ms

class Koopa(Enemy):
    def __init__(self, x, y, direction, color, in_range, range_start, range_end, name=c.KOOPA):
        """
        Initialize a Koopa enemy with specified parameters.
        Load frames for walking and flipped (dead) images.
        """
        Enemy.__init__(self)
        frame_rect_list = self.get_frame_rect(color)
        self.setup_enemy(x, y, direction, name, setup.GFX[c.ENEMY_SHEET],
                         frame_rect_list, in_range, range_start, range_end)
        # Add dead jump frame (flipped)
        self.frames.append(pg.transform.flip(self.frames[2], False, True))
        # Add right-facing walking frames
        self.frames.append(pg.transform.flip(self.frames[0], True, False))
        self.frames.append(pg.transform.flip(self.frames[1], True, False))

    def get_frame_rect(self, color):
        """
        Return the frame rectangle list for Koopa based on its color.
        Defines how Koopa's sprite is displayed.
        """
        if color == c.COLOR_TYPE_GREEN:
            frame_rect_list = [(150, 0, 16, 24), (180, 0, 16, 24), 
                               (360, 5, 16, 15)]  # Green Koopa frames
        elif color == c.COLOR_TYPE_RED:
            frame_rect_list = [(150, 30, 16, 24), (180, 30, 16, 24), 
                               (360, 35, 16, 15)]  # Red Koopa frames
        else:
            frame_rect_list = [(150, 60, 16, 24), (180, 60, 16, 24), 
                               (360, 65, 16, 15)]  # Default Koopa frames
        return frame_rect_list

    def jumped_on(self):
        """
        Handle Koopa being jumped on by the player.
        Stops horizontal movement, displays dead frame, and disables the in-range state.
        """
        self.x_vel = 0  # Stop movement
        self.frame_index = 2  # Set frame to the dead frame
        x = self.rect.x
        bottom = self.rect.bottom
        self.rect = self.frames[self.frame_index].get_rect()  # Update frame rect
        self.rect.x = x
        self.rect.bottom = bottom
        self.in_range = False  # Disable in-range state

class FlyKoopa(Enemy):
    def __init__(self, x, y, direction, color, in_range, range_start, range_end, isVertical, name=c.FLY_KOOPA):
        """
        Initialize a flying Koopa enemy with specified parameters.
        Load frames for walking, flying, and flipped (dead) images.
        """
        Enemy.__init__(self)
        frame_rect_list = self.get_frame_rect(color)
        self.setup_enemy(x, y, direction, name, setup.GFX[c.ENEMY_SHEET], 
                         frame_rect_list, in_range, range_start, range_end, isVertical)
        # Add dead jump frame (flipped)
        self.frames.append(pg.transform.flip(self.frames[2], False, True))
        # Add right-facing walking frames
        self.frames.append(pg.transform.flip(self.frames[0], True, False))
        self.frames.append(pg.transform.flip(self.frames[1], True, False))
        self.state = c.FLY  # Set state to flying

    def get_frame_rect(self, color):
        """
        Return the frame rectangle list for FlyKoopa based on its color.
        Defines how FlyKoopa's sprite is displayed.
        """
        if color == c.COLOR_TYPE_GREEN:
            frame_rect_list = [(90, 0, 16, 24), (120, 0, 16, 24), 
                               (330, 5, 16, 15)]  # Green FlyKoopa frames
        else:
            frame_rect_list = [(90, 30, 16, 24), (120, 30, 16, 24), 
                               (330, 35, 16, 15)]  # Default FlyKoopa frames
        return frame_rect_list


def jumped_on(self):
    # Handles the Koopa being jumped on and entering shell state
    self.x_vel = 0  # Stop horizontal movement
    self.frame_index = 2  # Set to the "in shell" frame
    x = self.rect.x
    bottom = self.rect.bottom
    self.rect = self.frames[self.frame_index].get_rect()  # Adjust hitbox for new frame
    self.rect.x = x
    self.rect.bottom = bottom
    self.in_range = False  # No longer moving within a range
    self.isVertical = False  # Stop vertical movement

class FireKoopa(Enemy):
    def __init__(self, x, y, direction, color, in_range,
                 range_start, range_end, level, name=c.FIRE_KOOPA):
        # Initialize FireKoopa with fire-shooting ability
        Enemy.__init__(self)
        frame_rect_list = [(2, 210, 32, 32), (42, 210, 32, 32),
                           (82, 210, 32, 32), (122, 210, 32, 32)]  # FireKoopa frames
        self.setup_enemy(x, y, direction, name, setup.GFX[c.ENEMY_SHEET], 
                         frame_rect_list, in_range, range_start, range_end)
        # Add mirrored frames for right-walking animations
        self.frames.append(pg.transform.flip(self.frames[0], True, False))
        self.frames.append(pg.transform.flip(self.frames[1], True, False))
        self.frames.append(pg.transform.flip(self.frames[2], True, False))
        self.frames.append(pg.transform.flip(self.frames[3], True, False))
        self.x_vel = 0  # Initial velocity
        self.gravity = 0.3  # Gravity for jumping/falling
        self.level = level  # Reference to the level
        self.fire_timer = 0  # Timer for shooting fire
        self.jump_timer = 0  # Timer for jumping behavior

    def load_frames(self, sheet, frame_rect_list):
        # Load the frames from the sprite sheet
        for frame_rect in frame_rect_list:
            self.frames.append(tools.get_image(sheet, *frame_rect,
                                               c.BLACK, c.BRICK_SIZE_MULTIPLIER))

    def walking(self):
        # Handle walking animation and fire shooting
        if (self.current_time - self.animate_timer) > 250:
            # Switch frames based on direction and reset animation timer
            if self.direction == c.RIGHT:
                self.frame_index += 1
                if self.frame_index > 7:
                    self.frame_index = 4  # Loop between right-walking frames
            else:
                self.frame_index += 1
                if self.frame_index > 3:
                    self.frame_index = 0  # Loop between left-walking frames
            self.animate_timer = self.current_time

        # Shoot fire and check if Koopa should jump
        self.shoot_fire()
        if self.should_jump():
            self.y_vel = -7  # Jump with velocity

    def falling(self):
        # Handle falling behavior with gravity
        if self.y_vel < 7:
            self.y_vel += self.gravity  # Increase downward velocity
        self.shoot_fire()  # Continue shooting fire while falling

    def should_jump(self):
        # Koopa will jump if the player is within 400 pixels and jump timer allows it
        if (self.rect.x - self.level.player.rect.x) < 400:
            if (self.current_time - self.jump_timer) > 2500:
                self.jump_timer = self.current_time
                return True
        return False

    def shoot_fire(self):
        # Koopa shoots fire every 3000 milliseconds
        if (self.current_time - self.fire_timer) > 3000:
            self.fire_timer = self.current_time
            # Create a new fireball in the level's enemy group
            self.level.enemy_group.add(Fire(self.rect.x, self.rect.bottom - 20, self.direction))

class Fire(Enemy):
    def __init__(self, x, y, direction, name=c.FIRE):
        # Initialize the fireball enemy
        Enemy.__init__(self)
        frame_rect_list = [(101, 253, 23, 8), (131, 253, 23, 8)]  # Fireball frames
        in_range, range_start, range_end = False, 0, 0
        self.setup_enemy(x, y, direction, name, setup.GFX[c.ENEMY_SHEET], 
                         frame_rect_list, in_range, range_start, range_end)
        # Add mirrored frames for right movement
        self.frames.append(pg.transform.flip(self.frames[0], True, False))
        self.frames.append(pg.transform.flip(self.frames[1], True, False))
        self.state = c.FLY  # Set fireball state to flying
        self.x_vel = 5 if self.direction == c.RIGHT else -5  # Set velocity based on direction

    def check_x_collisions(self, level):
        # Handle fireball collisions with ground, bricks, and boxes
        sprite_group = pg.sprite.Group(level.ground_step_pipe_group,
                                       level.brick_group, level.box_group)
        sprite = pg.sprite.spritecollideany(self, sprite_group)
        if sprite:
            self.kill()  # Fireball disappears upon collision

    def start_death_jump(self, direction):
        # Fireball simply disappears (no jump animation needed)
        self.kill()


class Piranha(Enemy):
    def __init__(self, x, y, direction, color, in_range, 
                 range_start, range_end, name=c.PIRANHA):
        # Initialize Piranha enemy with setup parameters
        Enemy.__init__(self)
        frame_rect_list = self.get_frame_rect(color)  # Get frames based on color
        self.setup_enemy(x, y, direction, name, setup.GFX[c.ENEMY_SHEET], 
                         frame_rect_list, in_range, range_start, range_end)
        self.state = c.REVEAL  # Initial state of the Piranha
        self.y_vel = 1  # Vertical velocity for Piranha movement
        self.wait_timer = 0  # Timer for Piranha pause at range limit
        self.group = pg.sprite.Group()  # Create a sprite group with just the Piranha
        self.group.add(self)

    def get_frame_rect(self, color):
        # Define frame rectangles for the Piranha based on color (Green or default)
        if color == c.COLOR_TYPE_GREEN:
            frame_rect_list = [(390, 30, 16, 24), (420, 30, 16, 24)]  # Green Piranha frames
        else:
            frame_rect_list = [(390, 60, 16, 24), (420, 60, 16, 24)]  # Default Piranha frames
        return frame_rect_list

    def revealing(self):
        # Animate Piranha's reveal motion by alternating between two frames
        if (self.current_time - self.animate_timer) > 250:
            if self.frame_index == 0:
                self.frame_index += 1  # Switch to next frame
            elif self.frame_index == 1:
                self.frame_index = 0  # Loop back to first frame
            self.animate_timer = self.current_time  # Reset animation timer

    def update_position(self, level):
        # Update Piranha's position based on range and vertical movement
        if self.check_player_is_on(level):
            pass  # If the player is directly on top of Piranha, no movement occurs
        else:
            # If Piranha is at the upper limit of its movement range
            if self.rect.y < self.range_start:
                self.rect.y = self.range_start  # Set to upper limit
                self.y_vel = 1  # Start moving down
            # If Piranha reaches bottom limit of its movement range
            elif self.rect.bottom > self.range_end:
                if self.wait_timer == 0:
                    self.wait_timer = self.current_time  # Start wait timer
                elif (self.current_time - self.wait_timer) < 3000:
                    return  # Piranha pauses for 3 seconds at the bottom
                else:
                    self.wait_timer = 0  # Reset wait timer
                    self.rect.bottom = self.range_end  # Set to bottom limit
                    self.y_vel = -1  # Start moving up
            self.rect.y += self.y_vel  # Update vertical position based on velocity

    def check_player_is_on(self, level):
        # Check if the player is directly above the Piranha
        result = False
        self.rect.y -= 5  # Temporarily adjust the Piranha's position
        sprite = pg.sprite.spritecollideany(level.player, self.group)  # Check collision
        if sprite:
            result = True  # Player is on the Piranha
        self.rect.y += 5  # Restore Piranha's position
        return result

    def start_death_jump(self, direction):
        # Kill the Piranha (no death jump animation, it simply dies)
        self.kill()

class FireStick(pg.sprite.Sprite):
    def __init__(self, center_x, center_y, direction, color, radius, name=c.FIRESTICK):
        '''FireStick rotates around a central point like a clock hand'''
        pg.sprite.Sprite.__init__(self)

        self.frames = []  # List to hold FireStick animation frames
        self.frame_index = 0  # Initial frame index
        self.animate_timer = 0  # Timer for frame animation
        self.name = name  # FireStick name
        rect_list = [(96, 144, 8, 8), (104, 144, 8, 8),
                     (96, 152, 8, 8), (104, 152, 8, 8)]  # FireStick frames
        self.load_frames(setup.GFX[c.ITEM_SHEET], rect_list)  # Load animation frames
        self.animate_timer = 0  # Initialize animation timer
        self.image = self.frames[self.frame_index]  # Set the initial image
        self.rect = self.image.get_rect()  # Set rectangle based on image
        self.rect.x = center_x - radius  # Initial X position based on radius
        self.rect.y = center_y  # Initial Y position
        self.center_x = center_x  # Center of the FireStick's circular motion
        self.center_y = center_y
        self.radius = radius  # Distance from the center of rotation
        self.angle = 0  # Initial angle of rotation

    def load_frames(self, sheet, frame_rect_list):
        # Load FireStick's frames from the sprite sheet
        for frame_rect in frame_rect_list:
            self.frames.append(tools.get_image(sheet, *frame_rect, 
                                               c.BLACK, c.BRICK_SIZE_MULTIPLIER))

    def update(self, game_info, level):
        # Update FireStick's animation and circular movement
        self.current_time = game_info[c.CURRENT_TIME]  # Get the current game time
        if (self.current_time - self.animate_timer) > 100:
            # Switch frames every 100ms to create animation
            if self.frame_index < 3:
                self.frame_index += 1  # Move to the next frame
            else:
                self.frame_index = 0  # Loop back to the first frame
            self.animate_timer = self.current_time  # Reset animation timer
        self.image = self.frames[self.frame_index]  # Update the current image

        # Update FireStick's angle for circular motion
        self.angle += 1  # Increment the angle
        if self.angle == 360:
            self.angle = 0  # Reset angle after full circle
        radian = math.radians(self.angle)  # Convert angle to radians for trigonometric functions
        self.rect.x = self.center_x + math.sin(radian) * self.radius  # Calculate new X position
        self.rect.y = self.center_y + math.cos(radian) * self.radius  # Calculate new Y position
