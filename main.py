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
# World
# ------------------------------------------------------------
terrain = Entity(
    model='plane',
    scale=(200, 1, 200),
    color=color.rgb(15, 20, 28),
    texture='white_cube',
    collider='mesh'
)

world = Entity()

# Stars / atmosphere
for i in range(300):
    star = Entity(
        parent=world,
        model='sphere',
        position=(random.uniform(-100, 100), random.uniform(15, 80), random.uniform(-100, 100)),
        scale=random.uniform(0.05, 0.25),
        color=color.rgba(200, 220, 255, 180),
    )

# Player
player = FirstPersonController(position=(0, 3, 50), speed=12, gravity=1.5, jump_height=6)
player.cursor.visible = False
player.mouse_sensitivity = Vec2(90, 90)
player.height = 1.8
mouse.locked = True
mouse.visible = False
camera.fov = 90

# Game state
game_state = {
    'current_location': None,
    'visited_locations': set(),
    'current_dialogue': None,
    'dialogue_index': 0,
    'show_interaction_prompt': False,
    'inventory': [],
    'health': 100,
}

# Character state
characters_met = {}

# ============================================================
# BOOK-ACCURATE LORE & LOCATIONS
# ============================================================

# Major locations from the books
locations = {
    'The Unraveling': {
        'name': 'The Unraveling',
        'description': 'The fractured capital city where the government maintains control through fear and division. Buildings stand in ruin, half-collapsed, symbolizing the breaking of civilization itself.',
        'extended_lore': 'This is where Juliette was imprisoned for 264 days. The Unraveling represents the physical manifestation of society crumbling. The government\'s power is slipping, yet they hold on with brutal force.',
        'hint': 'Feel the weight of oppression in the fractured architecture.',
        'position': (0, 8, 0),
        'color': color.rgba(200, 100, 100, 255),
        'scale': 4.0,
        'type': 'major_city',
        'faction': 'The Regime',
        'danger_level': 9,
    },
    'The Asylum': {
        'name': 'The Asylum',
        'description': 'A towering prison where those deemed dangerous to the state are locked away. Its walls are infused with technology meant to suppress extraordinary abilities.',
        'extended_lore': 'This is where Juliette was kept in isolation. A single touch from her caused death. The facility\'s white walls and sterile environment were designed to break the spirit. Room 1014 was her prison—and her only window to the world.',
        'hint': 'The walls remember every scream.',
        'position': (35, 6, -25),
        'color': color.rgba(240, 245, 250, 255),
        'scale': 3.2,
        'type': 'prison',
        'faction': 'The Regime',
        'danger_level': 10,
        'npc': 'Prison Guard',
    },
    'The Resistance Base': {
        'name': 'The Resistance Base',
        'description': 'A hidden sanctuary beneath the ruins where rebels gather to plan the overthrow of the regime. It\'s a place of hope, strategy, and dangerous dreams.',
        'extended_lore': 'The Resistance represents the last hope for change. Leaders like Adam Kent organize here in secret. It\'s where Juliette found allies and learned the truth about her power.',
        'hint': 'Hope blooms in darkness.',
        'position': (-40, 5, 15),
        'color': color.rgba(100, 200, 100, 255),
        'scale': 2.8,
        'type': 'base',
        'faction': 'The Resistance',
        'danger_level': 3,
        'npc': 'Adam Kent',
    },
    'Omega Point': {
        'name': 'Omega Point',
        'description': 'A massive underground complex and last refuge of superhuman rebels. Isolated from the outside world, it\'s a place where extraordinary abilities are celebrated, not feared.',
        'extended_lore': 'Omega Point exists as a counterpoint to the regime\'s oppression. Here, people with extraordinary powers live freely. It\'s protected and secret, representing a future free from persecution.',
        'hint': 'A world where power is not a curse.',
        'position': (-50, 10, -50),
        'color': color.rgba(150, 180, 255, 255),
        'scale': 3.5,
        'type': 'sanctuary',
        'faction': 'Extraordinary Beings',
        'danger_level': 2,
        'npc': 'Castle Cranshaw',
    },
    'The Sector': {
        'name': 'The Sector',
        'description': 'A walled-off region where those with extraordinary abilities are quarantined and studied. It\'s a prison disguised as a settlement.',
        'extended_lore': 'The government creates Sectors to control and monitor superhuman individuals. They market it as a place of refuge, but it\'s truly a concentration camp.',
        'hint': 'Freedom is an illusion here.',
        'position': (40, 5, 40),
        'color': color.rgba(200, 150, 100, 255),
        'scale': 3.0,
        'type': 'sector',
        'faction': 'The Regime',
        'danger_level': 7,
        'npc': 'Sector Commander',
    },
    'The Stronghold': {
        'name': 'The Stronghold',
        'description': 'The regime\'s military headquarters, bristling with weapons and surveillance. It\'s the nerve center of oppression.',
        'extended_lore': 'This is where the Supreme Leader orchestrates control. Soldiers, scientists, and strategists work here to maintain power over the fractured nation.',
        'hint': 'The heart of tyranny beats here.',
        'position': (50, 8, 0),
        'color': color.rgba(100, 100, 100, 255),
        'scale': 3.3,
        'type': 'military',
        'faction': 'The Regime',
        'danger_level': 10,
    },
    'The Wastelands': {
        'name': 'The Wastelands',
        'description': 'The ravaged territories outside the major cities. Here, nature struggles to survive alongside scattered survivors.',
        'extended_lore': 'The environment has been damaged by warfare and the regime\'s lack of care. Those who flee the cities often find themselves here, struggling for survival.',
        'hint': 'Desolation and danger in equal measure.',
        'position': (-30, 4, 50),
        'color': color.rgba(180, 140, 80, 255),
        'scale': 2.5,
        'type': 'wilderness',
        'faction': 'None',
        'danger_level': 6,
    },
    'The Archive': {
        'name': 'The Archive',
        'description': 'A hidden library of forbidden knowledge containing the truth about the world before the regime and evidence of their crimes.',
        'extended_lore': 'The regime tries to control history and truth. The Archive preserves what they want forgotten—records of the world before, evidence of atrocities, and plans for resistance.',
        'hint': 'Knowledge is power.',
        'position': (0, 6, -40),
        'color': color.rgba(180, 150, 80, 255),
        'scale': 2.4,
        'type': 'library',
        'faction': 'The Resistance',
        'danger_level': 4,
        'npc': 'Keeper of Records',
    },
}

# NPCs with book-accurate dialogue
npcs = {
    'Adam Kent': {
        'name': 'Adam Kent',
        'role': 'Leader of the Resistance',
        'first_dialogue': [
            'You\'ve found your way to us.',
            'The resistance fights against an impossible enemy.',
            'Your power—if you have one—could change everything.',
            'But first, you must decide: Will you join us?',
        ],
        'repeated_dialogue': [
            'The regime grows weaker every day.',
            'We believe in a world without fear.',
            'Have you learned anything about your abilities?',
        ]
    },
    'Castle Cranshaw': {
        'name': 'Castle Cranshaw',
        'role': 'Leader of Omega Point',
        'first_dialogue': [
            'Welcome to Omega Point.',
            'Here, we don\'t hide what we are.',
            'Extraordinary is not a curse—it\'s who we are.',
            'You\'re safe here.',
        ],
        'repeated_dialogue': [
            'The world outside grows darker.',
            'Our sanctuary is small, but it\'s real.',
            'What brings you to us today?',
        ]
    },
    'Prison Guard': {
        'name': 'Prison Guard',
        'role': 'Servant of the Regime',
        'first_dialogue': [
            'You don\'t belong here.',
            'This is a restricted area.',
            'If you\'ve got powers, you\'re a threat.',
            'Leave. Now.',
        ],
        'repeated_dialogue': [
            'Keep moving.',
            'No one escapes from here.',
        ]
    },
    'Sector Commander': {
        'name': 'Sector Commander',
        'role': 'Administrator of the Sector',
        'first_dialogue': [
            'Welcome to your new home.',
            'In the Sector, you\'re protected.',
            'But you must obey. Always.',
            'Resistance will be punished.',
        ],
        'repeated_dialogue': [
            'You\'re lucky to be here.',
            'The regime cares for those like you.',
        ]
    },
    'Keeper of Records': {
        'name': 'Keeper of Records',
        'role': 'Guardian of Truth',
        'first_dialogue': [
            'You seek knowledge.',
            'These archives hold the truth the regime tried to bury.',
            'Read carefully. Learn. Act.',
            'Knowledge is the first weapon against tyranny.',
        ],
        'repeated_dialogue': [
            'Have you found what you\'re looking for?',
            'The truth will set you free.',
        ]
    }
}

# ============================================================
# Landmark/Location Entities
# ============================================================

location_entities = {}

for loc_key, loc_data in locations.items():
    marker = Entity(
        parent=world,
        model='icosphere',
        position=loc_data['position'],
        scale=loc_data['scale'],
        color=loc_data['color'],
        emissive=loc_data['color'],
        highlight_color=loc_data['color'],
        collider='sphere',
    )
    marker.location_key = loc_key
    marker.location_data = loc_data
    marker.location_name = loc_data['name']
    marker.description = loc_data['description']
    marker.extended_lore = loc_data['extended_lore']
    marker.hint = loc_data['hint']
    marker.base_y = loc_data['position'][1]
    marker.visited = False
    location_entities[loc_key] = marker

    # Create supporting pillars/structures
    pillar = Entity(
        parent=world,
        model='cube',
        position=(loc_data['position'][0], loc_data['position'][1]-5, loc_data['position'][2]),
        scale=(2.0, 10, 2.0),
        color=color.rgba(100, 120, 150, 200),
        collider='box',
        texture='white_cube',
    )

    # Add atmospheric rings around major locations
    if loc_data['type'] in ['major_city', 'sanctuary', 'base']:
        ring = Entity(
            parent=world,
            model='torus',
            position=(loc_data['position'][0], loc_data['position'][1], loc_data['position'][2]),
            scale=(loc_data['scale'] * 2, 0.2, loc_data['scale'] * 2),
            color=loc_data['color'],
            emissive=loc_data['color'],
        )

# ============================================================
# UI Elements
# ============================================================

# Main info panel
info_text = Text(
    parent=camera.ui,
    position=(-0.78, 0.35),
    scale=1.0,
    text='Explore the world.\nApproach locations to interact.',
    origin=(0, 0),
    background=True,
    color=color.white,
    word_wrap=True,
)

# Status panel
status_text = Text(
    parent=camera.ui,
    position=(0.58, 0.35),
    scale=0.85,
    text='WASD: Move\nSPACE: Jump\nMouse: Look\nE: Interact\nESC: Unlock Cursor',
    origin=(0, 0),
    background=True,
    color=color.rgba(150, 180, 220, 255),
)

# Title
title_text = Text(
    parent=camera.ui,
    position=(-0.78, 0.80),
    scale=2.0,
    text='Shatter Me',
    origin=(0, 0),
    color=color.rgba(255, 100, 120, 255),
    bold=True,
)

# Subtitle
subtitle_text = Text(
    parent=camera.ui,
    position=(-0.78, 0.72),
    scale=0.85,
    text='A World of Fractured Hope',
    origin=(0, 0),
    color=color.rgba(200, 150, 180, 255),
)

# Dialogue panel (hidden by default)
dialogue_panel = Entity(
    parent=camera.ui,
    model='quad',
    position=(0, -0.4),
    scale=(1.6, 0.4),
    color=color.rgba(20, 20, 35, 200),
)

dialogue_text = Text(
    parent=camera.ui,
    position=(0, -0.3),
    scale=0.8,
    text='',
    origin=(0, 0),
    background=False,
    color=color.white,
    word_wrap=True,
)

speaker_text = Text(
    parent=camera.ui,
    position=(-0.7, -0.2),
    scale=0.9,
    text='',
    origin=(0, 0),
    background=False,
    color=color.rgba(255, 150, 150, 255),
    bold=True,
)

interaction_prompt = Text(
    parent=camera.ui,
    position=(0, -0.75),
    scale=0.8,
    text='Press E to interact',
    origin=(0, 0),
    color=color.rgba(150, 255, 200, 255),
    background=True,
)

interaction_prompt.visible = False

# Visited locations tracker
visited_text = Text(
    parent=camera.ui,
    position=(0.78, 0.80),
    scale=0.75,
    text='Locations Visited: 0/8',
    origin=(1, 0),
    background=True,
    color=color.rgba(180, 200, 220, 255),
)

# ============================================================
# Interaction System
# ============================================================

def inspect_target():
    hit = raycast(camera.world_position, camera.forward, distance=25, ignore=[player, terrain])
    if hit.hit and hasattr(hit.entity, 'location_key'):
        return hit.entity
    return None

def start_dialogue(npc_name, is_first_encounter=False):
    if npc_name in npcs:
        npc = npcs[npc_name]
        speaker_text.text = f"{npc['name']} - {npc['role']}"
        
        if is_first_encounter:
            dialogue = npc['first_dialogue']
        else:
            dialogue = npc['repeated_dialogue']
        
        dialogue_text.text = '\n'.join(dialogue)
        dialogue_panel.visible = True
        speaker_text.visible = True
        dialogue_text.visible = True

def end_dialogue():
    dialogue_panel.visible = False
    speaker_text.visible = False
    dialogue_text.visible = False

# ============================================================
# Update Loop
# ============================================================

def update():
    global game_state
    
    # Mouse/escape key handling
    if held_keys['escape']:
        mouse.locked = False
        mouse.visible = True
    
    if mouse.locked == False and held_keys['mouse1']:
        mouse.locked = True
        mouse.visible = False
    
    # Animate all locations
    for loc_key, entity in location_entities.items():
        entity.rotation_y += time.dt() * 20
        entity.y = entity.base_y + sin(time.time() * 2 + entity.position.x * 0.1) * 0.6
    
    # Check if player is looking at a location
    target = inspect_target()
    game_state['current_location'] = target
    
    if target:
        interaction_prompt.visible = True
        
        loc_data = target.location_data
        info_text.text = f"{loc_data['name']}\n\n{loc_data['description']}\n\nDanger Level: {loc_data['danger_level']}/10"
        
        # Track visited locations
        if not target.visited:
            target.visited = True
            game_state['visited_locations'].add(target.location_key)
            visited_text.text = f"Locations Visited: {len(game_state['visited_locations'])}/8"
            
            # Bonus info on first visit
            info_text.text += f"\n\n[First Visit]\n{loc_data['extended_lore']}"
    else:
        interaction_prompt.visible = False
        info_text.text = 'Explore the world.\nApproach locations to interact.'
    
    # Keep player from falling
    if player.y < -10:
        player.position = Vec3(0, 3, 50)

# ============================================================
# Input Handling
# ============================================================

def input(key):
    global game_state, characters_met
    
    if key == 'e':
        target = inspect_target()
        if target:
            loc_data = target.location_data
            loc_name = target.location_key
            
            # End previous dialogue
            end_dialogue()
            
            # Check if there's an NPC here
            if 'npc' in loc_data:
                npc_name = loc_data['npc']
                is_first = npc_name not in characters_met
                
                if is_first:
                    characters_met[npc_name] = True
                
                start_dialogue(npc_name, is_first)
            else:
                # Show location info
                info_text.text = f"{loc_data['name']}\n\n{loc_data['extended_lore']}"
    
    if key == 'space' or key == 'w' or key == 'a' or key == 's' or key == 'd':
        end_dialogue()

app.run()
