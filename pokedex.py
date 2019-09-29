"""
Copyright 2017 Tim Leysen

This file is part of PoGoPollBot.

PoGoPollBot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PoGoPollBot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import string

def get_name(id : int):
    try:
        return pokemon_list[id-1]
    except:
        return None

def get_names(ids : [int]):
    return [get_name(id) for id in ids]
    
def get_id(name : str):
    try:
        return pokemon_list.index(capwords(name)) + 1
    except:
        return None
    
def get_ids(names : [str]):
    return [get_id(name) for name in names]
    
def id_exists(id : int):
    return id >= 1 and id <= len(pokemon_list)
    
def name_exists(name : str):
    return capwords(name) in pokemon_list

def is_raid_boss(name : str):
    return name.lower() in list(raid_bosses.keys())
    
def is_exclusive_raid_boss(name : str):
    return name.lower() in exclusive_raid_bosses

def capwords(s : str):
    return '-'.join([x.capitalize() for x in s.split('-')])
    
def sprite_url(name : str):
    return 'http://floatzel.net/pokemon/black-white/sprites/images/{0}.png'.format(get_id(name))
    
pokemon_list = ['Bulbasaur','Ivysaur','Venusaur','Charmander','Charmeleon','Charizard','Squirtle','Wartortle','Blastoise','Caterpie','Metapod','Butterfree','Weedle','Kakuna','Beedrill','Pidgey','Pidgeotto','Pidgeot','Rattata','Raticate','Spearow','Fearow','Ekans','Arbok','Pikachu','Raichu','Sandshrew','Sandslash','Nidoran?','Nidorina','Nidoqueen','Nidoran?','Nidorino','Nidoking','Clefairy','Clefable','Vulpix','Ninetales','Jigglypuff','Wigglytuff','Zubat','Golbat','Oddish','Gloom','Vileplume','Paras','Parasect','Venonat','Venomoth','Diglett','Dugtrio','Meowth','Persian','Psyduck','Golduck','Mankey','Primeape','Growlithe','Arcanine','Poliwag','Poliwhirl','Poliwrath','Abra','Kadabra','Alakazam','Machop','Machoke','Machamp','Bellsprout','Weepinbell','Victreebel','Tentacool','Tentacruel','Geodude','Graveler','Golem','Ponyta','Rapidash','Slowpoke','Slowbro','Magnemite','Magneton','Farfetch\'d','Doduo','Dodrio','Seel','Dewgong','Grimer','Muk','Shellder','Cloyster','Gastly','Haunter','Gengar','Onix','Drowzee','Hypno','Krabby','Kingler','Voltorb','Electrode','Exeggcute','Exeggutor','Cubone','Marowak','Hitmonlee','Hitmonchan','Lickitung','Koffing','Weezing','Rhyhorn','Rhydon','Chansey','Tangela','Kangaskhan','Horsea','Seadra','Goldeen','Seaking','Staryu','Starmie','Mr. Mime','Scyther','Jynx','Electabuzz','Magmar','Pinsir','Tauros','Magikarp','Gyarados','Lapras','Ditto','Eevee','Vaporeon','Jolteon','Flareon','Porygon','Omanyte','Omastar','Kabuto','Kabutops','Aerodactyl','Snorlax','Articuno','Zapdos','Moltres','Dratini','Dragonair','Dragonite','Mewtwo','Mew','Chikorita','Bayleef','Meganium','Cyndaquil','Quilava','Typhlosion','Totodile','Croconaw','Feraligatr','Sentret','Furret','Hoothoot','Noctowl','Ledyba','Ledian','Spinarak','Ariados','Crobat','Chinchou','Lanturn','Pichu','Cleffa','Igglybuff','Togepi','Togetic','Natu','Xatu','Mareep','Flaaffy','Ampharos','Bellossom','Marill','Azumarill','Sudowoodo','Politoed','Hoppip','Skiploom','Jumpluff','Aipom','Sunkern','Sunflora','Yanma','Wooper','Quagsire','Espeon','Umbreon','Murkrow','Slowking','Misdreavus','Unown','Wobbuffet','Girafarig','Pineco','Forretress','Dunsparce','Gligar','Steelix','Snubbull','Granbull','Qwilfish','Scizor','Shuckle','Heracross','Sneasel','Teddiursa','Ursaring','Slugma','Magcargo','Swinub','Piloswine','Corsola','Remoraid','Octillery','Delibird','Mantine','Skarmory','Houndour','Houndoom','Kingdra','Phanpy','Donphan','Porygon2','Stantler','Smeargle','Tyrogue','Hitmontop','Smoochum','Elekid','Magby','Miltank','Blissey','Raikou','Entei','Suicune','Larvitar','Pupitar','Tyranitar','Lugia','Ho-Oh','Celebi','Treecko','Grovyle','Sceptile','Torchic','Combusken','Blaziken','Mudkip','Marshtomp','Swampert','Poochyena','Mightyena','Zigzagoon','Linoone','Wurmple','Silcoon','Beautifly','Cascoon','Dustox','Lotad','Lombre','Ludicolo','Seedot','Nuzleaf','Shiftry','Taillow','Swellow','Wingull','Pelipper','Ralts','Kirlia','Gardevoir','Surskit','Masquerain','Shroomish','Breloom','Slakoth','Vigoroth','Slaking','Nincada','Ninjask','Shedinja','Whismur','Loudred','Exploud','Makuhita','Hariyama','Azurill','Nosepass','Skitty','Delcatty','Sableye','Mawile','Aron','Lairon','Aggron','Meditite','Medicham','Electrike','Manectric','Plusle','Minun','Volbeat','Illumise','Roselia','Gulpin','Swalot','Carvanha','Sharpedo','Wailmer','Wailord','Numel','Camerupt','Torkoal','Spoink','Grumpig','Spinda','Trapinch','Vibrava','Flygon','Cacnea','Cacturne','Swablu','Altaria','Zangoose','Seviper','Lunatone','Solrock','Barboach','Whiscash','Corphish','Crawdaunt','Baltoy','Claydol','Lileep','Cradily','Anorith','Armaldo','Feebas','Milotic','Castform','Kecleon','Shuppet','Banette','Duskull','Dusclops','Tropius','Chimecho','Absol','Wynaut','Snorunt','Glalie','Spheal','Sealeo','Walrein','Clamperl','Huntail','Gorebyss','Relicanth','Luvdisc','Bagon','Shelgon','Salamence','Beldum','Metang','Metagross','Regirock','Regice','Registeel','Latias','Latios','Kyogre','Groudon','Rayquaza','Jirachi','Deoxys','Arceus','Darkrai','Manaphy','Phione','Cresselia','Heatran','Palkia','Dialga','Azelf','Mesprit','Uxie',
'Cobalion', 'Terrakion', 'Virizion', 'Tornadus', 'Thundurus', 'Reshiram', 'Zekrom', 'Landorus', 'Kyurem', 'Victini', 'Giratina', 'Shaymin', 'Regigias',
'Level4','Level5']

raid_bosses = {
    "cobalion": ["fighting", "fire", "ground"],
    "terrakion": ["fairy", "fighting", "grass", "ground", "psychic", "steel", "water"],
    "virizion": ["flyingx2", "fairy", "fire", "flying", "ice", "poison", "psychic"],
    "tornadus": ["electric", "ice", "rock"],
    "thundurus": ["ice", "rock"],
    "reshiram": ["dragon", "ground", "rock"],
    "zekrom": ["dragon", "fairy", "ground", "ice"],
    "landorus": ["icex2", "water"],
    "kyurem": ["dragon", "fairy", "fighting", "rock", "steel"],
    "victini": ["dark", "ghost", "ground", "rock", "water"],
    "giratina": ["dark", "dragon", "fairy", "ghost", "ice"],
    "shaymin": ["fire", "flying", "ice", "poison"],  # shared weaknesses of land and sky versions
    "regigigas": ["fighting"],

    "palkia": ["dragon", "fairy"],
    "rayquaza": ["rock", "icex2", "dragon", "fairy"],
    "jirachi": ["ground", "ghost", "fire", "dark"],
    "deoxys": ["bug", "ghost", "dark"],	

    "mawile": ["ground", "fire"],
    "groudon": ["water", "grass", "ice"],
    "absol": ["fighting", "bug", "fairy"],

    "moltres": ["rockx2", "water", "electric"],
    "zapdos": ["rock", "ice"],
    "articuno": ["rockx2", "steel", "fire", "electric"],
    "mewtwo": ["bug", "dark", "ghost"],
    "mew": ["bug", "dark", "ghost"],

    "raikou": ["ground"],
    "entei": ["ground", "rock", "water"],
    "suicune": ["grass", "electric"],
    "lugia": ["rock", "ghost", "electric", "ice", "dark"],
    "ho-oh": ["rockx2", "water", "electric"],

    "tyranitar": ["fightingx2", "ground", "bug", "steel", "water", "grass", "fairy"],
    "snorlax": ["fighting"],
    "lapras": ["fighting", "rock", "grass", "electric"],
    "rhydon": ["waterx2", "grassx2", "ice", "steel", "ground", "fighting"],
    "blastoise": ["electric", "grass"],
    "charizard": ["rockx2", "water", "electric"],
    "venusaur": ["flying", "fire", "psychic", "ice"],

    "flareon": ["water", "ground", "rock"],
    "jolteon": ["ground"],
    "vaporeon": ["electric", "grass"],
    "gengar": ["ground", "ghost", "psychic", "dark"],
    "machamp": ["flying", "psychic", "fairy"],
    "alakazam": ["bug", "ghost", "dark"],
    "arcanine": ["water", "ground", "rock"],

    "magmar": ["water", "ground", "rock"],
    "electabuzz": ["ground"],
    "weezing": ["ground", "psychic"],
    "exeggutor": ["bugx2", "flying", "poison", "ghost", "fire", "ice", "dark"],
    "muk": ["ground", "psychic"],

    "croconaw": ["electric", "grass"],
    "quilava": ["water", "ground", "rock"],
    "bayleef": ["flying", "poison", "bug", "fire", "ice"],
    "magikarp": ["electric", "grass"],
}