import pygame


WIDTH = 800
HEIGHT = 600
FPS = 10


class Hero(pygame.sprite.Sprite):
    character_go = ["images/go_r.png",
                    "images/stand.png",
                    "images/go_l.png",
                    "images/stand.png"]
    character_climb = ["images/climb_l.png",
                       "images/climb_r.png"]
    character_push = ["images/push_l.png",
                      "images/push_and_stand.png",
                      "images/push_r.png"]
    character_die = "images/die.png"
    character_jump = "images/jump.png"

    def __init__(self, pos):
        super().__init__(all_sprites)
        self.pos = pos
        self.image = pygame.image.load(Hero.character_go[1]).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 100))
        self.rect = pygame.Rect(self.pos[0], self.pos[1], 50, 100)
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
        self.x = self.pos[0]
        self.y = self.pos[1]
        self.go = False
        self.route = True
        self.frame_go = 0
        self.frame_climb = 0
        self.frame_push = 0
        self.flag = 0
        self.is_climb = False

        self.add(hero_sprites)

    def update(self):
        """
        Проверка событий.

        :return: None
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.go = True
                self.route = True
            if event.key == pygame.K_LEFT:
                self.go = True
                self.route = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                self.go = False
                self.route = True
            if event.key == pygame.K_LEFT:
                self.go = False
                self.route = False
        self.kill()
        self.action('go')
        self.collide()
        self.jump()

    def action(self, action):
        """
        Изменение картинки объекта в соответствии с выбранным действием.

        :param action: str
        :return: None
        """
        if action == 'jump':
            self.image = pygame.image.load(Hero.character_jump).convert_alpha()
        if action == 'climb':
            self.image = pygame.image.load(Hero.character_climb[self.frame_climb]).convert_alpha()
        if action == 'push':
            self.image = pygame.image.load(Hero.character_push[self.frame_push]).convert_alpha()
        if action == 'go':
            if self.go:
                if not self.route:
                    self.x -= 10
                else:
                    self.x += 10
                if self.flag == 1:
                    self.frame_go += 1
                if self.frame_go == 4:
                    self.frame_go = 0
                self.image = pygame.image.load(Hero.character_go[self.frame_go]).convert_alpha()
            else:
                self.image = pygame.image.load(Hero.character_go[1]).convert_alpha()
        if not self.route:
            self.image = pygame.transform.flip(self.image, 1, 0)
        self.image = pygame.transform.scale(self.image, (50, 100))
        self.add(all_sprites)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.flag = 0 if self.flag == 1 else 1
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN or \
                    event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                if self.flag == 0:
                    self.frame_climb = 1 if self.frame_climb == 0 else 0
        if self.flag == 1:
            self.frame_push += 1
        if self.frame_push == 3:
            self.frame_push = 0

    def collide(self):
        """
        Столкновение с другими группами спрайтов.

        :return: None
        """
        if not pygame.sprite.spritecollideany(self, platform_sprites) and \
                not pygame.sprite.spritecollideany(self, ladder_sprites) and \
                not pygame.sprite.spritecollideany(self, box_sprites):
            self.y += 10
            self.action('jump')
        if pygame.sprite.spritecollideany(self, ladder_sprites):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.y += 10
                if event.key == pygame.K_UP:
                    self.y -= 10
            self.action('climb')
            self.is_climb = True
        else:
            self.is_climb = False
        if pygame.sprite.spritecollideany(self, box_sprites) and pygame.sprite.spritecollideany(self, platform_sprites):
            push_box = pygame.sprite.spritecollideany(self, box_sprites)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    push_box.push(True)
                if event.key == pygame.K_LEFT:
                    push_box.push(False)
            self.action('push')
        if self.rect.y == 580:
            self.kill()

    def jump(self):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and not self.is_climb:
                self.y -= 50
                self.action('jump')


class Platform(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites)
        self.pos = pos
        self.image = pygame.Surface((100, 10))
        pygame.draw.rect(self.image, pygame.Color("grey"), pygame.Rect(0, 0, 100, 10))
        self.rect = pygame.Rect(self.pos[0], self.pos[1], 100, 10)
        self.vx = 0
        self.vy = 0
        self.add(platform_sprites)


class Ladder(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites)
        self.pos = pos
        self.image = pygame.Surface((10, 50))
        pygame.draw.rect(self.image, pygame.Color("red"), pygame.Rect(0, 0, 10, 50))
        self.rect = pygame.Rect(self.pos[0], self.pos[1], 10, 50)
        self.vx = 0
        self.vy = 0
        self.add(ladder_sprites)


class Box(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites)
        self.pos = pos
        self.image = pygame.Surface((50, 50))
        pygame.draw.rect(self.image, pygame.Color("white"), pygame.Rect(0, 0, 50, 50))
        self.rect = pygame.Rect(self.pos[0], self.pos[1], 50, 50)
        self.vx = 0
        self.vy = 0
        self.add(box_sprites)

    def update(self):
        self.collide()

    def collide(self):
        if not pygame.sprite.spritecollideany(self, platform_sprites) and \
                not pygame.sprite.spritecollideany(self, ladder_sprites):
            self.rect.y += 10

    def push(self, route):
        if route:
            self.rect.x += 10
        else:
            self.rect.x -= 10


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Game')
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True
    all_sprites = pygame.sprite.Group()
    hero_sprites = pygame.sprite.Group()
    platform_sprites = pygame.sprite.Group()
    ladder_sprites = pygame.sprite.Group()
    box_sprites = pygame.sprite.Group()
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_RIGHT and not pygame.KMOD_CTRL & pygame.key.get_mods():
                    Hero(event.pos)
                if event.button == pygame.BUTTON_LEFT and not pygame.KMOD_CTRL & pygame.key.get_mods():
                    Platform(event.pos)
                if event.button == pygame.BUTTON_LEFT and pygame.KMOD_CTRL & pygame.key.get_mods():
                    Ladder(event.pos)
                if event.button == pygame.BUTTON_RIGHT and pygame.KMOD_CTRL & pygame.key.get_mods():
                    Box(event.pos)
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()