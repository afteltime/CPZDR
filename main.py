import random
import math
import pygame

clock = pygame.time.Clock()
image_path = "/data/data/com.cpzdr/cpzdr/files/app/"
# source
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("CPZDR GAME")
icon = pygame.image.load("images/player/cpzdr_64x64.png").convert_alpha()
pygame.display.set_icon(icon)
gameplay = True

#txt
label = pygame.font.Font('fonts/PlaywriteGBS-Regular.ttf', 80)
lose_label = label.render('Chielipizdrik die...', False, ('white'))
restart_lable = label.render('Replay?', False, ("Red"))
restart_lable_range = restart_lable.get_rect(topleft=(800, 700))
small_label = pygame.font.Font('fonts/PlaywriteGBS-Regular.ttf', 40)
win_label = label.render('You save Chiliepizdrik!', False, ('white'))


#images
bg = pygame.image.load('images/fon for a game.jpg').convert()
bossfightbg = pygame.image.load('images/bossfightbg.png').convert()
player = pygame.image.load('images/player/cpzdr_64x64.png').convert()
playervsboss_right = pygame.image.load('images/player/angryhehe.png').convert()
playervsboss_left = pygame.image.load('images/player/angryhehe_left.png').convert()
enemy_boss = pygame.image.load('images/enemy/vacuum-cleaner_boss-removebg.png').convert_alpha()
enemy = pygame.image.load('images/enemy/vacuum-cleaner.png').convert_alpha()
walk_left = pygame.image.load('images/player/cpzdr_left64x64.png').convert_alpha()
walk_right = pygame.image.load('images/player/cpzdr_64x64.png').convert_alpha()
take_damage = pygame.image.load('images/player/nothehe.png').convert()
take_damage_left = pygame.image.load('images/player/nothehe_left.png').convert()
health = pygame.image.load('images/healts.png').convert_alpha()
health_d = pygame.image.load('images/healts_.png').convert_alpha()
bullet_image = pygame.image.load("images/fish.png").convert_alpha()
boss_bullet = pygame.image.load('images/enemy/trash.png')
win_bg = pygame.image.load('images/cpzds.png').convert_alpha()




#lists
enemys = []
bullets_list = []
boss_bullets_list = []


#god for a time
invincible = False
invincible_timer = 0
invincibility_duration = 1000
damage_flash_timer = 0
damage_flash_duration = 1000
flash_active = False


#stats
player_anim_count = 0
bg_x = 0
enemy_x = 0
player_speed = 3
player_x = 150
player_y = 300
health_state = [True, True, True]
small_enemy_speed = 1
destroyed_enemy_count = 0
bosfight_start = False
playervsboss = playervsboss_right
bossfight_start = None
boss_spawned = False
kills_couter = 0
Player_win = False


#sound
mmusic = pygame.mixer.Sound('sounds/mainmenu.mp3')
bg_sound = pygame.mixer.Sound('sounds/bgsound.mp3')
boss_sound = pygame.mixer.Sound('sounds/bossmusic.mp3')
boss_sound.set_volume(0.3)
bg_sound.set_volume(0.1)
bg_sound.play(fade_ms= 2000, loops= 0)
mmusic.set_volume(0.1)


#Bosslogic
class Boss:
    def __init__(self, x, y):
        self.image = pygame.image.load('images/enemy/vacuum-cleaner_boss-removebg.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = 100
        self.phase = 1
        self.boss_speed = 2
        self.attack_timer = 100
        self.charge_timer = 110
        self.attack_delay = 1600
        self.vacuum_charge = False
        self.spawn_minions_timer = 1
        self.minions_spawned = False

    def move(self):
        self.rect.x += self.boss_speed
        if self.rect.right >= 1920 or self.rect.left <= 0:
            self.boss_speed *= -1

    def vacuum_attack(self, player_hitbox):
        if not self.vacuum_charge:
            self.vacuum_charge = True
            self.charge_timer = pygame.time.get_ticks()

        if pygame.time.get_ticks() - self.charge_timer >= 100:
            if player_hitbox.x > self.rect.x:
                player_hitbox.x -= 3
            else:
                player_hitbox.x += 3

            if player_hitbox.colliderect(self.rect):
                self.vacuum_charge = False

    def shoot_trash(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.attack_timer > self.attack_delay:
            self.attack_timer = current_time
            #Logic boss bullet

            boss_bullet_rect = boss_bullet.get_rect(topleft=(self.rect.x + 30, self.rect.y + 10))
            direction_x = player_x - self.rect.x
            direction_y = player_y - self.rect.y
            # MATH OF BULLET DIRECTION
            magnitude = math.sqrt(direction_x ** 2 + direction_y ** 2)
            if magnitude != 0:
                direction_x /= magnitude
                direction_y /= magnitude
            #RANDOMIZE POLETA
            random_offset = random.uniform(-0.2, 0.2)
            direction_x += random_offset
            direction_y += random_offset

            boss_bullets_list.append([boss_bullet_rect, direction_x, direction_y, 'boss'])


    def spawn_minions(self):
        if not self.minions_spawned and pygame.time.get_ticks() - self.spawn_minions_timer > 0:
            self.minions_spawned = True
            #HERE SPAWN SMOL ENEMYS
            spawnenemy()

    def update(self, player_hitbox):
        self.move()
        self.shoot_trash()
        self.vacuum_attack(player_hitbox)
        self.spawn_minions()

        if self.health <= 70 and self.phase == 1:
            self.phase = 2
            self.boss_speed += 2
            self.attack_delay = 800

        if self.health <= 30 and self.phase == 2:
            self.phase = 3
            self.boss_speed += 2
            self.attack_delay = 500
        if self.health <= 0:
            self.health = 0
            global Player_win
            Player_win = True


boss = None
boss_spawn_time = 23000
boss_spawned = False
bossfight_start = pygame.time.get_ticks()


#LOGIKA NEUAZVIMOSTI
def handle_invincibility():
    global invincible, flash_active, player, damage_flash_timer, playervsboss

    if invincible:
        current_time = pygame.time.get_ticks()

        if current_time - damage_flash_timer < damage_flash_duration:
            if flash_active:
                if (current_time // 100) % 2 == 0:
                    player = take_damage_left if player == walk_left else take_damage
                    playervsboss = take_damage_left if player == walk_left else take_damage
                else:
                    player = take_damage if player == walk_right else take_damage_left


            if current_time - damage_flash_timer > damage_flash_duration:
                flash_active = False

        if current_time - invincible_timer > invincibility_duration:
            invincible = False
            flash_active = False
            player = walk_right


    #RASSCHET DAMAGA PO IGROKU
def damage_player(health_state):
    global invincible_timer, damage_flash_timer, invincible, flash_active, gameplay
    if not invincible:
        if health_state[2]:
            health_state[2] = False
            invincible_timer = pygame.time.get_ticks()
            damage_flash_timer = pygame.time.get_ticks()
            flash_active = True
            invincible = True
        elif health_state[1]:
            health_state[1] = False
            invincible_timer = pygame.time.get_ticks()
            damage_flash_timer = pygame.time.get_ticks()
            invincible = True
            flash_active = True
        elif health_state[0]:
            health_state[0] = False
            invincible_timer = pygame.time.get_ticks()
            damage_flash_timer = pygame.time.get_ticks()
            invincible = True
            flash_active = True
            gameplay = False
    handle_invincibility()

#LOGIKA DVIZENIA PULI
def move_bullets(bullets_list, player_hitbox, boss_hitbox):
    to_remove = []
    for bullet_data in bullets_list:
        bullet_rect, direction_x, direction_y, bullet_owner = bullet_data
        bullet_rect.x += int(direction_x * 4)
        bullet_rect.y += int(direction_y * 4)

        if bullet_owner == 'player' and bullet_rect.colliderect(boss_hitbox):
            boss.health -= 1
            to_remove.append(bullet_data)
        elif bullet_owner == 'boss' and bullet_rect.colliderect(player_hitbox):
            damage_player(health_state)
            to_remove.append(bullet_data)

        if bullet_rect.x > 1920 or bullet_rect.x < -64 or bullet_rect.y > 1080 or bullet_rect.y < -64:
            to_remove.append(bullet_data)

    for bullet in to_remove:
        bullets_list.remove(bullet)

#SPAWNBULLET
def spawnbullet():
    if bossfight_start:
        direction = "left" if playervsboss == playervsboss_left else "right"
    else:
        direction = "left" if player == walk_left else "right"
    bullet_rect = bullet_image.get_rect(topleft=(player_x + 30, player_y + 10))
    if direction == 'left':
        direction_x = -1
    else:
        direction_x = 1
    direction_y = 0
    bullets_list.append([bullet_rect, direction_x, direction_y, 'player'])


#enemylogic
def spawnenemy():
    for i in range(1):
        enemy_hitbox = enemy.get_rect(topleft=(random.randint(1920, 2000), random.randint(0, 1080 - 100)))
        enemys.append(enemy_hitbox)


#END OF GAME
def reset_game():
    global gameplay, bossfight_start, health_state, player_x, player_y, bullets_list, player, kills_counter, bosfight_start
    global bg, destroyed_enemy_count, playervsboss, boss_spawned, running
    gameplay = True
    bossfight_start = None
    bosfight_start = False
    health_state = [True, True, True]
    playervsboss = player
    player_x = 150
    player_y = 300
    bullets_list.clear()
    player = walk_right
    destroyed_enemy_count = 0
    boss_spawned = False
    kills_counter = 0
    running = False
    mmusic.stop()
    boss_sound.stop()
    bg_sound.stop()
    bg_sound.play(fade_ms=3000, loops=0)


#main cycle
running = True
while running:


    screen.blit(bg, (bg_x, 0))
    screen.blit(bg, (bg_x + 1920, 0))
    h_1 = screen.blit(health if health_state[0] else health_d, (0, 0))
    h_2 = screen.blit(health if health_state[1] else health_d, (100, 0))
    h_3 = screen.blit(health if health_state[2] else health_d, (200, 0))
    player_hitbox = player.get_rect(topleft= (player_x, player_y))


    if bosfight_start:
        if bossfight_start is None:
            bossfight_start = pygame.time.get_ticks()
        bg_sound.stop()
        boss_sound.play(fade_ms=3000)
        player = playervsboss
        if pygame.time.get_ticks() - bossfight_start >= boss_spawn_time and not boss_spawned:
            boss = Boss(100, 100)
            boss_spawned = True


        for el in bullets_list:
            bullet_rect = el[0]
            if boss_spawned and bullet_rect.colliderect(boss.rect):
                boss.health -= 1
                bullets_list.remove(el)


        if boss_spawned:
            bg = bossfightbg
            screen.blit(boss.image, boss.rect)
            boss.update(player_hitbox)


    if gameplay:

        screen.blit(player, (player_x, player_y))

        kills_couter = small_label.render(f'{destroyed_enemy_count} / 15', False, 'pink')
        if bosfight_start == False:
            screen.blit(kills_couter, (1600, 10))

        if not enemys and destroyed_enemy_count < 15:
            spawnenemy()

        for enemy_hitbox in enemys[:]:
            if not invincible and player_hitbox.colliderect(enemy_hitbox):
                damage_player(health_state)

        if not invincible and boss_spawned and player_hitbox.colliderect(boss.rect):
            damage_player(health_state)


        if boss_spawned:
            for boss_bullet_data in boss_bullets_list[:]:
                boss_bullet_rect, direction_x, direction_y, bullet_type = boss_bullet_data
                boss_bullet_rect.x += direction_x * 5
                boss_bullet_rect.y += direction_y * 5
                screen.blit(boss_bullet, boss_bullet_rect)

                if player_hitbox.colliderect(boss_bullet_rect):
                    damage_player(health_state)

                if boss_bullet_rect.x < 0 or boss_bullet_rect.x > 1920 or boss_bullet_rect.y < 0 or boss_bullet_rect.y > 1080:
                    boss_bullets_list.remove(boss_bullet_data)


        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            playervsboss = playervsboss_left
            player = walk_left
            player_x -= player_speed


        elif keys[pygame.K_RIGHT] and player_x < 1920 - 64:
            playervsboss = playervsboss_right
            player = walk_right
            player_x += player_speed

        elif keys[pygame.K_UP] and player_y > 0:
            player_y -= player_speed

        elif keys[pygame.K_DOWN] and player_y < 1080 - 64:
            player_y += player_speed

        if keys[pygame.K_SPACE] and not bullets_list:
            spawnbullet()


        if invincible and pygame.time.get_ticks() - invincible_timer >= invincibility_duration:
            invincible = False

        if bg_x == -1920:
            bg_x = 0
        bg_x -= 1

        for enemy_rect in enemys[:]:
            if player_x > enemy_rect.x:
                enemy_rect.x += small_enemy_speed
            elif player_x < enemy_rect.x:
                enemy_rect.x -= small_enemy_speed

            if player_y > enemy_rect.y:
                enemy_rect.y += small_enemy_speed
            elif player_y < enemy_rect.y:
                enemy_rect.y -= small_enemy_speed

            screen.blit(enemy, (enemy_rect.x, enemy_rect.y))


        if bullets_list:
            to_remove_bullets = []
            for el in bullets_list:
                bullet_rect =  el[0]
                direction_x = el[1]
                direction_y = el[2]
                bullet_owner = el[3]

                bullet_rect.x += int(direction_x * 4)

                if bullet_owner == 'player':
                    screen.blit(bullet_image, (bullet_rect.x, bullet_rect.y))

                if bullet_owner == 'player' and boss_spawned and bullet_rect.colliderect(boss.rect):
                    boss.health -= 1
                    to_remove_bullets.append(el)


                for enemy_rect in enemys[:]:
                    if bullet_owner == "player" and bullet_rect.colliderect(enemy_rect):
                        to_remove_bullets.append(el)
                        enemys.remove(enemy_rect)
                        destroyed_enemy_count += 1
                        break

                if bullet_rect.x > 1920 or bullet_rect.x < -64 or bullet_rect.y > 1080 or bullet_rect.y < -64:
                    to_remove_bullets.append(el)

            for bullet in to_remove_bullets:
                bullets_list.remove(bullet)


        if destroyed_enemy_count == 15:
            bosfight_start = True

    elif Player_win == True:
        screen.fill((87, 88, 89))
        screen.blit(win_label, (600, 100))
        screen.blit(win_bg, (0, 0))
        gameplay = False
        bg_sound.stop()
        boss_sound.stop()
        mmusic.play(fade_ms=4000, loops=0)


    #END OF GAME
    else:
        screen.fill((87, 88, 89))
        screen.blit(lose_label, (600, 100))
        screen.blit(restart_lable, restart_lable_range)
        gameplay = False
        bg_sound.stop()
        boss_sound.stop()
        mmusic.play(fade_ms=4000, loops=0)


        mouse = pygame.mouse.get_pos()
        if restart_lable_range.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
            reset_game()


    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
clock.tick(20)
pygame.quit()