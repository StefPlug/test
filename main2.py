import pygame
import sqlite3
import sys
import random
import math

WIDTH, HEIGHT = 1920, 1080
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Adventure Quest")
background = pygame.image.load('images2/background.jpg')
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
fireballs = pygame.sprite.Group()

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        stone_texture = pygame.image.load('images2/stone.png')
        stone_texture = pygame.transform.scale(stone_texture, (200, 40))
        self.image = stone_texture
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

""" Создание платформ для этажей """
platform1 = Platform(0, HEIGHT - 50, WIDTH, 50)  # Пол
platforms.add(platform1)

platform2 = Platform(500, 550, 10000, 40)
platforms.add(platform2)

platform3 = Platform(100, 550, 1720, 40)
platforms.add(platform3)

platform4 = Platform(100, 450, 1720, 40)
platforms.add(platform4)

platform5 = Platform(1720, 750, 900, 300)
platforms.add(platform5)

platform6 = Platform(100, 450, 40, 300)
platforms.add(platform6)

platform7 = Platform(1720, 150, 40, 300)
platforms.add(platform7)


conn = sqlite3.connect("game_data.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    level INTEGER DEFAULT 1,
    score INTEGER DEFAULT 0
)
""")
conn.commit()

def draw_text(surface, text, font, color, x, y):
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))

def draw_health_hearts(surface, hearts):
    heart_image = pygame.image.load('images2/heart.png')
    heart_image = pygame.transform.scale(heart_image, (40, 40))
    for i in range(hearts):
        surface.blit(heart_image, (10 + i * 50, 30))

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        stone_texture = pygame.image.load('images2/stone.png')
        stone_texture = pygame.transform.scale(stone_texture, (200, 40))
        self.image = stone_texture
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        fireball_image = pygame.image.load('images2/fireball.png')
        fireball_image = pygame.transform.scale(fireball_image, (40, 40))
        self.image = fireball_image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5

        self.angle = math.atan2(target_y - y, target_x - x)
        self.vel_x = self.speed * math.cos(self.angle)
        self.vel_y = self.speed * math.sin(self.angle)

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        if self.rect.x < 0 or self.rect.x > WIDTH or self.rect.y < 0 or self.rect.y > HEIGHT:
            self.kill()  # Удаляем огненный шар, если он выходит за границы экрана

class Dragon(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        dragon_image = pygame.image.load('images2/dragon.png')
        dragon_image = pygame.transform.scale(dragon_image, (200, 200))
        self.image = dragon_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.last_fire_time = pygame.time.get_ticks()
        self.speed = 2
        self.direction = random.choice([-1, 1])

    def update(self, hero):
        """ Двигаемся по верхней части экрана """
        self.rect.x += self.direction * self.speed
        if self.rect.x <= 0 or self.rect.x >= WIDTH - self.rect.width:
            self.direction *= -1

        """ Стреляем в героя """
        now = pygame.time.get_ticks()
        if now - self.last_fire_time > 2000:
            fireball = Fireball(self.rect.centerx, self.rect.bottom, hero.rect.centerx, hero.rect.top)
            fireballs.add(fireball)
            all_sprites.add(fireball)
            self.last_fire_time = now

""" Изменяем метод collide в классе Hero """
class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.walk_right = [pygame.image.load(f'images2/png{i}.png') for i in range(1, 8)]
        self.walk_left = [pygame.image.load(f'images2/png{i}.png') for i in range(8, 15)]
        self.image = self.walk_right[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.index = 0
        self.animation_speed = 0.1
        self.last_update = 0
        self.health = 3

    def update(self, keys, platforms):
        self.vel_x = 0

        if keys[pygame.K_LEFT]:
            self.vel_x = -5
            self.image = self.walk_left[int(self.index)]
        elif keys[pygame.K_RIGHT]:
            self.vel_x = 5
            self.image = self.walk_right[int(self.index)]
        else:
            self.image = self.walk_right[2]

        if not self.on_ground:
            self.vel_y += 0.5
        else:
            self.vel_y = 0

        if keys[pygame.K_UP] and self.on_ground:
            self.vel_y = -16
            self.on_ground = False

        self.rect.x += self.vel_x
        self.collide(platforms, 'x')
        self.rect.y += self.vel_y
        self.on_ground = False
        self.collide(platforms, 'y')

        if self.rect.y >= HEIGHT - 50 - 129:
            self.rect.y = HEIGHT - 50 - 129
            self.on_ground = True

        now = pygame.time.get_ticks()
        if now - self.last_update > 10:
            self.index = (self.index + self.animation_speed) % len(self.walk_right)
            self.last_update = now

    def collide(self, platforms, direction):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if direction == 'x':
                    if self.vel_x > 0:
                        self.rect.right = platform.rect.left
                    if self.vel_x < 0:
                        self.rect.left = platform.rect.right
                if direction == 'y':
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        self.on_ground = True
                    if self.vel_y < 0:
                        self.rect.top = platform.rect.bottom

def draw_health_hearts(surface, hearts):
    heart_image = pygame.image.load('images2/heart.png')
    heart_image = pygame.transform.scale(heart_image, (40, 40))
    for i in range(hearts):
        surface.blit(heart_image, (10 + i * 50, 30))


def game_over():
    running = True
    while running:
        screen.fill(BLACK)
        draw_text(screen, "Вы проиграли!", BIG_FONT, WHITE, WIDTH // 2 - 150, HEIGHT // 2 - 50)
        draw_text(screen, "Нажмите ESC для выхода", FONT, WHITE, WIDTH // 2 - 150, HEIGHT // 2 + 50)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    pygame.quit()
                    sys.exit()

if __name__ == "__main__":
    pygame.init()
    running = True
    FONT = pygame.font.Font(None, 48)
    BIG_FONT = pygame.font.Font(None, 96)
    while running:
        screen.fill(WHITE)
        draw_text(screen, "Adventure Quest", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 4)
        draw_text(screen, "1. Начать игру", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2 - 50)
        draw_text(screen, "2. Выбрать уровень", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2)
        draw_text(screen, "3. Настройки", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2 + 50)
        draw_text(screen, "4. Выход", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2 + 100)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    username = ""
                    password = ""
                    is_register = True
                    running1 = True
                    while running1:
                        screen.fill(WHITE)
                        draw_text(screen, "Регистрация" if is_register else "Вход", FONT, BLACK, WIDTH // 2 - 100,
                                  HEIGHT // 4)
                        draw_text(screen, f"Логин: {username}", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2 - 50)
                        draw_text(screen, f"Пароль: {'*' * len(password)}", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2)
                        draw_text(screen, "Enter - подтвердить", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2 + 100)
                        draw_text(screen, "Tab - переключить (регистрация/вход)", FONT, BLACK, WIDTH // 2 - 100,
                                  HEIGHT // 2 + 150)

                        pygame.display.flip()

                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running1 = False

                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_RETURN:
                                    if is_register:
                                        try:
                                            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                                                           (username, password))
                                            conn.commit()
                                            all_sprites.empty()
                                            fireballs.empty()

                                            hero = Hero(100, HEIGHT - 150)
                                            all_sprites.add(hero)

                                            for platform in platforms:
                                                all_sprites.add(platform)

                                            dragon = Dragon(600, 100)
                                            all_sprites.add(dragon)

                                            clock = pygame.time.Clock()

                                            running = True

                                            while running:
                                                keys = pygame.key.get_pressed()
                                                screen.blit(background, (0, 0))

                                                for event in pygame.event.get():
                                                    if event.type == pygame.QUIT:
                                                        running = False

                                                hero.update(keys, platforms)
                                                dragon.update(hero)
                                                fireballs.update()

                                                if pygame.sprite.spritecollide(hero, fireballs, True):
                                                    hero.health -= 1
                                                    if hero.health <= 0:
                                                        game_over()
                                                        running = False
                                                        break

                                                for platform in platforms:
                                                    pygame.draw.rect(screen, (0, 0, 255), platform)

                                                all_sprites.draw(screen)

                                                draw_text(screen, f"Игрок: {username}", FONT, BLACK, 10, 10)
                                                draw_health_hearts(screen, hero.health)

                                                pygame.display.flip()
                                                clock.tick(FPS)
                                        except sqlite3.IntegrityError:
                                            print("Логин уже существует!")
                                    else:
                                        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?",
                                                       (username, password))
                                        user = cursor.fetchone()
                                        if user:
                                            all_sprites.empty()
                                            fireballs.empty()

                                            hero = Hero(100, HEIGHT - 150)
                                            all_sprites.add(hero)

                                            for platform in platforms:
                                                all_sprites.add(platform)

                                            dragon = Dragon(600, 100)
                                            all_sprites.add(dragon)

                                            clock = pygame.time.Clock()

                                            running = True

                                            while running:
                                                keys = pygame.key.get_pressed()
                                                screen.blit(background, (0, 0))

                                                for event in pygame.event.get():
                                                    if event.type == pygame.QUIT:
                                                        running = False

                                                hero.update(keys, platforms)
                                                dragon.update(hero)
                                                fireballs.update()

                                                if pygame.sprite.spritecollide(hero, fireballs, True):
                                                    hero.health -= 1
                                                    if hero.health <= 0:
                                                        game_over()
                                                        running = False
                                                        break

                                                for platform in platforms:
                                                    pygame.draw.rect(screen, (0, 0, 255), platform)

                                                all_sprites.draw(screen)

                                                draw_text(screen, f"Игрок: {username}", FONT, BLACK, 10, 10)
                                                draw_health_hearts(screen, hero.health)

                                                pygame.display.flip()
                                                clock.tick(FPS)
                                        else:
                                            print("Неверный логин или пароль!")

                                elif event.key == pygame.K_TAB:
                                    is_register = not is_register

                                elif event.key == pygame.K_BACKSPACE:
                                    if len(password) > 0:
                                        password = password[:-1]
                                    elif len(username) > 0:
                                        username = username[:-1]
                                else:
                                    if len(username) < 10 and len(password) == 0:
                                        username += event.unicode
                                    elif len(password) < 10:
                                        password += event.unicode
                elif event.key == pygame.K_4:
                    pygame.quit()