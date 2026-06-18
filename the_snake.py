from random import choice

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
SCREEN_CENTRE = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

OPPOSITE_DIRECTIONS = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT
}

DIRECTION_MAP = {
    # (старое_направление, нажатая_клавиша): новое_направление
    (UP, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_LEFT): LEFT,
    (DOWN, pg.K_RIGHT): RIGHT,
    (LEFT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_UP): UP,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_a): LEFT,
    (UP, pg.K_d): RIGHT,
    (DOWN, pg.K_a): LEFT,
    (DOWN, pg.K_d): RIGHT,
    (LEFT, pg.K_w): UP,
    (LEFT, pg.K_s): DOWN,
    (RIGHT, pg.K_w): UP,
    (RIGHT, pg.K_s): DOWN
}
KEYS = {key for (_, key) in DIRECTION_MAP}

# Цвета
BOARD_BACKGROUND_COLOR = (211, 211, 211)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

ALL_CELLS = set(
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT))

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

pg.display.set_caption(
    'Змейка. Выход - Esc.'
)

clock = pg.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Супер-класс для объектов игры."""

    def __init__(self, body_color=None):
        self.position = SCREEN_CENTRE
        self.body_color = body_color

    def draw(self):
        """
        Метод - заготовка для отрисовок объектов класса.
        Перехватывает исключение произошедшие в классах наследниках
        """
        raise NotImplementedError(
            f'Метод класса {type(self).__name__} не отработал'
        )

    def one_cell_draw(self, position, color=None):
        """Отрисовка одной ячейки в составе объекта"""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        cell_color = color or self.body_color
        pg.draw.rect(screen, cell_color, rect)
        if cell_color != BOARD_BACKGROUND_COLOR:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс, описывающий яблоко."""

    def randomize_position(self, taken_coordinates):
        """Возвращает координаты яблока."""
        self.position = choice(tuple(ALL_CELLS - set(taken_coordinates)))

    def __init__(self, taken_coordinates=[], body_color=APPLE_COLOR):
        super().__init__(body_color)
        self.randomize_position(taken_coordinates)

    def draw(self):
        """Отрисовывает яблоко"""
        self.one_cell_draw(self.position)


class Snake(GameObject):
    """Класс, описывающий змейку."""

    def __init__(self, body_color=SNAKE_COLOR):
        super().__init__(body_color)
        self.reset(RIGHT)

    def get_head_position(self):
        """Возвращает координаты головы змейки"""
        return self.positions[0]

    def move(self):
        """Реализует движение змейки."""
        head_x, head_y = self.get_head_position()

        # Направление
        dx, dy = self.direction

        # Вставляем новую голову
        self.positions.insert(0, (
            (head_x // GRID_SIZE + dx) % GRID_WIDTH * GRID_SIZE,
            (head_y // GRID_SIZE + dy) % GRID_HEIGHT * GRID_SIZE))

        self.last = (
            self.positions.pop()
            if len(self.positions) > self.length
            else None
        )

    # Метод обновления направления после нажатия на кнопку
    def update_direction(self, new_direction):
        """Обновляет напрвление движения змейки."""
        if self.direction != OPPOSITE_DIRECTIONS[new_direction]:
            self.direction = new_direction

    def draw(self):
        """Отрисовывет змейку на экране."""
        self.one_cell_draw(self.get_head_position())

        # Затирание последнего сегмента
        if self.last:
            self.one_cell_draw(self.last, BOARD_BACKGROUND_COLOR)

    def reset(self, direction=None):
        """Сбрасывает змейку до начального состояния."""
        self.length = 1
        self.last = None
        self.positions = [SCREEN_CENTRE]
        self.direction = direction or choice([UP, DOWN, LEFT, RIGHT])


# Функция обработки действий пользователя
def handle_keys(snake):
    """
    Обрабатывает события ввода с клавиатуры или мыши.

    Функция достает событие из очереди событий.
    Если событие с клавиш напрвления,
    то функция изменяет направление движения змейки.
    Если закрытие игрового экрана, завершает игру.

    Returns: None.
    """
    for event in pg.event.get():
        if (event.type == pg.QUIT
                or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE)):
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key in KEYS:
                snake.update_direction(DIRECTION_MAP.get((
                    snake.direction, event.key), snake.direction
                ))


def main():
    """Инициализация pg."""
    pg.init()

    # Тут нужно создать экземпляры классов.
    snake = Snake()
    apple = Apple(snake.positions)
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)

        # Тут опишите основную логику игры.
        handle_keys(snake)
        snake.move()

        head = snake.get_head_position()
        if head in snake.positions[4:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)
        elif head == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
