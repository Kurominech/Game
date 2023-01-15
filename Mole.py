import pygame
import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("map", type=str, nargs="?", default="map.map")
args = parser.parse_args()
map_file = args.map


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        loading_image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    if color_key is not None:
        loading_image = loading_image.convert()
        if color_key == -1:
            color_key = loading_image.get_at((0, 0))
        loading_image.set_colorkey(color_key)
    else:
        loading_image = loading_image.convert_alpha()
    return loading_image


pygame.init()
screen_size = (500, 500)
screen = pygame.display.set_mode(screen_size)
FPS = 10

tile_images = {
    'wall': load_image('brick.png'),
    'empty': load_image('stone.png'),
    'good_empty': load_image('stone (1).png'),
    'move_block': load_image('move_block.jpg')
}

player_image = load_image('mole.png', -1)
player_image = pygame.transform.scale(player_image, (50, 50))

tile_width = tile_height = 50


block_num = 1


class ScreenFrame(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.rect = (0, 0, 500, 500)


class SpriteGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()

    def get_event(self, happening):
        for sprite in self:
            sprite.get_event(happening)

    def shift(self, vector):
        global level_map
        if vector == "up":
            max_lay_y = max(self, key=lambda sprite:
            sprite.abs_pos[1]).abs_pos[1]
            for sprite in self:
                sprite.abs_pos[1] -= (tile_height * max_y
                                      if sprite.abs_pos[1] == max_lay_y else 0)
        elif vector == "down":
            min_lay_y = min(self, key=lambda sprite:
            sprite.abs_pos[1]).abs_pos[1]
            for sprite in self:
                sprite.abs_pos[1] += (tile_height * max_y
                                      if sprite.abs_pos[1] == min_lay_y else 0)
        elif vector == "left":
            max_lay_x = max(self, key=lambda sprite:
            sprite.abs_pos[0]).abs_pos[0]
            for sprite in self:
                if sprite.abs_pos[0] == max_lay_x:
                    sprite.abs_pos[0] -= tile_width * max_x
        elif vector == "right":
            min_lay_x = min(self, key=lambda sprite:
            sprite.abs_pos[0]).abs_pos[0]
            for sprite in self:
                sprite.abs_pos[0] += (tile_height * max_x
                                      if sprite.abs_pos[0] == min_lay_x else 0)


class Sprite(pygame.sprite.Sprite):

    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, happening):
        pass


class Tile(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        self.image = tile_images[tile_type]
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = (self.rect.x, self.rect.y)

    def set_pos(self, x, y):
        self.abs_pos = [x, y]


class Mole(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(hero_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.pos = (pos_x, pos_y)

    def move(self, x, y):
        camera.dx -= tile_width * (x - self.pos[0])
        camera.dy -= tile_height * (y - self.pos[1])
        self.pos = (x, y)
        for sprite in sprite_group:
            camera.apply(sprite)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x = obj.abs_pos[0] + self.dx
        obj.rect.y = obj.abs_pos[1] + self.dy

    def update(self, target):
        self.dx = 0
        self.dy = 0


player = None
running = True
clock = pygame.time.Clock()
sprite_group = SpriteGroup()
hero_group = SpriteGroup()
# block_group = SpriteGroup()


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    screen.fill(pygame.Color("white"))

    intro_text = ["Управление: стрелочки 'вверх', 'вниз', 'вправо',",
                  "'влево'.",
                  "Цель: поставить все цветные блоки на",
                  "зелёные камушки."]

    fon = pygame.transform.scale(load_image('intro.png'), (500, 400))
    """player_image = load_image('mole.png', -1)
    player_image = pygame.transform.scale(player_image, (50, 50))"""
    screen.blit(fon, (0, 100))
    font = pygame.font.Font(None, 30)
    text_coord = 5
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for happening in pygame.event.get():
            if happening.type == pygame.QUIT:
                terminate()
            elif happening.type == pygame.KEYDOWN or \
                    happening.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        map_for_tis_level = [line.strip() for line in mapFile]
    max_width = max(map(len, map_for_tis_level))
    return list(map(lambda x: list(x.ljust(max_width, '.')), map_for_tis_level))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == 'g':
                Tile('good_empty', x, y)
                level[y][x] = "g"
            elif level[y][x] == 'b':
                Tile('move_block', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Mole(x, y)
                level[y][x] = "."
    return new_player, x, y


def move(person, movement):
    x, y = person.pos

    if movement == "up":
        if y > 0 and (level_map[y - 1][x] == "." or level_map[y - 1][x] == "g"):
            person.move(x, y - 1)
        elif y > 0 and (level_map[y - 1][x] == "b" or level_map[y - 1][x] == "gb") and (level_map[y - 2][x] == "." or
                                                                                        level_map[y - 2][x] == "g"):
            if level_map[y - 1][x] == "gb":
                Tile('good_empty', x, y - 1)
            else:
                Tile('empty', x, y - 1)
            level_map[y - 1][x] = "."
            if level_map[y - 2][x] == "g":
                level_map[y - 2][x] = "gb"
            else:
                level_map[y - 2][x] = "b"
            Tile('move_block', x, y - 2)
            person.move(x, y - 1)

    elif movement == "down":
        if y < max_y - 1 and (level_map[y + 1][x] == "." or level_map[y + 1][x] == "g"):
            person.move(x, y + 1)
        elif y < max_y - 1 and (level_map[y + 1][x] == "b" or level_map[y + 1][x] == "gb") and \
                (level_map[y + 2][x] == "." or level_map[y + 2][x] == "g"):
            if level_map[y + 1][x] == "gb":
                Tile('good_empty', x, y + 1)
            else:
                Tile('empty', x, y + 1)
            level_map[y + 1][x] = "."
            if level_map[y + 2][x] == "g":
                level_map[y + 2][x] = "gb"
            else:
                level_map[y + 2][x] = "b"
            Tile('move_block', x, y + 2)
            person.move(x, y + 1)

    elif movement == "left":
        if x > 0 and (level_map[y][x - 1] == "." or level_map[y][x - 1] == "g"):
            person.move(x - 1, y)
        elif x > 0 and (level_map[y][x - 1] == "b" or level_map[y][x - 1] == "gb") and (level_map[y][x - 2] == "." or
                                                                                        level_map[y][x - 2] == "g"):
            if level_map[y][x - 1] == "gb":
                Tile('good_empty', x - 1, y)
            else:
                Tile('empty', x - 1, y)
            level_map[y][x - 1] = "."
            if level_map[y][x - 2] == "g":
                level_map[y][x - 2] = "gb"
            else:
                level_map[y][x - 2] = "b"
            Tile('move_block', x - 2, y)
            person.move(x - 1, y)
    elif movement == "right":
        if x < max_x - 1 and (level_map[y][x + 1] == "." or level_map[y][x + 1] == "g"):
            person.move(x + 1, y)
        elif x < max_x - 1 and (level_map[y][x + 1] == "b" or level_map[y][x + 1] == "gb") and \
                (level_map[y][x + 2] == "." or level_map[y][x + 2] == "g"):
            if level_map[y][x + 1] == "gb":
                Tile('good_empty', x + 1, y)
            else:
                Tile('empty', x + 1, y)
            level_map[y][x + 1] = "."
            if level_map[y][x + 2] == "g":
                level_map[y][x + 2] = "gb"
            else:
                level_map[y][x + 2] = "b"
            Tile('move_block', x + 2, y)
            person.move(x + 1, y)


start_screen()
camera = Camera()
level_map = load_level("map.map")
hero, max_x, max_y = generate_level(level_map)
camera.update(hero)
motion = None
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                motion = 'UP'
            elif event.key == pygame.K_DOWN:
                motion = 'DOWN'
            elif event.key == pygame.K_LEFT:
                motion = 'LEFT'
            elif event.key == pygame.K_RIGHT:
                motion = 'RIGHT'
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                motion = 'STOP'
    screen.fill(pygame.Color("black"))
    sprite_group.draw(screen)
    hero_group.draw(screen)
    if motion == 'LEFT':
        move(hero, "left")
    elif motion == 'RIGHT':
        move(hero, "right")
    elif motion == 'UP':
        move(hero, "up")
    elif motion == 'DOWN':
        move(hero, "down")
    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()
