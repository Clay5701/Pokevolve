import random

class Pokemon:
    def __init__(self):
        self.level = None
        self.pokemon = None

    def pokemon_sel(self, region, level): 
        trainer_level = level

        base_level_dict = {
            'kantos': 0,
            'johto': 5,
            'hoenn': 5,
            'sinnoh': 10,
            'unova': 10,
            'kalos': 15,
            'aloha': 15,
            'galar': 20,
            'paldea': 20,
            'kitakami': 20,
        }

        base_level = (base_level_dict[region])

        level1 = list_creator(region, 1)
        level2 = list_creator(region, 2)
        level3 = list_creator(region, 3)
        legendary = list_creator(region, 4)

        rand_level1 = random.choice(level1)
        rand_level2 = random.choice(level2)
        rand_level3 = random.choice(level3)
        rand_legendary = random.choice(legendary)

        potential_pokemon = [rand_level1, rand_level2, rand_level3, rand_legendary]

        if trainer_level < base_level + 6:
            weights = [1, 0, 0, 0]
        elif trainer_level < base_level + 12:
            weights = [0.5, 0.47, 0.03, 0]
        else:
            weights = [0.35, 0.5, 0.1, 0.05]

        rand_pokemon = random.choices(potential_pokemon, weights=weights, k=1)[0]

        modifier = random.randint(1, 4)

        if rand_pokemon == rand_level1:
            self.level = 1 + modifier
        elif rand_pokemon == rand_level2:
            self.level = 15 + modifier
        elif rand_pokemon == rand_level3:
            self.level = 30 + modifier
        elif rand_pokemon == rand_legendary:
            self.level = 40 + modifier

        self.pokemon = rand_pokemon

def list_creator(region, level):
    with open(f'./regionpokemon/{region}/{region}{level}.txt', 'r') as file:
        pokemon_list = file.readlines()

    pokemon_list = [line.strip() for line in pokemon_list]

    return pokemon_list