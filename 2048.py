import pygame
import random
import math
pygame.init()

WIDTH, HEIGHT = 800, 800
ROWS, COLS = 4, 4
TILE_WIDTH = WIDTH // COLS
TILE_HEIGHT = HEIGHT // ROWS
OUTLINE_THICKNESS = 10
FONT = pygame.font.SysFont("comicsans", 60, bold=True)
MOVE_VELOCITY = 20

OUTLINE_COLOR = (187, 173, 160)
BACKGROUND_COLOR = (205, 192, 180)
FONT_COLOR = (119, 110, 101)



WINDOW = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("2048")


class Tile:
    COLORS = [(237, 229, 218),
              (238, 225, 201),
              (243, 178, 122),
              (246, 150, 101),
              (247, 124, 95),
              (247, 95, 59),
              (237, 208, 115),
              (237, 204, 99),
              (236, 202, 80),
              (156, 130, 160),
              (100, 20, 20)]
    
    def __init__(self, value, row, col) -> None:
        self.value = value
        self.row = row
        self.col = col
        self.x = col * TILE_WIDTH
        self.y = row * TILE_HEIGHT

    def get_color(self):
        if self.value < 512:
            color_index = int(math.log2(self.value)) - 1
        else:
            color_index = 10

        color = self.COLORS[color_index]
        return color

    def draw_tile(self, window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, TILE_WIDTH, TILE_HEIGHT))
        
        text = FONT.render(str(self.value), 1, FONT_COLOR)
        window.blit(text, 
                    (self.x + (TILE_WIDTH / 2 - text.get_width() / 2),
                     self.y + (TILE_HEIGHT / 2 - text.get_height() / 2)))


    def set_pos(self, ceil = False):
        if ceil:
            self.row = math.ceil(self.y / TILE_HEIGHT)
            self.col = math.ceil(self.x / TILE_WIDTH)
        else:
            self.row = math.floor(self.y / TILE_HEIGHT)
            self.col = math.floor(self.x / TILE_WIDTH)
        

    def move_tile(self, delta):
        self.x += delta[0]
        self.y += delta[1]






def draw_grid(window):
    pygame.draw.rect(window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)
    for row in range(1, ROWS):
        y = row * TILE_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)

    for col in range(1, COLS):
        x = col * TILE_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)


def draw(window, tiles):
    window.fill(BACKGROUND_COLOR)
    
    for tile in tiles.values():
        tile.draw_tile(window)

    draw_grid(WINDOW)
    pygame.display.update()


def end_game_text(window, string):

    print("Wywołano")
    font = pygame.font.SysFont("comicsans", 80, bold=True)
    padding = 4
    text = font.render(string, 1, Tile.COLORS[5])
    window.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 - text.get_height() / 2))
    text = font.render(string, 1, Tile.COLORS[3])
    window.blit(text, (WIDTH / 2 - text.get_width() / 2 - padding, HEIGHT / 2 - text.get_height() / 2 - padding))
    text = font.render(string, 1, FONT_COLOR)
    window.blit(text, (WIDTH / 2 - text.get_width() / 2 - 2*padding, HEIGHT / 2 - text.get_height() / 2 - 2*padding))
    pygame.display.update()


    waiting_for_close = True
    while waiting_for_close:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting_for_close = False
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Jeśli naciśnięto ESC
                    waiting_for_close = False
                    pygame.quit()
                elif event.key == pygame.K_SPACE:  # Dodaj inne klawisze jeśli potrzebne
                    waiting_for_close = False

    return False


def generate_tiles():
    tiles = {}
    for _ in range(2):
        row, col = get_random_pos(tiles)
        tiles[f"{row}{col}"] = Tile(2, row, col)

    return tiles


def get_random_pos(tiles):
    row = None
    col = None
    while True:
        row = random.randrange(0, ROWS)
        col = random.randrange(0, COLS)

        if f"{row}{col}" not in tiles:
            break

    return row, col


def move_tiles(window, tiles, clock, direction):
    updated = True
    blocks = set() #Które tile już się połączyły
                                                                #     0
    if direction == "left":                                     # 0      COL-1
        sort_func = lambda tile: tile.col                       #   ROW-1
        reverse = True
        delta = (-MOVE_VELOCITY, 0) #Przesunięcie
        boundary_check = lambda tile: tile.col == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row }{tile.col - 1}")
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOVE_VELOCITY
        move_check = lambda tile, next_tile: tile.x > next_tile.x + TILE_WIDTH + MOVE_VELOCITY
        ceil = True

    elif direction == "right":
        sort_func = lambda tile: tile.col
        reverse = False
        delta = (MOVE_VELOCITY, 0) #Przesunięcie
        boundary_check = lambda tile: tile.col == COLS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col + 1}")
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOVE_VELOCITY
        move_check = lambda tile, next_tile: tile.x < next_tile.x - TILE_WIDTH - MOVE_VELOCITY
        ceil = False

    elif direction == "up":
        sort_func = lambda tile: tile.row
        reverse = False
        delta = (0, -MOVE_VELOCITY) #Przesunięcie
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row - 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_VELOCITY
        move_check = lambda tile, next_tile: tile.y > next_tile.y + TILE_HEIGHT + MOVE_VELOCITY
        ceil = True

    elif direction == "down":
        sort_func = lambda tile: tile.row
        reverse = True
        delta = (0, MOVE_VELOCITY) #Przesunięcie
        boundary_check = lambda tile: tile.row == ROWS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row + 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - MOVE_VELOCITY
        move_check = lambda tile, next_tile: tile.y < next_tile.y - TILE_HEIGHT - MOVE_VELOCITY
        ceil = False

    while updated:
        clock.tick(60)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=reverse)
    


        for i, tile in enumerate(sorted_tiles):
            if boundary_check(tile):
                continue

            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move_tile(delta)

            #Merged albo w trakcie merge
            elif tile.value == next_tile.value and tile not in blocks and next_tile not in blocks: 
                if merge_check(tile, next_tile):
                    tile.move_tile(delta)
                else:
                    next_tile.value *= 2
                    sorted_tiles.pop(i) 
                    blocks.add(next_tile) #Żeby nie powtarzać merge

            elif move_check(tile, next_tile):
                tile.move_tile(delta)
            else:
                continue

            tile.set_pos(ceil)
            updated = True
        
        update_tiles(window, tiles, sorted_tiles)
    
    return end_move(tiles)


def end_move(tiles):
    if len(tiles) == ROWS * COLS:
        return True #Czy koniec gry
    
    row, col = get_random_pos(tiles)
    tiles[f"{row}{col}"] = Tile(random.choice([2,4]), row, col)
    return False


def update_tiles(window, tiles, sorted_tiles):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile
    draw(window, tiles)


def scan_board_for_win(tiles):
    for tile in tiles.values():
        if tile.value >= 2048:
            return True


def main():
    running = True
    GameOver = False
    Win = False
    clock = pygame.time.Clock()
    tiles = generate_tiles()
    # tiles = {"00": Tile(2048, 0, 0)}

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and not GameOver:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    GameOver = move_tiles(WINDOW, tiles, clock, "left")

                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    GameOver = move_tiles(WINDOW, tiles, clock, "right")

                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    GameOver =move_tiles(WINDOW, tiles, clock, "up")

                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    GameOver = move_tiles(WINDOW, tiles, clock, "down")

    
        draw(WINDOW, tiles)


        Win = scan_board_for_win(tiles)
        if GameOver:
            running = end_game_text(WINDOW, "GAME OVER")

        if Win:
            running = end_game_text(WINDOW, "YOU WIN!")




    if pygame.get_init():
        pygame.quit()

if __name__ == "__main__":
    main()