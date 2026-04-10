#!/usr/bin/env python3
"""
ELECEED: AWAKENED DUEL
COMPLETE EDITION - NUMBERS INSTEAD OF LETTERS FOR ALL COMMANDS
Kayden • Kartein • Pluton • Full Eleceed Villain Roster

BUGFIX LOG:
  FIX 1 - cleanup(): Removed random.random() early-expiry on Limit Breaker, Domain, Cloak timers.
           Timers now count down deterministically and expire only at 0.
  FIX 2 - use_ability(): Replaced recursive self-call on bad input with a while-loop.
           select_target(): Same — no more RecursionError on repeated bad input.
  FIX 3 - Cat Punch hint: Added "(requires cat form — press 0 to toggle)" note in ability list.
           Toggle command now shows its current state clearly.
  FIX 4 - Lensing buff removal: Moved remove() call to a single location after the lensing
           block so it is consumed exactly once per hit, regardless of hit/miss outcome.
  FIX 5 - Entropic Ward: Behaviour documented as intentional (triggers only when Kartein is targeted).
  FIX 6 - Energy regen moved to cleanup() (end-of-turn) so players cannot immediately spend
           energy they haven't earned yet at the start of a new turn.
  FIX 7 - Tournament quarterfinals: Fixed "vs Jinwoo" match that was calling create_enemy_jiwoo()
           instead of create_enemy_jinwoo().
"""

import random
import time
import sys
from enum import Enum

# ============================================================================
# TEXT SPEED CONTROL
# ============================================================================

TEXT_SPEED = 0.6
BATTLE_START_DELAY = 2.0
TURN_DELAY = 1.0
ACTION_DELAY = 0.8
VICTORY_DELAY = 2.5


def slow_print(text, delay=0.03):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


# ============================================================================
# GAME MODES ENUM
# ============================================================================

class GameMode(Enum):
    STORY = "1. Story Mode - Follow the Eleceed storyline"
    GAUNTLET = "2. Ranker Gauntlet - Fight through all ranks"
    BOSS_RUSH = "3. Boss Rush - Only major villains"
    SURVIVAL = "4. Endless Survival - How many waves?"
    FRAME_RAID = "5. Frame Raid - Infiltrate enemy headquarters"
    TOP_10 = "6. Top 10 Tournament - Face the world's strongest"
    SPARRING = "7. Training Room - Practice against any character"


# ============================================================================
# CHARACTER BASE CLASS
# ============================================================================

class Character:
    def __init__(self, name, title, hp, energy):
        self.name = name
        self.title = title
        self.hp = hp
        self.max_hp = hp
        self.energy = energy
        self.max_energy = energy
        self.abilities = {}
        self.buffs = []
        self.debuffs = []
        self.defending = False
        self.form = "Normal"
        self.wing_state = "none"
        self.affiliation = ""

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp


# ============================================================================
# KAYDEN BREAK
# ============================================================================

class Kayden(Character):
    def __init__(self):
        super().__init__("Kayden Break", "The Uncrowned King", 380, 280)
        self.abilities = {
            '1': {"name": "Lightning Strike", "cost": 15, "dmg": (45, 75), "type": "damage",
                  "desc": "Fundamental lightning projection. Fires pinpoint bolts or wide-area barrages."},
            '2': {"name": "Compressed Spear", "cost": 35, "dmg": (70, 100), "type": "damage",
                  "desc": "City-block energy compressed into a single lance. Near-infinite piercing capability."},
            '3': {"name": "Zero Impact", "cost": 30, "dmg": (60, 90), "type": "damage",
                  "desc": "Internal annihilation. All destructive force delivered internally, leaving small external wounds."},
            '4': {"name": "Zero Impact Spear", "cost": 55, "dmg": (90, 140), "type": "damage",
                  "desc": "Fusion of Compressed Spear and Zero Impact. Absolute piercing force + complete internal annihilation."},
            '5': {"name": "Grand Cross", "cost": 60, "dmg": (110, 150), "type": "damage",
                  "desc": "Two massive lightning waves overlapping to form a colossal cross."},
            '6': {"name": "Divine Judgment", "cost": 80, "dmg": (140, 190), "type": "damage",
                  "desc": "Monumental pillar of white-hot divine lightning from the heavens. Stuns target."},
            '7': {"name": "Lightning Cloak", "cost": 40, "dmg": (0, 0), "type": "domain", "domain": "cloak",
                  "desc": "CRACKLING ARMOR - Kayden engulfs himself in tangible, crackling armor of highly-compressed lightning. +30% damage (5 turns)."},
            '8': {"name": "Dominant Zone", "cost": 70, "dmg": (0, 0), "type": "domain", "domain": "zone",
                  "desc": "PERSONAL DOMAIN - Kayden creates his own personal isolated domain that amplifies his power. +40% damage (4 turns)."},
            '9': {"name": "Limit Breaker", "cost": 100, "dmg": (0, 0), "type": "domain", "domain": "limit",
                  "desc": "Emergency override. Hair and lightning turn arctic white. +80% damage to ALL moves (3 turns)."},
            '10': {"name": "Max Speed", "cost": 50, "dmg": (80, 120), "type": "damage",
                   "desc": "Concentrate all power within the body to pierce any skill."},
            '11': {"name": "Plasma Chains", "cost": 25, "dmg": (40, 60), "type": "damage",
                   "desc": "Razor-sharp chains of condensed lightning for binding and cutting."},
            '12': {"name": "Brain Shock", "cost": 15, "dmg": (1, 1), "type": "damage",
                   "desc": "Precise, non-lethal application. Controlled shock to the brain. Stuns target."},
            # FIX 3: description now clearly flags cat form requirement
            '13': {"name": "Cat Punch", "cost": 20, "dmg": (50, 80), "type": "damage",
                   "desc": "Special move developed in cat form. REQUIRES CAT FORM — press 0 to toggle cat form on."},
            '14': {"name": "Shield", "cost": 20, "dmg": (0, 0), "type": "utility",
                   "desc": "Force field of highly concentrated electrical energy. Protects self and allies."},
            '15': {"name": "Spatial Isolation Barrier", "cost": 45, "dmg": (0, 0), "type": "utility",
                   "desc": "Snap of the finger. Isolates space to create separate dimensional battlefield. Isolates all enemies."},
        }
        self.cloak = False
        self.domain = False
        self.cat_form = False
        self.form = "Normal"
        self.domain_placed = False
        self.domain_timer = 0
        self.cloak_timer = 0
        self.limit_timer = 0

    def get_damage_multiplier(self):
        mult = 1.0
        buffs = []
        if self.form == "Limit Breaker":
            mult *= 1.8
            buffs.append("LIMIT BREAKER")
        if self.domain:
            mult *= 1.4
            buffs.append("DOMINANT ZONE")
        if self.cloak:
            mult *= 1.3
            buffs.append("LIGHTNING CLOAK")
        return mult, buffs

    def activate_domain(self, domain_type):
        if domain_type == "cloak":
            self.cloak = True
            self.cloak_timer = 5
            self.domain_placed = True
            return "LIGHTNING CLOAK DEPLOYED! Crackling armor surrounds Kayden! [ACTIVE] +30% damage (5 turns)"
        elif domain_type == "zone":
            self.domain = True
            self.domain_timer = 4
            self.domain_placed = True
            return "DOMINANT ZONE ESTABLISHED! His world, his law! [ACTIVE] +40% damage (4 turns)"
        elif domain_type == "limit":
            self.form = "Limit Breaker"
            self.limit_timer = 3
            self.domain_placed = True
            self.hp = min(self.max_hp, self.hp + 50)
            return "LIMIT BREAKER! Kayden breaks past all ceilings! [LIMIT BREAKER] +80% damage (3 turns)"
        return ""


# ============================================================================
# KARTEIN
# ============================================================================

class Kartein(Character):
    def __init__(self):
        super().__init__("Kartein", "The Fearsome Healer", 300, 240)
        self.abilities = {
            '1': {"name": "Cellular Regeneration", "cost": 25, "heal": (40, 60), "mode": "healing", "type": "heal",
                  "desc": "Advanced cellular regeneration. Instantaneously regenerates severe wounds."},
            '2': {"name": "Healing Beam", "cost": 30, "heal": (50, 75), "mode": "healing", "type": "heal",
                  "desc": "Long-distance healing beam. Projects focused beam of green-gold healing energy."},
            '3': {"name": "Life-Force Transfer", "cost": 40, "heal": (70, 100), "mode": "healing", "type": "heal",
                  "desc": "Donates own vitality to save another. Costs self 20 HP."},
            '4': {"name": "Cellular Decay", "cost": 35, "dmg": (55, 85), "mode": "decay", "type": "damage",
                  "desc": "Reverses healing energy. Forces catastrophic, rapid cellular decay."},
            '5': {"name": "Life Drain", "cost": 40, "dmg": (45, 70), "mode": "decay", "type": "damage",
                  "desc": "Siphons life energy directly from target. Heals for half damage dealt."},
            '6': {"name": "Internal Rupture", "cost": 45, "dmg": (70, 100), "mode": "decay", "type": "damage",
                  "desc": "Precision technique. Causes fatal internal injuries with no external wound."},
            '7': {"name": "Monofilament Threads", "cost": 20, "dmg": (40, 65), "mode": "decay", "type": "damage",
                  "desc": "Near-invisible, razor-sharp threads of pure decay force."},
            '8': {"name": "Manifest Angel Wings", "cost": 35, "dmg": (0, 0), "type": "wing_manifest",
                  "desc": "Manifest Angel Wings. +50% healing for rest of battle."},
            '9': {"name": "Manifest Demon Wings", "cost": 35, "dmg": (0, 0), "type": "wing_manifest",
                  "desc": "Manifest Demon Wings. UNLOCKS Black Swamp, Wing Blade, Wing Split."},
            '10': {"name": "Manifest Dual Wings", "cost": 60, "dmg": (0, 0), "type": "wing_manifest",
                   "desc": "COMPLETE MANIFESTATION. Wields both Angel and Demon Wings."},
            '11': {"name": "Black Swamp", "cost": 60, "dmg": (80, 120), "type": "demon_ability",
                   "desc": "REQUIRES DEMON WINGS. Entropic swamp consumes target. Applies CRUSHED."},
            '12': {"name": "Wing Blade", "cost": 50, "dmg": (60, 90), "type": "demon_ability",
                   "desc": "REQUIRES DEMON WINGS. Bat wings as razor-sharp blades. 30% stun chance."},
            '13': {"name": "Wing Split", "cost": 60, "dmg": (70, 100), "type": "demon_ability",
                   "desc": "REQUIRES DEMON WINGS. Wings multiply mid-combat. 40% extra strike."},
            '14': {"name": "Dual Wings Judgment", "cost": 90, "dmg": (100, 150), "heal": (50, 80),
                   "type": "dual_ability",
                   "desc": "REQUIRES DUAL WINGS. Massive damage AND heals party!"},
            '15': {"name": "Reactive Reformation", "cost": 25, "dmg": (0, 0), "mode": "any", "type": "utility",
                   "desc": "Reinforces cells. Reduces next physical damage by 70%."},
            '16': {"name": "Entropic Ward", "cost": 30, "mode": "any", "type": "utility",
                   "desc": "Contact field of decay around Kartein. Enemies who attack Kartein take 15-25 counter-damage."},
            '17': {"name": "Power Seal", "cost": 50, "dmg": (0, 0), "mode": "any", "type": "utility",
                   "desc": "70% chance to seal enemy abilities."},
            '18': {"name": "Dimensional Isolation", "cost": 55, "dmg": (0, 0), "mode": "any", "type": "utility",
                   "desc": "Encases target in spatial barrier. Halves damage for 2 turns."},
        }
        self.healing_mode = True
        self.wing_state = "none"
        self.entropic_ward_active = False

    def get_available_abilities(self):
        available = {}
        for key, abil in self.abilities.items():
            if self.energy < abil["cost"]:
                continue
            if "mode" in abil:
                if abil["mode"] == "healing" and not self.healing_mode:
                    continue
                if abil["mode"] == "decay" and self.healing_mode:
                    continue
            if "type" in abil:
                if abil["type"] == "wing_manifest":
                    if "Angel" in abil["name"] and self.wing_state in ["angel", "dual"]:
                        continue
                    if "Demon" in abil["name"] and self.wing_state in ["demon", "dual"]:
                        continue
                    if "Dual" in abil["name"] and self.wing_state == "dual":
                        continue
                    available[key] = abil
                    continue
                elif abil["type"] == "demon_ability":
                    if self.wing_state in ["demon", "dual"]:
                        available[key] = abil
                    continue
                elif abil["type"] == "dual_ability":
                    if self.wing_state == "dual":
                        available[key] = abil
                    continue
            available[key] = abil
        return available

    def set_wings(self, wing_type):
        self.wing_state = wing_type
        if wing_type == "angel":
            return "ANGEL WINGS MANIFESTED! Healing +50%! [ACTIVE]"
        elif wing_type == "demon":
            return "DEMON WINGS MANIFESTED! Black Swamp, Wing Blade, Wing Split UNLOCKED! [ACTIVE]"
        elif wing_type == "dual":
            return "DUAL WINGS MANIFESTED! Perfect balance! Dual Wings Judgment UNLOCKED! [ACTIVE]"
        return ""


# ============================================================================
# PLUTON
# ============================================================================

class Pluton(Character):
    def __init__(self):
        super().__init__("Pluton", "The Steel Tower", 420, 260)
        self.abilities = {
            '1': {"name": "Gravity Press", "cost": 20, "dmg": (50, 75), "type": "damage",
                  "desc": "Crushing wave of amplified gravity. Pins target to ground."},
            '2': {"name": "Gravity Sphere", "cost": 30, "dmg": (60, 85), "type": "damage",
                  "desc": "Dense singular point of extreme gravitational force."},
            '3': {"name": "Gravity Shield", "cost": 25, "dmg": (0, 0), "type": "utility",
                  "desc": "Defensive field of warped space-time. -60% damage."},
            '4': {"name": "Crushing Field", "cost": 45, "dmg": (0, 0), "type": "utility",
                  "desc": "Dominates battlefield. Increases gravity over vast zone. Slows all enemies."},
            '5': {"name": "Event Horizon", "cost": 75, "dmg": (110, 160), "type": "damage",
                  "desc": "Zone of profound gravitational distortion. Point of no return."},
            '6': {"name": "Anchor Point", "cost": 20, "dmg": (0, 0), "type": "utility",
                  "desc": "Designates fixed gravitational pull. Disrupts mobility."},
            '7': {"name": "Kinetic Redirection", "cost": 25, "dmg": (0, 0), "type": "utility",
                  "desc": "Alters gravity vectors. Reflects 70% damage."},
            '8': {"name": "Gravitational Lensing", "cost": 20, "dmg": (0, 0), "type": "utility",
                  "desc": "Bends light and energy waves. Scrambles perception. Enemies have 50% miss chance for 1 hit."},
            '9': {"name": "Personal Gravity Well", "cost": 15, "dmg": (0, 0), "type": "utility",
                  "desc": "Ever-present subtle manipulation. Immovable stance. +20% damage."},
        }
        self.well_active = False
        self.field_active = False


# ============================================================================
# ENEMY CLASS
# ============================================================================

class Enemy(Character):
    def __init__(self, name, title, hp, energy, abilities, rank, affiliation=""):
        super().__init__(name, title, hp, energy)
        self.abilities = abilities
        self.rank = rank
        self.affiliation = affiliation
        self.ai_pattern = []


# ============================================================================
# ENEMY CREATION FUNCTIONS
# ============================================================================

def create_enemy_jinwoo():
    abilities = {
        'a': {"name": "Lightning Bolt", "dmg": (40, 60)},
        'b': {"name": "Shockwave", "dmg": (50, 75)},
        'c': {"name": "Thunderclap", "dmg": (60, 85)},
    }
    enemy = Enemy("Jinwoo", "The Lightning Inspector", 350, 220, abilities, 60, "Korean Association")
    enemy.ai_pattern = ['c', 'b', 'a']
    return enemy


def create_enemy_jiwoo():
    abilities = {
        'a': {"name": "Electric Spear", "dmg": (50, 75)},
        'b': {"name": "Max Speed", "dmg": (70, 100)},
        'c': {"name": "Zero Impact", "dmg": (75, 105)},
        'd': {"name": "Electric Max Speed", "dmg": (90, 130)},
    }
    enemy = Enemy("Jiwoo", "The Lightning Prodigy", 420, 270, abilities, 25, "Korean Association")
    enemy.ai_pattern = ['d', 'b', 'c', 'a']
    return enemy


def create_enemy_jisuk():
    abilities = {
        'a': {"name": "Force Control", "dmg": (45, 70)},
        'b': {"name": "Pressure Strike", "dmg": (60, 85)},
        'c': {"name": "Adaptive Counter", "dmg": (50, 75)},
    }
    enemy = Enemy("Jisuk", "The Force Prodigy", 380, 240, abilities, 35, "Korean Association")
    enemy.ai_pattern = ['b', 'c', 'a']
    return enemy


def create_enemy_subin():
    abilities = {
        'a': {"name": "Force Wave", "dmg": (40, 65)},
        'b': {"name": "Precision Strike", "dmg": (55, 80)},
        'c': {"name": "Barrier", "dmg": (0, 0)},
    }
    enemy = Enemy("Subin", "The Force Prodigy", 340, 220, abilities, 48, "Korean Association")
    enemy.ai_pattern = ['b', 'a', 'c']
    return enemy


def create_enemy_wooin():
    abilities = {
        'a': {"name": "Silent Step", "dmg": (45, 70)},
        'b': {"name": "Shadow Strike", "dmg": (60, 90)},
        'c': {"name": "Execution", "dmg": (75, 105)},
    }
    enemy = Enemy("Wooin", "The Silent Blade", 360, 230, abilities, 42, "Korean Association")
    enemy.ai_pattern = ['c', 'b', 'a']
    return enemy


def create_enemy_greg():
    abilities = {
        'a': {"name": "Force Blast", "dmg": (60, 90)},
        'b': {"name": "Pressure Wave", "dmg": (75, 105)},
        'c': {"name": "Chairman's Authority", "dmg": (0, 0)},
        'd': {"name": "Supreme Impact", "dmg": (100, 145)},
    }
    enemy = Enemy("Greg", "The Chairman", 600, 300, abilities, 9, "Korean Association")
    enemy.ai_pattern = ['d', 'b', 'a', 'c']
    return enemy


def create_enemy_roist():
    abilities = {
        'a': {"name": "Force Storm", "dmg": (65, 95)},
        'b': {"name": "Tempest Edge", "dmg": (80, 115)},
        'c': {"name": "Roaring Gale", "dmg": (55, 80)},
        'd': {"name": "Cyclone Prison", "dmg": (70, 100)},
    }
    enemy = Enemy("Roist", "The Storm Emperor", 620, 310, abilities, 8, "Independent")
    enemy.ai_pattern = ['d', 'b', 'a', 'c']
    return enemy


def create_enemy_arthur():
    abilities = {
        'a': {"name": "Light Blast", "dmg": (60, 90)},
        'b': {"name": "Radiant Lance", "dmg": (85, 120)},
        'c': {"name": "Flash Step", "dmg": (50, 75)},
        'd': {"name": "Divine Flash", "dmg": (95, 135)},
    }
    enemy = Enemy("Arthur", "The Light", 590, 290, abilities, 10, "Independent")
    enemy.ai_pattern = ['d', 'b', 'a', 'c']
    return enemy


def create_enemy_astra():
    abilities = {
        'a': {"name": "Shadow Pierce", "dmg": (55, 85)},
        'b': {"name": "Void Slash", "dmg": (70, 100)},
        'c': {"name": "Abyssal Bind", "dmg": (40, 60)},
        'd': {"name": "Dimensional Edge", "dmg": (90, 130)},
        'e': {"name": "Oblivion Call", "dmg": (120, 170)},
        'f': {"name": "Void Domain", "dmg": (80, 120)},
    }
    enemy = Enemy("Astra", "The Void Dancer", 680, 320, abilities, 7, "Astra Group")
    enemy.ai_pattern = ['e', 'd', 'f', 'b', 'a', 'c']
    return enemy


def create_enemy_vatore():
    abilities = {
        'a': {"name": "Flame Burst", "dmg": (65, 95)},
        'b': {"name": "Inferno Lance", "dmg": (85, 120)},
        'c': {"name": "Fire Prison", "dmg": (50, 75)},
        'd': {"name": "Hellfire", "dmg": (100, 145)},
        'e': {"name": "Volcanic Eruption", "dmg": (120, 170)},
    }
    enemy = Enemy("Vatore", "The Flame Emperor", 650, 310, abilities, 8, "Astra Group")
    enemy.ai_pattern = ['e', 'd', 'b', 'c', 'a']
    return enemy


def create_enemy_mugeni():
    abilities = {
        'a': {"name": "Mind Spike", "dmg": (50, 75)},
        'b': {"name": "Psychic Blast", "dmg": (70, 100)},
        'c': {"name": "Mental Domination", "dmg": (0, 0)},
        'd': {"name": "Psionic Storm", "dmg": (90, 130)},
        'e': {"name": "Reality Warp", "dmg": (110, 155)},
    }
    enemy = Enemy("Mugeni", "The Mind Master", 620, 300, abilities, 9, "Astra Group")
    enemy.ai_pattern = ['e', 'd', 'b', 'a', 'c']
    return enemy


def create_enemy_astra_elite():
    abilities = {
        'a': {"name": "Void Blade", "dmg": (60, 85)},
        'b': {"name": "Shadow Dance", "dmg": (55, 80)},
        'c': {"name": "Abyssal Strike", "dmg": (70, 95)},
    }
    enemy = Enemy("Astra Elite", "Void Operative", 350, 200, abilities, 55, "Astra Group")
    enemy.ai_pattern = ['c', 'a', 'b']
    return enemy


def create_enemy_dark_mage():
    abilities = {
        'a': {"name": "Shadow Bolt", "dmg": (50, 75)},
        'b': {"name": "Curse", "dmg": (40, 70)},
        'c': {"name": "Void Eruption", "dmg": (75, 100)},
    }
    enemy = Enemy("Dark Mage", "Void Caster", 320, 220, abilities, 58, "Astra Group")
    enemy.ai_pattern = ['c', 'a', 'b']
    return enemy


def create_enemy_yodore():
    abilities = {
        'a': {"name": "Force Compression", "dmg": (65, 95)},
        'b': {"name": "Compression Spear", "dmg": (85, 120)},
        'c': {"name": "Internal Collapse", "dmg": (100, 140)},
    }
    enemy = Enemy("Yodore", "The Compression Master", 540, 290, abilities, 15, "Frame")
    enemy.ai_pattern = ['c', 'b', 'a']
    return enemy


def create_enemy_mioru():
    abilities = {
        'a': {"name": "Wind Cutter", "dmg": (50, 75)},
        'b': {"name": "Storm Lance", "dmg": (70, 100)},
        'c': {"name": "Cyclone Burst", "dmg": (85, 120)},
    }
    enemy = Enemy("Mioru", "The Storm Blade", 500, 270, abilities, 20, "Frame")
    enemy.ai_pattern = ['c', 'b', 'a']
    return enemy


def create_enemy_sujin():
    abilities = {
        'a': {"name": "Force Blade", "dmg": (45, 70)},
        'b': {"name": "Crimson Slash", "dmg": (65, 95)},
        'c': {"name": "Blood Hunt", "dmg": (70, 100)},
    }
    enemy = Enemy("Sujin", "The Crimson Hunter", 430, 250, abilities, 28, "Frame")
    enemy.ai_pattern = ['c', 'b', 'a']
    return enemy


def create_enemy_andrei():
    abilities = {
        'a': {"name": "Force Explosion", "dmg": (50, 75)},
        'b': {"name": "Brute Charge", "dmg": (65, 90)},
        'c': {"name": "Crusher Fist", "dmg": (75, 105)},
    }
    enemy = Enemy("Andrei", "The Force Crusher", 450, 240, abilities, 45, "Frame")
    enemy.ai_pattern = ['c', 'b', 'a']
    return enemy


def create_enemy_kuen():
    abilities = {
        'a': {"name": "Twin Slash", "dmg": (55, 80)},
        'b': {"name": "Cross Cutter", "dmg": (70, 100)},
        'c': {"name": "Blade Dance", "dmg": (60, 90)},
    }
    enemy = Enemy("Kuen", "The Twin Blade", 410, 230, abilities, 52, "Frame")
    enemy.ai_pattern = ['b', 'c', 'a']
    return enemy


def create_enemy_gerald():
    abilities = {
        'a': {"name": "Shadow Step", "dmg": (45, 70)},
        'b': {"name": "Dark Strike", "dmg": (60, 90)},
        'c': {"name": "Umbral Bind", "dmg": (40, 65)},
        'd': {"name": "Abyssal Edge", "dmg": (75, 105)},
    }
    enemy = Enemy("Gerald", "The Shadow Walker", 420, 240, abilities, 48, "Frame")
    enemy.ai_pattern = ['d', 'b', 'a', 'c']
    return enemy


def create_enemy_valerie():
    abilities = {
        'a': {"name": "Ice Spear", "dmg": (50, 75)},
        'b': {"name": "Frost Nova", "dmg": (60, 85)},
        'c': {"name": "Glacial Prison", "dmg": (45, 70)},
        'd': {"name": "Absolute Zero", "dmg": (80, 115)},
    }
    enemy = Enemy("Valerie", "The Ice Witch", 440, 250, abilities, 46, "Frame")
    enemy.ai_pattern = ['d', 'b', 'a', 'c']
    return enemy


def create_enemy_klaus():
    abilities = {
        'a': {"name": "Thunder Bolt", "dmg": (55, 80)},
        'b': {"name": "Lightning Storm", "dmg": (70, 100)},
        'c': {"name": "Static Field", "dmg": (45, 70)},
        'd': {"name": "Judgment Bolt", "dmg": (85, 120)},
    }
    enemy = Enemy("Klaus", "The Thunder God", 460, 260, abilities, 44, "Frame")
    enemy.ai_pattern = ['d', 'b', 'a', 'c']
    return enemy


def create_enemy_frame_soldier():
    abilities = {'a': {"name": "Force Blast", "dmg": (25, 40)}}
    enemy = Enemy("Frame Soldier", "Elite Grunt", 150, 100, abilities, 100, "Frame")
    enemy.ai_pattern = ['a']
    return enemy


def create_enemy_frame_captain():
    abilities = {
        'a': {"name": "Force Blast", "dmg": (35, 55)},
        'b': {"name": "Tactical Strike", "dmg": (40, 60)},
        'c': {"name": "Command", "dmg": (0, 0)},
    }
    enemy = Enemy("Frame Captain", "Squad Commander", 220, 140, abilities, 75, "Frame")
    enemy.ai_pattern = ['c', 'b', 'a']
    return enemy


def create_enemy_frame_elite():
    abilities = {
        'a': {"name": "Force Blast", "dmg": (45, 65)},
        'b': {"name": "Tactical Strike", "dmg": (50, 70)},
        'c': {"name": "Assault", "dmg": (55, 75)},
    }
    enemy = Enemy("Frame Elite", "Special Operative", 280, 160, abilities, 65, "Frame")
    enemy.ai_pattern = ['c', 'b', 'a']
    return enemy


def create_enemy_frame_assassin():
    abilities = {
        'a': {"name": "Shadow Strike", "dmg": (50, 70)},
        'b': {"name": "Poison Blade", "dmg": (45, 75)},
        'c': {"name": "Execute", "dmg": (70, 95)},
    }
    enemy = Enemy("Frame Assassin", "Silent Killer", 250, 150, abilities, 70, "Frame")
    enemy.ai_pattern = ['c', 'a', 'b']
    return enemy


def create_enemy_dmitri():
    abilities = {
        'a': {"name": "Ice Spear", "dmg": (50, 75)},
        'b': {"name": "Frost Wave", "dmg": (60, 85)},
        'c': {"name": "Blizzard", "dmg": (70, 100)},
        'd': {"name": "Siberian Storm", "dmg": (85, 120)},
    }
    enemy = Enemy("Dmitri", "The Frost", 440, 250, abilities, 32, "World Association")
    enemy.ai_pattern = ['d', 'c', 'b', 'a']
    return enemy


def create_enemy_carlos():
    abilities = {
        'a': {"name": "Earth Spike", "dmg": (55, 80)},
        'b': {"name": "Tremor", "dmg": (60, 85)},
        'c': {"name": "Landslide", "dmg": (70, 100)},
        'd': {"name": "Earthquake", "dmg": (85, 115)},
    }
    enemy = Enemy("Carlos", "The Earth", 460, 240, abilities, 38, "World Association")
    enemy.ai_pattern = ['d', 'c', 'b', 'a']
    return enemy


def create_enemy_assassin():
    abilities = {
        'a': {"name": "Quick Strike", "dmg": (35, 55)},
        'b': {"name": "Shadow Step", "dmg": (40, 60)},
        'c': {"name": "Assassinate", "dmg": (50, 75)},
    }
    enemy = Enemy("Assassin", "Shadow Killer", 280, 180, abilities, 80, "Unknown")
    enemy.ai_pattern = ['c', 'b', 'a']
    return enemy


def create_enemy_cultist():
    abilities = {
        'a': {"name": "Dark Pulse", "dmg": (40, 65)},
        'b': {"name": "Corruption", "dmg": (35, 60)},
        'c': {"name": "Ritual Sacrifice", "dmg": (60, 85)},
    }
    enemy = Enemy("Cultist", "Dark Zealot", 300, 190, abilities, 72, "Cult")
    enemy.ai_pattern = ['c', 'a', 'b']
    return enemy


def create_enemy_shadow_leader():
    abilities = {
        'a': {"name": "Shadow Slash", "dmg": (70, 95)},
        'b': {"name": "Darkness Embrace", "dmg": (60, 85)},
        'c': {"name": "Umbral Prison", "dmg": (55, 80)},
        'd': {"name": "Void Call", "dmg": (90, 125)},
    }
    enemy = Enemy("Shadow Leader", "Darkness Incarnate", 520, 280, abilities, 22, "Cult")
    enemy.ai_pattern = ['d', 'a', 'c', 'b']
    return enemy


def create_enemy_phantom():
    abilities = {
        'a': {"name": "Phantom Strike", "dmg": (65, 90)},
        'b': {"name": "Illusion", "dmg": (0, 0)},
        'c': {"name": "Spectral Edge", "dmg": (75, 100)},
        'd': {"name": "Reality Break", "dmg": (95, 130)},
    }
    enemy = Enemy("Phantom", "The Illusionist", 480, 270, abilities, 26, "Independent")
    enemy.ai_pattern = ['d', 'c', 'a', 'b']
    return enemy


# ============================================================================
# GAME CLASS
# ============================================================================

class Game:
    def __init__(self):
        self.kayden = Kayden()
        self.kartein = Kartein()
        self.pluton = Pluton()
        self.party = [self.kayden, self.kartein, self.pluton]
        self.enemies = []
        self.turn_count = 0
        self.victories = 0
        self.total_kills = 0
        self.wave = 0
        self.mode = GameMode.STORY

    def add_log(self, message):
        print(f"[T{self.turn_count}] ", end='')
        slow_print(message, 0.02)
        time.sleep(0.2)

    def display_health_bars(self):
        print("\n" + "=" * 110)
        print("PARTY STATUS")
        print("-" * 110)
        time.sleep(0.3)

        for member in self.party:
            if member.is_alive():
                bar_len = 40
                filled = int(bar_len * member.hp / member.max_hp)
                bar = "#" * filled + "." * (bar_len - filled)
                status = []
                if member.name == "Kayden Break":
                    status.append(f"FORM: {member.form}")
                    if member.form == "Limit Breaker":
                        status.append("LIMIT BREAKER")
                        status.append(f"({member.limit_timer}t)")
                    if member.domain:
                        status.append("DOMAIN")
                        status.append(f"({member.domain_timer}t)")
                    if member.cloak:
                        status.append("CLOAK")
                        status.append(f"({member.cloak_timer}t)")
                    if member.cat_form:
                        status.append("[CAT FORM]")
                elif member.name == "Kartein":
                    mode = "HEAL" if member.healing_mode else "DECAY"
                    status.append(mode)
                    wing_display = {
                        "none": "NO WINGS",
                        "angel": "ANGEL WINGS",
                        "demon": "DEMON WINGS",
                        "dual": "DUAL WINGS"
                    }
                    status.append(wing_display[member.wing_state])
                    if member.entropic_ward_active:
                        status.append("[ENTROPIC WARD]")
                elif member.name == "Pluton":
                    if member.well_active:
                        status.append("[GRAVITY WELL]")
                    if member.field_active:
                        status.append("[CRUSHING FIELD]")
                status_str = " | ".join(status) if status else ""
                print(f"{member.name:15} [{bar}] {member.hp:3}/{member.max_hp:3} HP  {member.energy:3}E  {status_str}")
                time.sleep(0.2)

        print("\n" + "=" * 110)
        print("ENEMY STATUS")
        print("-" * 110)
        time.sleep(0.3)

        for enemy in self.enemies:
            if enemy.is_alive():
                bar_len = 40
                filled = int(bar_len * enemy.hp / enemy.max_hp)
                bar = "#" * filled + "." * (bar_len - filled)
                debuff = []
                if "stun" in enemy.debuffs:
                    debuff.append("[STUN]")
                if "sealed" in enemy.debuffs:
                    debuff.append("[SEALED]")
                if "isolated" in enemy.debuffs:
                    debuff.append("[ISOLATED]")
                if "crushed" in enemy.debuffs:
                    debuff.append("[CRUSHED]")
                debuff_str = " ".join(debuff) if debuff else ""
                affil = f" [{enemy.affiliation}]" if enemy.affiliation else ""
                print(f"{enemy.name:15} [{bar}] {enemy.hp:3}/{enemy.max_hp:3} HP  (Rank {enemy.rank}){affil}  {debuff_str}")
                time.sleep(0.2)

        print("=" * 110)
        time.sleep(0.5)

    # FIX 2: Now uses a while loop — no more recursion on bad input
    def select_target(self, allies=False):
        if allies:
            targets = [c for c in self.party if c.is_alive()]
        else:
            targets = [e for e in self.enemies if e.is_alive()]

        if not targets:
            return None

        while True:
            if allies:
                print("\n--- SELECT ALLY TARGET ---")
            else:
                print("\n--- SELECT ENEMY TARGET ---")

            for i, t in enumerate(targets):
                print(f"  {i + 1}. {t.name}  ({t.hp}/{t.max_hp} HP)")
                time.sleep(0.05)

            choice = input("> ").strip()
            print()

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(targets):
                    return targets[idx]
            except (ValueError, TypeError):
                pass

            print("Invalid target. Try again.")
            time.sleep(0.3)

    def display_ability_description(self, abil):
        print("\n" + "-" * 80)
        slow_print(f"  {abil['name']}", 0.04)
        print("-" * 80)
        slow_print(abil['desc'], 0.02)
        if "cost" in abil:
            print(f"\n  Energy Cost: {abil['cost']}")
        if "dmg" in abil and abil["dmg"] != (0, 0):
            print(f"  Damage: {abil['dmg'][0]}-{abil['dmg'][1]}")
        if "heal" in abil:
            print(f"  Healing: {abil['heal'][0]}-{abil['heal'][1]}")
        print("-" * 80)
        input("Press Enter to continue...")
        print()

    # FIX 2: Now uses a while loop — no more recursion on bad input
    def use_ability(self, character):
        while True:
            print(f"\n" + "=" * 110)
            slow_print(f"  {character.name}  [{character.title}]", 0.03)
            print("=" * 110)
            print(f"  HP: {character.hp}/{character.max_hp}    Energy: {character.energy}/{character.max_energy}")
            print("-" * 110)
            time.sleep(0.3)

            if character.name == "Kartein":
                mode_name = "HEALING MODE" if character.healing_mode else "DECAY MODE"
                wing_display = {
                    "none": "No Wings",
                    "angel": "Angel Wings (+50% Healing) [ACTIVE]",
                    "demon": "Demon Wings [ACTIVE]",
                    "dual": "Dual Wings [ACTIVE]"
                }
                print(f"  Mode: {mode_name}  |  Wings: {wing_display[character.wing_state]}")
                if character.entropic_ward_active:
                    print("  [ENTROPIC WARD ACTIVE]")
                time.sleep(0.2)

            elif character.name == "Kayden Break":
                print(f"  Form: {character.form}")
                # FIX 3: Always show cat form status so player knows about Cat Punch
                cat_status = "ON  <-- Cat Punch available!" if character.cat_form else "OFF  (press 0 to enable Cat Punch)"
                print(f"  Cat Form: {cat_status}")
                if character.domain_placed:
                    if character.form == "Limit Breaker":
                        print(f"  [LIMIT BREAKER] {character.limit_timer} turns remaining")
                    if character.domain:
                        print(f"  [DOMINANT ZONE] {character.domain_timer} turns remaining")
                    if character.cloak:
                        print(f"  [LIGHTNING CLOAK] {character.cloak_timer} turns remaining")
                time.sleep(0.2)

            elif character.name == "Pluton":
                if character.well_active:
                    print("  [GRAVITY WELL ACTIVE] +20% damage")
                if character.field_active:
                    print("  [CRUSHING FIELD ACTIVE]")
                time.sleep(0.2)

            available = {}
            if character.name == "Kartein":
                available = character.get_available_abilities()
            else:
                for key, abil in character.abilities.items():
                    if character.energy < abil["cost"]:
                        continue
                    if character.name == "Kayden Break":
                        if abil["name"] == "Lightning Cloak" and character.cloak:
                            continue
                        if abil["name"] == "Dominant Zone" and character.domain:
                            continue
                        if abil["name"] == "Limit Breaker" and character.form == "Limit Breaker":
                            continue
                        # FIX 3: Cat Punch only visible when cat form is on
                        if abil["name"] == "Cat Punch" and not character.cat_form:
                            continue
                    if character.name == "Pluton":
                        if abil["name"] == "Personal Gravity Well" and character.well_active:
                            continue
                        if abil["name"] == "Crushing Field" and character.field_active:
                            continue
                    available[key] = abil

            print("\n  AVAILABLE ABILITIES:")
            print("-" * 110)
            time.sleep(0.2)

            for key in sorted(available.keys(), key=lambda x: int(x) if x.isdigit() else x):
                abil = available[key]
                domain_tag = " [DOMAIN]" if "type" in abil and abil["type"] == "domain" else ""
                if "dmg" in abil and abil["dmg"] != (0, 0) and "heal" in abil:
                    d, h = abil["dmg"], abil["heal"]
                    print(f"  {key:>2}. {abil['name']:35} | {abil['cost']}E | {d[0]}-{d[1]} DMG / {h[0]}-{h[1]} HEAL{domain_tag}")
                elif "dmg" in abil and abil["dmg"] != (0, 0):
                    d = abil["dmg"]
                    print(f"  {key:>2}. {abil['name']:35} | {abil['cost']}E | {d[0]}-{d[1]} DMG{domain_tag}")
                elif "heal" in abil:
                    h = abil["heal"]
                    print(f"  {key:>2}. {abil['name']:35} | {abil['cost']}E | {h[0]}-{h[1]} HEAL")
                else:
                    print(f"  {key:>2}. {abil['name']:35} | {abil['cost']}E | BUFF/UTILITY{domain_tag}")
                time.sleep(0.07)

            print("\n  COMMANDS:")
            print("  00   Describe an ability")
            # FIX 3: Toggle label is context-aware so the player always knows what 0 does
            if character.name == "Kayden Break":
                cat_toggle = "Turn OFF" if character.cat_form else "Turn ON (enables Cat Punch)"
                print(f"   0   Toggle Cat Form  [{cat_toggle}]")
            elif character.name == "Kartein":
                cur = "HEALING" if character.healing_mode else "DECAY"
                nxt = "DECAY" if character.healing_mode else "HEALING"
                print(f"   0   Switch Mode  [{cur} -> {nxt}]")
            print("   -   Skip turn  (+15 Energy)")
            print("  back  Back to character select")
            print("-" * 110)

            choice = input("> ").strip().lower()
            print()

            if choice == 'back':
                return False

            if choice == '-':
                self.add_log(f"{character.name} skips turn. +15 Energy.")
                character.energy = min(character.max_energy, character.energy + 15)
                time.sleep(ACTION_DELAY)
                return True

            if choice == '0':
                if character.name == "Kayden Break":
                    character.cat_form = not character.cat_form
                    state = "ON  -- Cat Punch is now available!" if character.cat_form else "OFF"
                    self.add_log(f"Kayden toggles Cat Form: {state}")
                elif character.name == "Kartein":
                    character.healing_mode = not character.healing_mode
                    self.add_log(f"Kartein switches to {'HEALING MODE' if character.healing_mode else 'DECAY MODE'}.")
                time.sleep(ACTION_DELAY)
                return True

            if choice == '00':
                print("\n  Enter ability number to describe:")
                for key in sorted(available.keys(), key=lambda x: int(x) if x.isdigit() else x):
                    print(f"  {key:>2}. {available[key]['name']}")
                desc_choice = input("> ").strip()
                if desc_choice in available:
                    self.display_ability_description(available[desc_choice])
                # Loop back — no recursion
                continue

            if choice not in available:
                print("Invalid choice. Try again.")
                time.sleep(0.4)
                continue

            # ---- Execute chosen ability ----
            ability = available[choice]
            character.energy = max(0, character.energy - ability["cost"])

            # DOMAIN
            if "type" in ability and ability["type"] == "domain":
                self.add_log(character.activate_domain(ability["domain"]))

            # HEALING
            elif "type" in ability and ability["type"] == "heal":
                target = self.select_target(allies=True)
                if target:
                    heal = random.randint(ability["heal"][0], ability["heal"][1])
                    if character.wing_state in ["angel", "dual"]:
                        heal = int(heal * 1.5)
                    if ability["name"] == "Life-Force Transfer":
                        character.hp = max(1, character.hp - 20)
                    target.heal(heal)
                    self.add_log(f"Kartein heals {target.name} for {heal} HP!")

            # DAMAGE
            elif "type" in ability and ability["type"] == "damage":
                target = self.select_target()
                if target:
                    dmg = random.randint(ability["dmg"][0], ability["dmg"][1])
                    if character.name == "Kayden Break":
                        dmg_mult, _ = character.get_damage_multiplier()
                        dmg = int(dmg * dmg_mult)
                    if character.name == "Kartein" and not character.healing_mode:
                        if character.wing_state in ["demon", "dual"]:
                            dmg = int(dmg * 1.3)
                    if character.name == "Pluton" and character.well_active:
                        dmg = int(dmg * 1.2)
                    target.take_damage(dmg)
                    self.add_log(f"{character.name} uses {ability['name']} on {target.name} for {dmg} damage!")
                    if ability["name"] == "Divine Judgment":
                        target.debuffs.append("stun")
                        self.add_log(f"{target.name} is STUNNED!")
                    elif ability["name"] == "Brain Shock":
                        target.debuffs.append("stun")
                        self.add_log(f"{target.name} is STUNNED!")
                    elif ability["name"] == "Plasma Chains":
                        target.debuffs.append("chained")
                        self.add_log(f"{target.name} is CHAINED!")
                    if ability["name"] == "Life Drain":
                        h = dmg // 2
                        character.heal(h)
                        self.add_log(f"Kartein siphons {h} HP from {target.name}!")

            # WING MANIFEST
            elif "type" in ability and ability["type"] == "wing_manifest":
                wing_map = {"Angel": "angel", "Demon": "demon", "Dual": "dual"}
                new_wing = next((v for k, v in wing_map.items() if k in ability["name"]), None)
                if new_wing and character.wing_state not in ["none", new_wing]:
                    old = character.wing_state.upper()
                    print(f"\n  WARNING: You have {old} WINGS active.")
                    print(f"  Switching will lose current wing abilities. Confirm? (y/n)")
                    confirm = input("> ").strip().lower()
                    if confirm != 'y':
                        self.add_log("Wing manifestation cancelled.")
                        time.sleep(ACTION_DELAY)
                        return True
                if new_wing:
                    self.add_log(character.set_wings(new_wing))

            # DEMON ABILITIES
            elif "type" in ability and ability["type"] == "demon_ability":
                target = self.select_target()
                if target and character.wing_state in ["demon", "dual"]:
                    dmg = int(random.randint(ability["dmg"][0], ability["dmg"][1]) * 1.3)
                    target.take_damage(dmg)
                    self.add_log(f"{character.name} uses {ability['name']} on {target.name} for {dmg} damage!")
                    if "Black Swamp" in ability["name"]:
                        target.debuffs.append("crushed")
                        self.add_log(f"{target.name} is CRUSHED!")
                    elif "Wing Blade" in ability["name"] and random.random() < 0.3:
                        target.debuffs.append("stun")
                        self.add_log(f"{target.name} is STUNNED!")
                    elif "Wing Split" in ability["name"] and random.random() < 0.4:
                        extra = dmg // 2
                        target.take_damage(extra)
                        self.add_log(f"  Extra strike! +{extra} damage!")

            # DUAL WINGS
            elif "type" in ability and ability["type"] == "dual_ability":
                target = self.select_target()
                if target and character.wing_state == "dual":
                    dmg = random.randint(ability["dmg"][0], ability["dmg"][1])
                    target.take_damage(dmg)
                    self.add_log(f"DUAL WINGS JUDGMENT! {target.name} takes {dmg} damage!")
                    for ally in self.party:
                        if ally.is_alive():
                            h = random.randint(ability["heal"][0], ability["heal"][1])
                            ally.heal(h)
                            self.add_log(f"  {ally.name} healed for {h} HP!")

            # UTILITY
            elif "type" in ability and ability["type"] == "utility":
                if ability["name"] == "Shield":
                    character.defending = True
                    self.add_log(f"{character.name} raises a force shield!")
                elif ability["name"] == "Spatial Isolation Barrier":
                    for e in self.enemies:
                        if e.is_alive():
                            e.debuffs.append("isolated")
                    self.add_log("SPATIAL ISOLATION BARRIER! All enemies isolated!")
                elif ability["name"] == "Reactive Reformation":
                    character.buffs.append("reactive_armor")
                    self.add_log("REACTIVE REFORMATION! Next physical damage reduced by 70%!")
                elif ability["name"] == "Entropic Ward":
                    character.entropic_ward_active = True
                    self.add_log("ENTROPIC WARD! Attackers targeting Kartein take counter-damage!")
                elif ability["name"] == "Power Seal":
                    target = self.select_target()
                    if target:
                        if random.random() < 0.7:
                            target.debuffs.append("sealed")
                            self.add_log(f"POWER SEAL! {target.name}'s abilities sealed!")
                        else:
                            self.add_log(f"Power Seal failed on {target.name}!")
                elif ability["name"] == "Dimensional Isolation":
                    target = self.select_target()
                    if target:
                        target.debuffs.append("isolated")
                        self.add_log(f"DIMENSIONAL ISOLATION! {target.name} is isolated!")
                elif ability["name"] == "Gravity Shield":
                    character.defending = True
                    self.add_log("GRAVITY SHIELD! Warped space-time bends incoming attacks!")
                elif ability["name"] == "Personal Gravity Well":
                    character.well_active = True
                    self.add_log("PERSONAL GRAVITY WELL! Immovable stance! +20% damage!")
                elif ability["name"] == "Crushing Field":
                    character.field_active = True
                    for e in self.enemies:
                        if e.is_alive():
                            e.debuffs.append("crushed")
                    self.add_log("CRUSHING FIELD! Gravity intensifies across the battlefield!")
                elif ability["name"] == "Kinetic Redirection":
                    character.buffs.append("reflect")
                    self.add_log("KINETIC REDIRECTION! Next attack will be reflected!")
                elif ability["name"] == "Gravitational Lensing":
                    character.buffs.append("lensing")
                    self.add_log("GRAVITATIONAL LENSING! 50% chance next attack misses!")
                elif ability["name"] == "Anchor Point":
                    target = self.select_target()
                    if target:
                        target.debuffs.append("anchored")
                        self.add_log(f"ANCHOR POINT! {target.name} is immobilized!")

            time.sleep(ACTION_DELAY)
            return True

    def enemy_turn(self, enemy):
        if not enemy.is_alive():
            return
        if not any(c.is_alive() for c in self.party):
            return

        if "stun" in enemy.debuffs:
            self.add_log(f"{enemy.name} is stunned and cannot act!")
            enemy.debuffs.remove("stun")
            time.sleep(0.5)
            return

        if "sealed" in enemy.debuffs:
            self.add_log(f"{enemy.name}'s abilities are sealed! Basic attack only.")
            targets = [c for c in self.party if c.is_alive()]
            if targets:
                t = random.choice(targets)
                dmg = random.randint(15, 25)
                t.take_damage(dmg)
                # FIX 5: Entropic Ward intentionally triggers only when Kartein is the target
                if self.kartein.entropic_ward_active and t.name == "Kartein":
                    counter = random.randint(15, 25)
                    enemy.take_damage(counter)
                    self.add_log(f"ENTROPIC WARD counter! {enemy.name} takes {counter} damage!")
                self.add_log(f"{enemy.name} attacks {t.name} for {dmg} damage!")
            time.sleep(0.5)
            return

        if not enemy.ai_pattern:
            return

        key = enemy.ai_pattern[(self.turn_count - 1) % len(enemy.ai_pattern)]
        abil = enemy.abilities.get(key, list(enemy.abilities.values())[0])

        if abil["dmg"] == (0, 0):
            self.add_log(f"{enemy.name} uses {abil['name']}! [Preparing...]")
            time.sleep(0.8)
            return

        targets = [c for c in self.party if c.is_alive()]
        if not targets:
            return

        t = random.choice(targets)
        dmg = random.randint(abil["dmg"][0], abil["dmg"][1])

        if "isolated" in enemy.debuffs:
            dmg = int(dmg * 0.5)
        if "crushed" in enemy.debuffs:
            dmg = int(dmg * 0.7)
        if t.defending:
            dmg = int(dmg * 0.4) if t.name == "Pluton" else int(dmg * 0.6)
            t.defending = False

        if "reflect" in t.buffs and t.name == "Pluton":
            reflect = int(dmg * 0.7)
            enemy.take_damage(reflect)
            self.add_log(f"Pluton REFLECTS {reflect} damage back at {enemy.name}!")
            t.buffs.remove("reflect")

        # FIX 4: Lensing buff consumed exactly once, after hit/miss is fully resolved
        elif "lensing" in t.buffs:
            missed = random.random() < 0.5
            if missed:
                self.add_log(f"GRAVITATIONAL LENSING! {enemy.name}'s attack misses {t.name}!")
            else:
                self.add_log(f"Lensing flickered — {enemy.name}'s attack breaks through!")
                if "reactive_armor" in t.buffs:
                    dmg = int(dmg * 0.3)
                    self.add_log(f"Reactive Reformation! Damage reduced to {dmg}!")
                    t.buffs.remove("reactive_armor")
                t.take_damage(dmg)
                # FIX 5: Entropic Ward — triggers only when Kartein is targeted (by design)
                if self.kartein.entropic_ward_active and t.name == "Kartein":
                    counter = random.randint(15, 25)
                    enemy.take_damage(counter)
                    self.add_log(f"ENTROPIC WARD counter! {enemy.name} takes {counter} damage!")
                self.add_log(f"{enemy.name} uses {abil['name']} on {t.name} for {dmg} damage!")
            # FIX 4: Single removal point, outside hit/miss branch
            t.buffs.remove("lensing")

        else:
            if "reactive_armor" in t.buffs:
                dmg = int(dmg * 0.3)
                self.add_log(f"Reactive Reformation! Damage reduced to {dmg}!")
                t.buffs.remove("reactive_armor")
            t.take_damage(dmg)
            # FIX 5: Entropic Ward — triggers only when Kartein is targeted (by design)
            if self.kartein.entropic_ward_active and t.name == "Kartein":
                counter = random.randint(15, 25)
                enemy.take_damage(counter)
                self.add_log(f"ENTROPIC WARD counter! {enemy.name} takes {counter} damage!")
            self.add_log(f"{enemy.name} uses {abil['name']} on {t.name} for {dmg} damage!")

        time.sleep(0.8)

    def cleanup(self):
        """
        End-of-turn maintenance.
        FIX 1: Domain/cloak/limit timers tick down by exactly 1 and expire at 0.
                Removed random.random() early-expiry — timers are now deterministic.
        FIX 6: Energy regen moved here (end of turn) so players cannot spend energy
                before they have earned it.
        """
        for c in self.party + self.enemies:
            c.defending = False

            if c.name == "Kayden Break":
                # FIX 1: Deterministic timer countdown — no random early expiry
                if c.form == "Limit Breaker":
                    c.limit_timer -= 1
                    if c.limit_timer <= 0:
                        c.form = "Normal"
                        c.limit_timer = 0
                        self.add_log("Kayden's LIMIT BREAKER expires. Back to Normal.")
                if c.domain:
                    c.domain_timer -= 1
                    if c.domain_timer <= 0:
                        c.domain = False
                        c.domain_timer = 0
                        self.add_log("DOMINANT ZONE dissipates.")
                if c.cloak:
                    c.cloak_timer -= 1
                    if c.cloak_timer <= 0:
                        c.cloak = False
                        c.cloak_timer = 0
                        self.add_log("LIGHTNING CLOAK deactivates.")
                if not c.form == "Limit Breaker" and not c.domain and not c.cloak:
                    c.domain_placed = False

            if c.name == "Kartein" and c.entropic_ward_active:
                if random.random() < 0.25:
                    c.entropic_ward_active = False
                    self.add_log("Entropic Ward fades.")

            # Random debuff tick-off (unchanged from original)
            to_remove = []
            for debuff in c.debuffs:
                if debuff in ["stun", "sealed", "isolated", "crushed", "anchored", "chained"]:
                    if random.random() < 0.3:
                        to_remove.append(debuff)
            for debuff in to_remove:
                if debuff in c.debuffs:
                    c.debuffs.remove(debuff)
                    self.add_log(f"{c.name}'s {debuff} wore off.")

        # FIX 6: Energy regen at end of turn, not the start
        for char in self.party:
            if char.is_alive():
                char.energy = min(char.max_energy, char.energy + 12)

        time.sleep(0.3)

    def battle(self, enemies):
        self.enemies = enemies
        self.turn_count = 0
        print("\n" + "=" * 110)
        slow_print("--- BATTLE START ---", 0.04)
        print("=" * 110)
        print(f"  Party:   Kayden | Kartein | Pluton")
        print(f"  Enemies: {', '.join([e.name for e in self.enemies])}")
        if self.enemies[0].affiliation:
            print(f"  Affiliation: {self.enemies[0].affiliation}")
        print("=" * 110)
        time.sleep(BATTLE_START_DELAY)

        while True:
            self.turn_count += 1
            print(f"\n{'=' * 50} TURN {self.turn_count} {'=' * 50}")
            time.sleep(TURN_DELAY)

            # FIX 6: Energy regen removed from here — now in cleanup()
            for char in self.party:
                if char.is_alive():
                    action = False
                    while not action:
                        self.display_health_bars()
                        action = self.use_ability(char)
                    if not any(e.is_alive() for e in self.enemies):
                        break

            if not any(e.is_alive() for e in self.enemies):
                break
            if not any(c.is_alive() for c in self.party):
                break

            print("\n--- ENEMY PHASE ---")
            time.sleep(0.5)
            for enemy in self.enemies:
                if enemy.is_alive():
                    self.enemy_turn(enemy)
                    time.sleep(0.3)

            self.cleanup()

        self.display_health_bars()
        if any(e.is_alive() for e in self.enemies):
            print("\n" + "=" * 110)
            slow_print("--- DEFEAT ---", 0.05)
            print("=" * 110)
            time.sleep(VICTORY_DELAY)
            return False
        else:
            print("\n" + "=" * 110)
            slow_print("--- VICTORY! ---", 0.05)
            print("=" * 110)
            self.victories += 1
            self.total_kills += len([e for e in self.enemies if not e.is_alive()])
            time.sleep(VICTORY_DELAY)
            return True

    def rest(self):
        print("\n" + "=" * 110)
        slow_print("--- RESTING ---", 0.04)
        print("=" * 110)
        time.sleep(0.5)
        for char in self.party:
            char.hp = char.max_hp
            char.energy = char.max_energy
            char.buffs = []
            char.debuffs = []
            if char.name == "Kayden Break":
                char.cloak = False
                char.domain = False
                char.form = "Normal"
                char.cat_form = False
                char.domain_placed = False
                char.cloak_timer = 0
                char.domain_timer = 0
                char.limit_timer = 0
            elif char.name == "Kartein":
                char.wing_state = "none"
                char.healing_mode = True
                char.entropic_ward_active = False
            elif char.name == "Pluton":
                char.well_active = False
                char.field_active = False
            print(f"  {char.name} fully recovered.")
            time.sleep(0.2)
        print("\n  Party ready!")
        time.sleep(1.5)

    # ===== GAME MODES =====

    def story_mode(self):
        print("\n" + "=" * 110)
        slow_print("--- STORY MODE ---", 0.04)
        print("=" * 110)
        time.sleep(1)

        chapters = [
            ("Prologue: Frame Soldiers", [create_enemy_frame_soldier(), create_enemy_frame_soldier()]),
            ("Chapter 1: The Inspector", [create_enemy_jinwoo()]),
            ("Chapter 2: Frame Assault", [create_enemy_andrei(), create_enemy_frame_captain()]),
            ("Chapter 3: The Crimson Hunter", [create_enemy_sujin()]),
            ("Chapter 4: Shadow Killer", [create_enemy_assassin()]),
            ("Chapter 5: Frame Executives", [create_enemy_kuen(), create_enemy_gerald()]),
            ("Chapter 6: The Storm Blade", [create_enemy_mioru()]),
            ("Chapter 7: Dark Cult", [create_enemy_cultist(), create_enemy_phantom()]),
            ("Chapter 8: The Ice Witch", [create_enemy_valerie()]),
            ("Chapter 9: The Thunder God", [create_enemy_klaus()]),
            ("Chapter 10: World Association", [create_enemy_dmitri(), create_enemy_carlos()]),
            ("Chapter 11: The Compression Master", [create_enemy_yodore()]),
            ("Chapter 12: Shadow Leader", [create_enemy_shadow_leader()]),
            ("Chapter 13: Astra's Elite", [create_enemy_astra_elite(), create_enemy_dark_mage()]),
            ("Chapter 14: The Mind Master", [create_enemy_mugeni()]),
            ("Chapter 15: The Flame Emperor", [create_enemy_vatore()]),
            ("Final Chapter: The Void Dancer", [create_enemy_astra()]),
        ]

        for i, (chapter, enemies) in enumerate(chapters):
            print("\n" + "!" * 110)
            slow_print(f"  {chapter}  [{i+1}/{len(chapters)}]", 0.03)
            print("!" * 110)
            input("Press Enter to continue...")

            if not self.battle(enemies):
                print("\n--- GAME OVER ---")
                print(f"Defeated at: {chapter}")
                time.sleep(2)
                return False

            if chapter != "Final Chapter: The Void Dancer":
                self.rest()

        print("\n" + "=" * 110)
        slow_print("--- STORY MODE COMPLETE! ---", 0.04)
        print("=" * 110)
        print(f"Victories: {self.victories}  |  Enemies defeated: {self.total_kills}")
        print("=" * 110)
        time.sleep(3)
        return True

    def gauntlet_mode(self):
        print("\n" + "=" * 110)
        slow_print("--- RANKER GAUNTLET ---", 0.04)
        print("=" * 110)
        time.sleep(1)

        stages = [
            ("Rank 100: Frame Squad",
             [create_enemy_frame_soldier(), create_enemy_frame_soldier(), create_enemy_frame_soldier()]),
            ("Rank 90: Assassin", [create_enemy_assassin()]),
            ("Rank 80: Frame Captain", [create_enemy_frame_captain(), create_enemy_frame_soldier()]),
            ("Rank 75: Cultist", [create_enemy_cultist()]),
            ("Rank 70: Frame Elite", [create_enemy_frame_elite(), create_enemy_frame_assassin()]),
            ("Rank 65: Jinwoo", [create_enemy_jinwoo()]),
            ("Rank 60: Andrei", [create_enemy_andrei()]),
            ("Rank 55: Kuen", [create_enemy_kuen()]),
            ("Rank 52: Gerald", [create_enemy_gerald()]),
            ("Rank 50: Sujin", [create_enemy_sujin()]),
            ("Rank 48: Valerie", [create_enemy_valerie()]),
            ("Rank 46: Klaus", [create_enemy_klaus()]),
            ("Rank 45: Dmitri", [create_enemy_dmitri()]),
            ("Rank 42: Carlos", [create_enemy_carlos()]),
            ("Rank 40: Mioru", [create_enemy_mioru()]),
            ("Rank 35: Phantom", [create_enemy_phantom()]),
            ("Rank 32: Astra Elite", [create_enemy_astra_elite()]),
            ("Rank 30: Dark Mage", [create_enemy_dark_mage()]),
            ("Rank 28: Shadow Leader", [create_enemy_shadow_leader()]),
            ("Rank 25: Jiwoo", [create_enemy_jiwoo()]),
            ("Rank 22: Yodore", [create_enemy_yodore()]),
            ("Rank 20: Mugeni", [create_enemy_mugeni()]),
            ("Rank 18: Vatore", [create_enemy_vatore()]),
            ("Rank 15: Roist", [create_enemy_roist()]),
            ("Rank 12: Arthur", [create_enemy_arthur()]),
            ("Rank 10: Greg", [create_enemy_greg()]),
            ("Rank 7: Astra", [create_enemy_astra()]),
        ]

        for i, (stage, enemies) in enumerate(stages):
            self.wave = i + 1
            print(f"\n  STAGE {self.wave}: {stage}")
            input("Press Enter to challenge...")

            if not self.battle(enemies):
                print(f"\n--- GAUNTLET FAILED at Stage {self.wave}: {stage} ---")
                time.sleep(2)
                return False

            if stage != "Rank 7: Astra":
                self.rest()

        print("\n--- GAUNTLET COMPLETE! ---")
        print(f"Victories: {self.victories}  |  Enemies: {self.total_kills}")
        time.sleep(3)
        return True

    def boss_rush_mode(self):
        print("\n--- BOSS RUSH ---")
        time.sleep(1)

        bosses = [
            ("Frame Executive: Andrei", [create_enemy_andrei()]),
            ("Frame Executive: Kuen", [create_enemy_kuen()]),
            ("Frame Executive: Gerald", [create_enemy_gerald()]),
            ("Frame Executive: Valerie", [create_enemy_valerie()]),
            ("Frame Executive: Klaus", [create_enemy_klaus()]),
            ("Frame Executive: Mioru", [create_enemy_mioru()]),
            ("Cult Leader: Phantom", [create_enemy_phantom()]),
            ("Shadow Leader", [create_enemy_shadow_leader()]),
            ("World Association: Dmitri", [create_enemy_dmitri()]),
            ("World Association: Carlos", [create_enemy_carlos()]),
            ("Sujin - Crimson Hunter", [create_enemy_sujin()]),
            ("Jiwoo - Lightning Prodigy", [create_enemy_jiwoo()]),
            ("Yodore - Compression Master", [create_enemy_yodore()]),
            ("Mugeni - Mind Master", [create_enemy_mugeni()]),
            ("Vatore - Flame Emperor", [create_enemy_vatore()]),
            ("Astra - Void Dancer", [create_enemy_astra()]),
        ]

        for i, (boss, enemies) in enumerate(bosses):
            self.wave = i + 1
            print(f"\n  BOSS {self.wave}: {boss}")
            input("Press Enter to challenge...")

            if not self.battle(enemies):
                print(f"\n--- BOSS RUSH FAILED at Boss {self.wave}: {boss} ---")
                time.sleep(2)
                return False

            print("  Preparing next boss...")
            time.sleep(1.5)

        print("\n--- BOSS RUSH COMPLETE! ---")
        print(f"Victories: {self.victories}")
        time.sleep(3)
        return True

    def survival_mode(self):
        print("\n--- ENDLESS SURVIVAL ---")
        time.sleep(1)

        wave = 0
        score = 0

        while True:
            wave += 1
            self.wave = wave
            print(f"\n{'=' * 40}  WAVE {wave}  {'=' * 40}")
            time.sleep(0.5)

            wave_enemies = []
            if wave <= 5:
                for _ in range(min(3, wave)):
                    wave_enemies.append(create_enemy_frame_soldier())
            elif wave <= 10:
                wave_enemies += [create_enemy_frame_captain(), create_enemy_frame_soldier(), create_enemy_frame_soldier()]
            elif wave <= 15:
                wave_enemies += [create_enemy_andrei(), create_enemy_frame_elite()]
            elif wave <= 20:
                wave_enemies += [create_enemy_kuen(), create_enemy_gerald()]
            elif wave <= 25:
                wave_enemies += [create_enemy_mioru(), create_enemy_frame_elite(), create_enemy_frame_elite()]
            elif wave <= 30:
                wave_enemies += [create_enemy_sujin(), create_enemy_dmitri()]
            elif wave <= 35:
                wave_enemies += [create_enemy_yodore(), create_enemy_carlos()]
            elif wave <= 40:
                wave_enemies += [create_enemy_phantom(), create_enemy_shadow_leader()]
            elif wave <= 45:
                wave_enemies += [create_enemy_astra_elite(), create_enemy_dark_mage(), create_enemy_dark_mage()]
            elif wave <= 50:
                wave_enemies += [create_enemy_mugeni(), create_enemy_vatore()]
            else:
                bosses = [create_enemy_astra(), create_enemy_vatore(), create_enemy_mugeni()]
                wave_enemies += [random.choice(bosses), create_enemy_astra_elite(), create_enemy_astra_elite()]

            input("Press Enter to face the wave...")

            if not self.battle(wave_enemies):
                print(f"\n--- SURVIVAL ENDED AT WAVE {wave} ---")
                print(f"Waves cleared: {wave - 1}  |  Score: {score}  |  Kills: {self.total_kills}")
                time.sleep(3)
                break

            score += wave * 100
            print(f"\n  Wave {wave} cleared!  Score: {score}")
            time.sleep(1)

            if random.random() < 0.2:
                for char in self.party:
                    char.hp = min(char.max_hp, char.hp + int(char.max_hp * 0.2))
                    char.energy = min(char.max_energy, char.energy + int(char.max_energy * 0.2))
                print("  Found supplies! Party recovers 20% HP/Energy.")
                time.sleep(1)

        return score

    def frame_raid_mode(self):
        print("\n--- FRAME HEADQUARTERS RAID ---")
        time.sleep(1)

        missions = [
            ("Perimeter Breach",
             [create_enemy_frame_soldier(), create_enemy_frame_soldier(), create_enemy_frame_soldier()]),
            ("Security Checkpoint",
             [create_enemy_frame_captain(), create_enemy_frame_soldier(), create_enemy_frame_soldier()]),
            ("Elite Patrol", [create_enemy_frame_elite(), create_enemy_frame_elite()]),
            ("Research Wing",
             [create_enemy_frame_captain(), create_enemy_frame_elite(), create_enemy_frame_soldier()]),
            ("Assassin Encounter", [create_enemy_frame_assassin(), create_enemy_frame_assassin()]),
            ("Executive Floor: Kuen", [create_enemy_kuen(), create_enemy_frame_elite()]),
            ("Executive Floor: Gerald", [create_enemy_gerald(), create_enemy_frame_elite()]),
            ("Executive Floor: Valerie", [create_enemy_valerie(), create_enemy_frame_elite()]),
            ("Executive Floor: Klaus", [create_enemy_klaus(), create_enemy_frame_elite()]),
            ("Executive Floor: Mioru", [create_enemy_mioru(), create_enemy_frame_elite()]),
            ("Executive Floor: Andrei", [create_enemy_andrei(), create_enemy_frame_captain()]),
            ("Director's Office: Yodore",
             [create_enemy_yodore(), create_enemy_frame_elite(), create_enemy_frame_elite()]),
        ]

        for i, (mission, enemies) in enumerate(missions):
            self.wave = i + 1
            print(f"\n  MISSION {self.wave}: {mission}")
            input("Press Enter to proceed...")

            if not self.battle(enemies):
                print(f"\n--- RAID FAILED at Mission {self.wave}: {mission} ---")
                time.sleep(2)
                return False

            if mission != "Director's Office: Yodore":
                for char in self.party:
                    char.hp = min(char.max_hp, char.hp + int(char.max_hp * 0.3))
                    char.energy = min(char.max_energy, char.energy + int(char.max_energy * 0.3))
                print("  Party recovers 30% HP/Energy.")
                time.sleep(1)

        print("\n--- FRAME RAID SUCCESSFUL! ---")
        time.sleep(3)
        return True

    def top10_tournament_mode(self):
        print("\n--- TOP 10 TOURNAMENT ---")
        print("  Quarterfinals -> Semifinals -> Final -> Championship")
        time.sleep(1)

        # FIX 7: Was calling create_enemy_jiwoo() for "vs Jinwoo" — now correctly calls create_enemy_jinwoo()
        quarterfinals = [
            ("Quarterfinal 1: vs Jinwoo", [create_enemy_jinwoo()]),
            ("Quarterfinal 2: vs Sujin", [create_enemy_sujin()]),
            ("Quarterfinal 3: vs Mioru", [create_enemy_mioru()]),
            ("Quarterfinal 4: vs Yodore", [create_enemy_yodore()]),
        ]
        semifinals = [
            ("Semifinal 1: vs Arthur", [create_enemy_arthur()]),
            ("Semifinal 2: vs Roist", [create_enemy_roist()]),
        ]
        finals = [
            ("Final: vs Greg", [create_enemy_greg()]),
            ("Championship: vs Astra", [create_enemy_astra()]),
        ]

        for round_name, matches in [("QUARTERFINALS", quarterfinals), ("SEMIFINALS", semifinals), ("FINALS", finals)]:
            print(f"\n--- {round_name} ---")
            for match_name, enemies in matches:
                print(f"\n  {match_name}")
                self.rest()
                input("Press Enter to fight...")
                if not self.battle(enemies):
                    print("\n--- TOURNAMENT ELIMINATED ---")
                    time.sleep(2)
                    return False

        print("\n--- TOURNAMENT CHAMPIONS! ---")
        time.sleep(3)
        return True

    def sparring_mode(self):
        print("\n--- TRAINING ROOM ---")
        print("  Select an opponent:")
        time.sleep(0.5)

        sparring_options = [
            ("1", "Frame Soldier", create_enemy_frame_soldier),
            ("2", "Jinwoo - Lightning Inspector", create_enemy_jinwoo),
            ("3", "Andrei - Force Crusher", create_enemy_andrei),
            ("4", "Kuen - Twin Blade", create_enemy_kuen),
            ("5", "Gerald - Shadow Walker", create_enemy_gerald),
            ("6", "Valerie - Ice Witch", create_enemy_valerie),
            ("7", "Klaus - Thunder God", create_enemy_klaus),
            ("8", "Sujin - Crimson Hunter", create_enemy_sujin),
            ("9", "Mioru - Storm Blade", create_enemy_mioru),
            ("10", "Dmitri - The Frost", create_enemy_dmitri),
            ("11", "Carlos - The Earth", create_enemy_carlos),
            ("12", "Phantom - The Illusionist", create_enemy_phantom),
            ("13", "Shadow Leader", create_enemy_shadow_leader),
            ("14", "Jiwoo - Lightning Prodigy", create_enemy_jiwoo),
            ("15", "Yodore - Compression Master", create_enemy_yodore),
            ("16", "Mugeni - Mind Master", create_enemy_mugeni),
            ("17", "Vatore - Flame Emperor", create_enemy_vatore),
            ("18", "Arthur - The Light", create_enemy_arthur),
            ("19", "Roist - Storm Emperor", create_enemy_roist),
            ("20", "Greg - The Chairman", create_enemy_greg),
            ("21", "Astra - Void Dancer", create_enemy_astra),
        ]

        for key, name, _ in sparring_options:
            print(f"  {key:>2}. {name}")
            time.sleep(0.04)
        print("   b. Back")
        print()

        choice = input("> ").strip()
        if choice.lower() == 'b':
            return

        for key, name, func in sparring_options:
            if choice == key:
                print(f"\n  Sparring with {name}...")
                time.sleep(0.5)
                self.rest()
                self.battle([func()])
                break


# ============================================================================
# MAIN MENU
# ============================================================================

def main():
    print("\n" + "=" * 110)
    slow_print("  ELECEED: AWAKENED DUEL  --  COMPLETE EDITION", 0.03)
    print("  Kayden Break  |  Kartein  |  Pluton")
    print("=" * 110)
    time.sleep(1)

    game = Game()
    cumulative_victories = 0
    cumulative_kills = 0
    best_survival_score = 0

    while True:
        print("\n" + "-" * 50)
        print("  MAIN MENU")
        print("-" * 50)
        print("  1. Story Mode")
        print("  2. Ranker Gauntlet")
        print("  3. Boss Rush")
        print("  4. Endless Survival")
        print("  5. Frame Raid")
        print("  6. Top 10 Tournament")
        print("  7. Training Room")
        print("  8. Stats")
        print("  9. Exit")
        print("-" * 50)

        choice = input("> ").strip()
        print()

        if choice == "1":
            game = Game()
            game.story_mode()
            cumulative_victories += game.victories
            cumulative_kills += game.total_kills
        elif choice == "2":
            game = Game()
            game.gauntlet_mode()
            cumulative_victories += game.victories
            cumulative_kills += game.total_kills
        elif choice == "3":
            game = Game()
            game.boss_rush_mode()
            cumulative_victories += game.victories
            cumulative_kills += game.total_kills
        elif choice == "4":
            game = Game()
            score = game.survival_mode()
            cumulative_victories += game.victories
            cumulative_kills += game.total_kills
            if score > best_survival_score:
                best_survival_score = score
        elif choice == "5":
            game = Game()
            game.frame_raid_mode()
            cumulative_victories += game.victories
            cumulative_kills += game.total_kills
        elif choice == "6":
            game = Game()
            game.top10_tournament_mode()
            cumulative_victories += game.victories
            cumulative_kills += game.total_kills
        elif choice == "7":
            game.sparring_mode()
        elif choice == "8":
            print("-" * 50)
            print("  STATS & RECORDS")
            print("-" * 50)
            print(f"  Total victories : {cumulative_victories}")
            print(f"  Enemies defeated: {cumulative_kills}")
            print(f"  Best survival   : {best_survival_score}")
            print(f"\n  Last party HP:")
            print(f"    Kayden  : {game.kayden.hp}/{game.kayden.max_hp}")
            print(f"    Kartein : {game.kartein.hp}/{game.kartein.max_hp}")
            print(f"    Pluton  : {game.pluton.hp}/{game.pluton.max_hp}")
            print("-" * 50)
            input("Press Enter to continue...")
        elif choice == "9":
            slow_print("\nThanks for playing Eleceed: Awakened Duel!", 0.03)
            slow_print("See you next time, awakened one.\n", 0.03)
            time.sleep(1)
            break
        else:
            print("  Invalid choice.")
            time.sleep(0.4)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
        sys.exit(0)

