#!/usr/bin/env python3.7

import pygame
from pygame.locals import *
import random

pygame.init()

pygame.mixer.init()

clock = pygame.time.Clock()

fps = 30

window_width = 1216
window_height = 608

black = (0, 0, 0)
white = (255, 255, 255)

main_charac_height = 32
main_charac_width = 32

size = 32

ani = 4

screen_2 = pygame.Surface((window_width, window_height), SRCALPHA)
screen = pygame.display.set_mode((window_width, window_height), RESIZABLE)
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
guy_group = pygame.sprite.Group()

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
    return ground_group, coins_group, door_group, platform_list, guy_group


def find_location():
    guy_x = random.randint(300, 3000)
    guy_y = 300
    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == '/':
                guy_x = x * size
                guy_y = y * size

            x += 1
        y += 1

    return guy_x, guy_y


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


particles = []

guy_location = find_location()


class MainCharac(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.frame = 0
        self.images = []
        for i in range(1, 5):
            img = pygame.image.load('dino_' + str(i) + '.png').convert_alpha()
            img = pygame.transform.scale(img, (size, size))
            self.images.append(img)
            self.image = self.images[0]
            self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

        self.movex = 0
        self.movey = 0

        self.can_jump = False

        self.undo = False

        self.can_move = True

        self.coin_score = 0

        self.gravity = 1
        self.is_moving = False

        self.start_time = pygame.time.get_ticks()
        self.door_colliding_ = pygame.sprite.spritecollide(self, door_group, False)

        self.jump_sound = pygame.mixer.Sound('jump_sound_1.wav')

    def jumping(self):

        if self.can_jump:
            self.is_moving = True
            self.jump_sound.play()
            self.movey = -17
            self.can_jump = False

    def move_on_x(self, x):
        self.movex = x

    def update(self):

        if self.undo:

            for row in game_map:
                for i in range(len(game_map)):
                    for o in range(len(row)):
                        if game_map[i - 1][o - 1] == '6':
                            game_map[i - 1][o - 1] = '-'
                        elif game_map[i - 1][o - 1] == '/':
                            game_map[i - 1][o - 1] = '0'

            platform_list.clear()
            ground_group.empty()
            coins_group.empty()
            door_group.empty()

            platform_list.append(self)

            flag_exists = False
            charac_exists = False

            for row in game_map:
                while not flag_exists:
                    a = random.randint(0, len(row) - 1)
                    l = random.randint(0, len(game_map) - 1)

                    if game_map[l][a] == '-':
                        game_map[l][a] = '6'
                        flag_exists = True
                while not charac_exists:
                    a = random.randint(0, len(row) - 1)
                    l = random.randint(0, len(game_map) - 1)

                    if game_map[l][a] == '0':
                        game_map[l][a] = '/'
                        charac_exists = True

            create_map()
            guy_location = find_location()

            self.start_time = pygame.time.get_ticks()

            self.image = self.images[0]

            self.rect.center = guy_location[0], guy_location[1]
            self.undo = False
            self.can_move = True
            self.coin_score = 0

        if self.can_move:

            self.rect.x += self.movex

            ground_collide = pygame.sprite.spritecollide(self, ground_group, False)

            for block in ground_collide:

                if self.rect.x < block.rect.x:
                    self.rect.x -= self.movex
                    self.rect.x = block.rect.x - size

                elif self.rect.x > block.rect.x:
                    self.rect.x -= -self.movex
                    self.rect.x = block.rect.x + size

            self.rect.y += self.movey

            ground_collide = pygame.sprite.spritecollide(self, ground_group, False)

            for block in ground_collide:
                if self.movey < 0:

                    self.rect.y = block.rect.y + size
                    self.movey = 0

                elif self.movey > 0:
                    self.can_jump = True

                    self.rect.y = block.rect.y - size
                    self.movey = 0

            self.movey += self.gravity

            if not ground_collide:
                self.can_jump = False

            # colliding coins

            coin_colliding = pygame.sprite.spritecollide(self, coins_group, True)
            if coin_colliding:
                for a_coin in coin_colliding:
                    self.coin_score += 1

            # flipping image to a direction you are going in
            if self.movex < 0:
                self.frame += 1
                if self.frame > 3*ani:
                    self.frame = 0
                self.image = pygame.transform.flip(self.images[self.frame // ani], True, False)

            if self.movex > 0:
                self.frame += 1
                if self.frame > 3 * ani:
                    self.frame = 0
                self.image = self.images[self.frame//ani]

    def undo_win(self):
        window_width, window_height = pygame.display.get_window_size()
        end_game_surface = pygame.Surface((window_width, window_height))
        end_game_surface.set_alpha(0)

    def door_colliding(self, ticks):
        window_width, window_height = pygame.display.get_window_size()
        end_game_surface = pygame.Surface((window_width, window_height))
        font = pygame.font.Font('ka1.ttf', int(window_height / 105) * 10)

        text = font.render('PLAY AGAIN ', False, white)
        text_rect = text.get_rect()
        text_rect.center = (window_width / 2, window_height / 3)

        end_game_surface.set_alpha(200)
        pygame.Surface.fill(end_game_surface, (0, 0, 0))
        end_game_surface.blit(text, text_rect)
        millis = ticks % 1000
        seconds = int(ticks / 1000 % 60)
        minutes = int(ticks / 60000 % 24)
        out = '{minutes:02d}:{seconds:02d}:{millis}'.format(minutes=minutes, millis=millis, seconds=seconds)
        score_text_time = font.render(f'''You did it in  {out}''', False, white)
        score_text_time_rect = score_text_time.get_rect()
        score_text_time_rect.center = (window_width / 2, window_height / 2)
        end_game_surface.blit(score_text_time, score_text_time_rect)
        best_score = open('best_score.txt', 'r')
        data = best_score.read()
        data = data.split('\n')
        time_list = []
        for row in data:
            time_list.append(row)
        best_score.close()

        if time_list[0] == '':
            best_score = open('best_score.txt', 'w+')
            best_score.write(str(ticks))
            best_score.close()

        elif ticks < int(time_list[0]):
            best_score = open('best_score.txt', 'w+')
            best_score.write(str(ticks))
            best_score.close()

        best_score = open('best_score.txt', 'r')
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

# screen setup

speed = 10

guy = MainCharac(guy_location[0], guy_location[1], size, main_charac_height)
guy_group.add(guy)

font = pygame.font.Font('ka1.ttf', int(window_height / 105) * 10)

count_coins = font.render(f'Time : ', False, white)
count_coins_rect = count_coins.get_rect()
count_coins_rect.topleft = (0, 0)

background_music = pygame.mixer.Sound("background_music.wav")


def play():
    running = True

    while running:
        window_width, window_height = pygame.display.get_window_size()

        text = font.render('PLAY AGAIN ', False, white)
        text_rect = text.get_rect()
        text_rect.center = (window_width / 2, window_height / 3)

        screen.fill(black)

        screen_2.fill(black)

        true_scroll[0] += (guy.rect.x - true_scroll[0] - window_width / 3)
        true_scroll[1] += (guy.rect.y - true_scroll[1] - window_height / 2)
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        if guy.is_moving:
            particles.append([[guy.rect.centerx, guy.rect.centery], [random.randint(-3, 3), random.randint(-3, 3)],
                              [random.randint(20, 25), random.randint(20, 30)]])

        for particle in particles:
            if color[3] > 0:
                color[3] -= 1
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2][0] -= 1
            particle[2][1] -= 1
            pygame.draw.rect(screen_2, color,
                             (int(particle[0][0]), int(particle[0][1]), int(particle[2][0]), int(particle[2][1])))
            if particle[2][0] <= 0 or particle[2][1] <= 0:
                particles.remove(particle)
        screen.blit(screen_2, (0, 0))

        if guy.is_moving:
            color[3] = 255

        if guy.can_move:
            for i in platform_list:
                i.rect.x -= scroll[0]
                i.rect.y -= scroll[1]

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
                running = False
                pygame.quit()
                quit()

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
                        guy.move_on_x(speed)
                        guy.is_moving = True
                    elif analog_keys[0] < - 0.7:
                        guy.move_on_x(-speed)
                        guy.is_moving = True
                else:
                    guy.move_on_x(-0)
                    guy.is_moving = False

            if event.type == KEYDOWN:
                if event.key == K_RIGHT or event.key == K_d:
                    guy.move_on_x(speed)
                    guy.is_moving = True

                if event.key == K_LEFT or event.key == K_a:
                    guy.move_on_x(-speed)
                    guy.is_moving = True

                if event.key == K_SPACE:
                    guy.jumping()

                if event.key == K_q or event.key == K_ESCAPE:
                    background_music.stop()
                    main_menu()

            if event.type == KEYUP:
                if event.key == K_RIGHT or event.key == K_d:
                    guy.move_on_x(-0)
                    guy.is_moving = False

                if event.key == K_LEFT or event.key == K_a:
                    guy.move_on_x(0)
                    guy.is_moving = False

                if event.key == K_SPACE:
                    guy.is_moving = False

            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if text_rect.collidepoint(mouse_pos):
                    background_music.stop()
                    background_music.play(-1)
                    guy.undo = True
                    play()

        if guy.undo:
            guy.undo_win()

        guy_group.draw(screen)
        guy.door_colliding_ = pygame.sprite.spritecollide(guy, door_group, False)
        if guy.door_colliding_:

            guy.door_colliding(ticks)

        pygame.display.update()
        clock.tick(fps)


def how_to_play():
    running = True

    first_img = True
    second_img = False

    while running:
        window_width, window_height = pygame.display.get_window_size()
        img_size = int(window_height / 2)

        how_to_play_img_1 = pygame.image.load('how_to_play_1.png').convert_alpha()
        how_to_play_img_1 = pygame.transform.scale(how_to_play_img_1, (img_size, img_size))
        how_to_play_img_1_rect = how_to_play_img_1.get_rect()
        how_to_play_img_1_rect.center = (window_width / 2, window_height / 2)

        how_to_play_img_2 = pygame.image.load('how_to_play_2.png').convert_alpha()
        how_to_play_img_2 = pygame.transform.scale(how_to_play_img_2, (img_size, img_size))
        how_to_play_img_2_rect = how_to_play_img_2.get_rect()
        how_to_play_img_2_rect.center = (window_width / 2, window_height / 2)

        left_arrow_img = pygame.image.load('left_arrow.png').convert_alpha()
        left_arrow_img = pygame.transform.scale(left_arrow_img, (64, 64))
        left_arrow_img_rect = left_arrow_img.get_rect()
        left_arrow_img_rect.center = (window_width / 4, window_height / 2)

        right_arrow_img = pygame.image.load('right_arrow.png').convert_alpha()
        right_arrow_img = pygame.transform.scale(right_arrow_img, (64, 64))
        right_arrow_img_rect = right_arrow_img.get_rect()
        right_arrow_img_rect.center = (window_width - window_width / 4, window_height / 2)

        how_to_play_text = font.render('HOW TO PLAY ', False, white)
        how_to_play_text_rect = how_to_play_text.get_rect()
        how_to_play_text_rect.center = (window_width / 2, window_height / 5)

        screen.fill(black)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                pygame.quit()
                quit()

            if event.type == KEYDOWN:

                if event.key == K_q or event.key == K_ESCAPE:
                    main_menu()

                if event.key == K_RIGHT or event.key == K_LEFT:
                    if first_img:
                        second_img = True
                        first_img = False
                    elif second_img:
                        first_img = True
                        second_img = False

            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if right_arrow_img_rect.collidepoint(mouse_pos) or left_arrow_img_rect.collidepoint(mouse_pos):
                    if first_img:
                        second_img = True
                        first_img = False
                    elif second_img:
                        first_img = True
                        second_img = False

        if first_img:
            screen.blit(how_to_play_img_1, how_to_play_img_1_rect)
        elif second_img:
            screen.blit(how_to_play_img_2, how_to_play_img_2_rect)
        screen.blit(left_arrow_img, left_arrow_img_rect)
        screen.blit(right_arrow_img, right_arrow_img_rect)

        screen.blit(how_to_play_text, how_to_play_text_rect)

        pygame.display.update()
        clock.tick(fps)


def main_menu():
    running = True

    while running:
        window_width, window_height = pygame.display.get_window_size()
        img_size = int(window_height / 4)

        jumpman_light = pygame.image.load('jumpman_light.png').convert_alpha()
        jumpman_light = pygame.transform.scale(jumpman_light, (int(img_size * 4), img_size))
        jumpman_light_rect = jumpman_light.get_rect()
        jumpman_light_rect.center = (window_width / 2, window_height / 5)

        start_new_game = font.render('PLAY ', False, white)
        start_new_game_rect = start_new_game.get_rect()
        start_new_game_rect.center = (window_width / 2, window_height / 3)

        how_to_play_text = font.render('HOW TO PLAY ', False, white)
        how_to_play_text_rect = how_to_play_text.get_rect()
        how_to_play_text_rect.center = (window_width / 2, window_height / 2)

        screen.fill(black)

        best_score = open('best_score.txt', 'r')
        data = best_score.read()
        data = data.split('\n')
        time_list = []
        for row in data:
            time_list.append(row)
        best_score.close()

        if time_list[0] == '':
            blit_best_score = False
        else:

            best_score = open('best_score.txt', 'r')
            data = best_score.read()
            millis_1 = int(data) % 1000
            seconds_1 = int(int(data) / 1000 % 60)
            minutes_1 = int(int(data) / 60000 % 24)
            the_best_score = '{minutes:02d}:{seconds:02d}:{millis}'.format(minutes=minutes_1, millis=millis_1, seconds=seconds_1)
            best_score_text = font.render(f'''Best score: {the_best_score}''', False, white)
            best_score_text_rect = best_score_text.get_rect()
            best_score_text_rect.center = (window_width / 2, window_height - window_height / 3)

            best_score.close()
            blit_best_score = True

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                pygame.quit()
                quit()

            if event.type == KEYDOWN:

                if event.key == K_q or event.key == K_ESCAPE:
                    background_music.stop()

            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if start_new_game_rect.collidepoint(mouse_pos):
                    background_music.stop()
                    background_music.play(-1)
                    guy.undo = True
                    play()

                if how_to_play_text_rect.collidepoint(mouse_pos):
                    how_to_play()

        screen.blit(start_new_game, start_new_game_rect)
        screen.blit(how_to_play_text, how_to_play_text_rect)
        if blit_best_score:
            screen.blit(best_score_text, best_score_text_rect)
        screen.blit(jumpman_light, jumpman_light_rect)

        pygame.display.update()
        clock.tick(fps)


main_menu()
