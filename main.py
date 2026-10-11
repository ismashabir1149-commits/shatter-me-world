from ursina import *
import random

app = Ursina()
window.title = 'Shatter Me: Interactive World'
window.borderless = False
window.fps_counter.enabled = False
window.exit_button.visible = False
window.color = color.rgb(8, 12, 20)

# ------------------------------------------------------------
# Scene setup
# ------------------------------------------------------------
scene.fog_color = color.rgb(7, 10, 18)
scene.fog_density = 0.02
Sky(color=color.rgb(10, 16, 26))

AmbientLight(color=color.rgba(160, 170, 220, 180), brightness=0.75)
DirectionalLight(parent=scene, y=25, z=15, rotation=(45, -30, 0), color=color.white, shadows=True)
PointLight(parent=scene, x=-20, y=12, z=-8, color=color.azure, range=50)

# ------------------------------------------------------------
# World surface
# ------------------------------------------------------------
terrain = Entity(
    model='plane',
    scale=(200, 1, 200),
    color=color.rgb(15, 20, 28),
    texture='white_cube',
    collider='mesh'
)

world = Entity()

# Floating stars
for _ in range(300):
    star = Entity(
        parent=world,
        model='sphere',
        position=(random.uniform(-100, 100), random.uniform(15, 80), random.uniform(-100, 100)),
        scale=random.uniform(0.05, 0.25),
        color=color.rgba(200, 220, 255, 180),
    )

# ------------------------------------------------------------
# Player setup
# ------------------------------------------------------------
player = FirstPersonController(position=(0, 3, 50), speed=12, gravity=1.5, jump_height=6)
player.cursor.visible = False
player.mouse_sensitivity = Vec2(90, 90)
player.height = 1.8
mouse.locked = True
mouse.visible = False
camera.fov = 90

# ------------------------------------------------------------
# Game state
# ------------------------------------------------------------
visited_locations = set()
characters_met = {}

def create_info_text():
    return Text(
        parent=camera.ui,
        position=(-0.78, 0.35),
        scale=1.0,
        text='Explore the world.\nApproach a glowing landmark.',
        origin=(0, 0),
        background=True,
        color=color.white,
        word_wrap=True,
    )

info_text = create_info_text()
status_text = Text(
    parent=camera.ui,
    position=(0.58, 0.35),
    scale=0.85,
    text='WASD: Move\nSPACE: Jump\nMouse: Look\nE: Interact\nESC: Unlock Cursor',
    origin=(0, 0),
    background=True,
    color=color.rgba(150, 180, 220, 255),
)

title_text = Text(
    parent=camera.ui,
    position=(-0.78, 0.80),
    scale=2.0,
    text='Shatter Me',
    origin=(0, 0),
    color=color.rgba(255, 100, 120, 255),
    bold=True,
)

subtitle_text = Text(
    parent=camera.ui,
    position=(-0.78, 0.72),
    scale=0.85,
    text='A World of Fractured Hope',
    origin=(0, 0),
    color=color.rgba(200, 150, 180, 255),
)

interaction_prompt = Text(
    parent=camera.ui,
    position=(0, -0.75),
    scale=0.8,
    text='Press E to interact',
    origin=(0, 0),
    background=True,
    color=color.rgba(150, 255, 200, 255),
)
interaction_prompt.visible = False

visited_counter = Text(
    parent=camera.ui,
    position=(0.78, 0.80),
    scale=0.75,
    text='Locations Visited: 0/8',
    origin=(1, 0),
    background=True,
    color=color.rgba(180, 200, 220, 255),
)

# Dialogue panel
speaker_text = Text(
    parent=camera.ui,
    position=(-0.7, -0.15),
    scale=0.9,
    text='',
    origin=(0, 0),
    background=False,
    color=color.rgba(255, 150, 150, 255),
    bold=True,
)

dialogue_text = Text(
    parent=camera.ui,
    position=(-0.7, -0.35),
    scale=0.8,
    text='',
    origin=(0, 0),
    background=False,
    color=color.white,
    word_wrap=True,
)

dialogue_panel = Entity(
    parent=camera.ui,
    model='quad',
    position=(0, -0.35),
    scale=(1.8, 0.45),
    color=color.rgba(20, 20, 35, 200),
)
dialogue_panel.visible = False
speaker_text.visible = False
dialogue_text.visible = False

# ------------------------------------------------------------
# Locations & lore
# ------------------------------------------------------------
locations = {
    'The Asylum': {
        'name': 'The Asylum',
        'description': 'A sterile prison of isolation, terror, and unbearable control. A place where fear is treated as law.',
        'extended_lore': 'This is the prison where Juliette was kept hidden from the world. The walls are designed to isolate, quiet, and erase individuality.',
        'hint': 'The walls have seen too much silence.',
        'position': (35, 6, -25),
        'color': color.rgba(240, 245, 250, 255),
        'scale': 3.2,
        'type': 'prison',
        'danger_level': 10,
        'npc': 'Prison Guard',
    },
    'The Resistance Base': {
        'name': 'The Resistance Base',
        'description': 'A hidden sanctuary where rebels gather to plan, dream, and continue fighting.',
        'extended_lore': 'This secret refuge is rooted in hope and resistance. It is the opposite of the regime: vigilant, human, and uncertain.',
        'hint': 'Hope survives here in the dark.',
        'position': (-40, 5, 15),
        'color': color.rgba(100, 200, 100, 255),
        'scale': 2.8,
        'type': 'base',
        'danger_level': 4,
        'npc': 'Adam Kent',
    },
    'Omega Point': {
        'name': 'Omega Point',
        'description': 'A hidden refuge for extraordinary people, where identity and power are not feared but protected.',
        'extended_lore': 'Omega Point is the place where fear gives way to possibility. It is not just a safe haven; it is a beginning.',
        'hint': 'Freedom feels possible here.',
        'position': (-50, 10, -50),
        'color': color.rgba(150, 180, 255, 255),
        'scale': 3.5,
        'type': 'sanctuary',
        'danger_level': 2,
        'npc': 'Castle Cranshaw',
    },
    'The Sector': {
        'name': 'The Sector',
        'description': 'A walled zone of control, surveillance, and rigid discipline. It is a prison of order disguised as protection.',
        'extended_lore': 'The regime uses sectors to monitor, shape, and confine extraordinary people under the guise of safety.',
        'hint': 'The walls are built to watch you.',
        'position': (40, 5, 40),
        'color': color.rgba(200, 150, 100, 255),
        'scale': 3.0,
        'type': 'sector',
        'danger_level': 7,
        'npc': 'Sector Commander',
    },
    'The Stronghold': {
        'name': 'The Stronghold',
        'description': 'The regime\'s heavy military center, designed to dominate and terrorize the rest of the world.',
        'extended_lore': 'This is where power becomes architecture. Walls, weapons, and surveillance enforce fear and obedience.',
        'hint': 'This place is built to intimidate.',
        'position': (50, 8, 0),
        'color': color.rgba(100, 100, 100, 255),
        'scale': 3.3,
        'type': 'military',
        'danger_level': 10,
    },
    'The Archive': {
        'name': 'The Archive',
        'description': 'A hidden storehouse of forbidden truth, where stories and documents the regime wanted erased still remain.',
        'extended_lore': 'The Archive protects memory itself. It keeps records of the past that the state would rather bury.',
        'hint': 'Knowledge is one of the last forms of resistance.',
        'position': (0, 6, -40),
        'color': color.rgba(180, 150, 80, 255),
        'scale': 2.4,
        'type': 'library',
        'danger_level': 4,
        'npc': 'Keeper of Records',
    },
    'The Sanctuary': {
        'name': 'The Sanctuary',
        'description': 'A place of healing, recovery, and peace — a rare pause in a world shaped by violence.',
        'extended_lore': 'Even in a fractured world, there are places where people can breathe. The Sanctuary offers relief, rest, and fragments of hope.',
        'hint': 'A quiet place feels almost impossible here.',
        'position': (-18, 5, 20),
        'color': color.rgba(130, 255, 215, 255),
        'scale': 1.9,
        'type': 'sanctuary',
        'danger_level': 2,
    },
    'The Wastelands': {
        'name': 'The Wastelands',
        'description': 'A ruined frontier of ash, broken roads, and survivors trying to remain hidden from the world.',
        'extended_lore': 'Beyond the cities and strongholds lie strips of abandoned land where survival becomes the only law.',
        'hint': 'This land remembers what war left behind.',
        'position': (-30, 4, 50),
        'color': color.rgba(180, 140, 80, 255),
        'scale': 2.5,
        'type': 'wilderness',
        'danger_level': 6,
    },
}

npcs = {
    'Adam Kent': {
        'name': 'Adam Kent',
        'role': 'Leader of the Resistance',
        'first_dialogue': [
            'You\'ve made it here.',
            'This is where the resistance learns to fight another day.',
            'Power is dangerous, but hope is stronger.',
            'We need people who can choose a future, not just survive a present.',
        ],
        'repeat_dialogue': [
            'The regime is cracking.',
            'Every day, more people refuse to live in fear.',
            'If you understand what this world has done to people, then you understand what we are fighting for.',
        ],
    },
    'Castle Cranshaw': {
        'name': 'Castle Cranshaw',
        'role': 'Leader of Omega Point',
        'first_dialogue': [
            'Welcome to Omega Point.',
            'We do not hide who we are here.',
            'Our powers are not a burden. They are our future.',
            'You are not alone in this world.',
        ],
        'repeat_dialogue': [
            'There is strength in surviving what others could not.',
            'We are not monsters. We are the next step.',
            'If you stay long enough, you may understand what freedom really means.',
        ],
    },
    'Prison Guard': {
        'name': 'Prison Guard',
        'role': 'Servant of the Regime',
        'first_dialogue': [
            'This place is not for you.',
            'The state controls what it fears.',
            'You should leave before you become part of the problem.',
            'There is no mercy here.',
        ],
        'repeat_dialogue': [
            'Keep moving.',
            'The regime does not forgive rebellion.',
            'Mind your own business.',
        ],
    },
    'Sector Commander': {
        'name': 'Sector Commander',
        'role': 'Administrator of the Sector',
        'first_dialogue': [
            'This is order.',
            'Security is peace, and peace is necessary.',
            'You will learn to obey, or you will fall.',
            'The state protects you from yourself.',
        ],
        'repeat_dialogue': [
            'Disobedience is not freedom.',
            'Control is the only way to survive this kind of world.',
        ],
    },
    'Keeper of Records': {
        'name': 'Keeper of Records',
        'role': 'Guardian of History',
        'first_dialogue': [
            'History is a weapon when it is hidden.',
            'The regime wants the truth buried, but it cannot vanish.',
            'Read carefully. Memories are stronger than walls.',
            'The past is still alive under all this ruin.',
        ],
        'repeat_dialogue': [
            'Truth is often more dangerous than violence.',
            'A country disappears when its story disappears.',
        ],
    },
}

location_entities = {}

for key, data in locations.items():
    marker = Entity(
        parent=world,
        model='icosphere',
        position=data['position'],
        scale=data['scale'],
        color=data['color'],
        emissive=data['color'],
        highlight_color=data['color'],
        collider='sphere',
    )
    marker.location_key = key
    marker.location_data = data
    marker.base_y = data['position'][1]
    location_entities[key] = marker

    pillar = Entity(
        parent=world,
        model='cube',
        position=(data['position'][0], data['position'][1] - 5, data['position'][2]),
        scale=(2.0, 10, 2.0),
        color=color.rgba(100, 120, 150, 200),
        collider='box',
        texture='white_cube',
    )

    if data['type'] in ['prison', 'sanctuary', 'base']:
        ring = Entity(
            parent=world,
            model='torus',
            position=(data['position'][0], data['position'][1], data['position'][2]),
            scale=(data['scale'] * 2.2, 0.2, data['scale'] * 2.2),
            color=data['color'],
            emissive=data['color'],
        )

# ------------------------------------------------------------
# Interaction helpers
# ------------------------------------------------------------
def inspect_target():
    hit = raycast(camera.world_position, camera.forward, distance=25, ignore=[player, terrain])
    if hit.hit and hasattr(hit.entity, 'location_key'):
        return hit.entity
    return None


def dialogue_panel_show(text, speaker_name=''):
    speaker_text.text = speaker_name
    dialogue_text.text = text
    dialogue_panel.visible = True
    speaker_text.visible = True
    dialogue_text.visible = True


def dialogue_panel_hide():
    dialogue_panel.visible = False
    speaker_text.visible = False
    dialogue_text.visible = False


def start_conversation(location):
    loc_data = location.location_data
    npc_name = loc_data.get('npc')
    if npc_name is None:
        info_text.text = f"{loc_data['name']}\n\n{loc_data['extended_lore']}"
        return

    if npc_name not in characters_met:
        characters_met[npc_name] = True
        lines = npcs[npc_name]['first_dialogue']
        dialogue_panel_show('\n'.join(lines), npcs[npc_name]['name'])
    else:
        lines = npcs[npc_name]['repeat_dialogue']
        dialogue_panel_show('\n'.join(lines), npcs[npc_name]['name'])


# ------------------------------------------------------------
# Update loop
# ------------------------------------------------------------
def update():
    if held_keys['escape']:
        mouse.locked = False
        mouse.visible = True

    if not mouse.locked and held_keys['mouse1']:
        mouse.locked = True
        mouse.visible = False

    # Float landmarks gently
    for entity in location_entities.values():
        entity.rotation_y += time.dt * 18
        entity.y = entity.base_y + sin(time.time() * 2 + entity.position.x * 0.12) * 0.7

    target = inspect_target()
    if target:
        interaction_prompt.visible = True
        data = target.location_data
        info_text.text = f"{data['name']}\n\n{data['description']}\n\nDanger Level: {data['danger_level']}/10"

        if not target.location_key in visited_locations:
            visited_locations.add(target.location_key)
            visited_counter.text = f"Locations Visited: {len(visited_locations)}/8"
            info_text.text += f"\n\n[New Location]\n{data['extended_lore']}"
    else:
        interaction_prompt.visible = False
        info_text.text = 'Explore the world.\nApproach a glowing landmark.'

    if player.y < -10:
        player.position = Vec3(0, 3, 50)


# ------------------------------------------------------------
# Input handling
# ------------------------------------------------------------
def input(key):
    if key == 'e':
        target = inspect_target()
        if target:
            start_conversation(target)
    if key in ('space', 'w', 'a', 's', 'd'):
        dialogue_panel_hide()

    if key == 'mouse1':
        if mouse.locked:
            mouse.locked = False
            mouse.visible = True
        else:
            mouse.locked = True
            mouse.visible = False

    if key == 'escape':
        mouse.locked = False
        mouse.visible = True


app.run()
