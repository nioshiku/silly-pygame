import pygame
import os
import random

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

RED = (178, 103, 103)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
PURPLE = (255, 0, 255)
DARK_BLUE = (0, 0, 128)
DARK_RED = (139, 0, 0)
GREEN = (103, 178, 125)
BOSS_COLOR = (108, 59, 170) 
LAVANDER = (81, 68, 138) 
MAGENTA = (202, 88, 202)
LIGHT_BLUE = (173, 216, 230)
DARK_PURPLE = (54, 15, 90)

score = 0
count = 0
SPEED = 5

BULLET_VEL = 7
ENEMY_SPEED = 2 
MAX_BULLETS = 3
PLAYER_MAX_HP = 5
player_hp = PLAYER_MAX_HP

ENEMY_HIT = pygame.USEREVENT + 1
EVENT_SPAWN = pygame.USEREVENT + 2
BOSS_HIT = pygame.USEREVENT + 3

ENEMY_HEALTH = 3
SPAWN_STEP = 10
MIN_DISTANCE = 250
BOSS_HEALTH = 30

screen = pygame.display.set_mode((WIDTH, HEIGHT))
bg_image = pygame.image.load('assets/bgg-export.png')
space_bg = pygame.image.load('assets/bgg-export.png')
coin_img = pygame.image.load('assets/coin-sprite1.png')

pygame.display.set_caption("My First Game!")
clock = pygame.time.Clock()

player = pygame.Rect(100, 275, 60, 80)
enemy = pygame.Rect(500, 450, 70, 70)
coin = pygame.Rect(400, 300, 50, 30)
boss = pygame.Rect(-1000, -1000, 110, 110) 

octo = pygame.image.load('assets/octo-thing.png').convert_alpha()
octo = pygame.transform.scale(octo, (90, 90))
marley = pygame.image.load('assets/marley-sprite-01.png').convert_alpha()
marley = pygame.transform.scale(marley, (90, 120))
bones = pygame.image.load('assets/bones.png').convert_alpha()
bones = pygame.transform.scale(bones, (180, 180))

enemy_pos = pygame.math.Vector2(enemy.x, enemy.y)
boss_pos = pygame.math.Vector2(boss.x, boss.y)

pygame.time.set_timer(EVENT_SPAWN, 10000)

font = pygame.font.SysFont("Arial", 36)
font2 = pygame.font.SysFont("Arial", 80)
end_text = font2.render("You lost!", True, DARK_PURPLE)

player_bullets = []
enemy_alive = True
played_67_sound = False
played_87_sound = False
boss_active = False
boss_channel = None

# Sounds
try:
    collected = pygame.mixer.Sound(os.path.join('assets', 'collect.ogg'))
    collected.set_volume(0.4)
    lost = pygame.mixer.Sound(os.path.join('assets', 'You_lost.ogg'))
    bullet_fire_sound = pygame.mixer.Sound(os.path.join('assets', 'shot_sound.ogg'))
    attack_sound = pygame.mixer.Sound(os.path.join('assets', 'boss_ouch.ogg')) 
    hit_sound = pygame.mixer.Sound(os.path.join('assets', 'explosion.ogg'))
    spawn_sound = pygame.mixer.Sound(os.path.join('assets', 'spawn.ogg'))
    six_seven = pygame.mixer.Sound(os.path.join('assets', 'six_seven.ogg'))
    bite87 = pygame.mixer.Sound(os.path.join('assets', 'bite87.ogg')) 

    victory = pygame.mixer.Sound(os.path.join('assets', 'fairy-victory.ogg'))
    bossf = pygame.mixer.Sound(os.path.join('assets', 'why-do-i-hear-boss-music.ogg'))
    

    pygame.mixer.music.load(os.path.join('assets','arcade_mode.ogg'))
    pygame.mixer.music.set_volume(0.4)

except Exception as e:
    print(f"Error occurred while uploading sound: {e}")
    collected = lost = bullet_fire_sound = attack_sound = hit_sound = die = spawn_sound = six_seven = None

def handle_bullets(bullets, enemy, enemy_alive, boss, boss_active):
    for bullet in bullets[:]:  
        bullet["rect"].x += bullet["dx"]
        bullet["rect"].y += bullet["dy"]

        if enemy_alive and enemy.colliderect(bullet["rect"]):
            pygame.event.post(pygame.event.Event(ENEMY_HIT))
            if bullet in bullets:
                bullets.remove(bullet)
        
        elif boss_active and boss.colliderect(bullet["rect"]):
            pygame.event.post(pygame.event.Event(BOSS_HIT))
            if bullet in bullets:
                bullets.remove(bullet)

        elif (bullet["rect"].right < 0 or bullet["rect"].left > WIDTH or 
              bullet["rect"].bottom < 0 or bullet["rect"].top > HEIGHT):
            if bullet in bullets:
                bullets.remove(bullet)

def draw_window(bullets, enemy_alive, boss_active):
    screen.blit(bg_image, (0, 0))
    
    screen.blit(marley, player)  
    screen.blit(coin_img, coin)  
   
    if enemy_alive and not boss_active:
        screen.blit(octo, enemy)

    if boss_active:
        #pygame.draw.rect(screen, BOSS_COLOR, boss)
        screen.blit(bones, boss)

        # Boss Hp Scale
        pygame.draw.rect(screen, RED, (WIDTH // 2 - 120, 20, 200, 15))
        pygame.draw.rect(screen, GREEN, (WIDTH // 2 - 120, 20, max(0, (BOSS_HEALTH / 20) * 200), 15))
    
    # Player's Hp Scale
    if boss_active:
        pygame.draw.rect(screen, RED, (20, 100, 100, 10))
        pygame.draw.rect(screen, GREEN, (20, 100, max(0, (player_hp / PLAYER_MAX_HP) * 100), 10))

    for bullet in bullets:
        pygame.draw.rect(screen, LIGHT_BLUE, bullet["rect"])
    
    score_text = font.render(f"Score: {score}", True, WHITE)
    kill_count = font.render(f"Kill count: {count}", True, WHITE)
    screen.blit(kill_count, (20, 60))
    screen.blit(score_text, (20, 20)) 

    pygame.display.flip()

def shooting(direction):
    if len(player_bullets) < MAX_BULLETS:
        bullet_size = 8
        
        center_x = (player.x + 15) + ((player.width // 2) + 30)
        center_y = (player.y + player.height // 2) + 10

        dx = 0
        dy = 0

        if direction == "UP":
            dy = -BULLET_VEL
        elif direction == "DOWN":
            dy = BULLET_VEL
        elif direction == "RIGHT":
            dx = BULLET_VEL
        elif direction == "LEFT":
            dx = -BULLET_VEL    

        rect = pygame.Rect(center_x - bullet_size // 2,
                           center_y - bullet_size // 2,
                           bullet_size, bullet_size)
        player_bullets.append({
            "rect": rect,
            "dx": dx,
            "dy": dy
        })
        if bullet_fire_sound:
            bullet_fire_sound.play()

def difficulty_update(current_score):
    global ENEMY_SPEED, ENEMY_HEALTH, SPEED, boss_active, enemy_alive, boss_pos, BOSS_HEALTH, enemies_frozen, MAX_BULLETS, boss_channel
    if current_score <= 30:
        ENEMY_HEALTH = 3
        ENEMY_SPEED = 2
        SPEED = 5
    elif 30 < current_score <= 50:
        ENEMY_HEALTH = 4
        ENEMY_SPEED = 3
        SPEED = 5
        MAX_BULLETS = 4
    elif 50 < current_score <= 100:
        ENEMY_HEALTH = 4
        ENEMY_SPEED = 4
        SPEED = 6
        MAX_BULLETS = 4
    elif 100 < current_score <= 150:
        ENEMY_HEALTH = 5
        ENEMY_SPEED = 5
        SPEED = 6
        MAX_BULLETS = 4
    elif 160 >= current_score >= 150:
        if not boss_active:
            enemy_alive = False
            enemy.x = -1000
            enemy.y = -1000

            player_pos = pygame.math.Vector2(player.x, player.y)
            boss_channel = bossf.play(-1)
                    
            while True:
                boss.x = random.randint(200, WIDTH - boss.width)
                boss.y = random.randint(0, HEIGHT - boss.height)
                boss_pos = pygame.math.Vector2(boss.x, boss.y)
                pygame.mixer.music.pause()
                    
                distance = boss_pos.distance_to(player_pos)
                if distance >= MIN_DISTANCE:
                    break

            BOSS_HEALTH = 30
            boss_active = True
    else:
        boss_active = False
        enemies_frozen = True
        win = True

def end_game(player_lost):
    
    pygame.mixer_music.pause()
    if boss_channel:
        boss_channel.stop()
    win_text = font.render("You've completed the game!", True, WHITE)
    sub_text = font.render("Press [R] to restart | [Q] to quit", True, WHITE)
    screen.fill(LAVANDER)
    if(player_lost != True):
        if victory: victory.play()
        screen.blit(win_text, (200, HEIGHT/2 - 100))
    screen.blit(sub_text, (180, HEIGHT/2 - 60))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    exit()
                if event.key == pygame.K_r:
                    waiting = False
                    reset_game() 
    
def reset_game():
    global score, count, ENEMY_HEALTH, enemy_alive, boss_active, BOSS_HEALTH, player_hp, enemy_pos, boss_pos, played_67_sound, player_bullets

    score = 0
    count = 0
    player_bullets.clear()

    player_hp = PLAYER_MAX_HP
    ENEMY_HEALTH = 3
    BOSS_HEALTH = 20

    enemy_alive = False
    boss_active = False
    played_67_sound = False

    enemy.x = -1000
    enemy.y = -1000
    boss.x = -1000
    boss.y = -1000

    player.x = 100
    player.y = 275

    if boss_channel:
        boss_channel.stop()

    pygame.mixer.music.rewind()
    pygame.mixer.music.unpause()

    difficulty_update(0)

def main():
    global score, count, enemy_pos, boss_pos, player_bullets, player_hp, ENEMY_HEALTH, enemy_alive, played_67_sound, played_87_sound, BOSS_HEALTH, boss_active

    running = True
    enemies_frozen = False
    player_lost = False
    boss_frozen_until = 0

    pygame.mixer.music.unpause()
    if not pygame.mixer.music.get_busy():
        try:
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    while running:
        clock.tick(FPS)

        if score == 67 and not played_67_sound:
            if six_seven: six_seven.play()
            played_67_sound = True
        if score == 87 and not played_87_sound:
            if bite87: bite87.play()
            played_87_sound = True

        # Boss Movement
        current_time = pygame.time.get_ticks()

        if boss_active and current_time > boss_frozen_until:
            player_pos = pygame.math.Vector2(player.x, player.y)
            boss_pos = boss_pos.move_towards(player_pos, 4) 
            boss.x = int(boss_pos.x)
            boss.y = int(boss_pos.y)
            #special attack

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == EVENT_SPAWN:
                if not boss_active and not enemy_alive:
                    if spawn_sound: spawn_sound.play()

                    player_pos = pygame.math.Vector2(player.x, player.y)
                    
                    if not enemies_frozen:
                        while True:
                            enemy.x = random.randint(200, WIDTH - enemy.width)
                            enemy.y = random.randint(0, HEIGHT - enemy.height)
                            enemy_pos = pygame.math.Vector2(enemy.x, enemy.y)
                        
                            distance = enemy_pos.distance_to(player_pos)

                            if distance >= MIN_DISTANCE:
                                break
                        enemy_alive = True

            elif event.type == pygame.KEYDOWN:
                # Dev cheat
                if event.key == pygame.K_0:
                    score = 150
                    difficulty_update(score)
                if event.key == pygame.K_9:
                    score += 10
                    difficulty_update(score)

                if event.key == pygame.K_UP:
                    shooting("UP")
                elif event.key == pygame.K_DOWN:
                    shooting("DOWN")
                elif event.key == pygame.K_LEFT:
                    shooting("LEFT")
                elif event.key == pygame.K_RIGHT:
                    shooting("RIGHT")

            elif event.type == ENEMY_HIT:
                ENEMY_HEALTH -= 1
                if hit_sound: hit_sound.play()

                if ENEMY_HEALTH <= 0:
                    score += 5 
                    count += 1
                    enemy_alive = False
                    enemy.x = -1000
                    enemy.y = -1000    

            elif event.type == BOSS_HIT:
                BOSS_HEALTH -= 1
                if hit_sound: hit_sound.play()

                if BOSS_HEALTH <= 0:
                    score += 100
                    count += 1
                    boss_active = False
                    boss.x = -1000
                    boss.y = -1000
                    enemy_alive = False
                    end_game(player_lost)

        # Enemy Movement
        if enemy_alive and not boss_active:
            player_pos = pygame.math.Vector2(player.x, player.y)
            enemy_pos = enemy_pos.move_towards(player_pos, ENEMY_SPEED)
            enemy.x = int(enemy_pos.x)
            enemy.y = int(enemy_pos.y)

        # Player Controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d] and player.right + 25 < WIDTH:
            player.x += SPEED
        if keys[pygame.K_a] and player.left > 0:
            player.x -= SPEED
        if keys[pygame.K_w] and player.top > 0:
            player.y -= SPEED
        if keys[pygame.K_s] and player.bottom + 25 < HEIGHT:
            player.y += SPEED

        handle_bullets(player_bullets, enemy, enemy_alive, boss, boss_active)

        # Collect Coins
        if player.colliderect(coin):
            if collected: collected.play()
            score += 1
            difficulty_update(score)
            coin.x = random.randint(0, WIDTH - coin.width) 
            coin.y = random.randint(0, HEIGHT - coin.height)

        # Boss Collidirect 
        if boss_active and player.colliderect(boss):
            player_hp -= 1
            if attack_sound: attack_sound.play()
            
            # Push the player!
            player.x -= 40
            player.y -= 40
            
            boss_frozen_until = pygame.time.get_ticks() + 500
        
            if player_hp <= 0:
                draw_window(player_bullets, enemy_alive, boss_active)
                screen.blit(end_text, end_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
                pygame.display.flip()
                if lost: lost.play()
                pygame.time.wait(2000)
                reset_game()

        #  Enemy Collidirect - Game Over
        if enemy_alive and not boss_active and player.colliderect(enemy):
            draw_window(player_bullets, enemy_alive, boss_active)
            screen.blit(end_text, end_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))
            pygame.display.flip()

            if lost:
                pygame.mixer.music.pause()
                lost.play()
                pygame.time.wait(500)
                
            player_lost = True
            pygame.time.wait(2000)
            end_game(player_lost)

        draw_window(player_bullets, enemy_alive, boss_active)

    pygame.quit()

if __name__ == "__main__":
    main()