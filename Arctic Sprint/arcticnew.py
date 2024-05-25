import pygame, sys
import random
import os 
pygame.init()
pygame.display.set_caption("ARCTIC SPRINT")

clock = pygame.time.Clock()

WIDTH = 1000
HEIGHT = 600
GROUND_HEIGHT = HEIGHT - 70

PLAY_GAME = True
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=200)
pygame.mixer.set_num_channels(4)

pygame.mixer.latency = 10

jump_sound = pygame.mixer.Sound("sound/jump.ogg")
bg_sound= pygame.mixer.Sound("sound/bg.ogg")


FPS = 30
FALL_SPEED = 4
MAX_SIZE_SNOW = 5
SNOW_NUM = WIDTH//4
snow_list = []

for i in range(SNOW_NUM):
    snow_list.append([
        random.randrange(0, WIDTH),
        random.randrange(0, HEIGHT),
        random.randrange(0, MAX_SIZE_SNOW),
        random.randrange(-1, 2)
    ])

screen = pygame.display.set_mode([WIDTH, HEIGHT])

def draw_text(text, size, text_color, position_x, position_y, position):

    font = pygame.font.Font()  

    text_plane = font.render(text, True, text_color)  
    text_rect = text_plane.get_rect()

    
    if position == "midtop":
        text_rect.midtop = (int(position_x), int(position_y))
    elif position == "topright":
        text_rect.topright = (int(position_x), int(position_y))

    screen.blit(text_plane, text_rect)

def load_image(path, size_x=0, size_y=0):

    image = pygame.image.load(path).convert_alpha()  

    if size_x > 0 and size_y > 0:
        image = pygame.transform.scale(image, (size_x, size_y))  

    return image, image.get_rect()

def load_sprites(image_path, image_name_prefix, number_of_image, size_x=0, size_y=0):

    images = []  

    for i in range(0, number_of_image):

        path = image_path + image_name_prefix + str(i) + ".png" 
        image = pygame.image.load(path).convert_alpha()  

        if size_x > 0 and size_y > 0:
            image = pygame.transform.scale(image, (size_x, size_y))  
        images.append(image)

    return images

class Background:

    def __init__(self, image_path, speed=10):

        self.image0, self.rect0 = load_image(image_path, 1280, 720)
        self.image1, self.rect1 = load_image(image_path, 1280, 720)


        self.rect0.bottom = HEIGHT
        self.rect1.bottom = HEIGHT 

        self.rect1.left = self.rect0.right

        self.speed = speed

    def draw(self):
        screen.blit(self.image0, self.rect0)
        screen.blit(self.image1, self.rect1)

    def update(self):

        self.rect0.left -= int(self.speed)
        self.rect1.left -= int(self.speed)

        if self.rect0.right < 0:
            self.rect0.left = self.rect1.right

        if self.rect1.right < 0:
            self.rect1.left = self.rect0.right

class AllBackgrounds:

    def __init__(self, game_speed):

        self.background_0 = Background("images/mount_1.png", game_speed)
        self.background_1 = Background("images/path.png", game_speed )
        self.background_1.rect0.bottom = HEIGHT + 180
        self.background_1.rect1.bottom = HEIGHT + 180

    def update_speed(self, speed):

        self.background_0.speed = speed
        self.background_1.speed = speed 
    

    def draw(self):

        self.background_0.draw()
        self.background_1.draw()

    def update(self):

        self.background_0.update()
        self.background_1.update()

class Obstacles:

    def __init__(self, speed=10):

        self.obstacles_images = load_sprites("images/obstacles/", "obstacles_", 4, 90,110)
        sizes = [(70, 60), (70, 80), (100, 150), (100, 70)]

        self.obstacles_images = [pygame.transform.scale(image, size) for image, size in zip(self.obstacles_images, sizes)]

        self.obstacles_image_0, self.rect_0 = self.obstacles_images[0], self.obstacles_images[0].get_rect()
        self.obstacles_image_1, self.rect_1 = self.obstacles_images[1], self.obstacles_images[1].get_rect()

        self.rect_0.bottomleft = (WIDTH, GROUND_HEIGHT-70)
        self.rect_1.bottomleft = (int(WIDTH / 2), GROUND_HEIGHT-70)

        self.speed = speed

        self.range_0 = 200
        self.range_1 = 400

    def get_obstacles(self):
        current_obstacle = [self.obstacles_image_0, self.obstacles_image_1]
        obstacle_rect = [self.rect_0, self.rect_1]

        return current_obstacle, obstacle_rect 

    def update_speed(self, speed):
        self.speed = speed
        self.range_0 += 1
        self.range_1 += 1

    def draw(self):
        # blitting once and we obtain the same result as before
        screen.blit(self.obstacles_image_0, self.rect_0)
        screen.blit(self.obstacles_image_1, self.rect_1)
        
        

    def update(self):

        self.rect_0.left -= int(self.speed)
        self.rect_1.left -= int(self.speed)

        if self.rect_0.right < 0:

            temp_position = self.rect_1.right + random.randrange(self.range_0, self.range_1)

            if temp_position > WIDTH:
                self.rect_0.left = temp_position
            else:
                self.rect_0.left = WIDTH

            temp_index = random.randrange(0, 4) 
            self.obstacles_image_0 = self.obstacles_images[temp_index]
            self.rect_0 = self.obstacles_image_0.get_rect(bottomleft= (self.rect_0.left, GROUND_HEIGHT-70))

        if self.rect_1.right < 0:

            temp_position = self.rect_0.right + random.randrange(self.range_0, self.range_1)

            if temp_position > WIDTH:
                self.rect_1.left = temp_position
            else:
                self.rect_1.left = WIDTH

            temp_index = random.randrange(0, 4) 
            self.obstacles_image_1 = self.obstacles_images[temp_index]
            self.rect_1 = self.obstacles_image_1.get_rect(bottomleft= (self.rect_1.left, GROUND_HEIGHT-70))

class Penguin:

    def __init__(self):

        self.running_images = load_sprites("images/penguin/", "penguin_", 1, 50, 70)
        self.jumping_images = load_sprites("images/penguin/", "penguin_",  1, 50, 70)
        self.rect = self.running_images[0].get_rect()
        self.rect.bottom = GROUND_HEIGHT - 75
        self.rect.left = 70

        self.jump_limit = GROUND_HEIGHT - 300
        self.jump_speed = 40
        self.gravity_up = 3
        self.gravity_down = 3

        self.running_index = 0
        self.jumping_index = 0

        self.running = False
        self.jumping = False
        self.falling = False

        self.call_count = 0  

    def check_collision(self, all_obstacles):
        # i just erased the weird stuff of this function
        if self.running:
            peng_mask = pygame.mask.from_surface(self.running_images[self.running_index])
        else: 
            peng_mask = pygame.mask.from_surface(self.jumping_images[self.jumping_index])

        current_obstacle, obstacle_rect = all_obstacles
        offset_0 = (obstacle_rect[0].left - self.rect.left, obstacle_rect[0].top - self.rect.top)
        offset_1 = (obstacle_rect[1].left - self.rect.left, obstacle_rect[1].top - self.rect.top)
        collide = peng_mask.overlap(pygame.mask.from_surface(current_obstacle[0]), offset_0) or \
            peng_mask.overlap(pygame.mask.from_surface(current_obstacle[1]), offset_1)

        return collide

    def draw(self):

        if self.running:
            screen.blit(self.running_images[self.running_index], self.rect)
        else :
            screen.blit(self.jumping_images[self.jumping_index], self.rect)

    def update(self):

        if self.running and self.call_count % 3 == 0:
           self.running_index = (self.running_index + 1) % len(self.running_images)

        elif self.jumping:
            
            if not self.falling:
                self.rect.bottom -= self.jump_speed

                if self.jump_speed >= self.gravity_up:
                    self.jump_speed -= self.gravity_up

                if self.rect.bottom < self.jump_limit:
                    self.jump_speed = 0
                    self.falling = True
            else:
                self.rect.bottom += self.jump_speed
                self.jump_speed += self.gravity_down

                if self.rect.bottom > GROUND_HEIGHT - 75:
                    self.rect.bottom = GROUND_HEIGHT - 75
                    self.jump_speed = 40
                    self.jumping_index = 0  
                    self.running_index = 0
                    self.jumping = False
                    self.falling = False
                    self.running = True

            if self.call_count % 2 == 0 or self.call_count % 3 == 0:
                if len(self.jumping_images) > 1: 
                    self.jumping_index = (self.jumping_index + 1) % len(self.jumping_images)

        self.call_count += 1

class Score:
    def __init__(self):
        self.rect_high = pygame.Rect(WIDTH - 15, 20, 0, 0)  
        self.rect_current = pygame.Rect(WIDTH - 15, 65, 0, 0)  

        self.high_score = 0
        self.score = 0
        self.load()

        self.high_score_achieved = False
        self.call_count = 0

    def count(self):

        if self.call_count % 2 == 0:

            self.score += 1

            if self.high_score_achieved:
                self.high_score = self.score

            elif self.score > self.high_score:
                self.high_score = self.score
                self.high_score_achieved = True

        self.call_count = self.call_count + 1

    def draw(self):

        draw_text(str(self.high_score), 28, (19, 130, 98), WIDTH - 60, 20, "topright")
        draw_text(str(self.score), 28, (19, 130, 98), WIDTH - 60, 65, "topright")

    def load(self):
        
        try:
            with open("high_score.txt", "r") as file:
                self.high_score = int(file.read())
        except (IOError, ValueError):
            self.high_score = 0

    def save(self):
        
        if self.high_score_achieved:
            with open("high_score.txt", "w") as file:
                file.write(str(self.high_score))


class GameOver:

    def __init__(self):
        self.replay_image, self.rect_a = load_image("images/game_over/replay.png", 200, 70)

        self.rect_a.center = (int(WIDTH/2), int(HEIGHT/2))

        self.game_over, self.rect_b = load_image("images/game_over/gameover.png", 220, 60)

        self.rect_b.midtop = (int(WIDTH/2), int(HEIGHT/4))

        

    def draw(self, screen, high_score, current_score):
        screen.blit(self.game_over, self.rect_b)
        screen.blit(self.replay_image, self.rect_a)
        draw_text("High Score: " + str(high_score), 28, (255, 0, 0), 500, 500, "midtop")
        draw_text("Current Score: " + str(current_score), 28, (255, 0, 0), 510, 510, "midtop")


class StartGame:

    def __init__(self):
        self.start, self.rect_c = load_image("images/game_over/startgame.png", 200, 70)

        self.rect_c.midtop = (int(WIDTH/2), int(HEIGHT/4))

        self.play_game, self.rect_d = load_image("images/game_over/play.png", 220, 60)

        self.rect_d.center = (int(WIDTH/2), int(HEIGHT/2))

        self.instrctions_pic, self.rect_e = load_image("images/game_over/instructions.png", 220, 100)

        self.rect_e.center = (300, 420)

        self.speaker_pic, self.rect_f = load_image("images/game_over/speaker.png", 50, 40)

        self.rect_f.topleft = (70, 50)

    def draw(self):
        screen.blit(self.start, self.rect_c)
        screen.blit(self.play_game, self.rect_d)
        screen.blit(self.instrctions_pic, self.rect_e)
        screen.blit(self.speaker_pic, self.rect_f)


PLAY_GAME = True



def start_game():
    bg_sound.play()
    run = True
    play_again = False
    game_over = False
    strt_game = True
    game_speed = 15 

    backgrounds = AllBackgrounds(game_speed)
    obstacle = Obstacles(game_speed)
    peng = Penguin()
    score = Score()
    game_over_screen = GameOver()
    start_game_screen = StartGame()
    while run:
        clock.tick(FPS)      
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit() 
                sys.exit()  
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos() 
                if strt_game:
                    if start_game_screen.rect_d.left < mx < start_game_screen.rect_d.right and \
                            start_game_screen.rect_d.top < my < start_game_screen.rect_d.bottom:
                        strt_game = False
                        game_over = False                        
                elif game_over:
                    if game_over_screen.rect_a.left < mx < game_over_screen.rect_a.right and \
                            game_over_screen.rect_a.top < my < game_over_screen.rect_a.bottom:
                        play_again = True
                        run = False

        screen.fill((179, 243, 252))

        key = pygame.key.get_pressed() 

        if key[pygame.K_SPACE] or key[pygame.K_UP]:
            if game_over:
                print('hi')
                play_again = True
                run = False
            elif not peng.jumping:
                peng.jumping = True
                jump_sound.play()
                jump_sound.set_volume(0.3)
                peng.running = False

        elif key[pygame.K_RIGHT]:
            if game_over:
                play_again = True
                run = False
            elif not peng.running:
                peng.jumping = False
                peng.running = True
            elif peng.jumping:
                    peng.running=False     

        backgrounds.draw()
        obstacle.draw()
        peng.draw()
        score.draw()

        if strt_game:
            start_game_screen.draw()
        elif game_over:
            game_over_screen.draw(screen, score.high_score, score.score)
        else:
            if peng.running or peng.jumping:
                
                score.count()   

                backgrounds.update() 
                obstacle.update()

                if score.score % 120 == 0:
                    game_speed += 0.9
                    backgrounds.update_speed(game_speed)
                    obstacle.update_speed(game_speed)
                    peng.jump_speed += 2

            peng.update()
            if peng.check_collision(obstacle.get_obstacles()):
                game_over = True
                  
                score.save()  
                game_over_screen.draw(screen, score.high_score, score.score)  


        for particle in snow_list:
            
            particle[1] += FALL_SPEED
            
            particle[0] += particle[3]
            
            if particle[1] > HEIGHT:
                particle[1] = 0                
            if particle[0] > WIDTH:
                    particle[0] = 0
            if particle[0] < 0:
                        particle[0] = WIDTH
                        
        for particle in snow_list:
            pygame.draw.circle(screen, (255, 255, 255), (particle[0], particle[1]), particle[2])

        pygame.display.flip() 

    return run, play_again

def run_again():
    bg_sound.play()
    global PLAY_AGAIN
    if PLAY_AGAIN:
        game_over = False
         # strt_game ints in false now so your code doesn't draw start_game_screen.draw()
        strt_game = False
        game_speed = 15 
        backgrounds = AllBackgrounds(game_speed)
        obstacle = Obstacles(game_speed)
        peng = Penguin()
        score = Score()
        game_over_screen = GameOver()
        start_game_screen = StartGame()
         # peng.running inits in True so penguin starts running eternally until death since the start
        peng.running = True
        while PLAY_AGAIN:
            clock.tick(FPS) 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit() 
                    sys.exit()  
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos() 
                    if strt_game:
                        if start_game_screen.rect_d.left < mx < start_game_screen.rect_d.right and \
                                start_game_screen.rect_d.top < my < start_game_screen.rect_d.bottom:
                            strt_game = False
                            game_over = False
                            return False
                    elif game_over:
                        if game_over_screen.rect_a.left < mx < game_over_screen.rect_a.right and \
                                game_over_screen.rect_a.top < my < game_over_screen.rect_a.bottom:
                            PLAY_AGAIN = True
                            return run_again()

            screen.fill((179, 243, 252))

            key = pygame.key.get_pressed() 

            if key[pygame.K_SPACE] or key[pygame.K_UP]:

                if game_over:
                    return run_again()
                elif not peng.jumping:
                    peng.jumping = True
                    jump_sound.play()
                    jump_sound.set_volume(0.3)
                    peng.running = False

            elif key[pygame.K_RIGHT]:
                    
                if game_over:
                    return run_again()
                elif not peng.running:
                    peng.jumping = False
                    peng.running = True
                elif peng.jumping:
                    peng.running=False    


            backgrounds.draw()
            obstacle.draw()
            peng.draw()
            score.draw()

            if strt_game:
                start_game_screen.draw()                
            elif game_over:
                game_over_screen.draw(screen, score.high_score, score.score)
            else:
                if peng.running or peng.jumping:
                    score.count()   

                    backgrounds.update() 
                    obstacle.update()

                    if score.score % 120 == 0:
                        game_speed += 0.9
                        backgrounds.update_speed(game_speed)
                        obstacle.update_speed(game_speed)
                        peng.jump_speed += 2

                peng.update()
                if peng.check_collision(obstacle.get_obstacles()):
                    game_over = True
                  
                    score.save()  
                    game_over_screen.draw(screen, score.high_score, score.score)  


            for particle in snow_list:
                particle[1] += FALL_SPEED
                
                particle[0] += particle[3]
                
                if particle[1] > HEIGHT:
                    particle[1] = 0                    
                if particle[0] > WIDTH:
                        particle[0] = 0
                if particle[0] < 0:
                            particle[0] = WIDTH
                            
            for particle in snow_list:
                pygame.draw.circle(screen, (255, 255, 255), (particle[0], particle[1]), particle[2])
            pygame.display.flip() 
      
RUN = True
while RUN:
    RUN, PLAY_AGAIN=start_game()

while PLAY_AGAIN:
    PLAY_AGAIN=run_again()
pygame.quit()