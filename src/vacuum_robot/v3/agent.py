from collections import deque
from enum import Enum
import sys
import numpy as np
import pygame
from os import path

class RobotAction(Enum):
    LEFT = 0
    DOWN = 1
    RIGHT = 2
    UP = 3
    SUCK = 4

class GridTile(Enum):
    FLOOR = 0
    ROBOT = 1
    DIRT = 2
    STATION = 3
    WALL = 4

    def __str__(self):
        symbols = {
            GridTile.FLOOR: "⬛",
            GridTile.ROBOT: "🤖",
            GridTile.STATION: "🏠",
            GridTile.DIRT: "💩",
            GridTile.WALL: "🧱", # 🚧
        }
        return symbols.get(self, self.name)
    
class VacuumRobot:

    def __init__(self, grid_rows=5, grid_cols=5, n_dirt=5, n_wall=2, fps=1):
        if n_dirt + n_wall >= grid_rows * grid_cols:
            raise ValueError(f"n_dirt and n_wall do not fit inside the grid")
        self.grid_rows = grid_rows
        self.grid_cols = grid_cols
        self.n_dirt = n_dirt
        self.n_wall = n_wall
        self.np_random = np.random.RandomState()
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

        file_name = path.join(path.dirname(__file__), "images/wall.png")
        img = pygame.image.load(file_name)
        self.wall_img = pygame.transform.scale(img, self.cell_size)

        file_name = path.join(path.dirname(__file__), "images/package.png")
        img = pygame.image.load(file_name)
        self.dust_img = pygame.transform.scale(img, self.cell_size)

        file_name = path.join(path.dirname(__file__), "images/house.png")
        img = pygame.image.load(file_name)
        self.station_img = pygame.transform.scale(img, self.cell_size)
    
    def _init_wall_position(self):
        self.wall_list = [
            (1, 1),
            (1, 3),
            (3, 1),
            (3, 3)
        ]

    def _init_robot_position(self):
        new_pos = None
        while new_pos is None:
            new_pos = (
                self.np_random.randint(0, self.grid_rows - 1),
                self.np_random.randint(0, self.grid_cols - 1)
            )
            if new_pos in self.wall_list:
                new_pos = None

        self.robot_pos = new_pos
        self.robot_station_pos = new_pos
    
    def _init_target_position(self):
        self.got_all_dirt = False
        self.dust_list = []
        while len(self.dust_list) < self.n_dirt:
            new_pos = (
                self.np_random.randint(0, self.grid_rows - 1),
                self.np_random.randint(0, self.grid_cols - 1)
            )
            if new_pos not in self.dust_list and new_pos != self.robot_pos and new_pos not in self.wall_list:
                self.dust_list.append(new_pos)

    def _get_next_target_pos(self):
        if len(self.dust_list) > 0:
            return min(self.dust_list, key=lambda x: abs(x[0] - self.robot_pos[0]) + abs(x[1] - self.robot_pos[1]))
        else:
            return self.robot_station_pos
    
    def reset(self, seed=None):
        if seed is not None:
            self.np_random = np.random.RandomState(seed)
        self._init_wall_position()
        self._init_robot_position()
        self._init_target_position()

    # def can_reach_all_dust(self):
    #     # Set für Wände und besuchte Felder
    #     visited = []

    #     # BFS Queue initialisieren
    #     queue = deque([self.robot_pos])
    #     visited.append(self.robot_pos)

    #     # Alle erreichbaren Felder finden
    #     while queue:
    #         row, col = queue.popleft()

    #         for d_row, d_col in [(-1,0), (1,0), (0,-1), (0,1)]:  # Nachbarn: oben, unten, links, rechts
    #             n_row, n_col = row + d_row, col + d_col
    #             neighbor = [n_row, n_col]

    #             if (0 <= n_row < self.grid_rows and
    #                 0 <= n_col < self.grid_cols and
    #                 neighbor not in visited and
    #                 neighbor not in self.wall_list):
    #                 visited.append(neighbor)
    #                 queue.append(neighbor)

    #     # Prüfen, ob alle Dust-Zellen besucht wurden
    #     return all(pos in visited for pos in self.dust_list)

    def perform_action(self, robot_action:RobotAction) -> bool:

        self.last_action = robot_action

        tile_cleaned = False
        hit_wall = False

        # self.wall_list = [[0, 2], [1, 0], [1, 1], [1, 2]]
        # self.dust_list = [[0, 0], [4, 2], [4, 3], [4, 3], [4, 4]]

        if robot_action == RobotAction.SUCK:
            if self.robot_pos in self.dust_list:
                self.dust_list.remove(self.robot_pos)
                tile_cleaned = True
        else:
            new_pos = self.robot_pos

            if robot_action == RobotAction.LEFT:
                new_pos = (new_pos[0], max(0, new_pos[1] - 1))
            elif robot_action == RobotAction.RIGHT:
                new_pos = (new_pos[0], min(self.grid_cols - 1, new_pos[1] + 1))
            elif robot_action == RobotAction.UP:
                new_pos = (max(0, new_pos[0] - 1), new_pos[1])
            elif robot_action == RobotAction.DOWN:
                new_pos = (min(self.grid_rows - 1, new_pos[0] + 1), new_pos[1])

            
            if new_pos in self.wall_list or new_pos == self.robot_pos:
                hit_wall = True
            else:
                self.robot_pos = new_pos

        all_cleaned = len(self.dust_list) == 0
        robot_at_station = self.robot_pos == self.robot_station_pos

        return tile_cleaned, all_cleaned, robot_at_station, hit_wall
    
    def render(self):
        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                if (r, c) == self.robot_pos:
                    print(GridTile.ROBOT, end=" ")
                elif (r, c) == self.robot_station_pos:
                    print(GridTile.STATION, end=" ")
                elif (r, c) in self.dust_list:
                    print(GridTile.DIRT, end=" ")
                elif (r, c) in self.wall_list:
                    print(GridTile.WALL, end=" ")
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

                if (r, c) in self.wall_list:
                    # Draw wall
                    self.window_surface.blit(self.wall_img, pos)

                if (r, c) in self.dust_list:
                    # Draw target
                    self.window_surface.blit(self.dust_img, pos)

                if (r, c) == self.robot_station_pos:
                    # Draw station
                    self.window_surface.blit(self.station_img, pos)

                if (r, c) == self.robot_pos:
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
        random_action = np.random.choice(list(RobotAction))
        print(f"Performing action: {random_action}")

        vacuumRobot.perform_action(random_action)
        vacuumRobot.render()