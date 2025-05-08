from enum import Enum
import random
import sys
import pygame
from os import path

class RobotAction(Enum):
    LEFT = 0
    DOWN = 1
    RIGHT = 2
    UP = 3
    # SUCK = 4

class GridTile(Enum):
    FLOOR = 0
    ROBOT = 1
    DIRT = 2
    # WALL = 3
    # STATION = 4

    def __str__(self):
        symbols = {
            GridTile.FLOOR: "⬛",
            GridTile.ROBOT: "🤖",
            GridTile.DIRT: "💩",
            # GridTile.WALL: "🧱",
            # GridTile.STATION: "🏠",
        }
        return symbols.get(self, self.name)
    
class VacuumRobot:

    def __init__(self, grid_rows=5, grid_cols=5, fps=1):
        self.grid_rows = grid_rows
        self.grid_cols = grid_cols
        self.reset()

        self.fps = fps
        self.last_action = None
        self._init_pygame()
    
    def _init_pygame(self):
        pygame.init() # initialize pygame
        pygame.display.init() # Initialize the display module

        # Game clock
        self.clock = pygame.time.Clock()

        # Default font
        self.action_font = pygame.font.SysFont("Calibre",30)
        self.action_info_height = self.action_font.get_height()

        # For rendering
        self.cell_height = 64
        self.cell_width = 64
        self.cell_size = (self.cell_width, self.cell_height)        

        # Define game window size (width, height)
        self.window_size = (self.cell_width * self.grid_cols, self.cell_height * self.grid_rows + self.action_info_height)

        # Initialize game window
        self.window_surface = pygame.display.set_mode(self.window_size) 

        # Load & resize images
        file_name = path.join(path.dirname(__file__), "images/bot_blue.png")
        img = pygame.image.load(file_name)
        self.robot_img = pygame.transform.scale(img, self.cell_size)

        file_name = path.join(path.dirname(__file__), "images/floor.png")
        img = pygame.image.load(file_name)
        self.floor_img = pygame.transform.scale(img, self.cell_size)

        file_name = path.join(path.dirname(__file__), "images/package.png")
        img = pygame.image.load(file_name)
        self.goal_img = pygame.transform.scale(img, self.cell_size)
    
    def _init_robot_position(self):
        self.robot_pos = [0, 0]
    
    def _init_target_position(self, seed=None):
        random.seed(seed)
        self.target_pos = [0, 0]
        while self.target_pos == self.robot_pos:
            self.target_pos = [
                random.randint(0, self.grid_rows - 1),
                random.randint(0, self.grid_cols - 1)
            ]
    
    def reset(self, seed=None):
        self._init_robot_position()
        self._init_target_position(seed)

    def perform_action(self, robot_action:RobotAction) -> bool:

        self.last_action = robot_action
        
        if robot_action == RobotAction.LEFT:
            self.robot_pos[1] = max(0, self.robot_pos[1] - 1)
        elif robot_action == RobotAction.DOWN:
            self.robot_pos[0] = min(self.grid_rows - 1, self.robot_pos[0] + 1)
        elif robot_action == RobotAction.RIGHT:
            self.robot_pos[1] = min(self.grid_cols - 1, self.robot_pos[1] + 1)
        elif robot_action == RobotAction.UP:
            self.robot_pos[0]= max(0, self.robot_pos[0] - 1)
        # elif robot_action == RobotAction.SUCK:
        #     ToDO: Implement suck action
        return self.robot_pos[0] == self.target_pos[0] and self.robot_pos[1] == self.target_pos[1]
    
    def render(self):
        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                if [r, c] == self.robot_pos:
                    print(GridTile.ROBOT, end=" ")
                elif [r, c] == self.target_pos:
                    print(GridTile.DIRT, end=" ")
                # ToDO: Implement station and wall tiles
                else:
                    print(GridTile.FLOOR, end=" ")
            print()
        print()

        self._process_events()

        # clear to white background, otherwise text with varying length will leave behind prior rendered portions
        self.window_surface.fill((255,255,255))

        # Print current state on console
        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                
                # Draw floor
                pos = (c * self.cell_width, r * self.cell_height)
                self.window_surface.blit(self.floor_img, pos)

                if([r,c] == self.target_pos):
                    # Draw target
                    self.window_surface.blit(self.goal_img, pos)

                if([r,c] == self.robot_pos):
                    # Draw robot
                    self.window_surface.blit(self.robot_img, pos)
                
        text_img = self.action_font.render(f'Action: {self.last_action}', True, (0,0,0), (255,255,255))
        text_pos = (0, self.window_size[1] - self.action_info_height)
        self.window_surface.blit(text_img, text_pos)       

        pygame.display.update()
                
        # Limit frames per second
        self.clock.tick(self.fps)  

    def _process_events(self):
        # Process user events, key presses
        for event in pygame.event.get():
            # User clicked on X at the top right corner of window
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if(event.type == pygame.KEYDOWN):
                # User hit escape
                if(event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()


if __name__ == "__main__":
    # Test the GridTile enum
    for tile in GridTile:
        print(f"{tile.name}: {tile.value} - {str(tile)}")

    vacuumRobot = VacuumRobot()
    vacuumRobot.render()

    while(True):
        random_action = random.choice(list(RobotAction))
        print(f"Performing action: {random_action}")

        vacuumRobot.perform_action(random_action)
        vacuumRobot.render()