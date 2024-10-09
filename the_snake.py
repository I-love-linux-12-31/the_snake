import os
from random import randint
import pygame

# from tests.conftest import apple

os.environ['PYGAME_DETECT_AVX2'] = '1'
DEBUG = os.environ.get("DEBUG", False)
# Константы для размеров поля и сетки:

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

CENTER = (
    GRID_SIZE * (GRID_WIDTH // 2),
    GRID_SIZE * (GRID_HEIGHT // 2)
)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (205, 210, 191)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)
BAD_APPLE_COLOR = (170, 139, 99)
ROCK_COLOR = (193, 186, 176)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

ALL_CELLS = set(
    (x, y) for x in range(0, SCREEN_WIDTH, GRID_SIZE)
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE)
)

# Скорость движения змейки:
speed = 5

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

can_run = True


def save_max_score(score):
    """Сохранение лучшего счёта."""
    with open('max_score.txt', 'wt') as f:
        f.write(str(score))


def load_max_score():
    """Загрузка лучшего счёта."""
    with open('max_score.txt', 'rt') as f:
        return int(f.read())


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

    def randomize_position(self, snake: GameObject = None):
        """Метод для изменения позиции на случайную."""
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )
        if snake:
            if self.position in snake.positions:
                self.randomize_position(snake)

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


class BadApple(Apple):
    """Класс испорченного яблока"""

    def __init__(self, position: [(int, int)] = None, color=BAD_APPLE_COLOR):
        super().__init__(position, color)

    # def randomize_position(self, snake: GameObject = None):
    #     """Метод для изменения позиции на случайную.
    #     С вероятностью 90% испорченное яблоко не появится.
    #     """
    #     r = randint(0, 32)
    #     if r % 10 == 0:
    #         super().randomize_position(snake)
    #     else:
    #         self.position = (-GRID_SIZE * 2, -GRID_SIZE)


class Rock(Apple):
    """Класс камня"""

    def __init__(self, position: [(int, int)] = None, color=ROCK_COLOR):
        super().__init__(position, color)

    def draw(self):
        """Метод для отрисовки."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BAD_APPLE_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змеи"""

    length: int = 1
    positions: list = None
    direction: tuple = RIGHT
    next_direction: tuple = None
    body_color: tuple = SNAKE_COLOR
    last: tuple = None

    def __init__(self):
        position = CENTER
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
        nx, ny = (
            (self.get_head_position()[0] + self.direction[0]
             * GRID_SIZE) % SCREEN_WIDTH,
            (self.get_head_position()[1] + self.direction[1]
             * GRID_SIZE) % SCREEN_HEIGHT
        )
        self.positions.insert(0, (nx, ny))
        self.last = self.positions.pop()

    # # Метод draw класса Snake
    def draw(self):
        """Метод для отрисовки."""
        # for position in self.positions:
        #     rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
        #     pygame.draw.rect(screen, self.body_color, rect)
        #     pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(
            screen,
            tuple(map(lambda a: int(round(a * 0.9)), self.body_color)),
            head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        # if self.positions[-1][0] < 0 and len(self.positions) > 1:
        #     self.last = self.positions[-2]
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """Метод для сброса змеи в исходное состояние."""
        self.position = CENTER
        self.positions = [self.positions[-1], ]
        self.direction = RIGHT
        self.length = 1
        self.last = (-1, -1)

    def add_segment(self):
        """Метод увеличение змейки."""
        self.length += 1
        # self.last = self.positions[-1]
        self.positions.append(self.last)

    def remove_segment(self):
        """Метод уменьшения змейки."""
        if len(self.positions) > 1:
            self.length -= 1
            self.last = self.positions.pop()


def handle_key(key, game_object: Snake):
    """Функция обработки нажатий клавиш"""
    global speed, can_run

    if key == pygame.K_ESCAPE:
        can_run = False
    elif key == pygame.K_UP and game_object.direction != DOWN:
        game_object.next_direction = UP
    elif key == pygame.K_DOWN and game_object.direction != UP:
        game_object.next_direction = DOWN
    elif key == pygame.K_LEFT and game_object.direction != RIGHT:
        game_object.next_direction = LEFT
    elif key == pygame.K_RIGHT and game_object.direction != LEFT:
        game_object.next_direction = RIGHT
    elif key == pygame.K_KP_PLUS and DEBUG:
        game_object.add_segment()
    elif key == pygame.K_q:
        speed += 1
    elif key == pygame.K_w and speed > 1:
        speed -= 1


# Функция обработки действий пользователя
def handle_keys(game_object):
    """Функция обработки событий pygame"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            handle_key(event.key, game_object)


def process_snake_collisions(gameobjects: [GameObject, ]):
    """Функция обработки столкновений змеи."""
    fruits, snake, *rocks = gameobjects
    result = None

    for fruit in fruits:
        if fruit.position == snake.positions[0]:
            if isinstance(fruit, BadApple):
                result = snake.last
                snake.remove_segment()
                fruits.remove(fruit)

            else:
                snake.add_segment()
                fruits.remove(fruit)

    if snake.get_head_position() in snake.positions[2:]:
        snake.reset()
        result = "clear_background"

    if snake.get_head_position() in [
        rock.position for rock in rocks
    ]:
        snake.reset()
        for _obj in gameobjects:
            if isinstance(_obj, Rock):
                _obj.randomize_position(snake)

        result = "clear_background"
    return result


def update_fruits(fruits: [GameObject, ], snake: Snake):
    """Функция обновления списка фруктов"""
    if all((isinstance(i, BadApple) for i in fruits)) or not fruits:
        old_fruits = fruits.copy()
        fruits.clear()
        good = randint(1, 3)
        bad = randint(1, 3)
        for i in range(good):
            apple = Apple()
            apple.randomize_position(snake)
            fruits.append(apple)
        for i in range(bad):
            badapple = BadApple()
            badapple.randomize_position(snake)
            fruits.append(badapple)
        # return lambda *args: screen.fill(BOARD_BACKGROUND_COLOR)

        def res(*args):
            for f in old_fruits:
                pygame.draw.rect(
                    screen,
                    BOARD_BACKGROUND_COLOR,
                    pygame.Rect(f.position, (GRID_SIZE, GRID_SIZE))
                )
            old_fruits.clear()
        return res
    return lambda *args: None


def main():
    """Основная функция программы."""
    if os.path.exists("max_score.txt"):
        best_score = load_max_score()
    else:
        best_score = 1

    screen.fill(BOARD_BACKGROUND_COLOR)

    snake = Snake()
    fruits = []
    # apple = Apple()
    # bad_apple = BadApple()
    gameobjects = [fruits, snake]
    for i in range(randint(2, 7)):
        rock = Rock()
        if not any(rock.position == i for i in snake.positions):
            gameobjects.append(rock)

    while can_run:
        clock.tick(speed)
        # screen.fill(BOARD_BACKGROUND_COLOR)
        handle_keys(snake)
        snake.move()
        res = process_snake_collisions(gameobjects)
        if res == "clear_background":
            screen.fill(BOARD_BACKGROUND_COLOR)

        for obj in gameobjects[1:] + gameobjects[0]:
            obj.draw()
        snake.draw()

        if isinstance(res, tuple):
            pygame.draw.rect(
                screen,
                BOARD_BACKGROUND_COLOR,
                pygame.Rect(res, (GRID_SIZE, GRID_SIZE))
            )

        pygame.display.update()
        if best_score < snake.length:
            best_score = snake.length
        pygame.display.set_caption(
            f'Змейка | Лучший счёт: {best_score} | Скорость: {speed}'
        )

        update_fruits(fruits, snake)()
        # print(fruits)
    save_max_score(score=best_score)


if __name__ == '__main__':
    main()
