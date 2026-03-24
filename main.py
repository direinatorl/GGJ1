import pygame
import random
import asyncio

# Initialize pygame
pygame.init()

# Set up the display
width, height = 1920, 1080
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Car Game')

# Game states
GAME_RUNNING = 0
GAME_OVER = 1
SETTINGS = 2

# Lives system
lives_font = pygame.font.Font(None, 72)

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 100)
LIGHT_BLUE = (135, 206, 235)
YELLOW = (127, 127, 1)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (128, 128, 128)

# Car properties
car_width, car_height = 78, 156
car_speed = 7

# Lane properties
lane_width = 600
lane_x = width // 2 - lane_width // 2

# Timer and score fonts
timer_font = pygame.font.Font(None, 72)
score_font = pygame.font.Font(None, 180)

# Load assets
# We do this globally to avoid reloading in the loop
try:
    car_image = pygame.image.load('CARROs.png')
    car_image = pygame.transform.scale(car_image, (car_width, car_height))
    obstacle_image = pygame.image.load('images.jpg')
    pygame.mixer.music.load('AUDIO2.ogg')
except Exception as e:
    print(f"Error loading assets: {e}")

# Power-up properties
power_up_radius = 30
power_up_color = (0, 255, 0)
score_power_up_color = (128, 0, 128)

async def main():
    game_state = GAME_RUNNING
    lives = 3
    car_x = width // 2 - car_width // 2
    car_y = height - car_height - 40
    timer = 0
    score = 0
    checkpoint_active = False
    checkpoint_car_x = 0
    checkpoint_car_y = 0
    checkpoint_time = 30
    checkpoint_score = 0
    obstacles = []
    power_ups = []

    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.15)

    running = True
    clock = pygame.time.Clock()

    while running:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if game_state == GAME_OVER:
                    # Restart button logic
                    restart_rect = pygame.Rect(width // 2 - 200, height // 2 + 250, 400, 100)
                    if restart_rect.collidepoint(mouse_pos):
                        game_state = GAME_RUNNING
                        lives = 3
                        car_x = width // 2 - car_width // 2
                        car_y = height - car_height - 40
                        timer = 0
                        score = 0
                        obstacles = []
                        power_ups = []
                        checkpoint_active = False
                
                elif game_state == GAME_RUNNING:
                    # Moon/Settings click logic
                    moon_radius = 60
                    moon_x = width - moon_radius - 40
                    moon_y = moon_radius + 40
                    if ((mouse_pos[0] - moon_x) ** 2 + (mouse_pos[1] - moon_y) ** 2) <= moon_radius ** 2:
                        game_state = SETTINGS
                
                elif game_state == SETTINGS:
                    # Back button and volume logic
                    back_rect = pygame.Rect(width // 2 - 100, height // 2 + 200, 200, 50)
                    if back_rect.collidepoint(mouse_pos):
                        game_state = GAME_RUNNING
                    
                    volume_slider_rect = pygame.Rect(width // 2 - 100, height // 2 + 50, 200, 20)
                    if volume_slider_rect.collidepoint(mouse_pos):
                        volume = (mouse_pos[0] - (width // 2 - 100)) / 200
                        volume = max(0, min(1, volume))
                        pygame.mixer.music.set_volume(volume)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and checkpoint_active:
                    car_x = checkpoint_car_x
                    car_y = checkpoint_car_y
                    timer = checkpoint_time
                    score = checkpoint_score
                    game_state = GAME_RUNNING
                elif event.key == pygame.K_ESCAPE and game_state == GAME_RUNNING:
                    game_state = SETTINGS

        if game_state == GAME_RUNNING:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] and car_x > lane_x:
                car_x -= car_speed
            if keys[pygame.K_d] and car_x < lane_x + lane_width - car_width:
                car_x += car_speed
            if keys[pygame.K_w]:
                car_y -= car_speed
            if keys[pygame.K_s]:
                car_y += car_speed

            if car_y < 0 or car_y + car_height > height:
                lives = 0
                game_state = GAME_OVER

            # Obstacle Logic
            if random.randint(0, 100) < 5:
                w_obs = random.randint(60, 120)
                h_obs = random.randint(60, 120)
                x_obs = random.randint(lane_x, lane_x + lane_width - w_obs)
                # [x, y, width, height, type]
                obstacles.append([float(x_obs), float(-h_obs), w_obs, h_obs, random.choice(['rectangle', 'circle', 'triangle'])])

            for obs in obstacles[:]:
                obs[1] += 9
                if obs[1] > height:
                    score += 50
                    obstacles.remove(obs)
                else:
                    # Drawing Obstacles with explicit cast
                    scaled_obs = pygame.transform.scale(obstacle_image, (int(obs[2]), int(obs[3])))
                    screen.blit(scaled_obs, (int(obs[0]), int(obs[1])))
                    
                    # Collision detection
                    obs_rect = pygame.Rect(int(obs[0]), int(obs[1]), int(obs[2]), int(obs[3]))
                    car_rect = pygame.Rect(car_x, car_y, car_width, car_height)
                    if car_rect.colliderect(obs_rect):
                        lives -= 1
                        obstacles.remove(obs)
                        if lives <= 0:
                            game_state = GAME_OVER

            # Power-up Logic
            if random.randint(0, 200) < 2:
                power_ups.append([float(random.randint(lane_x, lane_x + lane_width - power_up_radius*2)), float(-power_up_radius*2), 'life'])
            if random.randint(0, 300) < 1:
                power_ups.append([float(random.randint(lane_x, lane_x + lane_width - power_up_radius*2)), float(-power_up_radius*2), 'score'])

            for pu in power_ups[:]:
                pu[1] += 5
                pu_rect = pygame.Rect(int(pu[0]), int(pu[1]), power_up_radius*2, power_up_radius*2)
                car_rect = pygame.Rect(car_x, car_y, car_width, car_height)
                if car_rect.colliderect(pu_rect):
                    if pu[2] == 'life' and lives < 7:
                        lives += 1
                    elif pu[2] == 'score':
                        score += 10000
                    power_ups.remove(pu)
                elif pu[1] > height:
                    power_ups.remove(pu)
                else:
                    color = power_up_color if pu[2] == 'life' else score_power_up_color
                    pygame.draw.circle(screen, color, (int(pu[0]) + power_up_radius, int(pu[1]) + power_up_radius), power_up_radius)

            # Drawing (Road and Moon)
            # ... already handled above for obstacles and power-ups for efficiency ...
            
            timer += 1/60
            if timer >= 30 and not checkpoint_active:
                checkpoint_active = True
                checkpoint_car_x, checkpoint_car_y = car_x, car_y
                checkpoint_score = score
                print("Checkpoint!")

            screen.blit(timer_font.render(f"Timer: {int(timer)}", True, WHITE), (20, 20))
            
            s_color = (255,0,0) if score < 1000 else (255,165,0) if score < 5000 else (0,255,0)
            screen.blit(score_font.render(str(score), True, s_color), (180, 600))
            screen.blit(lives_font.render(f"Lives: {lives}", True, RED), (20, height - 100))

        elif game_state == GAME_OVER:
            screen.fill(BLACK)
            go_text = pygame.font.Font(None, 148).render('Game Over', True, RED)
            screen.blit(go_text, (width//2 - go_text.get_width()//2, height//2 - go_text.get_height()//2))
            
            res_text = pygame.font.Font(None, 72).render(f'Score: {score} | Time: {int(timer)}s', True, WHITE)
            screen.blit(res_text, (width//2 - res_text.get_width()//2, height//2 + 100))

            if lives <= 0:
                btn_font = pygame.font.Font(None, 100)
                btn_text = btn_font.render('Restart Game', True, WHITE)
                btn_rect = btn_text.get_rect(center=(width//2, height//2 + 300))
                pygame.draw.rect(screen, LIGHT_BLUE, btn_rect.inflate(40, 20))
                screen.blit(btn_text, btn_rect)
            
            if checkpoint_active and lives > 0:
                cp_text = pygame.font.Font(None, 60).render('Press R to respawn at checkpoint', True, WHITE)
                screen.blit(cp_text, (width//2 - cp_text.get_width()//2, height//2 + 400))

        elif game_state == SETTINGS:
            screen.fill(BLACK)
            set_text = pygame.font.Font(None, 120).render('Settings', True, WHITE)
            screen.blit(set_text, (width//2 - set_text.get_width()//2, 100))
            
            vol_rect = pygame.Rect(width//2 - 100, height//2, 200, 20)
            pygame.draw.rect(screen, WHITE, vol_rect)
            handle_x = width//2 - 100 + int(pygame.mixer.music.get_volume() * 200)
            pygame.draw.rect(screen, LIGHT_BLUE, (handle_x - 10, height//2 - 10, 20, 40))
            
            back_text = pygame.font.Font(None, 72).render('Back', True, WHITE)
            back_rect = back_text.get_rect(center=(width//2, height//2 + 200))
            pygame.draw.rect(screen, LIGHT_BLUE, back_rect.inflate(40, 20))
            screen.blit(back_text, back_rect)

        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(60)

if __name__ == "__main__":
    asyncio.run(main())
