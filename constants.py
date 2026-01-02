from enum import Enum
class Constants:
    MAIN_WIN_WIDTH = 1200
    MAIN_WIN_HEIGHT = 800

    FPS_LIMIT = 60

    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 40

    DATA_SAVE_FILENAME = "data/player_profile.json"

    DEFAULT_DATA = {
        "stats": {}
    }

    MAX_POINTS = 1000
    TILE_SIZE = 32
    BG_COLOR = (10, 10, 10)
    GRID_OFFSET_X = 50
    GRID_OFFSET_Y = 100
    TRACK_COLOR = (150, 150, 150)

    CAMERA_MOVE_SPEED = 250

    ISOLATION_WIDTH = 4
    LINE_ISOLATION_WIDTH = 2
    
    POINT_CHANGE_DELAY = 2
    CROSSING_CHANGE_DELAY = 5
    BLOCKADE_CHANGE_DELAY = 4
    
    MAX_WAITING_TRAINS = 5
    TRAIN_MOVE_SPEED = 0.4
    
    FINISHED_ROUTE_POINTS = 5
    
class MoveDirection(Enum):
    LEFT = 0,
    RIGHT = 1,
    UP = 2,
    BOTTOM = 3