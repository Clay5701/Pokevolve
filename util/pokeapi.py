import requests
import random

def get_type(pokemon: str):
    try:
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon.lower()}')

        if response.status_code == 200:
            data = response.json()

            types = [type_data['type']['name'] for type_data in data['types']]
            return types
        else:
            return None

    except requests.RequestException as e:
        print(f'An error with the request occurred: ', e)
        return None
    
def fetch_evolution(pokemon, level):
    if level < 15:
        return None
    elif level == 15:
        evolution_data = evolve_data(pokemon)
        if evolution_data:
            evolution = evolve_pokemon(evolution_data, pokemon)

            if evolution:
                return evolution
            else:
                return None
    elif level < 30:
        return None
    elif level == 30:
        evolution_data = evolve_data(pokemon)
        if evolution_data:
            evolution = evolve_pokemon(evolution_data, pokemon)

            if evolution:
                return evolution
            else:
                return None

def evolve_data(pokemon):
    species_url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon.lower()}"
    species_response = requests.get(species_url)

    if species_response.status_code != 200:
        print(f"Couldn't find information for {pokemon}.")
        return None

    species_data = species_response.json()

    evolution_chain_url = species_data['evolution_chain']['url']

    evolution_response = requests.get(evolution_chain_url)

    if evolution_response.status_code != 200:
        print(f"Couldn't get evolution chain for {pokemon}.")
        return None

    return evolution_response.json()

def evolve_pokemon(evolution_data, current_name):

    def find_next_evolution(chain, current_name):
        if chain['species']['name'] == current_name:
            if chain['evolves_to']:
                next_evolution = random.choice(chain['evolves_to'])
                return next_evolution['species']['name']

        for evolution in chain['evolves_to']:
            next_evolution = find_next_evolution(evolution, current_name)
            if next_evolution:
                return next_evolution
        return None

    return find_next_evolution(evolution_data['chain'], current_name)