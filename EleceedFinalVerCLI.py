#!/usr/bin/env python3
"""
ELECEED: AWAKENED DUEL
COMPLETE EDITION - NUMBERS INSTEAD OF LETTERS FOR ALL COMMANDS
Kayden • Kartein • Pluton • Full Eleceed Villain Roster
"""

import random
import time
import sys
from enum import Enum
#Final version
# ============================================================================
# TEXT SPEED CONTROL
# ============================================================================

TEXT_SPEED = 0.6  # Seconds between log messages
BATTLE_START_DELAY = 2.0  # Seconds before battle starts
TURN_DELAY = 1.0  # Seconds between turns
ACTION_DELAY = 0.8  # Seconds after actions
VICTORY_DELAY = 2.5  # Seconds after victory/defeat


def slow_print(text, delay=0.03):
    """Print text character by character for dramatic effect"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


# ============================================================================
# GAME MODES ENUM
# ============================================================================

class GameMode(Enum):
    STORY = "1. 📖 Story Mode - Follow the Eleceed storyline"
    GAUNTLET = "2. 🏆 Ranker Gauntlet - Fight through all ranks"
    BOSS_RUSH = "3. 👑 Boss Rush - Only major villains"
    SURVIVAL = "4. ♾️ Endless Survival - How many waves?"
    FRAME_RAID = "5. 🔴 Frame Raid - Infiltrate enemy headquarters"
    TOP_10 = "6. 🌍 Top 10 Tournament - Face the world's strongest"
    SPARRING = "7. 🥋 Training Room - Practice against any character"


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
# KAYDEN BREAK - ALL ABILITIES REMAPPED TO NUMBERS 1-20
# ============================================================================

class Kayden(Character):
    def __init__(self):
        super().__init__("Kayden Break", "The Uncrowned King", 380, 280)
        self.abilities = {
            '1': {"name": "⚡ Lightning Strike", "cost": 15, "dmg": (45, 75), "type": "damage",
                  "desc": "Fundamental lightning projection. Fires pinpoint bolts or wide-area barrages."},
            '2': {"name": "🗡️ Compressed Spear", "cost": 35, "dmg": (70, 100), "type": "damage",
                  "desc": "City-block energy compressed into a single lance. Near-infinite piercing capability."},
            '3': {"name": "💢 Zero Impact", "cost": 30, "dmg": (60, 90), "type": "damage",
                  "desc": "Internal annihilation. All destructive force delivered internally, leaving small external wounds."},
            '4': {"name": "⚡💢 Zero Impact Spear", "cost": 55, "dmg": (90, 140), "type": "damage",
                  "desc": "Fusion of Compressed Spear and Zero Impact. Absolute piercing force + complete internal annihilation."},
            '5': {"name": "❌ Grand Cross", "cost": 60, "dmg": (110, 150), "type": "damage",
                  "desc": "Two massive lightning waves overlapping to form a colossal cross. Killed Astra."},
            '6': {"name": "👁️ Divine Judgment", "cost": 80, "dmg": (140, 190), "type": "damage",
                  "desc": "Monumental pillar of white-hot divine lightning from the heavens. Stuns target."},
            '7': {"name": "⚡ Lightning Cloak", "cost": 40, "dmg": (0, 0), "type": "domain", "domain": "cloak",
                  "desc": "CRACKLING ARMOR - Kayden engulfs himself in tangible, crackling armor of highly-compressed lightning. +30% damage (5 turns)."},
            '8': {"name": "👑 Dominant Zone", "cost": 70, "dmg": (0, 0), "type": "domain", "domain": "zone",
                  "desc": "PERSONAL DOMAIN - Kayden creates his own personal isolated domain that amplifies his power. +40% damage (4 turns)."},
            '9': {"name": "⚡⚡⚡ Limit Breaker", "cost": 100, "dmg": (0, 0), "type": "domain", "domain": "limit",
                  "desc": "WHITE IGNITION - Emergency override. Hair and lightning turn arctic white. +80% damage to ALL moves (3 turns)."},
            '10': {"name": "💨 Max Speed", "cost": 50, "dmg": (80, 120), "type": "damage",
                   "desc": "Concentrate all power within the body to pierce any skill. Perfected from Jiwoo."},
            '11': {"name": "⛓️ Plasma Chains", "cost": 25, "dmg": (40, 60), "type": "damage",
                   "desc": "Razor-sharp chains of condensed lightning for binding and cutting."},
            '12': {"name": "🧠 Brain Shock", "cost": 15, "dmg": (1, 1), "type": "damage",
                   "desc": "Precise, non-lethal application. Controlled shock to the brain. Stuns target."},
            '13': {"name": "🐱 Cat Punch", "cost": 20, "dmg": (50, 80), "type": "damage",
                   "desc": "Special move developed in cat form. Researched how cats attack each other."},
            '14': {"name": "🛡️ Shield", "cost": 20, "dmg": (0, 0), "type": "utility",
                   "desc": "Force field of highly concentrated electrical energy. Protects self and allies."},
            '15': {"name": "🔮 Spatial Isolation Barrier", "cost": 45, "dmg": (0, 0), "type": "utility",
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
            buffs.append("WHITE IGNITION")
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
            return "⚡⚡⚡ LIGHTNING CLOAK DEPLOYED! Crackling armor surrounds Kayden! [ACTIVE] +30% damage (5 turns)"
        elif domain_type == "zone":
            self.domain = True
            self.domain_timer = 4
            self.domain_placed = True
            return "👑👑👑 DOMINANT ZONE ESTABLISHED! His world, his law! [ACTIVE] +40% damage (4 turns)"
        elif domain_type == "limit":
            self.form = "Limit Breaker"
            self.limit_timer = 3
            self.domain_placed = True
            self.hp = min(self.max_hp, self.hp + 50)
            return "⚡⚡⚡⚡⚡ WHITE IGNITION! Kayden breaks past all ceilings! [LIMIT BREAKER] +80% damage (3 turns)"
        return ""


# ============================================================================
# KARTEIN - ALL ABILITIES REMAPPED TO NUMBERS 1-20
# ============================================================================

class Kartein(Character):
    def __init__(self):
        super().__init__("Kartein", "The Fearsome Healer", 300, 240)
        self.abilities = {
            '1': {"name": "🟢 Cellular Regeneration", "cost": 25, "heal": (40, 60), "mode": "healing", "type": "heal",
                  "desc": "Advanced cellular regeneration. Instantaneously regenerates severe wounds."},
            '2': {"name": "💚 Healing Beam", "cost": 30, "heal": (50, 75), "mode": "healing", "type": "heal",
                  "desc": "Long-distance healing beam. Projects focused beam of green-gold healing energy."},
            '3': {"name": "❤️ Life-Force Transfer", "cost": 40, "heal": (70, 100), "mode": "healing", "type": "heal",
                  "desc": "Donates own vitality to save another. Costs self 20 HP."},
            '4': {"name": "💀 Cellular Decay", "cost": 35, "dmg": (55, 85), "mode": "decay", "type": "damage",
                  "desc": "Reverses healing energy. Forces catastrophic, rapid cellular decay."},
            '5': {"name": "🩸 Life Drain", "cost": 40, "dmg": (45, 70), "mode": "decay", "type": "damage",
                  "desc": "Siphons life energy directly from target. Heals for half damage dealt."},
            '6': {"name": "💢 Internal Rupture", "cost": 45, "dmg": (70, 100), "mode": "decay", "type": "damage",
                  "desc": "Precision technique. Causes fatal internal injuries with no external wound."},
            '7': {"name": "🕸️ Monofilament Threads", "cost": 20, "dmg": (40, 65), "mode": "decay", "type": "damage",
                  "desc": "Near-invisible, razor-sharp threads of pure decay force."},
            '8': {"name": "🕊️ Manifest Angel Wings", "cost": 35, "dmg": (0, 0), "type": "wing_manifest",
                  "desc": "Manifest Angel Wings. +50% healing for rest of battle."},
            '9': {"name": "👿 Manifest Demon Wings", "cost": 35, "dmg": (0, 0), "type": "wing_manifest",
                  "desc": "Manifest Demon Wings. UNLOCKS Black Swamp, Wing Blade, Wing Split."},
            '10': {"name": "🦋✨ Manifest Dual Wings", "cost": 60, "dmg": (0, 0), "type": "wing_manifest",
                   "desc": "COMPLETE MANIFESTATION. Wields both Angel and Demon Wings."},
            '11': {"name": "🌑 Black Swamp", "cost": 60, "dmg": (80, 120), "type": "demon_ability",
                   "desc": "REQUIRES DEMON WINGS. Entropic swamp consumes target. Applies CRUSHED."},
            '12': {"name": "🦇 Wing Blade", "cost": 50, "dmg": (60, 90), "type": "demon_ability",
                   "desc": "REQUIRES DEMON WINGS. Bat wings as razor-sharp blades. 30% stun chance."},
            '13': {"name": "🦇🦇 Wing Split", "cost": 60, "dmg": (70, 100), "type": "demon_ability",
                   "desc": "REQUIRES DEMON WINGS. Wings multiply mid-combat. 40% extra strike."},
            '14': {"name": "🦋✨ Dual Wings Judgment", "cost": 90, "dmg": (100, 150), "heal": (50, 80),
                   "type": "dual_ability",
                   "desc": "REQUIRES DUAL WINGS. Massive damage AND heals party!"},
            '15': {"name": "🛡️ Reactive Reformation", "cost": 25, "dmg": (0, 0), "mode": "any", "type": "utility",
                   "desc": "Reinforces cells. Reduces next physical damage by 70%."},
            '16': {"name": "☠️ Entropic Ward", "cost": 30, "mode": "any", "type": "utility",
                   "desc": "Contact field of decay. Attackers take 20-40 damage (reactive counter only)."},
            '17': {"name": "🔒 Power Seal", "cost": 50, "dmg": (0, 0), "mode": "any", "type": "utility",
                   "desc": "70% chance to seal enemy abilities."},
            '18': {"name": "🔮 Dimensional Isolation", "cost": 55, "dmg": (0, 0), "mode": "any", "type": "utility",
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
            return "🕊️🕊️🕊️ ANGEL WINGS MANIFESTED! Healing +50%! [ACTIVE]"
        elif wing_type == "demon":
            return "👿👿👿 DEMON WINGS MANIFESTED! Black Swamp, Wing Blade, Wing Split UNLOCKED! [ACTIVE]"
        elif wing_type == "dual":
            return "🦋✨🦋✨ DUAL WINGS MANIFESTED! Perfect balance! Dual Wings Judgment UNLOCKED! [ACTIVE]"
        return ""


# ============================================================================
# PLUTON - ALL ABILITIES REMAPPED TO NUMBERS 1-20
# ============================================================================

class Pluton(Character):
    def __init__(self):
        super().__init__("Pluton", "The Steel Tower", 420, 260)
        self.abilities = {
            '1': {"name": "🌍 Gravity Press", "cost": 20, "dmg": (50, 75), "type": "damage",
                  "desc": "Crushing wave of amplified gravity. Pins target to ground."},
            '2': {"name": "⚫ Gravity Sphere", "cost": 30, "dmg": (60, 85), "type": "damage",
                  "desc": "Dense singular point of extreme gravitational force."},
            '3': {"name": "🛡️ Gravity Shield", "cost": 25, "dmg": (0, 0), "type": "utility",
                  "desc": "Defensive field of warped space-time. -60% damage."},
            '4': {"name": "🌋 Crushing Field", "cost": 45, "dmg": (0, 0), "type": "utility",
                  "desc": "Dominates battlefield. Increases gravity over vast zone. Slows all enemies."},
            '5': {"name": "🌀 Event Horizon", "cost": 75, "dmg": (110, 160), "type": "damage",
                  "desc": "Zone of profound gravitational distortion. Point of no return."},
            '6': {"name": "⚓ Anchor Point", "cost": 20, "dmg": (0, 0), "type": "utility",
                  "desc": "Designates fixed gravitational pull. Disrupts mobility."},
            '7': {"name": "🔄 Kinetic Redirection", "cost": 25, "dmg": (0, 0), "type": "utility",
                  "desc": "Alters gravity vectors. Reflects 70% damage."},
            '8': {"name": "✨ Gravitational Lensing", "cost": 20, "dmg": (0, 0), "type": "utility",
                  "desc": "Bends light and energy waves. Scrambles perception. Enemies have 50% miss chance for 1 hit."},
            '9': {"name": "⚖️ Personal Gravity Well", "cost": 15, "dmg": (0, 0), "type": "utility",
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
# COMPLETE ENEMY CREATION FUNCTIONS
# ============================================================================

# ===== KOREAN ASSOCIATION / ALLIES =====

def create_enemy_jinwoo():
    """Jinwoo - Lightning Inspector"""
    abilities = {
        'a': {"name": "Lightning Bolt", "dmg": (40, 60)},
        'b': {"name": "Shockwave", "dmg": (50, 75)},
        'c': {"name": "Thunderclap", "dmg": (60, 85)},
    }
    enemy = Enemy("Jinwoo", "The Lightning Inspector", 350, 220, abilities, 60, "Korean Association")
    enemy.ai_pattern = ['c', 'b', 'a']
    return enemy


def create_enemy_jiwoo():
    """Jiwoo - Lightning Prodigy"""
    abilities = {
        'a': {"name": "Electric Spear", "dmg": (50, 75)},
        'b': {"name": "Max Speed", "dmg": (70, 100)},
        'c': {"name": "Zero Impact", "dmg": (75, 105)},
        'd': {"name": "Electric Max Speed", "dmg": (90, 130)},
    }
    enemy = Enemy("Jiwoo", "The Lightning Prodigy", 420, 270, abilities, 25, "World Association")
    enemy.ai_pattern = ['d', 'b', 'c', 'a']
    return enemy


def create_enemy_jisuk():
    """Jisuk - Force Prodigy"""
    abilities = {
        'a': {"name": "Force Control", "dmg": (45, 70)},
        'b': {"name": "Pressure Strike", "dmg": (60, 85)},
        'c': {"name": "Adaptive Counter", "dmg": (50, 75)},
    }
    enemy = Enemy("Jisuk", "The Force Prodigy", 380, 240, abilities, 35, "Korean Association")
    enemy.ai_pattern = ['b', 'c', 'a']
    return enemy


def create_enemy_subin():
    """Subin - Force Prodigy"""
    abilities = {
        'a': {"name": "Force Wave", "dmg": (40, 65)},
        'b': {"name": "Precision Strike", "dmg": (55, 80)},
        'c': {"name": "Barrier", "dmg": (0, 0)},
    }
    enemy = Enemy("Subin", "The Force Prodigy", 340, 220, abilities, 48, "Korean Association")
    enemy.ai_pattern = ['b', 'a', 'c']
    return enemy


def create_enemy_wooin():
    """Wooin - Silent Blade"""
    abilities = {
        'a': {"name": "Silent Step", "dmg": (45, 70)},
        'b': {"name": "Shadow Strike", "dmg": (60, 90)},
        'c': {"name": "Execution", "dmg": (75, 105)},
    }
    enemy = Enemy("Wooin", "The Silent Blade", 360, 230, abilities, 42, "Korean Association")
    enemy.ai_pattern = ['c', 'b', 'a']
    return enemy


# ===== TOP 10 RANKERS =====

def create_enemy_greg():
    """Greg - Top 10, Chairman"""
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
    """Roist - Top 10, Storm Emperor"""
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
    """Arthur - Top 10, The Light"""
    abilities = {
        'a': {"name": "Light Blast", "dmg": (60, 90)},
        'b': {"name": "Radiant Lance", "dmg": (85, 120)},
        'c': {"name": "Flash Step", "dmg": (50, 75)},
        'd': {"name": "Divine Flash", "dmg": (95, 135)},
    }
    enemy = Enemy("Arthur", "The Light", 590, 290, abilities, 10, "Independent")
    enemy.ai_pattern = ['d', 'b', 'a', 'c']
    return enemy


# ===== ASTRA GROUP (TOP RANKERS - VILLAINS) =====

def create_enemy_astra():
    """Astra - Top 7, Main Antagonist, Void Dancer"""
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
    """Vatore - Top 8, Flame Emperor"""
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
    """Mugeni - Top 9, Mind Master"""
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
    """Astra Group Elite - Top Operatives"""
    abilities = {
        'a': {"name": "Void Blade", "dmg": (60, 85)},
        'b': {"name": "Shadow Dance", "dmg": (55, 80)},
        'c': {"name": "Abyssal Strike", "dmg": (70, 95)},
    }
    enemy = Enemy("Astra Elite", "Void Operative", 350, 200, abilities, 55, "Astra Group")
    enemy.ai_pattern = ['c', 'a', 'b']
    return enemy


def create_enemy_dark_mage():
    """Dark Mage - Astra Group Caster"""
    abilities = {
        'a': {"name": "Shadow Bolt", "dmg": (50, 75)},
        'b': {"name": "Curse", "dmg": (40, 70)},
        'c': {"name": "Void Eruption", "dmg": (75, 100)},
    }
    enemy = Enemy("Dark Mage", "Void Caster", 320, 220, abilities, 58, "Astra Group")
    enemy.ai_pattern = ['c', 'a', 'b']
    return enemy


# ===== FRAME EXECUTIVES =====

def create_enemy_yodore():
    """Yodore - Top 15, Compression Master"""
    abilities = {
        'a': {"name": "Force Compression", "dmg": (65, 95)},
        'b': {"name": "Compression Spear", "dmg": (85, 120)},
        'c': {"name": "Internal Collapse", "dmg": (100, 140)},
    }
    enemy = Enemy("Yodore", "The Compression Master", 540, 290, abilities, 15, "Frame")
    enemy.ai_pattern = ['c', 'b', 'a']
    return enemy


def create_enemy_mioru():
    """Mioru - Top 20, Storm Blade"""
    abilities = {
        'a': {"name": "Wind Cutter", "dmg": (50, 75)},
        'b': {"name": "Storm Lance", "dmg": (70, 100)},
        'c': {"name": "Cyclone Burst", "dmg": (85, 120)},
    }
    enemy = Enemy("Mioru", "The Storm Blade", 500, 270, abilities, 20, "Frame")
    enemy.ai_pattern = ['c', 'b', 'a']
    return enemy


def create_enemy_sujin():
    """Sujin - Top 30, Crimson Hunter"""
    abilities = {
        'a': {"name": "Force Blade", "dmg": (45, 70)},
        'b': {"name": "Crimson Slash", "dmg": (65, 95)},
        'c': {"name": "Blood Hunt", "dmg": (70, 100)},
    }
    enemy = Enemy("Sujin", "The Crimson Hunter", 430, 250, abilities, 28, "Frame")
    enemy.ai_pattern = ['c', 'b', 'a']
    return enemy


def create_enemy_andrei():
    """Andrei - Top 50, Force Crusher"""
    abilities = {
        'a': {"name": "Force Explosion", "dmg": (50, 75)},
        'b': {"name": "Brute Charge", "dmg": (65, 90)},
        'c': {"name": "Crusher Fist", "dmg": (75, 105)},
    }
    enemy = Enemy("Andrei", "The Force Crusher", 450, 240, abilities, 45, "Frame")
    enemy.ai_pattern = ['c', 'b', 'a']
    return enemy


def create_enemy_kuen():
    """Kuen - Frame Executive, Twin Blade"""
    abilities = {
        'a': {"name": "Twin Slash", "dmg": (55, 80)},
        'b': {"name": "Cross Cutter", "dmg": (70, 100)},
        'c': {"name": "Blade Dance", "dmg": (60, 90)},
    }
    enemy = Enemy("Kuen", "The Twin Blade", 410, 230, abilities, 52, "Frame")
    enemy.ai_pattern = ['b', 'c', 'a']
    return enemy


def create_enemy_gerald():
    """Gerald - Frame Executive, Shadow Walker"""
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
    """Valerie - Frame Executive, Ice Witch"""
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
    """Klaus - Frame Executive, Thunder God"""
    abilities = {
        'a': {"name": "Thunder Bolt", "dmg": (55, 80)},
        'b': {"name": "Lightning Storm", "dmg": (70, 100)},
        'c': {"name": "Static Field", "dmg": (45, 70)},
        'd': {"name": "Judgment Bolt", "dmg": (85, 120)},
    }
    enemy = Enemy("Klaus", "The Thunder God", 460, 260, abilities, 44, "Frame")
    enemy.ai_pattern = ['d', 'b', 'a', 'c']
    return enemy


# ===== FRAME ARMY =====

def create_enemy_frame_soldier():
    """Frame Soldier - Basic Unit"""
    abilities = {
        'a': {"name": "Force Blast", "dmg": (25, 40)},
    }
    enemy = Enemy("Frame Soldier", "Elite Grunt", 150, 100, abilities, 100, "Frame")
    enemy.ai_pattern = ['a']
    return enemy


def create_enemy_frame_captain():
    """Frame Captain - Squad Leader"""
    abilities = {
        'a': {"name": "Force Blast", "dmg": (35, 55)},
        'b': {"name": "Tactical Strike", "dmg": (40, 60)},
        'c': {"name": "Command", "dmg": (0, 0)},
    }
    enemy = Enemy("Frame Captain", "Squad Commander", 220, 140, abilities, 75, "Frame")
    enemy.ai_pattern = ['c', 'b', 'a']
    return enemy


def create_enemy_frame_elite():
    """Frame Elite - Special Forces"""
    abilities = {
        'a': {"name": "Force Blast", "dmg": (45, 65)},
        'b': {"name": "Tactical Strike", "dmg": (50, 70)},
        'c': {"name": "Assault", "dmg": (55, 75)},
    }
    enemy = Enemy("Frame Elite", "Special Operative", 280, 160, abilities, 65, "Frame")
    enemy.ai_pattern = ['c', 'b', 'a']
    return enemy


def create_enemy_frame_assassin():
    """Frame Assassin - Stealth Unit"""
    abilities = {
        'a': {"name": "Shadow Strike", "dmg": (50, 70)},
        'b': {"name": "Poison Blade", "dmg": (45, 75)},
        'c': {"name": "Execute", "dmg": (70, 95)},
    }
    enemy = Enemy("Frame Assassin", "Silent Killer", 250, 150, abilities, 70, "Frame")
    enemy.ai_pattern = ['c', 'a', 'b']
    return enemy


# ===== WORLD AWAKENED ASSOCIATION =====

def create_enemy_dmitri():
    """Dmitri - Russian Ranker"""
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
    """Carlos - South American Ranker"""
    abilities = {
        'a': {"name": "Earth Spike", "dmg": (55, 80)},
        'b': {"name": "Tremor", "dmg": (60, 85)},
        'c': {"name": "Landslide", "dmg": (70, 100)},
        'd': {"name": "Earthquake", "dmg": (85, 115)},
    }
    enemy = Enemy("Carlos", "The Earth", 460, 240, abilities, 38, "World Association")
    enemy.ai_pattern = ['d', 'c', 'b', 'a']
    return enemy


# ===== INDEPENDENT VILLAINS =====

def create_enemy_assassin():
    """Mystery Assassin - Early Game Villain"""
    abilities = {
        'a': {"name": "Quick Strike", "dmg": (35, 55)},
        'b': {"name": "Shadow Step", "dmg": (40, 60)},
        'c': {"name": "Assassinate", "dmg": (50, 75)},
    }
    enemy = Enemy("Assassin", "Shadow Killer", 280, 180, abilities, 80, "Unknown")
    enemy.ai_pattern = ['c', 'b', 'a']
    return enemy


def create_enemy_cultist():
    """Cultist - Mysterious Organization"""
    abilities = {
        'a': {"name": "Dark Pulse", "dmg": (40, 65)},
        'b': {"name": "Corruption", "dmg": (35, 60)},
        'c': {"name": "Ritual Sacrifice", "dmg": (60, 85)},
    }
    enemy = Enemy("Cultist", "Dark Zealot", 300, 190, abilities, 72, "Cult")
    enemy.ai_pattern = ['c', 'a', 'b']
    return enemy


def create_enemy_shadow_leader():
    """Shadow Leader - Mid Game Boss"""
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
    """Phantom - Elusive Villain"""
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
# GAME CLASS WITH ALL MODES - NUMBERS FOR ALL COMMANDS
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
        """Slower, more dramatic log messages"""
        print(f"[T{self.turn_count}] ", end='')
        slow_print(message, 0.02)
        time.sleep(0.2)

    def display_health_bars(self):
        """Health bars with dramatic pauses"""
        print("\n" + "=" * 110)
        print("✦✦✦ PARTY STATUS ✦✦✦")
        print("-" * 110)
        time.sleep(0.3)

        for member in self.party:
            if member.is_alive():
                bar_len = 40
                filled = int(bar_len * member.hp / member.max_hp)
                bar = "█" * filled + "░" * (bar_len - filled)
                status = []
                if member.name == "Kayden Break":
                    status.append(f"FORM: {member.form}")
                    if member.form == "Limit Breaker":
                        status.append("⚡WHITE IGNITION")
                        status.append(f"⏳{member.limit_timer}")
                    if member.domain:
                        status.append("👑DOMAIN")
                        status.append(f"⏳{member.domain_timer}")
                    if member.cloak:
                        status.append("⚡CLOAK")
                        status.append(f"⏳{member.cloak_timer}")
                    if member.cat_form:
                        status.append("🐱CAT")
                elif member.name == "Kartein":
                    mode = "💚HEAL" if member.healing_mode else "💀DECAY"
                    status.append(mode)
                    wing_display = {
                        "none": "❌NO WINGS",
                        "angel": "🕊️ANGEL",
                        "demon": "👿DEMON",
                        "dual": "🦋✨DUAL"
                    }
                    status.append(wing_display[member.wing_state])
                    if member.entropic_ward_active:
                        status.append("☠️ENTROPIC")
                elif member.name == "Pluton":
                    if member.well_active:
                        status.append("⚖️WELL")
                    if member.field_active:
                        status.append("🌋FIELD")
                status_str = " | ".join(status) if status else ""
                print(f"{member.name:15} |{bar}| {member.hp:3}/{member.max_hp:3} HP {member.energy:3}E  {status_str}")
                time.sleep(0.2)

        print("\n" + "=" * 110)
        print("☠☠☠ ENEMY STATUS ☠☠☠")
        print("-" * 110)
        time.sleep(0.3)

        for enemy in self.enemies:
            if enemy.is_alive():
                bar_len = 40
                filled = int(bar_len * enemy.hp / enemy.max_hp)
                bar = "█" * filled + "░" * (bar_len - filled)
                debuff = []
                if "stun" in enemy.debuffs:
                    debuff.append("⚡STUN")
                if "sealed" in enemy.debuffs:
                    debuff.append("🔒SEALED")
                if "isolated" in enemy.debuffs:
                    debuff.append("🔮ISOLATED")
                if "crushed" in enemy.debuffs:
                    debuff.append("🌋CRUSHED")
                debuff_str = " | ".join(debuff) if debuff else ""
                affil = f" [{enemy.affiliation}]" if enemy.affiliation else ""
                print(f"{enemy.name:15} |{bar}| {enemy.hp:3}/{enemy.max_hp:3} HP (R{enemy.rank}){affil} {debuff_str}")
                time.sleep(0.2)

        print("=" * 110)
        time.sleep(0.5)

    def select_target(self, allies=False):
        """Target selection with clear prompts"""
        if allies:
            targets = [c for c in self.party if c.is_alive()]
            if not targets:
                return None
            print("\n" + "✦" * 50)
            slow_print("✦✦✦ SELECT ALLY TARGET ✦✦✦", 0.03)
            print("✦" * 50)
            for i, t in enumerate(targets):
                print(f"  {i + 1}. {t.name} ({t.hp}/{t.max_hp} HP)")
                time.sleep(0.1)
        else:
            targets = [e for e in self.enemies if e.is_alive()]
            if not targets:
                return None
            print("\n" + "☠" * 50)
            slow_print("☠☠☠ SELECT ENEMY TARGET ☠☠☠", 0.03)
            print("☠" * 50)
            for i, t in enumerate(targets):
                print(f"  {i + 1}. {t.name} ({t.hp}/{t.max_hp} HP)")
                time.sleep(0.1)

        choice = input("> ").strip()
        print()

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(targets):
                return targets[idx]
        except:
            pass
        print("❌ Invalid target. Try again.")
        time.sleep(0.5)
        return self.select_target(allies)

    def display_ability_description(self, abil):
        """Dramatic ability description display"""
        print("\n" + "─" * 80)
        slow_print(f"📖 {abil['name']}", 0.04)
        print("─" * 80)
        slow_print(abil['desc'], 0.02)
        if "cost" in abil:
            print(f"\n⚡ Energy Cost: {abil['cost']}")
        if "dmg" in abil and abil["dmg"] != (0, 0):
            print(f"💢 Damage: {abil['dmg'][0]}-{abil['dmg'][1]}")
        if "heal" in abil:
            print(f"💚 Healing: {abil['heal'][0]}-{abil['heal'][1]}")
        print("─" * 80)
        input("Press Enter to continue...")
        print()

    def use_ability(self, character):
        """Ability selection with dramatic presentation - ALL NUMBERS NOW"""
        print(f"\n" + "=" * 110)
        slow_print(f"✦✦✦ {character.name} [{character.title}] ✦✦✦", 0.03)
        print("=" * 110)
        print(f"❤️ HP: {character.hp}/{character.max_hp}  ⚡ Energy: {character.energy}/{character.max_energy}")
        print("-" * 110)
        time.sleep(0.3)

        if character.name == "Kartein":
            mode_icon = "💚" if character.healing_mode else "💀"
            mode_name = "HEALING MODE" if character.healing_mode else "DECAY MODE"
            wing_display = {
                "none": "❌ No Wings",
                "angel": "🕊️ Angel Wings (+50% Healing) [ACTIVE]",
                "demon": "👿 Demon Wings [ACTIVE]",
                "dual": "🦋✨ Dual Wings [ACTIVE]"
            }
            print(f"🔄 {mode_icon} {mode_name}  |  {wing_display[character.wing_state]}")
            if character.entropic_ward_active:
                print("   ☠️ ENTROPIC WARD [ACTIVE]")
            time.sleep(0.2)

        elif character.name == "Kayden Break":
            print(f"⚡ FORM: {character.form}")
            if character.domain_placed:
                print("\n🏰━━━━━━━━━━ DOMAINS ━━━━━━━━━━🏰")
                if character.form == "Limit Breaker":
                    print(f"   ⚡⚡⚡ LIMIT BREAKER - {character.limit_timer} turns")
                if character.domain:
                    print(f"   👑 DOMINANT ZONE - {character.domain_timer} turns")
                if character.cloak:
                    print(f"   ⚡ LIGHTNING CLOAK - {character.cloak_timer} turns")
                print("🏰━━━━━━━━━━━━━━━━━━━━━━━━━━━━🏰\n")
                time.sleep(0.3)

        elif character.name == "Pluton":
            if character.well_active:
                print("   ⚖️ GRAVITY WELL [ACTIVE] - +20% damage")
            if character.field_active:
                print("   🌋 CRUSHING FIELD [ACTIVE] - All enemies slowed")
            time.sleep(0.2)

        available = {}
        if character.name == "Kartein":
            available = character.get_available_abilities()
        else:
            for key, abil in character.abilities.items():
                if character.energy < abil["cost"]:
                    continue
                if character.name == "Kayden Break":
                    if abil["name"] == "⚡ Lightning Cloak" and character.cloak:
                        continue
                    if abil["name"] == "👑 Dominant Zone" and character.domain:
                        continue
                    if abil["name"] == "⚡⚡⚡ Limit Breaker" and character.form == "Limit Breaker":
                        continue
                    if abil["name"] == "🐱 Cat Punch" and not character.cat_form:
                        continue
                if character.name == "Pluton":
                    if abil["name"] == "⚖️ Personal Gravity Well" and character.well_active:
                        continue
                    if abil["name"] == "🌋 Crushing Field" and character.field_active:
                        continue
                available[key] = abil

        print("\n" + "📋 AVAILABLE ABILITIES:")
        print("-" * 110)
        time.sleep(0.2)

        for key in sorted(available.keys(), key=lambda x: int(x) if x.isdigit() else x):
            abil = available[key]
            if "dmg" in abil and abil["dmg"] != (0, 0) and "heal" in abil:
                d = abil["dmg"]
                h = abil["heal"]
                domain_icon = "🏰 " if "type" in abil and abil["type"] == "domain" else ""
                print(f"  {key}. {domain_icon}{abil['name']:35} | {abil['cost']}E | {d[0]}-{d[1]} DMG / {h[0]}-{h[1]} HEAL")
            elif "dmg" in abil and abil["dmg"] != (0, 0):
                d = abil["dmg"]
                domain_icon = "🏰 " if "type" in abil and abil["type"] == "domain" else ""
                print(f"  {key}. {domain_icon}{abil['name']:35} | {abil['cost']}E | {d[0]}-{d[1]} DMG")
            elif "heal" in abil:
                h = abil["heal"]
                print(f"  {key}. {abil['name']:35} | {abil['cost']}E | {h[0]}-{h[1]} HEAL")
            else:
                domain_icon = "🏰 " if "type" in abil and abil["type"] == "domain" else ""
                print(f"  {key}. {domain_icon}{abil['name']:35} | {abil['cost']}E | BUFF")
            time.sleep(0.1)

        print("\n" + "🎮 COMMANDS:")
        print("  00. 📖 Describe Ability")
        print("  0. 🔄 Toggle Mode/Cat Form")
        print("  -. ⏭️  Skip Turn (+15E)")
        print("  back. ↩️  Back")
        print("-" * 110)

        choice = input("> ").strip().lower()
        print()

        if choice == 'back':
            return False
        if choice == '-':
            self.add_log(f"{character.name} skips turn. +15 Energy")
            character.energy = min(character.max_energy, character.energy + 15)
            time.sleep(ACTION_DELAY)
            return True
        if choice == '0':
            if character.name == "Kayden Break":
                character.cat_form = not character.cat_form
                self.add_log(f"Kayden: {'🐱 CAT' if character.cat_form else '👤 HUMAN'}")
            elif character.name == "Kartein":
                character.healing_mode = not character.healing_mode
                self.add_log(f"Kartein: {'💚 HEALING' if character.healing_mode else '💀 DECAY'}")
            time.sleep(ACTION_DELAY)
            return True
        if choice == '00':
            print("\n📖 SELECT ABILITY NUMBER TO DESCRIBE:")
            for key in sorted(available.keys(), key=lambda x: int(x) if x.isdigit() else x):
                abil = available[key]
                print(f"  {key}. {abil['name']}")
            desc_choice = input("> ").strip()
            if desc_choice in available:
                self.display_ability_description(available[desc_choice])
            return self.use_ability(character)

        if choice in available:
            ability = available[choice]
            character.energy = max(0, character.energy - ability["cost"])

            # DOMAIN
            if "type" in ability and ability["type"] == "domain":
                if ability["domain"] == "cloak":
                    self.add_log(character.activate_domain("cloak"))
                elif ability["domain"] == "zone":
                    self.add_log(character.activate_domain("zone"))
                elif ability["domain"] == "limit":
                    self.add_log(character.activate_domain("limit"))

            # HEALING
            elif "type" in ability and ability["type"] == "heal":
                target = self.select_target(allies=True)
                if target:
                    heal = random.randint(ability["heal"][0], ability["heal"][1])
                    if character.wing_state in ["angel", "dual"]:
                        heal = int(heal * 1.5)
                    if ability["name"] == "❤️ Life-Force Transfer":
                        character.hp = max(1, character.hp - 20)
                    target.heal(heal)
                    self.add_log(f"✨ Kartein heals {target.name} for {heal} HP!")

            # DAMAGE
            elif "type" in ability and ability["type"] == "damage":
                target = self.select_target()
                if target:
                    dmg = random.randint(ability["dmg"][0], ability["dmg"][1])
                    buffs = []
                    if character.name == "Kayden Break":
                        dmg_mult, buffs = character.get_damage_multiplier()
                        dmg = int(dmg * dmg_mult)
                    if character.name == "Kartein" and not character.healing_mode:
                        if character.wing_state in ["demon", "dual"]:
                            dmg = int(dmg * 1.3)
                    if character.name == "Pluton" and character.well_active:
                        dmg = int(dmg * 1.2)
                    target.take_damage(dmg)
                    if ability["name"] == "👁️ Divine Judgment":
                        target.debuffs.append("stun")
                        self.add_log("⚡⚡ DIVINE JUDGMENT! A pillar of white-hot lightning descends! Target stunned!")
                    elif ability["name"] == "❌ Grand Cross":
                        self.add_log("❌❌ GRAND CROSS! Two massive lightning waves overlap! Devastating!")
                    elif ability["name"] == "🌀 Event Horizon":
                        self.add_log("🌀🌀 EVENT HORIZON! Space warps and collapses around the target!")
                    elif ability["name"] == "🧠 Brain Shock":
                        target.debuffs.append("stun")
                        self.add_log("🧠 BRAIN SHOCK! Precise, non-lethal shock! Target unconscious!")
                    elif ability["name"] == "⛓️ Plasma Chains":
                        target.debuffs.append("chained")
                        self.add_log("⛓️ PLASMA CHAINS! Razor-sharp chains bind the enemy!")
                    self.add_log(f"{character.name} hits {target.name} for {dmg} damage!")
                    if ability["name"] == "🩸 Life Drain":
                        heal = dmg // 2
                        character.heal(heal)
                        self.add_log(f"🩸 Kartein siphons {heal} HP from the target!")

            # WING MANIFEST
            elif "type" in ability and ability["type"] == "wing_manifest":
                wing_map = {"Angel": "angel", "Demon": "demon", "Dual": "dual"}
                new_wing = next((v for k, v in wing_map.items() if k in ability["name"]), None)
                if new_wing and character.wing_state not in ["none", new_wing]:
                    old = character.wing_state.upper()
                    print(f"\n⚠️  WARNING: You have {old} WINGS active!")
                    print(f"   Switching will LOSE your current wings and their unlocked abilities.")
                    print(f"   Confirm? (y/n)")
                    confirm = input("> ").strip().lower()
                    if confirm != 'y':
                        self.add_log("Wing manifestation cancelled.")
                        time.sleep(ACTION_DELAY)
                        return True
                if new_wing == "angel":
                    self.add_log(character.set_wings("angel"))
                elif new_wing == "demon":
                    self.add_log(character.set_wings("demon"))
                elif new_wing == "dual":
                    self.add_log(character.set_wings("dual"))

            # DEMON ABILITIES
            elif "type" in ability and ability["type"] == "demon_ability":
                target = self.select_target()
                if target and character.wing_state in ["demon", "dual"]:
                    dmg = random.randint(ability["dmg"][0], ability["dmg"][1])
                    if character.wing_state in ["demon", "dual"]:
                        dmg = int(dmg * 1.3)
                    target.take_damage(dmg)
                    if "Black Swamp" in ability["name"]:
                        self.add_log("🌑🌑🌑 BLACK SWAMP! Entropic jaws emerge from bat wings and consume the target!")
                        target.debuffs.append("crushed")
                    elif "Wing Blade" in ability["name"]:
                        self.add_log("🦇🦇🦇 WING BLADE! Bat wings slice through the target like razors!")
                        if random.random() < 0.3:
                            target.debuffs.append("stun")
                    elif "Wing Split" in ability["name"]:
                        self.add_log("🦇🦇🦇 WING SPLIT! Demon wings multiply and strike from multiple angles!")
                        if random.random() < 0.4:
                            extra = dmg // 2
                            target.take_damage(extra)
                            self.add_log(f"  Extra strike! +{extra} damage!")
                    self.add_log(f"{character.name} hits {target.name} for {dmg} damage!")

            # DUAL WINGS
            elif "type" in ability and ability["type"] == "dual_ability":
                target = self.select_target()
                if target and character.wing_state == "dual":
                    dmg = random.randint(ability["dmg"][0], ability["dmg"][1])
                    target.take_damage(dmg)
                    self.add_log(f"🦋✨🦋✨ DUAL WINGS JUDGMENT! {target.name} takes {dmg} damage!")
                    for ally in self.party:
                        if ally.is_alive():
                            heal = random.randint(ability["heal"][0], ability["heal"][1])
                            ally.heal(heal)
                            self.add_log(f"  ✨ {ally.name} healed for {heal} HP!")

            # UTILITY
            elif "type" in ability and ability["type"] == "utility":
                if ability["name"] == "🛡️ Shield":
                    character.defending = True
                    self.add_log("🛡️ SHIELD! Force field of concentrated electrical energy!")
                elif ability["name"] == "🔮 Spatial Isolation Barrier":
                    for e in self.enemies:
                        if e.is_alive():
                            e.debuffs.append("isolated")
                    self.add_log("🔮🔮 SPATIAL ISOLATION BARRIER! Kayden snaps his fingers and isolates space!")
                elif ability["name"] == "🛡️ Reactive Reformation":
                    character.buffs.append("reactive_armor")
                    self.add_log("🛡️ REACTIVE REFORMATION! Cells reinforced! Next physical damage -70%!")
                elif ability["name"] == "☠️ Entropic Ward":
                    character.entropic_ward_active = True
                    self.add_log("☠️☠️ ENTROPIC WARD! Contact field of decay! Attackers will wither!")
                elif ability["name"] == "🔒 Power Seal":
                    target = self.select_target()
                    if target:
                        if random.random() < 0.7:
                            target.debuffs.append("sealed")
                            self.add_log(f"🔒 POWER SEAL! {target.name}'s core energy flow suppressed!")
                        else:
                            self.add_log(f"❌ Power Seal failed on {target.name}!")
                elif ability["name"] == "🔮 Dimensional Isolation":
                    target = self.select_target()
                    if target:
                        target.debuffs.append("isolated")
                        self.add_log(f"🔮 DIMENSIONAL ISOLATION! {target.name} encased in spatial barrier!")
                elif ability["name"] == "🛡️ Gravity Shield":
                    character.defending = True
                    self.add_log("🛡️ GRAVITY SHIELD! Warped space-time bends incoming attacks!")
                elif ability["name"] == "⚖️ Personal Gravity Well":
                    character.well_active = True
                    self.add_log("⚖️⚖️ PERSONAL GRAVITY WELL! Immovable stance! +20% damage!")
                elif ability["name"] == "🌋 Crushing Field":
                    character.field_active = True
                    for e in self.enemies:
                        if e.is_alive():
                            e.debuffs.append("crushed")
                    self.add_log("🌋🌋 CRUSHING FIELD! Gravity intensifies over the entire battlefield!")
                elif ability["name"] == "🔄 Kinetic Redirection":
                    character.buffs.append("reflect")
                    self.add_log("🔄 KINETIC REDIRECTION! Gravity vectors manipulated! Next attack reflected!")
                elif ability["name"] == "✨ Gravitational Lensing":
                    character.buffs.append("lensing")
                    self.add_log("✨ GRAVITATIONAL LENSING! Light and energy waves bent! Perception scrambled!")
                elif ability["name"] == "⚓ Anchor Point":
                    target = self.select_target()
                    if target:
                        target.debuffs.append("anchored")
                        self.add_log(f"⚓ ANCHOR POINT! Powerful gravitational pull! {target.name} immobilized!")

            time.sleep(ACTION_DELAY)
            return True
        else:
            print("❌ Invalid ability number. Try again.")
            time.sleep(0.5)
            return self.use_ability(character)

    def enemy_turn(self, enemy):
        if not enemy.is_alive():
            return
        if not any(c.is_alive() for c in self.party):
            return
        if "stun" in enemy.debuffs:
            self.add_log(f"⚡ {enemy.name} is stunned and cannot act!")
            enemy.debuffs.remove("stun")
            time.sleep(0.5)
            return
        if "sealed" in enemy.debuffs:
            self.add_log(f"🔒 {enemy.name}'s abilities are sealed! Using basic attack.")
            targets = [c for c in self.party if c.is_alive()]
            if targets:
                t = random.choice(targets)
                dmg = random.randint(15, 25)
                if self.kartein.entropic_ward_active and t.name == "Kartein":
                    dmg = int(dmg * 0.7)
                    counter = random.randint(15, 25)
                    enemy.take_damage(counter)
                    self.add_log(f"☠️ Entropic Ward! {enemy.name} takes {counter} damage!")
                t.take_damage(dmg)
                self.add_log(f"{enemy.name} attacks for {dmg} damage!")
            time.sleep(0.5)
            return
        if enemy.ai_pattern:
            key = enemy.ai_pattern[(self.turn_count - 1) % len(enemy.ai_pattern)]
            abil = enemy.abilities.get(key, list(enemy.abilities.values())[0])
            # If this is a 0-dmg flavor ability, show a message and skip damage
            if abil["dmg"] == (0, 0):
                self.add_log(f"✨ {enemy.name} uses {abil['name']}! [Preparing next move...]")
                time.sleep(0.8)
                return
            targets = [c for c in self.party if c.is_alive()]
            if targets:
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
                    self.add_log(f"🔄 Pluton reflects {reflect} damage back at {enemy.name}!")
                    t.buffs.remove("reflect")
                elif "lensing" in t.buffs:
                    if random.random() < 0.5:
                        self.add_log(f"✨ GRAVITATIONAL LENSING! {enemy.name}'s attack bends away and misses {t.name}!")
                    else:
                        self.add_log(f"✨ Lensing flickered — {enemy.name}'s attack breaks through!")
                        if "reactive_armor" in t.buffs:
                            dmg = int(dmg * 0.3)
                            self.add_log(f"🛡️ Reactive Reformation! Damage reduced to {dmg}!")
                            t.buffs.remove("reactive_armor")
                        t.take_damage(dmg)
                        if self.kartein.entropic_ward_active and t.name == "Kartein":
                            counter = random.randint(15, 25)
                            enemy.take_damage(counter)
                            self.add_log(f"☠️ Entropic Ward! {enemy.name} takes {counter} damage!")
                        self.add_log(f"{enemy.name} uses {abil['name']} for {dmg} damage!")
                    t.buffs.remove("lensing")
                else:
                    if "reactive_armor" in t.buffs:
                        dmg = int(dmg * 0.3)
                        self.add_log(f"🛡️ Reactive Reformation! Damage reduced to {dmg}!")
                        t.buffs.remove("reactive_armor")
                    t.take_damage(dmg)
                    if self.kartein.entropic_ward_active and t.name == "Kartein":
                        counter = random.randint(15, 25)
                        enemy.take_damage(counter)
                        self.add_log(f"☠️ Entropic Ward! {enemy.name} takes {counter} damage!")
                    self.add_log(f"{enemy.name} uses {abil['name']} for {dmg} damage!")
            time.sleep(0.8)

    def cleanup(self):
        for c in self.party + self.enemies:
            c.defending = False
            if c.name == "Kayden Break":
                if c.form == "Limit Breaker":
                    c.limit_timer -= 1
                    if c.limit_timer <= 0 or random.random() < 0.3:
                        c.form = "Normal"
                        c.limit_timer = 0
                        self.add_log("⚡ Kayden's WHITE IGNITION fades. Returns to Normal form.")
                if c.domain:
                    c.domain_timer -= 1
                    if c.domain_timer <= 0 or random.random() < 0.2:
                        c.domain = False
                        c.domain_timer = 0
                        self.add_log("👑 DOMINANT ZONE dissipates. His world fades away.")
                if c.cloak:
                    c.cloak_timer -= 1
                    if c.cloak_timer <= 0 or random.random() < 0.15:
                        c.cloak = False
                        c.cloak_timer = 0
                        self.add_log("⚡ LIGHTNING CLOAK deactivates. The crackling armor fades.")
                if not c.form == "Limit Breaker" and not c.domain and not c.cloak:
                    c.domain_placed = False
            if c.name == "Kartein" and c.entropic_ward_active:
                if random.random() < 0.25:
                    c.entropic_ward_active = False
                    self.add_log("☠️ Entropic Ward fades.")
            to_remove = []
            for debuff in c.debuffs:
                if debuff in ["stun", "sealed", "isolated", "crushed", "anchored", "chained"]:
                    if random.random() < 0.3:
                        to_remove.append(debuff)
            for debuff in to_remove:
                if debuff in c.debuffs:
                    c.debuffs.remove(debuff)
                    if hasattr(c, 'name'):
                        self.add_log(f"{c.name}'s {debuff} effect wore off.")
            time.sleep(0.3)

    def battle(self, enemies):
        self.enemies = enemies
        self.turn_count = 0
        print("\n" + "=" * 110)
        slow_print("⚔️⚔️⚔️ BATTLE START ⚔️⚔️⚔️", 0.04)
        print("=" * 110)
        print(f"✦ PARTY: Kayden • Kartein • Pluton")
        print(f"☠ ENEMIES: {', '.join([e.name for e in self.enemies])}")
        if hasattr(self.enemies[0], 'affiliation') and self.enemies[0].affiliation:
            print(f"🏴 AFFILIATION: {self.enemies[0].affiliation}")
        print("=" * 110)
        time.sleep(BATTLE_START_DELAY)

        while True:
            self.turn_count += 1
            print(f"\n{'=' * 55} TURN {self.turn_count} {'=' * 55}")
            time.sleep(TURN_DELAY)

            for char in self.party:
                if char.is_alive():
                    char.energy = min(char.max_energy, char.energy + 12)
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
            print("\n" + "☠☠☠ ENEMY PHASE ☠☠☠")
            time.sleep(0.5)
            for enemy in self.enemies:
                if enemy.is_alive():
                    self.enemy_turn(enemy)
                    time.sleep(0.3)
            self.cleanup()

        self.display_health_bars()
        if any(e.is_alive() for e in self.enemies):
            print("\n" + "=" * 110)
            slow_print("💀💀💀 DEFEAT... 💀💀💀", 0.05)
            print("=" * 110)
            time.sleep(VICTORY_DELAY)
            return False
        else:
            print("\n" + "=" * 110)
            slow_print("✨✨✨ VICTORY! ✨✨✨", 0.05)
            print("=" * 110)
            self.victories += 1
            self.total_kills += len([e for e in self.enemies if not e.is_alive()])
            time.sleep(VICTORY_DELAY)
            return True

    def rest(self):
        """Rest and recover with dramatic effect"""
        print("\n" + "=" * 110)
        slow_print("🛌🛌🛌 RESTING & RECOVERY 🛌🛌🛌", 0.04)
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
            print(f"  ✦ {char.name} fully recovered!")
            time.sleep(0.2)

        print("\n✦ Party fully healed and recovered! ✦")
        time.sleep(1.5)

    # ===== GAME MODES =====

    def story_mode(self):
        """Story Mode - Follow the Eleceed storyline"""
        print("\n" + "=" * 110)
        slow_print("📖📖📖 STORY MODE 📖📖📖", 0.04)
        print("=" * 110)
        slow_print("Follow Kayden, Kartein, and Pluton through the Eleceed storyline!", 0.02)
        slow_print("Face villains from Frame, Astra Group, and more!", 0.02)
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
            slow_print(f"📖 {chapter}", 0.03)
            print(f"Battle {i + 1}/{len(chapters)}")
            print("!" * 110)
            time.sleep(0.5)
            input("Press Enter to continue...")
            print()

            if not self.battle(enemies):
                print("\n💀 GAME OVER 💀")
                print(f"Defeated at {chapter}")
                time.sleep(2)
                return False

            if chapter != "Final Chapter: The Void Dancer":
                self.rest()

        print("\n" + "=" * 110)
        slow_print("🏆🏆🏆 STORY MODE COMPLETE! 🏆🏆🏆", 0.04)
        print("=" * 110)
        slow_print("You have defeated Astra and saved the awakened world!", 0.02)
        print(f"Total victories: {self.victories}")
        print(f"Enemies defeated: {self.total_kills}")
        print("=" * 110)
        time.sleep(3)
        return True

    def gauntlet_mode(self):
        """Ranker Gauntlet - Fight through all ranks"""
        print("\n" + "=" * 110)
        slow_print("🏆🏆🏆 RANKER GAUNTLET 🏆🏆🏆", 0.04)
        print("=" * 110)
        slow_print("Face increasingly powerful awakened ones!", 0.02)
        slow_print("From rank 100 to rank 7!", 0.02)
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
            ("Rank 8: Astra", [create_enemy_astra()]),
        ]

        for i, (stage, enemies) in enumerate(stages):
            self.wave = i + 1
            print("\n" + "!" * 110)
            slow_print(f"🏆 STAGE {self.wave}: {stage}", 0.03)
            print("!" * 110)
            time.sleep(0.5)
            input("Press Enter to challenge...")
            print()

            if not self.battle(enemies):
                print("\n💀 GAUNTLET FAILED 💀")
                print(f"Defeated at Stage {self.wave}: {stage}")
                time.sleep(2)
                return False

            if stage != "Rank 8: Astra":
                self.rest()

        print("\n" + "=" * 110)
        slow_print("🏆🏆🏆 GAUNTLET COMPLETE! 🏆🏆🏆", 0.04)
        print("=" * 110)
        slow_print("You have conquered all ranks!", 0.02)
        print(f"Total victories: {self.victories}")
        print(f"Enemies defeated: {self.total_kills}")
        print("=" * 110)
        time.sleep(3)
        return True

    def boss_rush_mode(self):
        """Boss Rush - Only major villains"""
        print("\n" + "=" * 110)
        slow_print("👑👑👑 BOSS RUSH 👑👑👑", 0.04)
        print("=" * 110)
        slow_print("Face the most powerful villains back-to-back!", 0.02)
        slow_print("No rest between battles!", 0.02)
        print("=" * 110)
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
            print("\n" + "!" * 110)
            slow_print(f"👑 BOSS {self.wave}: {boss}", 0.03)
            print("!" * 110)
            time.sleep(0.5)
            input("Press Enter to challenge...")
            print()

            if not self.battle(enemies):
                print("\n💀 BOSS RUSH FAILED 💀")
                print(f"Defeated at Boss {self.wave}: {boss}")
                time.sleep(2)
                return False

            print("⚔️ Preparing next boss... ⚔️")
            time.sleep(1.5)

        print("\n" + "=" * 110)
        slow_print("👑👑👑 BOSS RUSH COMPLETE! 👑👑👑", 0.04)
        print("=" * 110)
        slow_print("You have defeated every major villain!", 0.02)
        print(f"Total victories: {self.victories}")
        print("=" * 110)
        time.sleep(3)
        return True

    def survival_mode(self):
        """Endless Survival - How many waves can you survive?"""
        print("\n" + "=" * 110)
        slow_print("♾️♾️♾️ ENDLESS SURVIVAL ♾️♾️♾️", 0.04)
        print("=" * 110)
        slow_print("Fight wave after wave of enemies!", 0.02)
        slow_print("No recovery between waves!", 0.02)
        slow_print("How long can you last?", 0.02)
        print("=" * 110)
        time.sleep(1)

        wave = 0
        score = 0

        while True:
            wave += 1
            self.wave = wave

            print("\n" + "🔥" * 55)
            slow_print(f"🔥 WAVE {wave} 🔥", 0.05)
            print("🔥" * 55)
            time.sleep(0.5)

            # Generate wave enemies based on wave number
            wave_enemies = []

            if wave <= 5:
                count = min(3, wave)
                for _ in range(count):
                    wave_enemies.append(create_enemy_frame_soldier())
            elif wave <= 10:
                wave_enemies.append(create_enemy_frame_captain())
                wave_enemies.append(create_enemy_frame_soldier())
                wave_enemies.append(create_enemy_frame_soldier())
            elif wave <= 15:
                wave_enemies.append(create_enemy_andrei())
                wave_enemies.append(create_enemy_frame_elite())
            elif wave <= 20:
                wave_enemies.append(create_enemy_kuen())
                wave_enemies.append(create_enemy_gerald())
            elif wave <= 25:
                wave_enemies.append(create_enemy_mioru())
                wave_enemies.append(create_enemy_frame_elite())
                wave_enemies.append(create_enemy_frame_elite())
            elif wave <= 30:
                wave_enemies.append(create_enemy_sujin())
                wave_enemies.append(create_enemy_dmitri())
            elif wave <= 35:
                wave_enemies.append(create_enemy_yodore())
                wave_enemies.append(create_enemy_carlos())
            elif wave <= 40:
                wave_enemies.append(create_enemy_phantom())
                wave_enemies.append(create_enemy_shadow_leader())
            elif wave <= 45:
                wave_enemies.append(create_enemy_astra_elite())
                wave_enemies.append(create_enemy_dark_mage())
                wave_enemies.append(create_enemy_dark_mage())
            elif wave <= 50:
                wave_enemies.append(create_enemy_mugeni())
                wave_enemies.append(create_enemy_vatore())
            else:
                bosses = [create_enemy_astra(), create_enemy_vatore(), create_enemy_mugeni()]
                wave_enemies.append(random.choice(bosses))
                wave_enemies.append(create_enemy_astra_elite())
                wave_enemies.append(create_enemy_astra_elite())

            input("Press Enter to face the wave...")
            print()

            if not self.battle(wave_enemies):
                print("\n" + "=" * 110)
                slow_print(f"☠️☠️☠️ SURVIVAL ENDED AT WAVE {wave} ☠️☠️☠️", 0.04)
                print("=" * 110)
                print(f"Enemies defeated: {self.total_kills}")
                print(f"Waves cleared: {wave - 1}")
                print(f"Score: {score}")
                print("=" * 110)
                time.sleep(3)
                break

            score += wave * 100
            print(f"\n✨ Wave {wave} cleared! Score: {score}")
            time.sleep(1)

            if random.random() < 0.2:
                for char in self.party:
                    char.hp = min(char.max_hp, char.hp + int(char.max_hp * 0.2))
                    char.energy = min(char.max_energy, char.energy + int(char.max_energy * 0.2))
                slow_print("🩹 Found supplies! Party recovers 20% HP/Energy.", 0.02)
                time.sleep(1)

        return score

    def frame_raid_mode(self):
        """Frame Raid - Infiltrate Frame Headquarters"""
        print("\n" + "=" * 110)
        slow_print("🔴🔴🔴 FRAME HEADQUARTERS RAID 🔴🔴🔴", 0.04)
        print("=" * 110)
        slow_print("Infiltrate the enemy stronghold!", 0.02)
        slow_print("Defeat Frame executives and their forces!", 0.02)
        print("=" * 110)
        time.sleep(1)

        missions = [
            ("Perimeter Breach",
             [create_enemy_frame_soldier(), create_enemy_frame_soldier(), create_enemy_frame_soldier()]),
            ("Security Checkpoint",
             [create_enemy_frame_captain(), create_enemy_frame_soldier(), create_enemy_frame_soldier()]),
            ("Elite Patrol", [create_enemy_frame_elite(), create_enemy_frame_elite()]),
            ("Research Wing", [create_enemy_frame_captain(), create_enemy_frame_elite(), create_enemy_frame_soldier()]),
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
            print("\n" + "!" * 110)
            slow_print(f"🔴 MISSION {self.wave}: {mission}", 0.03)
            print("!" * 110)
            time.sleep(0.5)
            input("Press Enter to proceed...")
            print()

            if not self.battle(enemies):
                print("\n💀 RAID FAILED 💀")
                print(f"Defeated at Mission {self.wave}: {mission}")
                time.sleep(2)
                return False

            if mission != "Director's Office: Yodore":
                for char in self.party:
                    char.hp = min(char.max_hp, char.hp + int(char.max_hp * 0.3))
                    char.energy = min(char.max_energy, char.energy + int(char.max_energy * 0.3))
                slow_print("🔋 Quick breather... Party recovers 30% HP/Energy.", 0.02)
                time.sleep(1)

        print("\n" + "=" * 110)
        slow_print("✅✅✅ FRAME RAID SUCCESSFUL! ✅✅✅", 0.04)
        print("=" * 110)
        slow_print("Headquarters neutralized!", 0.02)
        slow_print("Frame's operations have been disrupted!", 0.02)
        print("=" * 110)
        time.sleep(3)
        return True

    def top10_tournament_mode(self):
        """Top 10 Tournament - Face the world's strongest"""
        print("\n" + "=" * 110)
        slow_print("🌍🌍🌍 TOP 10 TOURNAMENT 🌍🌍🌍", 0.04)
        print("=" * 110)
        slow_print("Face the world's most powerful awakened ones!", 0.02)
        slow_print("8 competitors. 3 rounds. 1 champion.", 0.02)
        print("=" * 110)
        time.sleep(1)

        quarterfinals = [
            ("Quarterfinal 1: vs Jinwoo", [create_enemy_jiwoo()]),
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

        print("\n🏆 TOURNAMENT BRACKET 🏆")
        print("Quarterfinals → Semifinals → Final → Championship")
        print("-" * 50)
        time.sleep(1)

        for match_name, enemies in quarterfinals:
            print("\n" + "-" * 110)
            slow_print(f"🏟️ {match_name}", 0.03)
            print("-" * 110)
            self.rest()
            input("Press Enter to fight...")
            print()
            if not self.battle(enemies):
                print("\n💀 TOURNAMENT ELIMINATED 💀")
                time.sleep(2)
                return False

        print("\n" + "=" * 110)
        slow_print("🏆 SEMIFINALS 🏆", 0.04)
        print("=" * 110)
        time.sleep(0.5)

        for match_name, enemies in semifinals:
            print("\n" + "-" * 110)
            slow_print(f"🏟️ {match_name}", 0.03)
            print("-" * 110)
            self.rest()
            input("Press Enter to fight...")
            print()
            if not self.battle(enemies):
                print("\n💀 TOURNAMENT ELIMINATED 💀")
                time.sleep(2)
                return False

        print("\n" + "=" * 110)
        slow_print("🏆 FINALS 🏆", 0.04)
        print("=" * 110)
        time.sleep(0.5)

        for match_name, enemies in finals:
            print("\n" + "-" * 110)
            slow_print(f"🏟️ {match_name}", 0.03)
            print("-" * 110)
            self.rest()
            input("Press Enter to fight...")
            print()
            if not self.battle(enemies):
                print("\n💀 TOURNAMENT ELIMINATED 💀")
                time.sleep(2)
                return False

        print("\n" + "=" * 110)
        slow_print("👑👑👑 TOURNAMENT CHAMPIONS! 👑👑👑", 0.04)
        print("=" * 110)
        slow_print("Kayden Break, Kartein, and Pluton stand above all!", 0.02)
        slow_print("You are the strongest in the world!", 0.02)
        print("=" * 110)
        time.sleep(3)
        return True

    def sparring_mode(self):
        """Training Room - Practice against any character"""
        print("\n" + "=" * 110)
        slow_print("🥋🥋🥋 TRAINING ROOM 🥋🥋🥋", 0.04)
        print("=" * 110)
        slow_print("Select an opponent to spar with.", 0.02)
        print("=" * 110)
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
            print(f"  {key}. {name}")
            time.sleep(0.05)
        print("  b. Back")
        print()

        choice = input("> ").strip()
        print()

        if choice.lower() == 'b':
            return

        for key, name, func in sparring_options:
            if choice == key:
                print(f"\nSparring with {name}...")
                time.sleep(0.5)
                self.rest()
                self.battle([func()])
                break


# ============================================================================
# MAIN MENU
# ============================================================================

def main():
    print("\n" + "=" * 110)
    slow_print("    ⚡⚡⚡ ELECEED: AWAKENED DUEL ⚡⚡⚡", 0.03)
    print("    COMPLETE EDITION - ALL VILLAINS, ALL MODES")
    print("    Kayden Break • Kartein • Pluton")
    print("=" * 110)
    print("\n🎮 GAME MODES:")
    time.sleep(0.3)
    print("  1. 📖 Story Mode - Follow the Eleceed storyline")
    print("  2. 🏆 Ranker Gauntlet - Fight through all ranks")
    print("  3. 👑 Boss Rush - Only major villains")
    print("  4. ♾️ Endless Survival - How many waves?")
    print("  5. 🔴 Frame Raid - Infiltrate Frame headquarters")
    print("  6. 🌍 Top 10 Tournament - Face the world's strongest")
    print("  7. 🥋 Training Room - Practice against any character")
    print("  8. 📊 Stats & Records")
    print("  9. ❌ Exit")
    print("=" * 110)
    print("\n📚 VILLAIN ROSTER:")
    time.sleep(0.2)
    print("   • Astra Group: Astra, Vatore, Mugeni, Elite Forces")
    print("   • Frame: Yodore, Mioru, Sujin, Andrei, Kuen, Gerald, Valerie, Klaus")
    print("   • World Association: Dmitri, Carlos")
    print("   • Independent: Phantom, Shadow Leader, Assassins")
    print("=" * 110)
    time.sleep(1)

    game = Game()
    cumulative_victories = 0
    cumulative_kills = 0
    best_survival_score = 0

    while True:
        print("\n" + "-" * 110)
        print("✦ MAIN MENU ✦")
        print("-" * 110)
        print("1. 📖 Story Mode")
        print("2. 🏆 Ranker Gauntlet")
        print("3. 👑 Boss Rush")
        print("4. ♾️ Endless Survival")
        print("5. 🔴 Frame Raid")
        print("6. 🌍 Top 10 Tournament")
        print("7. 🥋 Training Room")
        print("8. 📊 Stats & Records")
        print("9. ❌ Exit")
        print("-" * 110)

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
            print("\n" + "=" * 110)
            print("📊 STATS & RECORDS")
            print("=" * 110)
            print(f"🏆 Total victories (all sessions): {cumulative_victories}")
            print(f"💀 Enemies defeated (all sessions): {cumulative_kills}")
            print(f"🔥 Best Survival Score: {best_survival_score}")
            print("\n✦ LAST PARTY STATUS:")
            print(f"   ⚡ Kayden Break - {game.kayden.hp}/{game.kayden.max_hp} HP")
            print(f"   💚 Kartein - {game.kartein.hp}/{game.kartein.max_hp} HP")
            print(f"   ⚖️ Pluton - {game.pluton.hp}/{game.pluton.max_hp} HP")
            print("\n📚 UNLOCKED:")
            print("   • All Villains ✓")
            print("   • All Game Modes ✓")
            print("   • All Abilities ✓")
            print("=" * 110)
            input("\nPress Enter to continue...")
            print()
        elif choice == "9":
            slow_print("\nThanks for playing Eleceed: Awakened Duel!", 0.03)
            slow_print("See you next time, awakened one.\n", 0.03)
            time.sleep(1)
            break
        else:
            print("❌ Invalid choice.")
            time.sleep(0.5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
        sys.exit(0)
