from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

window.title = "Zombie Survival 3D"
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = True

# sky
Sky(color=color.black)

# lighting
DirectionalLight(
    shadows=True,
    rotation=(60,-30,30),
    color=color.rgb(255,240,220)
)

AmbientLight(
    color=color.rgba(15,15,15,0.25)
)

# ground
ground = Entity(
    model ='plane',
    scale = (120,1,120),
    texture ='grass',
    texture_scale = (60,60),
    color = color.rgb(35, 35, 35),
    collider ='box'
)

# player
player = FirstPersonController(
    position=(0,2,0)
)

player.speed = 5
player.jump_height = 5
player.gravity = 0.5
camera.fov = 90

# walls
wall_height = 5
wall_thickness = 1
ground_size = 120

Entity(
    mode = 'cube',
    position = (0, wall_height/2, ground_size/2),
    scale = (ground_size, wall_height, wall_thickness),
    collider = 'box',
    visible = False
)

Entity(
    mode = 'cube',
    position = (0, wall_height/2, -ground_size/2),
    scale = (ground_size, wall_height, wall_thickness),
    collider = 'box',
    visible = False
)

Entity(
    mode = 'cube',
    position = (-ground_size/2, wall_height/2),
    scale = (wall_thickness, wall_height, ground_size),
    collider = 'box',
    visible = False
)

# trees
for i in range(1):
    x = random.randint(-50,50)
    z = random.randint(-50,50)
    
    Entity(
        model='tree2.glb',
        scale=3,
        position=(0,3.5,0)
    )

# zombies
zombies = []
for i in range(10):
    zombie = Entity(
        model='zombie2.glb',
        scale=1.5,
        position=(
            random.randint(-30,30),
            1.5,
            random.randint(-30,30)
        ),
        rotation_y=-180
    )

    zombies.append(zombie)

# medicine
meds = []
for i in range(10):
    med = Entity(
        model='med.obj',
        color=color.red,
        scale=0.02,
        position=(
            random.randint(-40,40),
            1,
            random.randint(-40,40)
        )
    )
    
    meds.append(med)

# ui
score = 0
health = 100
game_over = False
paused = False
game_over_text = None
restart_text = None
win_text = None

score_text = Text(
    text=f"Score : {score}",
    position=(-0.85,0.45),
    scale=2
)

health_text = Text(
    text=f"Health : {health}",
    position=(-0.85,0.40),
    scale=2
)

title = Text(
    text="ZOMBIE SURVIVAL",
    position=(-0.2,0.45),
    scale=2
)

# pause menu
pause_bg = Panel(
    scale=(0.4,0.5),
    enabled=False
)

pause_text = Text(
    "PAUSED",
    parent=pause_bg,
    y=.18,
    scale=2
)

resume_button = Button(
    text="RESUME",
    parent=pause_bg,
    y=.05,
    scale=(0.5,0.15)
)

restart_button = Button(
    text="RESTART",
    parent=pause_bg,
    y=-.1,
    scale=(0.5,0.15)
)

exit_button = Button(
    text="EXIT",
    parent=pause_bg,
    y=-.25,
    scale=(0.5,0.15),
    color=color.red
)

# functions
def resume_game():
    global paused
    paused = False
    pause_bg.disable()
    mouse.locked = True
    player.enabled = True

def reset_game():
    global score, health, game_over

    score = 0
    health = 100
    game_over = False

    score_text.text = f"Score : {score}"
    health_text.text = f"Health : {health}"

    # reset player
    player.position = (0,2,0)
    player.enabled = True
    mouse.locked = True

    # reset zombies
    for zombie in zombies:
        zombie.position = (
            random.randint(-30,30),
            1,
            random.randint(-30,30)
        )

    # reset medicine
    for med in meds:
        med.enable()
        med.position = (      
        random.randint(-30, 30),
        1,
        random.randint(-30, 30)
        )

    # hapus UI game over
    if game_over_text:
        game_over_text.disable()

    if restart_text:
        restart_text.disable()

    if win_text:
        win_text.disable()
        
def restart_game():
    reset_game()
    pause_bg.disable()
    mouse.locked = True

def exit_game():
    application.quit()

resume_button.on_click = resume_game
restart_button.on_click = restart_game
exit_button.on_click = exit_game

# input
def input(key):
    global paused
    if key == 'escape':
        paused = not paused
        pause_bg.enabled = paused
        mouse.locked = not paused
        player.enabled = not paused

    if key == 'r' and game_over:
        reset_game()

# update
def update():
    global score
    global health
    global game_over
    global game_over_text
    global restart_text
    global win_text

    if paused or game_over:
        return

    # zombie movement
    for zombie in zombies:
        direction = (player.position - zombie.position).normalized()
        zombie.position += direction * time.dt * 1.2
        zombie.look_at(player)

        # zombie collision
        if distance(player.position, zombie.position) < 2:
            health -= 20 * time.dt
            
            if health < 0:
                health = 0
                
            health_text.text = f"Health : {int(health)}"

    # medicine collision
    for med in meds:
        if med.enabled and distance(player.position, med.position) < 1.5:
            med.disable()
            score += 1
            score_text.text = f"Score : {score}"

    # win condition
    all_collected = True
    for med in meds:
        if med.enabled:
            all_collected = False

    if all_collected and not game_over:
        game_over = True
        mouse.locked = False
        
        def set_pause(state):
            global paused
            paused = state
            pause_bg.enabled = state
            mouse.locked = not state
            player.cursor.enabled = not state
            
        def input(key):
            if key == 'escape':
                set_pause(not paused)

        win_text = Text(
            text="YOU WIN!",
            scale=5,
            origin=(0,0),
            background=True
        )

        restart_text = Text(
            text="Press R To Restart",
            y=-0.1,
            scale=2,
            origin=(0,0)
        )

    # game over
    if health <= 0 and not game_over:
        game_over = True
        mouse.locked = False
        player.enabled = False

        game_over_text = Text(
            text="GAME OVER",
            scale=5,
            origin=(0,0),
            background=True
        )

        restart_text = Text(
            text="Press R To Restart",
            y=-0.1,
            scale=2,
            origin=(0,0)
        )

app.run()