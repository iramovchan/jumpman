#!/usr/bin/env python3.7

import pygame
from pygame.locals import *
import random
import time

pygame.init()

clock = pygame.time.Clock()

fps = 30

window_width = 1216
window_height = 608

black = (0, 0, 0)
white = (255, 255, 255)
mint_green_bg = (144, 247, 227)

main_charac_height = 32
main_charac_width = 32

size = 32

end_game_surface = pygame.Surface((window_width, window_height))

screen_2 = pygame.Surface((window_width, window_height), SRCALPHA)
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Platformer game')

true_scroll = [0, 0]

color = [255, 255, 255, 255]

joystics = []
for i in range(pygame.joystick.get_count()):
    joystics.append(pygame.joystick.Joystick(i))
for joystick in joystics:
    joystick.init()

# 0: Left analog horizonal, 1: Left Analog Vertical, 2: Right Analog Horizontal
# 3: Right Analog Vertical 4: Left Trigger, 5: Right Trigger
analog_keys = {0: 0, 1: 0, 2: 0, 3: 0, 4: -1, 5: -1}


class MainMenu(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.start_a_game = False
        self.start_again = False
        self.main_menu = pygame.Surface((window_width, window_height))

    def update(self):
        screen.blit(self.main_menu, (0, 0))
        if not self.start_a_game:
            self.main_menu.set_alpha(255)
        if self.start_a_game:
            self.main_menu.set_alpha(0)

        pygame.Surface.fill(self.main_menu, (0, 0, 0))

        self.main_menu.blit(start_new_game, start_new_game_rect)

    def again(self):
        if self.start_again:
            self.main_menu.set_alpha(255)


def load_map():
    level_map = open('map_1.txt', 'r')
    data = level_map.read()
    level_map.close()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map


ground_group = pygame.sprite.Group()
coins_group = pygame.sprite.Group()
door_group = pygame.sprite.Group()
game_map = load_map()


def create_map():
    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == '1':
                ground = Platform(x * size, y * size, 'ground.png')
                ground_group.add(ground)
                platform_list.append(ground)

            elif tile == '2':
                grass = Platform(x * size, y * size, 'grass_ground.png')
                ground_group.add(grass)
                platform_list.append(grass)

            elif tile == '3':
                grass = Platform(x * size, y * size, 'grass_ground_left_up.png')
                ground_group.add(grass)
                platform_list.append(grass)

            elif tile == '4':
                grass = Platform(x * size, y * size, 'grass_ground_right_up.png')
                ground_group.add(grass)
                platform_list.append(grass)

            elif tile == '7':
                grass = Platform(x * size, y * size, 'grass_ground_right_left_up.png')
                ground_group.add(grass)
                platform_list.append(grass)

            elif tile == '8':
                grass = Platform(x * size, y * size, 'ground_left_down.png')
                ground_group.add(grass)
                platform_list.append(grass)

            elif tile == '9':
                grass = Platform(x * size, y * size, 'ground_right_down.png')
                ground_group.add(grass)
                platform_list.append(grass)

            elif tile == '5':
                coin = Platform(x * size, y * size, 'coin.png')
                coins_group.add(coin)
                platform_list.append(coin)

            elif tile == '6':
                flag = Platform(x * size, y * size, 'flag.png')
                door_group.add(flag)
                platform_list.append(flag)

            x += 1
        y += 1
    return ground_group, coins_group, door_group, platform_list


platform_list = []


class Platform(pygame.sprite.Sprite):
    def __init__(self, x_loc, y_loc, image):
        super().__init__()
        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect()
        self.rect.x = x_loc
        self.rect.y = y_loc
        self.movex = 0
        self.movey = 0

    def update(self):
        self.rect.x -= scroll[0]
        self.rect.y -= scroll[1]


class Coins(pygame.sprite.Sprite):
    def __init__(self, x_loc, y_loc):
        super().__init__()
        self.image = pygame.image.load('coin.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect()
        self.rect.x = x_loc
        self.rect.y = y_loc


particles = []


class MainCharac(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.image.load('16x16_pacman_right.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

        self.movex = 0
        self.movey = 0

        self.is_jumping = False

        self.undo = False

        self.can_move = True

        self.coin_score = 0

        self.gravity = 1
        self.is_moving = False

        self.start_time = pygame.time.get_ticks()
        self.door_colliding_ = pygame.sprite.spritecollide(self, door_group, False)

        self.jumped = 0

    def jumping(self):

        if self.is_jumping:
            self.is_moving = True
            self.movey = -17
            self.jumped = 0
            self.is_jumping = False

    def move_on_x(self, x):
        self.movex = x

    def update(self):

        ground_collide = pygame.sprite.spritecollide(self, ground_group, False)
        if ground_collide:
            self.is_jumping = True

        if self.undo:
            self.start_time = pygame.time.get_ticks()
            for i in door_group:
                door_group.remove(i)
                for row in game_map:
                    for i in range(len(game_map)):
                        for o in range(len(row)):
                            if game_map[i - 1][o - 1] == '6':
                                game_map[i - 1][o - 1] = '-'

            platform_list.clear()
            ground_group.empty()
            coins_group.empty()
            door_group.empty()

            flag_exists = False

            for row in game_map:
                while not flag_exists:
                    a = random.randint(0, len(row) - 1)
                    l = random.randint(0, len(game_map) - 1)

                    if game_map[l][a] == '-':
                        game_map[l][a] = '6'
                        flag_exists = True

            self.image = pygame.image.load("16x16_pacman_right.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (size, size))
            self.rect.center = (random.randint(200, 100 * size), random.randint(200, 50 * size))

            self.undo = False
            self.can_move = True
            self.coin_score = 0
            create_map()

        if self.can_move:

            self.rect.x -= scroll[0]
            self.rect.y -= scroll[1]

            self.rect.x += self.movex

            ground_collide = pygame.sprite.spritecollide(self, ground_group, False)
            # if ground_collide:
            #     self.touched_ground = pygame.time.get_ticks()

            for block in ground_collide:

                if self.rect.x < block.rect.x:
                    self.rect.x -= self.movex
                    # self.movex = 0
                    self.rect.x = block.rect.x - size

                elif self.rect.x > block.rect.x:
                    self.rect.x -= -self.movex
                    #
                    # self.movex = 0
                    self.rect.x = block.rect.x + size

            self.rect.y += self.movey

            ground_collide = pygame.sprite.spritecollide(self, ground_group, False)

            for block in ground_collide:
                if self.movey < 0:

                    self.rect.y = block.rect.y + size
                    self.movey = 0

                elif self.movey > 0:
                    self.is_jumping = True

                    self.rect.y = block.rect.y - size
                    self.movey = 0

            if not ground_collide:
                self.is_jumping = False

            self.movey += self.gravity

            # colliding coins

            coin_colliding = pygame.sprite.spritecollide(self, coins_group, True)
            if coin_colliding:
                for a_coin in coin_colliding:
                    self.coin_score += 1

    def undo_win(self):
        end_game_surface.set_alpha(0)

    def door_colliding(self):
        self.door_colliding_ = pygame.sprite.spritecollide(self, door_group, False)

        if self.door_colliding_:
            end_game_surface.set_alpha(200)
            pygame.Surface.fill(end_game_surface, (0, 0, 0))
            end_game_surface.blit(text, text_rect)
            millis = ticks % 1000
            seconds = int(ticks / 1000 % 60)
            minutes = int(ticks / 60000 % 24)
            out = '{minutes:02d}{seconds:02d}{millis}'.format(minutes=minutes, millis=millis, seconds=seconds)
            score_text_time = font.render(f'''You did it in  {out}''', False, white)
            score_text_time_rect = score_text_time.get_rect()
            score_text_time_rect.center = (window_width / 2, window_height / 2)
            end_game_surface.blit(score_text_time, score_text_time_rect)

            best_score = open('best_score.txt', 'w+')
            data = best_score.read()
            data = data.split('\n')
            time_list = []
            for row in data:
                time_list.append(row)
            # best_score.close()
            print(time_list[0])
            if not time_list[0]:
                # best_score = open('best_score.txt', 'w+')
                best_score.write(str(ticks))
                # best_score.close()

            elif ticks < int(time_list[0]):
                # best_score = open('best_score.txt', 'w+')
                best_score.write(str(ticks))
                # best_score.close()

            # best_score = open('best_score.txt', 'r')
            data = best_score.read()
            millis_1 = int(data) % 1000
            seconds_1 = int(int(data) / 1000 % 60)
            minutes_1 = int(int(data) / 60000 % 24)
            the_best_score = '{minutes:02d}:{seconds:02d}:{millis}'.format(minutes=minutes_1, millis=millis_1, seconds=seconds_1)
            best_score_text = font.render(f'''Best score: {the_best_score}''', False, white)
            best_score_text_rect = best_score_text.get_rect()
            best_score_text_rect.center = (window_width / 2, window_height - window_height / 3)
            end_game_surface.blit(best_score_text, best_score_text_rect)

            best_score.close()

            screen.blit(end_game_surface, (0, 0))
            self.can_move = False


class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, size_x, size_y, place_x, place_y):
        super().__init__()
        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (size_x, size_y))  # add a size to where you want to resize
        self.rect = self.image.get_rect()
        self.rect.center = (place_x, place_y)
        self.movex = 0
        self.movey = 0
        self.count_move = 0

    def movement(self):

        distance = 50
        speed = 5

        if self.count_move >= 0 and self.count_move <= distance:
            self.rect.x += speed
        elif self.count_move >= distance and self.count_move <= distance * 2:
            self.rect.x -= speed
        else:
            self.count_move = 0

        self.count_move += 1


# screen setup

blockx = 64
blocky = size

guy = MainCharac(300, 300, size, main_charac_height)

guy_group = pygame.sprite.Group()
guy_group.add(guy)

steps = 10

main_menu = MainMenu()

main_menu_group = pygame.sprite.Group()
main_menu_group.add(main_menu)

font = pygame.font.Font('ka1.ttf', 48)
text = font.render('PLAY AGAIN ', False, white)
text_rect = text.get_rect()
text_rect.center = (window_width / 2, window_height / 3)

start_new_game = font.render('PLAY ', False, white)
start_new_game_rect = start_new_game.get_rect()
start_new_game_rect.center = (window_width / 2, window_height / 3)

count_coins = font.render(f'Time : ', False, white)
count_coins_rect = count_coins.get_rect()
count_coins_rect.topleft = (0, 0)

end_game = False
move_platforms_right = False
move_platforms_left = False

right = False
left = False
jump = False

while not end_game:

    screen.fill(black)

    screen_2.fill(black)

    true_scroll[0] += (guy.rect.x - true_scroll[0] - 400)
    true_scroll[1] += (guy.rect.y - true_scroll[1] - 300)
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    if guy.is_moving:
        particles.append([[guy.rect.centerx, guy.rect.centery], [random.randint(-3, 3), random.randint(-3, 3)], [random.randint(20, 25), random.randint(20, 30)]])

    for particle in particles:
        if color[3] > 0:
            color[3] -= 1
        particle[0][0] += particle[1][0]
        particle[0][1] += particle[1][1]
        particle[2][0] -= 1
        particle[2][1] -= 1
        pygame.draw.rect(screen_2, color, (int(particle[0][0]), int(particle[0][1]), int(particle[2][0]), int(particle[2][1])))
        if particle[2][0] <= 0 or particle[2][1] <= 0:
            particles.remove(particle)
    screen.blit(screen_2, (0, 0))

    if guy.is_moving:
        color[3] = 255

    if guy.can_move:
        for i in platform_list:
            i.update()
    guy_group.update()

    coins_group.draw(screen)
    ground_group.draw(screen)
    door_group.draw(screen)
    if not guy.door_colliding_:
        ticks = pygame.time.get_ticks() - guy.start_time
        millis = ticks % 1000
        seconds = int(ticks / 1000 % 60)
        minutes = int(ticks / 60000 % 24)
        out = '{minutes:02d}:{seconds:02d}:{millis}'.format(minutes=minutes, millis=millis, seconds=seconds)
        count_time = font.render(out, False, white)
        screen.blit(count_time, (0, 0))

    for event in pygame.event.get():
        if event.type == QUIT:
            end_game = True

        if event.type == JOYBUTTONDOWN:
            if event.button == 1:
                guy.jumping()

        if event.type == JOYBUTTONUP:
            if event.button == 1:
                guy.is_moving = False

        if event.type == JOYAXISMOTION:
            analog_keys[event.axis] = event.value
            if abs(analog_keys[0]) > .4:
                if analog_keys[0] > 0.7:
                    guy.move_on_x(10)
                    move_platforms_left = True
                    guy.image = pygame.image.load("16x16_pacman_right.png").convert_alpha()
                    guy.image = pygame.transform.scale(guy.image, (size, size))
                    guy.is_moving = True
                elif analog_keys[0] < - 0.7:
                    guy.move_on_x(-10)
                    move_platforms_right = True
                    guy.image = pygame.image.load("16x16_pacman_left.png").convert_alpha()
                    guy.image = pygame.transform.scale(guy.image, (size, size))
                    guy.is_moving = True
            else:
                guy.move_on_x(-0)
                move_platforms_left = False
                move_platforms_right = False
                guy.is_moving = False

        if event.type == KEYDOWN:
            if event.key == K_RIGHT or event.key == K_d:
                guy.move_on_x(10)
                move_platforms_left = True
                guy.image = pygame.image.load("16x16_pacman_right.png").convert_alpha()
                guy.image = pygame.transform.scale(guy.image, (size, size))
                guy.is_moving = True

            if event.key == K_LEFT or event.key == K_a:
                guy.move_on_x(-10)
                move_platforms_right = True
                guy.image = pygame.image.load("16x16_pacman_left.png").convert_alpha()
                guy.image = pygame.transform.scale(guy.image, (size, size))
                guy.is_moving = True

            if event.key == K_SPACE:
                guy.jumped = pygame.time.get_ticks()
                guy.jumping()

            if event.key == K_q:
                main_menu.start_again = True

        if event.type == KEYUP:
            if event.key == K_RIGHT or event.key == K_d:
                guy.move_on_x(-0)
                move_platforms_left = False
                guy.is_moving = False

            if event.key == K_LEFT or event.key == K_a:
                guy.move_on_x(0)
                move_platforms_right = False
                guy.is_moving = False

            if event.key == K_SPACE:
                guy.is_moving = False

        if event.type == MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if text_rect.collidepoint(mouse_pos):
                guy.undo = True
                guy.can_move = True
            if start_new_game_rect.collidepoint(mouse_pos):
                main_menu.start_a_game = True
                guy.undo = True
                main_menu.start_again = False

    if guy.undo:
        guy.undo_win()

    if main_menu.start_again:
        main_menu.again()

    guy_group.draw(screen)

    guy.door_colliding()

    main_menu.update()

    pygame.display.update()
    clock.tick(fps)

pygame.quit()
quit()
