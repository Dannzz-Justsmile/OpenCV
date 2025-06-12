import pygame
import random
import time

pygame.init()

# --- CONFIG & GLOBALS ---
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

WHITE = (255, 255, 255)
MORNING_COLOR = (135, 206, 250)
NIGHT_COLOR = (25, 25, 60)
day_cycle_length = 1350
day_cycle_counter = 0

pipe_width = 60
pipe_gap = 200
pipe_speed = 2
pipes = [{'x': WIDTH, 'height': random.randint(120, 280)}]

bird_img = pygame.transform.scale(pygame.image.load("bird.png"), (50, 50))
bird_up = pygame.transform.scale(pygame.image.load("bird_up.png"), (50, 50))
bird_down = pygame.transform.scale(pygame.image.load("bird_down.png"), (50, 50))
cloud_img = pygame.transform.scale(pygame.image.load("cloud.png"), (80, 50))
plane_img = pygame.transform.scale(pygame.image.load("plane.png"), (70, 40))
boss_img = pygame.transform.scale(pygame.image.load("boss.png"), (120, 120))
bird_boss_img = pygame.transform.scale(pygame.image.load("bird_boss.png"), (70, 70))

clouds = [{'x': random.randint(WIDTH, WIDTH + 200), 'y': random.randint(100, 300), 'speed': random.uniform(0.5, 2)} for _ in range(5)]

def get_valid_plane_y(pipe):
    above_pipe = random.randint(20, pipe['height'] - 40) if pipe['height'] > 60 else 20
    below_pipe = random.randint(pipe['height'] + pipe_gap + 40, HEIGHT - 80) if (pipe['height'] + pipe_gap + 40) < (HEIGHT - 80) else HEIGHT - 80
    return random.choice([above_pipe, below_pipe])

plane = {'x': WIDTH + 50, 'y': get_valid_plane_y(pipes[-1]), 'speed': 12}

player_name = ""
show_stats = False
stats_button_rect = pygame.Rect(WIDTH-50, 10, 40, 40)
chatbot_button_rect = pygame.Rect(WIDTH-100, 10, 40, 40)
flap_defeats = 0
boss_defeats = 0
play_start_time = time.time()

# Chatbot variables
chatbot_active = False
chatbot_input = ""
chatbot_history = []
chatbot_rect = pygame.Rect(40, HEIGHT-480, WIDTH-80, 440)
chatbot_input_rect = pygame.Rect(50, HEIGHT-30-40, WIDTH-100, 40)

# --- GAME STATE GLOBALS ---
score = 0
high_score = 0
bird = pygame.Rect(WIDTH // 4, HEIGHT // 2, 50, 50)
boss_x = WIDTH - 150
boss_y = HEIGHT // 2 - 60
bullets = []
boss_bullets = []
game_over = False
bird_boss_hp = 100
bird_boss_max_hp = 100
boss_defeats = 0

# --- UTILS ---
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def draw_stats_button():
    pygame.draw.rect(screen, (180,180,180), stats_button_rect)
    pygame.draw.rect(screen, (80,80,80), stats_button_rect, 2)
    s = font.render("i", True, (0,0,0))
    screen.blit(s, (stats_button_rect.x+13, stats_button_rect.y+5))

def draw_chatbot_button():
    pygame.draw.rect(screen, (180, 220, 180), chatbot_button_rect)
    pygame.draw.rect(screen, (80, 120, 80), chatbot_button_rect, 2)
    s = font.render("💬", True, (0, 80, 0))
    screen.blit(s, (chatbot_button_rect.x+7, chatbot_button_rect.y+2))

def draw_stats_window():
    now = time.time()
    play_time = int(now - play_start_time)
    mins, secs = divmod(play_time, 60)
    stats_rect = pygame.Rect(WIDTH-210, 60, 200, 140)
    pygame.draw.rect(screen, (40,40,40), stats_rect)
    pygame.draw.rect(screen, WHITE, stats_rect, 2)
    lines = [
        f"Time: {time.strftime('%H:%M:%S')}",
        f"Score: {score}",
        f"Play Time: {mins:02d}:{secs:02d}",
        f"Flap Defeats: {flap_defeats}",
        f"Boss Defeats: {boss_defeats}"
    ]
    for i, line in enumerate(lines):
        txt = font.render(line, True, WHITE)
        screen.blit(txt, (stats_rect.x+10, stats_rect.y+10+i*24))

def draw_button(rect, text, selected=False):
    color = (200, 200, 200) if selected else (120, 120, 120)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, WHITE, rect, 2)
    label = font.render(text, True, WHITE)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)

def draw_chatbot_ui():
    y = chatbot_rect.y + 10
    max_line_width = chatbot_rect.width - 40
    visible_lines = []
    for line in chatbot_history[-20:]:
        is_user = line.startswith("You:")
        bubble_color = (70, 130, 180) if is_user else (60, 60, 60)
        text_color = WHITE
        wrapped = wrap_text(line, font, max_line_width)
        visible_lines.append((wrapped, is_user, bubble_color, text_color))
    for wrapped, is_user, bubble_color, text_color in visible_lines:
        for txt_line in wrapped:
            txt = font.render(txt_line, True, text_color)
            bubble_rect = txt.get_rect()
            bubble_rect.y = y
            bubble_rect.height += 10
            bubble_rect.width += 20
            if is_user:
                bubble_rect.right = chatbot_rect.right - 10
            else:
                bubble_rect.x = chatbot_rect.x + 10
            pygame.draw.rect(screen, bubble_color, bubble_rect, border_radius=10)
            screen.blit(txt, (bubble_rect.x + 10, bubble_rect.y + 5))
            y += bubble_rect.height + 2
    pygame.draw.rect(screen, (50,50,50), chatbot_input_rect, border_radius=8)
    pygame.draw.rect(screen, WHITE, chatbot_input_rect, 2, border_radius=8)
    input_surf = font.render(chatbot_input, True, WHITE)
    screen.blit(input_surf, (chatbot_input_rect.x+8, chatbot_input_rect.y+8))
    hint = font.render("Ask something...💬", True, (180,180,180))
    screen.blit(hint, (chatbot_rect.x+10, chatbot_rect.bottom-30))

# --- PASSWORD & NAME ENTRY ---
def password_screen():
    password = ""
    correct_password = "190409"
    attempts = 0
    max_attempts = 3
    input_box = pygame.Rect(WIDTH//2-100, HEIGHT//2-25, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    result = None
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if password == correct_password:
                            result = "ok"
                        else:
                            attempts += 1
                            result = "fail"
                            if attempts >= max_attempts:
                                pygame.quit()
                                exit()
                        password = ""
                    elif event.key == pygame.K_BACKSPACE:
                        password = password[:-1]
                    else:
                        if len(password) < 16 and event.unicode.isprintable():
                            password += event.unicode
        screen.fill((30, 30, 60))
        prompt = font.render("Enter password:", True, WHITE)
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2-80))
        pygame.draw.rect(screen, color, input_box, 2)
        pw_surface = font.render("*" * len(password), True, WHITE)
        screen.blit(pw_surface, (input_box.x+5, input_box.y+10))
        if result == "ok":
            v = font.render("✔", True, (0,255,0))
            screen.blit(v, (input_box.right+10, input_box.y+5))
            pygame.display.flip()
            pygame.time.wait(700)
            return
        elif result == "fail":
            x = font.render("✖", True, (255,0,0))
            screen.blit(x, (input_box.right+10, input_box.y+5))
        pygame.display.flip()
        clock.tick(30)

def name_entry_screen():
    global player_name
    input_box = pygame.Rect(WIDTH//2-100, HEIGHT//2-25, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    player_name = ""
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if player_name.strip():
                            done = True
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        if len(player_name) < 16 and event.unicode.isprintable():
                            player_name += event.unicode
        screen.fill((30, 30, 60))
        prompt = font.render("Enter your name:", True, WHITE)
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2-80))
        pygame.draw.rect(screen, color, input_box, 2)
        name_surface = font.render(player_name, True, WHITE)
        screen.blit(name_surface, (input_box.x+5, input_box.y+10))
        pygame.display.flip()
        clock.tick(30)

# --- MODE SELECTION ---
def show_start_screen():
    selected = 0
    buttons = [
        pygame.Rect(WIDTH//2-100, HEIGHT//2-110, 200, 50),  # Flappy Bird
        pygame.Rect(WIDTH//2-100, HEIGHT//2-40, 200, 50),   # Boss Mode
        pygame.Rect(WIDTH//2-100, HEIGHT//2+30, 200, 50),   # Snake
    ]
    while True:
        screen.fill((40, 40, 80))
        title = font.render("Choose Game Mode", True, WHITE)
        screen.blit(title, (WIDTH//2-title.get_width()//2, HEIGHT//2-170))
        draw_button(buttons[0], "Flappy Bird", selected==0)
        draw_button(buttons[1], "Boss Mode", selected==1)
        draw_button(buttons[2], "Snake", selected==2)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    selected = (selected-1)%3
                if event.key in [pygame.K_DOWN, pygame.K_s]:
                    selected = (selected+1)%3
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    return selected
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                for i, rect in enumerate(buttons):
                    if rect.collidepoint(mx, my):
                        return i

# --- FLAPPY BIRD GAME ---
def reset_game():
    global bird, velocity, pipes, score, game_over, plane, bird_boss_hp
    bird = pygame.Rect(WIDTH // 4, HEIGHT // 2, 50, 50)
    velocity = 0
    pipes.clear()
    pipes.append({'x': WIDTH, 'height': random.randint(120, 280)})
    plane['x'] = WIDTH + 50
    plane['y'] = get_valid_plane_y(pipes[-1])
    score = 0
    game_over = False
    bird_boss_hp = 100

def run_flappy_bird():
    global running, game_over, score, high_score, pipes, velocity, bird, plane, flap_defeats, chatbot_active, show_stats, boss_mode
    reset_game()
    space_pressed = False
    frame_counter = 0
    boss_mode = False
    gravity = 1.2
    running = True
    while running:
        global day_cycle_counter
        day_cycle_counter = (day_cycle_counter + 1) % day_cycle_length
        t = abs((day_cycle_counter / (day_cycle_length / 2)) - 1)
        bg_color = (
            int(MORNING_COLOR[0] * t + NIGHT_COLOR[0] * (1 - t)),
            int(MORNING_COLOR[1] * t + NIGHT_COLOR[1] * (1 - t)),
            int(MORNING_COLOR[2] * t + NIGHT_COLOR[2] * (1 - t)),
        )
        screen.fill(bg_color)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_2:  # Back to menu
                    running = False
                    return
                if event.key == pygame.K_1:  # Quit
                    running = False
                    pygame.quit()
                    exit()
                if event.key == pygame.K_SPACE and not game_over:
                    space_pressed = True
                if event.key == pygame.K_5 and game_over:
                    reset_game()
                    game_over = False
                if event.key == pygame.K_0:
                    chatbot_active = True
                if event.key == pygame.K_3:
                    show_stats = not show_stats
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    space_pressed = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if stats_button_rect.collidepoint(event.pos):
                    show_stats = not show_stats
                elif chatbot_button_rect.collidepoint(event.pos):
                    chatbot_active = not chatbot_active
                elif event.button == 1:
                    if chatbot_rect.collidepoint(event.pos):
                        chatbot_active = True
                    else:
                        chatbot_active = False

        if not game_over:
            if space_pressed:
                velocity = -10
            velocity += gravity
            bird.y += velocity

            if bird.y < 0 or bird.y > HEIGHT:
                game_over = True
                flap_defeats += 1

            for pipe in pipes:
                pipe['x'] -= pipe_speed
                pygame.draw.rect(screen, NIGHT_COLOR, (pipe['x'], 0, pipe_width, pipe['height']))
                pygame.draw.rect(screen, NIGHT_COLOR, (pipe['x'], pipe['height'] + pipe_gap, pipe_width, HEIGHT))
                if bird.colliderect((pipe['x'], 0, pipe_width, pipe['height'])) or bird.colliderect((pipe['x'], pipe['height'] + pipe_gap, pipe_width, HEIGHT)):
                    game_over = True
                    flap_defeats += 1

            if pipes[-1]['x'] < WIDTH - 200:
                pipes.append({'x': WIDTH, 'height': random.randint(120, 280)})
                score += 1

            if score > high_score:
                high_score = score

            for cloud in clouds:
                cloud['x'] -= cloud['speed']
                if cloud['x'] < -80:
                    cloud['x'] = WIDTH + random.randint(50, 150)
                    cloud['y'] = random.randint(100, 300)
                    cloud['speed'] = random.uniform(0.5, 2)
                screen.blit(cloud_img, (cloud['x'], cloud['y']))

            plane['x'] -= plane['speed']
            if plane['x'] < -70:
                plane['x'] = WIDTH + 50
                plane['y'] = get_valid_plane_y(pipes[-1])
            screen.blit(plane_img, (plane['x'], plane['y']))

            plane_rect = pygame.Rect(plane['x'], plane['y'], 70, 40)
            if bird.colliderect(plane_rect):
                game_over = True
                flap_defeats += 1

            frame_counter += 1
            wing_img = bird_up if (frame_counter // 5) % 2 == 0 else bird_down

            screen.blit(bird_img, (bird.x, bird.y))
            screen.blit(wing_img, (bird.x, bird.y))

            if score >= 10:
                running = False
                return  # Switch to boss mode

        # Draw UI
        score_text = font.render(f"Score: {score}  Best: {high_score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        if player_name:
            name_surf = font.render(player_name, True, WHITE)
            screen.blit(name_surf, (WIDTH//2 - name_surf.get_width()//2, HEIGHT - name_surf.get_height() - 10))
        draw_stats_button()
        draw_chatbot_button()
        if show_stats:
            draw_stats_window()
        if chatbot_active:
            draw_chatbot_ui()
        if game_over and not chatbot_active:
            game_over_text1 = font.render("Game Over!", True, WHITE)
            text_rect1 = game_over_text1.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
            game_over_text2 = font.render("Press R or Enter to Restart", True, WHITE)
            text_rect2 = game_over_text2.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
            screen.blit(game_over_text1, text_rect1)
            screen.blit(game_over_text2, text_rect2)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r] or keys[pygame.K_RETURN]:
                reset_game()
                game_over = False
        pygame.display.flip()
        clock.tick(60)

# --- BOSS MODE GAME ---
def run_boss_mode():
    global running, game_over, boss_mode, boss_level, boss_max_hp, boss_hp, shoot_dmg, boss_alive, bullets, velocity, bird_boss_hp, bird_boss_max_hp, boss_dir, boss_bullets, boss_shoot_timer, score, bird, plane, chatbot_active, show_stats, boss_x, boss_y, boss_cooldown, boss_defeats, chatbot_input, chatbot_history

    def reset_boss_level():
        global boss_hp, boss_alive, bullets, boss_bullets, bird_boss_hp, game_over, boss_shoot_timer, boss_cooldown, bird, WIDTH, HEIGHT, boss_max_hp, bird_boss_max_hp
        boss_hp = boss_max_hp
        boss_alive = True
        bullets.clear()
        boss_bullets.clear()
        bird_boss_hp = bird_boss_max_hp
        game_over = False
        boss_shoot_timer = 0
        boss_cooldown = 0
        bird.x = WIDTH // 4
        bird.y = HEIGHT // 2

    # Setup boss mode
    boss_mode = True
    score = 10
    bird.width = 70
    bird.height = 70
    bird.x = WIDTH // 4
    bird.y = HEIGHT // 2
    boss_level = 1
    boss_max_hp = 100
    boss_hp = boss_max_hp
    bird_boss_max_hp = 100
    shoot_dmg = 20
    boss_alive = True
    bullets.clear()
    velocity = 0
    bird_boss_hp = 100
    boss_dir = 1
    boss_bullets.clear()
    boss_shoot_timer = 0
    boss_cooldown = 0
    boss_x = WIDTH - 150
    boss_y = HEIGHT // 2 - 60
    frame_counter = 0
    gravity = 1.2
    game_over = False
    running = True

    # Reset plane and clouds
    plane['x'] = WIDTH + 50
    plane['y'] = random.randint(40, HEIGHT - 120)
    for cloud in clouds:
        cloud['x'] = random.randint(WIDTH, WIDTH + 200)
        cloud['y'] = random.randint(100, 300)
        cloud['speed'] = random.uniform(0.5, 2)

    while running:
        screen.fill((30, 30, 60))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return
            if chatbot_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if chatbot_input.strip():
                            chatbot_history.append("You: " + chatbot_input)
                            reply = chatbot_response(chatbot_input)
                            chatbot_history.append("Bot: " + reply)
                            chatbot_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        chatbot_input = chatbot_input[:-1]
                    elif event.key == pygame.K_0:
                        chatbot_active = False
                    else:
                        if len(chatbot_input) < 40 and event.unicode.isprintable():
                            chatbot_input += event.unicode
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if chatbot_button_rect.collidepoint(event.pos):
                        chatbot_active = False
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_4 and boss_alive and boss_cooldown == 0 and not game_over:
                    bullets.append({'x': bird.x + bird.width // 2, 'y': bird.y + bird.height})
                    boss_cooldown = 8
                if (event.key == pygame.K_5 or event.key == pygame.K_r or event.key == pygame.K_RETURN) and game_over:
                    reset_boss_level()
                if event.key == pygame.K_1:
                    running = False
                    return
                if event.key == pygame.K_2:
                    boss_mode = False
                    return  # Back to menu
                if event.key == pygame.K_0:
                    chatbot_active = True
                if event.key == pygame.K_3:
                    show_stats = not show_stats
            if event.type == pygame.MOUSEBUTTONDOWN:
                if stats_button_rect.collidepoint(event.pos):
                    show_stats = not show_stats
                elif chatbot_button_rect.collidepoint(event.pos):
                    chatbot_active = not chatbot_active
                elif event.button == 1:
                    if chatbot_rect.collidepoint(event.pos):
                        chatbot_active = True
                    else:
                        chatbot_active = False

        if boss_cooldown > 0:
            boss_cooldown -= 1

        if not game_over:
            # Bird movement
            keys = pygame.key.get_pressed()
            move_speed = 7
            if keys[pygame.K_LEFT] and bird.x > 0:
                bird.x -= move_speed
            if keys[pygame.K_RIGHT] and bird.x < WIDTH - bird.width:
                bird.x += move_speed
            if keys[pygame.K_UP] and bird.y > 0:
                bird.y -= move_speed
            if keys[pygame.K_DOWN] and bird.y < HEIGHT - bird.height:
                bird.y += move_speed

            # Boss movement
            boss_x += boss_dir * 4
            if boss_x < 0:
                boss_x = 0
                boss_dir = 1
            if boss_x > WIDTH - 120:
                boss_x = WIDTH - 120
                boss_dir = -1

            # Boss attack
            boss_shoot_timer += 1
            if boss_shoot_timer > 40:
                boss_bullets.append({'x': boss_x + 60, 'y': boss_y + 120})
                boss_shoot_timer = random.randint(0, 30)
            for b in boss_bullets[:]:
                b['y'] += 8
                pygame.draw.circle(screen, (255, 0, 0), (int(b['x']), int(b['y'])), 8)
                if pygame.Rect(bird.x, bird.y, bird.width, bird.height).collidepoint(b['x'], b['y']):
                    bird_boss_hp -= 20
                    boss_bullets.remove(b)
                    if bird_boss_hp <= 0:
                        game_over = True
                        boss_defeats += 1
                if b['y'] > HEIGHT:
                    boss_bullets.remove(b)

            # Clouds and plane
            for cloud in clouds:
                cloud['x'] -= cloud['speed']
                if cloud['x'] < -80:
                    cloud['x'] = WIDTH + random.randint(50, 150)
                    cloud['y'] = random.randint(100, 300)
                    cloud['speed'] = random.uniform(0.5, 2)
                screen.blit(cloud_img, (cloud['x'], cloud['y']))

            plane['x'] -= plane['speed']
            if plane['x'] < -70:
                plane['x'] = WIDTH + 50
                plane['y'] = random.randint(40, HEIGHT - 120)
            screen.blit(plane_img, (plane['x'], plane['y']))

            plane_rect = pygame.Rect(plane['x'], plane['y'], 70, 40)
            if bird.colliderect(plane_rect):
                game_over = True
                boss_defeats += 1

            # Draw boss
            if boss_alive:
                screen.blit(boss_img, (boss_x, boss_y))
                bar_w = 120
                bar_h = 18
                hp_ratio = boss_hp / boss_max_hp
                pygame.draw.rect(screen, (80, 0, 0), (boss_x, boss_y - 24, bar_w, bar_h))
                pygame.draw.rect(screen, (255, 0, 0), (boss_x, boss_y - 24, int(bar_w * hp_ratio), bar_h))
                hp_text = font.render(f"Boss {boss_level}", True, WHITE)
                screen.blit(hp_text, (boss_x, boss_y - 48))

            # Draw and move player bullets
            for bullet in bullets[:]:
                bullet['y'] -= 12
                pygame.draw.line(screen, (255, 0, 0), (bullet['x'], bullet['y']), (bullet['x'], bullet['y'] - 15), 4)
                boss_rect = pygame.Rect(boss_x, boss_y, 120, 120)
                if boss_alive and boss_rect.collidepoint(bullet['x'], bullet['y']):
                    boss_hp -= shoot_dmg
                    bullets.remove(bullet)
                    if boss_hp <= 0:
                        boss_alive = False
                        if boss_level == 1:
                            boss_level = 2
                            boss_max_hp = 200
                            boss_hp = boss_max_hp
                            shoot_dmg = 30
                            boss_alive = True
                            boss_bullets.clear()
                        elif boss_level == 2:
                            boss_level = 3
                            boss_max_hp = 1000
                            boss_hp = boss_max_hp
                            shoot_dmg = 50
                            boss_alive = True
                            boss_bullets.clear()
                        else:
                            running = False

            frame_counter += 1
            wing_img = bird_up if (frame_counter // 5) % 2 == 0 else bird_down

            screen.blit(bird_boss_img, (bird.x, bird.y))
            bar_w = 70
            bar_h = 10
            hp_ratio = bird_boss_hp / bird_boss_max_hp
            pygame.draw.rect(screen, (80, 0, 0), (bird.x, bird.y - 16, bar_w, bar_h))
            pygame.draw.rect(screen, (255, 0, 0), (bird.x, bird.y - 16, int(bar_w * hp_ratio), bar_h))

        # Draw UI
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        if player_name:
            name_surf = font.render(player_name, True, WHITE)
            screen.blit(name_surf, (WIDTH//2 - name_surf.get_width()//2, HEIGHT - name_surf.get_height() - 10))
        draw_stats_button()
        draw_chatbot_button()
        if show_stats:
            draw_stats_window()
        if chatbot_active:
            draw_chatbot_ui()
        if game_over and not chatbot_active:
            game_over_text1 = font.render("Game Over!", True, WHITE)
            text_rect1 = game_over_text1.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
            game_over_text2 = font.render("Press 5 or R to Restart", True, WHITE)
            text_rect2 = game_over_text2.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
            screen.blit(game_over_text1, text_rect1)
            screen.blit(game_over_text2, text_rect2)
        pygame.display.flip()
        clock.tick(60)

# --- SNAKE GAME ---
def run_snake_game():
    global running, game_over, score, show_stats, chatbot_active, chatbot_input, chatbot_history

    block_size = 20
    snake = [(WIDTH // 2, HEIGHT // 2)]
    direction = (block_size, 0)
    food = (random.randrange(0, WIDTH, block_size), random.randrange(0, HEIGHT, block_size))
    score = 0
    game_over = False
    running = True

    while running:
        screen.fill((20, 40, 20))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return
            if chatbot_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if chatbot_input.strip():
                            chatbot_history.append("You: " + chatbot_input)
                            reply = chatbot_response(chatbot_input)
                            chatbot_history.append("Bot: " + reply)
                            chatbot_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        chatbot_input = chatbot_input[:-1]
                    elif event.key == pygame.K_0:
                        chatbot_active = False
                    else:
                        if len(chatbot_input) < 40 and event.unicode.isprintable():
                            chatbot_input += event.unicode
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if chatbot_button_rect.collidepoint(event.pos):
                        chatbot_active = False
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, block_size):
                    direction = (0, -block_size)
                elif event.key == pygame.K_DOWN and direction != (0, -block_size):
                    direction = (0, block_size)
                elif event.key == pygame.K_LEFT and direction != (block_size, 0):
                    direction = (-block_size, 0)
                elif event.key == pygame.K_RIGHT and direction != (-block_size, 0):
                    direction = (block_size, 0)
                elif event.key == pygame.K_2:
                    running = False
                    return
                elif event.key == pygame.K_1:
                    running = False
                    pygame.quit()
                    exit()
                elif event.key == pygame.K_0:
                    chatbot_active = True
                elif event.key == pygame.K_3:
                    show_stats = not show_stats
            if event.type == pygame.MOUSEBUTTONDOWN:
                if stats_button_rect.collidepoint(event.pos):
                    show_stats = not show_stats
                elif chatbot_button_rect.collidepoint(event.pos):
                    chatbot_active = not chatbot_active
                elif event.button == 1:
                    if chatbot_rect.collidepoint(event.pos):
                        chatbot_active = True
                    else:
                        chatbot_active = False

        if not game_over:
            new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
            if (new_head[0] < 0 or new_head[0] >= WIDTH or
                new_head[1] < 0 or new_head[1] >= HEIGHT or
                new_head in snake):
                game_over = True
            else:
                snake.insert(0, new_head)
                if new_head == food:
                    score += 1
                    food = (random.randrange(0, WIDTH, block_size), random.randrange(0, HEIGHT, block_size))
                else:
                    snake.pop()

        # Draw snake and food
        for s in snake:
            pygame.draw.rect(screen, (0, 200, 0), (s[0], s[1], block_size, block_size))
        pygame.draw.rect(screen, (200, 0, 0), (food[0], food[1], block_size, block_size))

        # Draw UI
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        if player_name:
            name_surf = font.render(player_name, True, WHITE)
            screen.blit(name_surf, (WIDTH//2 - name_surf.get_width()//2, HEIGHT - name_surf.get_height() - 10))
        draw_stats_button()
        draw_chatbot_button()
        if show_stats:
            draw_stats_window()
        if chatbot_active:
            draw_chatbot_ui()
        if game_over and not chatbot_active:
            game_over_text1 = font.render("Game Over!", True, WHITE)
            text_rect1 = game_over_text1.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
            game_over_text2 = font.render("Press R or Enter to Restart", True, WHITE)
            text_rect2 = game_over_text2.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
            screen.blit(game_over_text1, text_rect1)
            screen.blit(game_over_text2, text_rect2)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r] or keys[pygame.K_RETURN] or keys[pygame.K_5]:
                # Restart snake game
                snake[:] = [(WIDTH // 2, HEIGHT // 2)]
                direction = (block_size, 0)
                food = (random.randrange(0, WIDTH, block_size), random.randrange(0, HEIGHT, block_size))
                score = 0
                game_over = False
        pygame.display.flip()
        clock.tick(12)

# --- CHATBOT LOGIC ---
def chatbot_response(msg):
    msg = msg.lower()
    if "hello" in msg or "hi" in msg:
        return "Hello! How can I help you?"
    elif "name" in msg:
        return "I'm your game chatbot!"
    elif "score" in msg:
        return f"Your current score is {score}."
    elif "bye" in msg or "exit" in msg:
        return "Goodbye! Press 0 or click 💬 to close the chatbot."
    elif "how" in msg and "play" in msg:
        return (
            "How to play:\n"
            "- Flappy Bird: Press SPACE to flap and avoid pipes and the plane.\n"
            "- Get 10 points to enter Boss Mode.\n"
            "- Boss Mode: Use arrow keys to move, 4 to shoot. Dodge red balls and the plane.\n"
            "Defeat all boss levels to win!\n"
        )
    elif "shortcut" in msg or "key" in msg or "control" in msg:
        return (
            "Shortcuts:\n"
            "0: Open/close chatbot\n"
            "3: Open/close stats\n"
            "2: Back to menu\n"
            "5: Restart after game over\n"
            "1: Quit\n"
            "SPACE: Flap (Flappy Bird)\n"
            "4: Shoot (Boss Mode)"
        )
    elif "boss" in msg:
        return (
            "Boss Mode:\n"
            "- Move with arrow keys.\n"
            "- Press 4 to shoot the boss.\n"
            "- Dodge red balls and the plane.\n"
            "- Defeat all boss levels to win!"
        )
    elif "flappy" in msg or "bird" in msg:
        return (
            "Flappy Bird Mode:\n"
            "- Press SPACE to flap.\n"
            "- Avoid pipes and the plane.\n"
            "- Get 10 points to enter Boss Mode."
        )
    elif "instruction" in msg or "help" in msg:
        return (
            "Type 'how to play' for instructions, 'shortcut' for keys, "
            "'boss', 'flappy' for mode info."
        )
    else:
        return "Sorry, I don't understand. Type 'help' for instructions."

# --- MAIN GAME LOOP ---
password_screen()
name_entry_screen()

while True:
    if not pygame.display.get_init():
        break

    mode = show_start_screen()
    if mode is None:
        break

    if mode == 0:
        running = True
        run_flappy_bird()
        if score >= 10:
            running = True
            run_boss_mode()
    elif mode == 1:
        running = True
        run_boss_mode()
    elif mode == 2:
        running = True
        run_snake_game()

pygame.quit()

