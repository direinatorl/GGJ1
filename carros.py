import pygame
import random

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
game_state = GAME_RUNNING

# Lives system
lives = 3
lives_font = pygame.font.Font(None, 72)  # Font for displaying lives

# Load and play background music
pygame.mixer.music.load('AUDIO2.mp3')
pygame.mixer.music.play(-1)  # -1 means loop indefinitely
pygame.mixer.music.set_volume(0.15)

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 100)
LIGHT_BLUE = (135, 206, 235)  # Added light blue color
YELLOW = (127, 127, 1)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (128, 128, 128)  # Added gray color for the moon

# Car properties
car_width, car_height = 78, 156  # Increased by 30%
car_x = width // 2 - car_width // 2
car_y = height - car_height - 40  # Adjusted for larger car
car_speed = 7  # Doubled the car speed

# Lane properties
lane_width = 600  # Increased by 50%
lane_x = width // 2 - lane_width // 2

# Obstacles
obstacles = []

# Timer properties
timer = 0
timer_font = pygame.font.Font(None, 72)  # Doubled the font size

# Score properties
score = 0
score_font = pygame.font.Font(None, 180)  # Doubled the font size

# Checkpoint properties
checkpoint_active = False
checkpoint_car_x = 0
checkpoint_car_y = 0
checkpoint_time = 30
checkpoint_score = 0  # Added to store score at checkpoint

# Load car image
car_image = pygame.image.load('CARROs.png')
car_image = pygame.transform.scale(car_image, (car_width, car_height))
car_image = pygame.transform.rotate(car_image, 0)  # Rotate the car image to face forward

# Load obstacle image
obstacle_image = pygame.image.load('images.jpg')

# Power-up properties
power_ups = []
power_up_radius = 30
power_up_color = (0, 255, 0)  # Green color for power-ups
score_power_up_color = (128, 0, 128)  # Purple color for score power-ups

# Game loop
running = True
clock = pygame.time.Clock()

def reset_game():
    global car_x, car_y, timer, obstacles, score, checkpoint_active, game_state, lives, checkpoint_score
    car_x = width // 2 - car_width // 2
    car_y = height - car_height - 40
    timer = 0
    obstacles = []
    score = 0
    checkpoint_active = False
    checkpoint_score = 0  # Reset checkpoint score
    game_state = GAME_RUNNING
    lives = 3  # Reset lives to 3

while running:
    # Check if music is playing, if not, restart it
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if game_state == GAME_OVER:
                if restart_button_rect.collidepoint(mouse_pos):
                    reset_game()
            elif game_state == GAME_RUNNING:
                # Check if moon is clicked
                moon_radius = 60
                moon_x = width - moon_radius - 40
                moon_y = moon_radius + 40
                if ((mouse_pos[0] - moon_x) ** 2 + (mouse_pos[1] - moon_y) ** 2) <= moon_radius ** 2:
                    game_state = SETTINGS
            elif game_state == SETTINGS:
                # Check if back button is clicked
                back_button_rect = pygame.Rect(width // 2 - 100, height // 2 + 200, 200, 50)
                if back_button_rect.collidepoint(mouse_pos):
                    game_state = GAME_RUNNING
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and checkpoint_active:
                car_x = checkpoint_car_x
                car_y = checkpoint_car_y
                timer = checkpoint_time
                score = checkpoint_score  # Restore score from checkpoint
                game_state = GAME_RUNNING
            elif event.key == pygame.K_ESCAPE and game_state == GAME_RUNNING:
                # Abrir tela de configurações ao apertar ESC durante o jogo
                game_state = SETTINGS

    if game_state == GAME_RUNNING:
        # Handle car movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and car_x > lane_x:
            car_x -= car_speed
        if keys[pygame.K_d] and car_x < lane_x + lane_width - car_width:
            car_x += car_speed
        if keys[pygame.K_w]:
            car_y -= car_speed
        if keys[pygame.K_s]:
            car_y += car_speed

        # Se o carro sair da tela no eixo Y (para cima ou para baixo),
        # perde todas as vidas e o jogo acaba.
        if car_y < 0 or car_y + car_height > height:
            lives = 0
            game_state = GAME_OVER

        # Generate obstacles
        if random.randint(0, 100) < 5:
            obstacle_type = random.choice(['rectangle', 'circle', 'triangle'])
            obstacle_width = random.randint(60, 120)  # Increased by 50%
            obstacle_height = random.randint(60, 120)  # Increased by 50%
            obstacle_x = random.randint(lane_x, lane_x + lane_width - obstacle_width)
            obstacle_y = -obstacle_height
            obstacles.append((obstacle_x, obstacle_y, obstacle_width, obstacle_height, obstacle_type))

        # Move obstacles
        obstacles = [(x, y + 9, w, h, t) for x, y, w, h, t in obstacles if y < height]  # Decreased the obstacle speed by 10%
        # Increase score when obstacles leave the screen
        score += 50 * (len(obstacles) - len([(x, y, w, h, t) for x, y, w, h, t in obstacles if y < height]))

        # Check for collisions
        for obstacle in obstacles:
            obstacle_x, obstacle_y, obstacle_width, obstacle_height, obstacle_type = obstacle
            if obstacle_type == 'rectangle':
                if (car_x < obstacle_x + obstacle_width and
                    car_x + car_width > obstacle_x and
                    car_y < obstacle_y + obstacle_height and
                    car_y + car_height > obstacle_y):
                    if lives > 0:  # Only decrement lives if they are greater than 0
                        lives -= 1  # Lose one life
                    obstacles.remove(obstacle)  # Remove the obstacle after collision
                    if lives <= 0:  # Check if all lives are lost
                        game_state = GAME_OVER
            elif obstacle_type == 'circle':
                circle_center_x = obstacle_x + obstacle_width // 2
                circle_center_y = obstacle_y + obstacle_height // 2
                circle_radius = min(obstacle_width, obstacle_height) // 2
                car_center_x = car_x + car_width // 2
                car_center_y = car_y + car_height // 2
                distance = ((car_center_x - circle_center_x) ** 2 + (car_center_y - circle_center_y) ** 2) ** 0.5
                if distance < circle_radius + min(car_width, car_height) // 2:
                    if lives > 0:  # Only decrement lives if they are greater than 0
                        lives -= 1  # Lose one life
                    obstacles.remove(obstacle)  # Remove the obstacle after collision
                    if lives <= 1:  # Check if all lives are lost
                        game_state = GAME_OVER
            elif obstacle_type == 'triangle':
                if (car_x < obstacle_x + obstacle_width and
                    car_x + car_width > obstacle_x and
                    car_y < obstacle_y + obstacle_height and
                    car_y + car_height > obstacle_y):
                    if lives > 0:  # Only decrement lives if they are greater than 0
                        lives -= 1  # Lose one life
                    obstacles.remove(obstacle)  # Remove the obstacle after collision
                    if lives <= 0:  # Check if all lives are lost
                        game_state = GAME_OVER

        # Generate power-ups
        if random.randint(0, 200) < 2:  # 1% chance to generate a power-up
            power_up_x = random.randint(lane_x, lane_x + lane_width - power_up_radius * 2)
            power_up_y = -power_up_radius * 2
            power_ups.append((power_up_x, power_up_y, 'life'))  # Added type to power-ups

        # Generate score power-ups
        if random.randint(0, 300) < 1:  # 0.33% chance to generate a score power-up
            power_up_x = random.randint(lane_x, lane_x + lane_width - power_up_radius * 2)
            power_up_y = -power_up_radius * 2
            power_ups.append((power_up_x, power_up_y, 'score'))  # Added type to power-ups

        # Move power-ups
        power_ups = [(x, y + 5, t) for x, y, t in power_ups if y < height]  # Increased the power-up speed by 10%

        # Check for power-up collection
        for power_up in power_ups[:]:
            power_up_x, power_up_y, power_up_type = power_up
            car_center_x = car_x + car_width // 2
            car_center_y = car_y + car_height // 2
            distance = ((car_center_x - (power_up_x + power_up_radius)) ** 2 + (car_center_y - (power_up_y + power_up_radius)) ** 2) ** 0.5
            if distance < power_up_radius + min(car_width, car_height) // 2:
                if power_up_type == 'life' and lives < 7:  # Only add a life if the player has less than 7 lives
                    lives += 1  # Recover one life
                elif power_up_type == 'score':
                    score += 10000 # Add 1000 points
                power_ups.remove(power_up)  # Remove the power-up after collection

        # Draw everything
        screen.fill(BLUE)
        pygame.draw.rect(screen, BLACK, (lane_x, 0, lane_width, height))
        pygame.draw.rect(screen, WHITE, (lane_x, 0, 10, height))  # Doubled the lane border width
        pygame.draw.rect(screen, WHITE, (lane_x + lane_width - 10, 0, 10, height))  # Doubled the lane border width
        
        # Draw yellow stripes in the middle of the road
        stripe_width = 20  # Doubled the stripe width
        stripe_height = 60  # Doubled the stripe height
        stripe_gap = 40  # Doubled the stripe gap
        for y in range(0, height, stripe_height + stripe_gap):
            pygame.draw.rect(screen, YELLOW, (lane_x + lane_width//2 - stripe_width//2, y, stripe_width, stripe_height))

        # Draw car
        screen.blit(car_image, (car_x, car_y))

        # Draw obstacles
        for obstacle in obstacles:
            obstacle_x, obstacle_y, obstacle_width, obstacle_height, obstacle_type = obstacle
            scaled_obstacle = pygame.transform.scale(obstacle_image, (obstacle_width, obstacle_height))
            screen.blit(scaled_obstacle, (obstacle_x, obstacle_y))

        # Draw moon in the upper right corner
        moon_radius = 60  # Doubled the moon size
        moon_x = width - moon_radius - 40  # Adjusted for larger moon
        moon_y = moon_radius + 40  # Adjusted for larger moon
        pygame.draw.circle(screen, GRAY, (moon_x, moon_y), moon_radius)
        
        # Draw craters on the moon
        crater_positions = [
            (moon_x - 20, moon_y - 10),  # Doubled the crater positions
            (moon_x + 30, moon_y + 20),  # Doubled the crater positions
            (moon_x + 10, moon_y - 30),  # Doubled the crater positions
            (moon_x - 30, moon_y + 30)   # Doubled the crater positions
        ]
        for crater_x, crater_y in crater_positions:
            pygame.draw.circle(screen, WHITE, (crater_x, crater_y), 6)  # Doubled the crater size

        # Draw power-ups
        for power_up_x, power_up_y, power_up_type in power_ups:
            color = power_up_color if power_up_type == 'life' else score_power_up_color
            pygame.draw.circle(screen, color, (power_up_x + power_up_radius, power_up_y + power_up_radius), power_up_radius)
            # Add "+1" or "+1000" text to power-ups
            power_up_text = pygame.font.Font(None, 36).render("+1" if power_up_type == 'life' else "+10000", True, WHITE)
            text_rect = power_up_text.get_rect(center=(power_up_x + power_up_radius, power_up_y + power_up_radius))
            screen.blit(power_up_text, text_rect)

        # Update timer
        timer += 1 / 60  # Increase timer by 1/60 of a second

        # Check for checkpoint activation
        if timer >= 30 and not checkpoint_active:
            checkpoint_active = True
            checkpoint_car_x = car_x
            checkpoint_car_y = car_y
            checkpoint_score = score  # Store current score at checkpoint
            print("Checkpoint activated!")

        # Draw timer
        timer_text = timer_font.render(f"Timer: {int(timer)}", True, WHITE)
        screen.blit(timer_text, (20, 20))  # Adjusted position for larger font

        # Draw score with color gradient
        if score < 1000:
            score_color = (255, 0, 0)  # Red for low scores
        elif score < 5000:
            score_color = (255, 165, 0)  # Orange for medium scores
        else:
            score_color = (0, 255, 0)  # Green for high scores
        score_text = score_font.render(str(score), True, score_color)
        screen.blit(score_text, (180, 600))  # Adjusted position for larger font

        # Draw lives HUD
        lives_text = lives_font.render(f"Lives: {lives}", True, RED)
        screen.blit(lives_text, (20, height - 100))  # Display lives in the lower left corner

    elif game_state == GAME_OVER:
        # Game over screen
        screen.fill(BLACK)
        game_over_font = pygame.font.Font(None, 148)  # Doubled the font size
        game_over_text = game_over_font.render('Game Over', True, RED)
        screen.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2 - game_over_text.get_height() // 2))

        time_survived_font = pygame.font.Font(None, 72)  # Doubled the font size
        time_survived_text = time_survived_font.render(f'Time Survived: {int(timer)} seconds', True, WHITE)
        screen.blit(time_survived_text, (width // 2 - time_survived_text.get_width() // 2, height // 2 + 100))  # Adjusted position for larger font

        # Display the player's score
        score_text = time_survived_font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (width // 2 - score_text.get_width() // 2, height // 2 + 200))  # Adjusted position for larger font

        # Draw restart button only when lives reach 0
        if lives <= 1:
            restart_button_font = pygame.font.Font(None, 144)  # Increased font size for the restart button
            restart_button_text = restart_button_font.render('Restart Game', True, WHITE)
            restart_button_rect = restart_button_text.get_rect(center=(width // 2, height // 2 + 300))  # Adjusted position for larger font
            pygame.draw.rect(screen, LIGHT_BLUE, restart_button_rect.inflate(40, 20))  # Added padding to the button
            screen.blit(restart_button_text, restart_button_rect)

        # Check for checkpoint respawn
        if checkpoint_active and lives > 0:  # Only show checkpoint respawn if player still has lives
            respawn_font = pygame.font.Font(None, 72)  # Doubled the font size
            respawn_text = respawn_font.render('Press R to respawn at checkpoint', True, WHITE)
            screen.blit(respawn_text, (width // 2 - respawn_text.get_width() // 2, height // 2 + 400))  # Adjusted position for larger font

    elif game_state == SETTINGS:
        # Settings screen
        screen.fill(BLACK)
        settings_font = pygame.font.Font(None, 148)  # Doubled the font size
        settings_text = settings_font.render('Settings', True, WHITE)
        screen.blit(settings_text, (width // 2 - settings_text.get_width() // 2, height // 2 - settings_text.get_height() // 2 - 100))  # Moved up by 100 pixels

        # Draw volume slider
        volume_slider_rect = pygame.Rect(width // 2 - 100, height // 2 + 50, 200, 20)  # Moved down by 50 pixels
        pygame.draw.rect(screen, WHITE, volume_slider_rect)
        volume_handle_rect = pygame.Rect(width // 2 - 100 + int(pygame.mixer.music.get_volume() * 200), height // 2 + 50, 20, 20)  # Moved down by 50 pixels
        pygame.draw.rect(screen, LIGHT_BLUE, volume_handle_rect)

        # Draw back button
        back_button_font = pygame.font.Font(None, 72)  # Doubled the font size
        back_button_text = back_button_font.render('Back', True, WHITE)
        back_button_rect = pygame.Rect(width // 2 - 100, height // 2 + 200, 200, 50)  # Fixed position and size
        pygame.draw.rect(screen, LIGHT_BLUE, back_button_rect)  # Changed button color to light blue
        screen.blit(back_button_text, (width // 2 - back_button_text.get_width() // 2, height // 2 + 200 + (50 - back_button_text.get_height()) // 2))  # Centered text in button

        # Handle volume adjustment  
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if volume_slider_rect.collidepoint(mouse_pos):
                volume = (mouse_pos[0] - (width // 2 - 100)) / 200
                volume = max(0, min(1, volume))  # Clamp volume between 0 and 1
                pygame.mixer.music.set_volume(volume)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
