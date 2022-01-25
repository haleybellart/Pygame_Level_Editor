import pygame
import button
import csv
import pickle

pygame.init()

clock = pygame.time.Clock()
FPS = 60

#set game wsindow size
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
LOWER_MARGIN = 100
SIDE_MARGIN=300

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('PewPew Level Editor')


#Define game varaibles 
ROWS = 16
MAX_COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 23 # add more to value for more tile types 
level = 0
current_tile = 0
scroll_left = False 
scroll_right = False
scroll = 0
scroll_speed = 1 

#define colors
GREEN = (100, 189, 104)
BLACk = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 25, 25)
BG = (252, 182, 96)

font = pygame.font.SysFont('Futura', 30)

#create empty tile list
world_data = []
for row in range (ROWS):
    r = [-1] * MAX_COLS
    world_data.append(r)

#create ground 
for tile in range(0, MAX_COLS):
    world_data[ROWS - 1][tile] = 0

#function for drawing text onto screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

#load background/button images
bg_grass = pygame.image.load('data/img/background/bg_grass.png').convert_alpha()
bg_mount = pygame.image.load('data/img/background/bg_mount.png').convert_alpha()
bg_clouds = pygame.image.load('data/img/background/bg_clouds.png').convert_alpha()
bg_sky = pygame.image.load('data/img/background/bg_sky.png').convert_alpha()
save_img = pygame.image.load('data/img/save_btn.png').convert_alpha()
load_img = pygame.image.load('data/img/load_btn.png').convert_alpha()

#store tiles in list 
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'data/img/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)


#create funcion for drawing background, make background parallax  
def draw_bg():
    screen.fill(BG)
    width = bg_sky.get_width()
    for x in range(4):
        screen.blit(bg_sky, ((x * width) - scroll * 0.5, 0))
        screen.blit(bg_clouds, ((x * width) - scroll * 0.6, SCREEN_HEIGHT - bg_clouds.get_height() - 250))
        screen.blit(bg_mount, ((x * width) - scroll * 0.7, SCREEN_HEIGHT - bg_mount.get_height() - 150))
        screen.blit(bg_grass, ((x * width) - scroll * 0.8, SCREEN_HEIGHT - bg_grass.get_height()))

#create function for tile grid 
def draw_grid():
    #vertical lines
    for c in range(MAX_COLS + 1):
        pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
    #horizontal lines
    for c in range(ROWS + 1):
        pygame.draw.line(screen, WHITE, (0, c * TILE_SIZE), (SCREEN_WIDTH, c * TILE_SIZE))


#drawing world tiles
def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))

#create buttons
save_button = button.Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT + LOWER_MARGIN-50, save_img, 1)
load_button = button.Button(SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT + LOWER_MARGIN-50, load_img, 1)

#make buttons/tiles list
button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
    tile_button = button.Button(SCREEN_WIDTH + (75 * button_col) + 50, 75 * button_row + 50, img_list[i], 1) 
    button_list.append(tile_button)
    button_col += 1
    if button_col == 3:
        button_row += 1
        button_col = 0

#main loop
run = True
while run: 

    clock.tick(FPS)

    draw_bg()
    draw_grid()
    draw_world()

    draw_text(f'Level: {level}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
    draw_text('Press UP or DOWN to change level', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)
    draw_text('Hold CONTROL to speed up scrolling', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 30)

    #save/load data
    if save_button.draw(screen):
        with open(f'data/levels/level_{level}_data.csv', 'w', newline='') as csvfile: 
            writer = csv.writer(csvfile, delimiter = ',')
            for row in world_data: 
                writer.writerow(row)
            
    if load_button.draw(screen):
        #load in level data
        #reset scroll 
        scroll = 0 
        #world_data = []
        #pickle_in = open(f'level_{level}_data', 'rb')
        #world_data = pickle.load(pickle_in)
        with open(f'data/levels/level_{level}_data.csv', newline='') as csvfile: 
            reader = csv.reader(csvfile, delimiter = ',')
            for x, row in enumerate(reader): 
              for y, tile in enumerate(row):
                  world_data[x][y] = int(tile)
                


    #draw tile panel and tiles 
    pygame.draw.rect(screen, BG, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))

    #choose a tile
    button_count = 0 
    for button_count, i in enumerate(button_list): 
        if i.draw(screen):
            current_tile = button_count

    #highlight selected tile
    pygame.draw.rect(screen, WHITE, button_list[current_tile].rect, 3)

    #scroll map
    if scroll_left == True and scroll > 0: 
        scroll  -= 5 * scroll_speed
    if scroll_right == True and scroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH: 
        scroll += 5 * scroll_speed

    #get mouse position 
    pos = pygame.mouse.get_pos()
    x = (pos[0]+ scroll) // TILE_SIZE
    y = pos[1] // TILE_SIZE

    #check that coordinates are in tile area 
    if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
        #update tile value
        if pygame.mouse.get_pressed()[0] == 1:
            if world_data[y][x] != current_tile:
                world_data[y][x] = current_tile
        #delete tile
        if pygame.mouse.get_pressed()[2] == 1:
            world_data[y][x] = -1


    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            run = False 
        #keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and level < 10:
                level += 1
            if event.key == pygame.K_DOWN and level > 0:
                level -= 1
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_LEFT:
                scroll_left = True                
            if event.key ==pygame. K_LSHIFT:
                scroll_speed = 5
            if event.key == pygame.K_ESCAPE:
                run=False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key ==pygame.K_LSHIFT:
                scroll_speed  = 1

    pygame.display.update()

pygame.quit()
