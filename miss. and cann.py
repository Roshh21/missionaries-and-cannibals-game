import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 1000, 600
WHITE, BLACK, RED, GREEN, BLUE, BROWN = (255,255,255), (0,0,0), (200,0,0), (0,200,0), (135,206,250), (139,69,19)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Missionaries and Cannibals")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 36)
BIG_FONT = pygame.font.SysFont(None, 64)
FPS = 60

state = 'start'
boat_position = 'left'
boat_x = 200
boat = {'M': 0, 'C': 0}
left_bank = {'M': 3, 'C': 3}
right_bank = {'M': 0, 'C': 0}
boat_moving = False

def draw_start_screen():
    screen.fill(BLUE)
    lines = [
        "Missionaries and Cannibals",
        "Rules:",
        "1. Boat can carry at most 2 people.",
        "2. If cannibals outnumber missionaries after crossing, you lose.",
        "3. Boat can't move without people.",
        "Click START to begin."
    ]
    for i, line in enumerate(lines):
        text = FONT.render(line, True, BLACK)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 50 + i*40))
    start_btn = pygame.Rect(WIDTH//2 - 100, 400, 200, 60)
    pygame.draw.rect(screen, GREEN, start_btn)
    screen.blit(FONT.render("START", True, BLACK), (WIDTH//2 - 40, 415))
    return start_btn

def draw_character(label, x, y, small=False):
    color = WHITE if label == 'M' else RED
    radius = 20 if small else 30
    pygame.draw.circle(screen, color, (x, y), radius)
    screen.blit(FONT.render(label, True, BLACK), (x - 10, y - 10))

def draw_characters():
    # Left bank
    for i in range(left_bank['M']):
        draw_character("M", 80, 100 + i * 60)
    for i in range(left_bank['C']):
        draw_character("C", 140, 100 + i * 60)
    # Right bank
    for i in range(right_bank['M']):
        draw_character("M", WIDTH - 160, 100 + i * 60)
    for i in range(right_bank['C']):
        draw_character("C", WIDTH - 100, 100 + i * 60)
    # Boat passengers
    offset = 0
    for i in range(boat['M']):
        draw_character("M", boat_x + 30 + offset, HEIGHT - 160, small=True)
        offset += 40
    for i in range(boat['C']):
        draw_character("C", boat_x + 30 + offset, HEIGHT - 160, small=True)
        offset += 40

def draw_game():
    screen.fill(BLUE)
    pygame.draw.rect(screen, GREEN, (0, HEIGHT - 100, WIDTH, 100))
    pygame.draw.rect(screen, BROWN, (boat_x, HEIGHT - 140, 120, 40))  # Boat
    draw_characters()

def is_safe(bank):
    return bank['M'] == 0 or bank['M'] >= bank['C']

def toggle_passenger(char):
    global boat, boat_position
    bank = left_bank if boat_position == 'left' else right_bank
    if bank[char] > 0 and sum(boat.values()) < 2:
        bank[char] -= 1
        boat[char] += 1
    elif boat[char] > 0:
        boat[char] -= 1
        bank[char] += 1

def transfer_passengers():
    global boat
    target = right_bank if boat_position == 'left' else left_bank
    for char in ['M', 'C']:
        target[char] += boat[char]
        boat[char] = 0

def move_boat():
    global boat_position, boat_x, boat_moving
    if sum(boat.values()) == 0 or boat_moving:
        return
    boat_moving = True
    target_x = 700 if boat_position == 'left' else 200
    step = 5 if boat_position == 'left' else -5
    while (step > 0 and boat_x < target_x) or (step < 0 and boat_x > target_x):
        boat_x += step
        draw_game()
        pygame.display.flip()
        clock.tick(FPS)
    transfer_passengers()
    boat_position = 'right' if boat_position == 'left' else 'left'
    boat_moving = False

def check_game_over():
    if right_bank['M'] == 3 and right_bank['C'] == 3:
        return "Congratulations, You won the game."
    if not is_safe(left_bank) or not is_safe(right_bank):
        return "Cannibals ate the missionaries! You lost!"
    return None

def display_result(message):
    screen.fill(BLACK)
    text = BIG_FONT.render(message, True, RED if "lost" in message else GREEN)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 40))
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()

# Game loop
while True:
    if state == 'start':
        start_button = draw_start_screen()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    state = 'play'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: 
                    state = 'play'

    elif state == 'play':
        draw_game()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    toggle_passenger('M')
                elif event.key == pygame.K_c:
                    toggle_passenger('C')
                elif event.key == pygame.K_SPACE:
                    move_boat()
                    result = check_game_over()
                    if result:
                        display_result(result)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Click left bank characters if boat on left
                if boat_position == 'left':
                    if 60 < x < 100 and y < 300:
                        toggle_passenger('M')
                    elif 120 < x < 160 and y < 300:
                        toggle_passenger('C')
                # Click right bank characters if boat on right
                elif boat_position == 'right':
                    if WIDTH - 180 < x < WIDTH - 140 and y < 300:
                        toggle_passenger('M')
                    elif WIDTH - 120 < x < WIDTH - 80 and y < 300:
                        toggle_passenger('C')

                # Click boat passengers to remove them back to bank
                offset = 0
                # M on boat
                for i in range(boat['M']):
                    cx = boat_x + 30 + offset
                    cy = HEIGHT - 160
                    if (cx - x)**2 + (cy - y)**2 <= 20**2:  # radius=20 small circles
                        boat['M'] -= 1
                        if boat_position == 'left':
                            left_bank['M'] += 1
                        else:
                            right_bank['M'] += 1
                        break
                    offset += 40
                # C on boat
                for i in range(boat['C']):
                    cx = boat_x + 30 + offset
                    cy = HEIGHT - 160
                    if (cx - x)**2 + (cy - y)**2 <= 20**2:
                        boat['C'] -= 1
                        if boat_position == 'left':
                            left_bank['C'] += 1
                        else:
                            right_bank['C'] += 1
                        break
                    offset += 40

                # Click boat itself to move
                if boat_x < x < boat_x + 120 and HEIGHT - 140 < y < HEIGHT - 100:
                    move_boat()
                    result = check_game_over()
                    if result:
                        display_result(result)

    clock.tick(FPS)
    
