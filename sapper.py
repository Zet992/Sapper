from random import sample, choice
import sys

import pygame
pygame.init()


SIZE = 600, 650
CELL_WIDTH = 60
BOMBS_COUNT = 10
CELL_FONT = pygame.font.SysFont("microsofttalie", 40)
FONT50 = pygame.font.SysFont("microsofttalie", 50)
FONT20 = pygame.font.SysFont("microsofttalie", 20)
WIN = 1
DEFEAT = 2

screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Sapper")
clock = pygame.time.Clock()

game_over = False


class Cell:
    cells = []

    def __init__(self, x, y, bomb=False):
        self.x = x
        self.y = y
        self.bomb = bomb
        self.color = (50, 50, 50)
        self.color_border = (255, 255, 255)
        self.color_label = None
        self.near_bombs = 0
        self.opened = False
        self.label = ""

        self.cells.append(self)

    def check_cursor(self):
        x, y = pygame.mouse.get_pos()
        if self.x <= x < (self.x + CELL_WIDTH):
            if self.y <= y < (self.y + CELL_WIDTH):
                return True

    def check_click(self, event):
        if self.opened:
            return None

        x, y = self.x, self.y
        if x <= event.pos[0] < (x + CELL_WIDTH):
            if y <= event.pos[1] < (y + CELL_WIDTH):
                buttons = pygame.mouse.get_pressed(num_buttons=3)
                if buttons[0] and not self.label:
                    if self.bomb:
                        self.boom()
                    else:
                        self.open()
                    return True

                elif buttons[2]:
                    self.set_label()

    def open(self):
        if self.label:
            return None

        near_cells = self._find_near_cells()
        for cell in near_cells:
            if cell.bomb:
                self.near_bombs += 1

        self.color = (255, 255, 255)
        self.color_border = (0, 0, 0)
        self.opened = True

        if self.near_bombs == 0:
            for cell in near_cells:
                if not cell.opened:
                    cell.open()

    def boom(self):
        self.color = (255, 0, 0)
        self.color_border = (0, 0, 0)
        self.opened = True

    def set_label(self):
        if not self.label:
            self.label = "!"
            self.color_label = (255, 0, 0)
        elif self.label == "!":
            self.label = "?"
            self.color_label = (255, 255, 0)
        else:
            self.label = ""
            self.color_label = None

    def draw(self):
        if self.check_cursor():
            color = list(map(lambda x: x // 1.5, self.color))
        else:
            color = self.color
        pygame.draw.rect(screen, color,
                         (self.x, self.y,
                          CELL_WIDTH, CELL_WIDTH),
                         width=0)
        pygame.draw.rect(screen, self.color_border,
                         (self.x, self.y,
                          CELL_WIDTH, CELL_WIDTH),
                         width=1)
        if self.opened and not self.bomb and self.near_bombs:
            text = str(self.near_bombs)
            follow = CELL_FONT.render(text, True, (0, 0, 0))
            screen.blit(follow, (self.x + 22, self.y + 20))

        if self.label:
            text = self.label
            follow = CELL_FONT.render(text, True, self.color_label)
            screen.blit(follow, (self.x + 22, self.y + 20))

    def _find_near_cells(self):
        index = self.cells.index(self)
        row, column = index % 10, index // 10
        near_cells = []

        if row != 0:
            near_cells.append(self.cells[index - 1])
        if row != 0 and column != 0:
            near_cells.append(self.cells[index - 11])
        if row != 0 and column != 9:
            near_cells.append(self.cells[index + 9])

        if column != 0:
            near_cells.append(self.cells[index - 10])
        if column != 9:
            near_cells.append(self.cells[index + 10])

        if row != 9:
            near_cells.append(self.cells[index + 1])
        if row != 9 and column != 0:
            near_cells.append(self.cells[index - 9])
        if row != 9 and column != 9:
            near_cells.append(self.cells[index + 11])

        return near_cells


def create_field():
    Cell.cells = []
    for x in range(0, SIZE[0], CELL_WIDTH):
        for y in range(0, SIZE[1] - 50, CELL_WIDTH):
            Cell(x, y)


def create_bomb():
    for cell in sample(Cell.cells, k=BOMBS_COUNT):
        cell.bomb = True


def count_labels():
    count = 0
    for cell in Cell.cells:
        if cell.label == "!":
            count += 1
    return count


def draw_interface():
    y = SIZE[1] - 50
    pygame.draw.rect(screen, (255, 255, 255),
                     (0, y, SIZE[0], 50),
                     width=0)

    pygame.draw.rect(screen, (255, 0, 0),
                     (50, y + 5, 40, 40),
                     width=0)
    text = str(BOMBS_COUNT - count_labels())
    follow = CELL_FONT.render(text, True, (0, 0, 0))
    screen.blit(follow, (100, y + 12))

    text = "Нажмите любую кнопку на клавиатуре, чтобы начать новую игру"
    follow = FONT20.render(text, True, (0, 0, 0))
    screen.blit(follow, (SIZE[0] - 160, y + 8))
    text = "на клавиатуре, чтобы"
    follow = FONT20.render(text, True, (0, 0, 0))
    screen.blit(follow, (SIZE[0] - 160, y + 20))
    text = "начать новую игру"
    follow = FONT20.render(text, True, (0, 0, 0))
    screen.blit(follow, (SIZE[0] - 160, y + 32))


create_field()
create_bomb()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for cel in Cell.cells:
                if not game_over:
                    if cel.check_click(event) and cel.bomb:
                        game_over = DEFEAT
        elif event.type == pygame.KEYDOWN:
            game_over = False
            Cell.cells = []
            create_field()
            create_bomb()

    for cel in Cell.cells:
        if not cel.opened and not cel.bomb:
            break
    else:
        game_over = WIN

    for cel in Cell.cells:
        cel.draw()
    draw_interface()

    if game_over == WIN:
        text = "Вы победили!"
        follow = FONT50.render(text, True, (0, 0, 0))
        screen.blit(follow, (160, SIZE[1] - 42))
    elif game_over == DEFEAT:
        text = "Вы проиграли!"
        follow = FONT50.render(text, True, (0, 0, 0))
        screen.blit(follow, (160, SIZE[1] - 42))

    pygame.display.update()
    clock.tick(30)
