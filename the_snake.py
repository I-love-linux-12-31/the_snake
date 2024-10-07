from random import randint
import os
import pygame
from pygame.examples.midi import BACKGROUNDCOLOR
from pygame.examples.moveit import WIDTH, HEIGHT

# from tests.conftest import apple

os.environ['PYGAME_DETECT_AVX2'] = '1'
# Константы для размеров поля и сетки:

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 5

pygame.init()
# Настройка игрового окна:
screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    0,
    32,
    display=0)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов"""

    position: [int, int] = None
    body_color: (int, int, int) = None

    def __init__(
            self,
            position: [(int, int)] = None,
            color: (int, int, int) = BORDER_COLOR
    ):
        """Базовый конструктор класса"""
        self.position = position
        self.body_color = color

    def draw(self):
        """Базовый метод для отрисовки. Должен быть переопределён."""
        pass


class Apple(GameObject):
    """Класс яблока"""

    def randomize_position(self):
        """Метод для изменения позиции на случайную."""
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )

    def __init__(self, position: [(int, int)] = None, color=APPLE_COLOR):
        if position is None:
            self.randomize_position()
            position = self.position
        super().__init__(position, color)

    def draw(self):
        """Метод для отрисовки."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змеи"""

    length: int = 1
    positions: list = None
    direction: tuple = RIGHT
    next_direction: tuple = None
    body_color: tuple = SNAKE_COLOR
    last: tuple = None

    def __init__(self):
        position = (
            GRID_SIZE * (GRID_WIDTH // 2),
            GRID_SIZE * (GRID_WIDTH // 2)
        )
        super().__init__(position, SNAKE_COLOR)
        self.positions = [position, ]
        self.last = (-1, -1)

    # Метод обновления направления после нажатия на кнопку
    def update_direction(self):
        """Метод для обновления направления движения змеи."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self) -> (int, int):
        """Метод для получения координат головы."""
        return self.positions[0]

    def move(self):
        """Метод движения змеи."""
        self.update_direction()
        dx, dy = self.direction
        x, y = self.get_head_position()
        nx, ny = x + dx * GRID_SIZE, y + dy * GRID_SIZE
        if nx > WIDTH:
            nx = 0
        if nx < 0:
            nx = WIDTH - GRID_SIZE
        if ny > HEIGHT:
            ny = 0
        if ny < 0:
            ny = HEIGHT - GRID_SIZE

        self.positions.insert(0, (nx, ny))
        self.last = self.positions.pop()

    # # Метод draw класса Snake
    def draw(self):
        """Метод для отрисовки."""
        for position in self.positions:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(
            screen,
            tuple(map(lambda a: int(round(a * 0.9)), self.body_color)),
            head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # # Затирание последнего сегмента
        # if self.last:
        #     last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
        #     pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """Метод для сброса змеи в исходное состояние."""
        self.position = (
            GRID_SIZE * (GRID_WIDTH // 2),
            GRID_SIZE * (GRID_WIDTH // 2)
        )
        self.positions = [self.position, ]
        self.direction = RIGHT
        self.length = 1
        self.last = (-1, -1)


# Функция обработки действий пользователя
def handle_keys(game_object):
    """Функция обработки событий pygame"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основная функция программы."""
    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(SPEED)
        screen.fill(BACKGROUNDCOLOR)
        handle_keys(snake)
        snake.move()
        if apple.position in snake.positions:
            snake.length += 1
            snake.positions.append((-1 * GRID_SIZE, -1 * GRID_SIZE))
            apple.randomize_position()
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
