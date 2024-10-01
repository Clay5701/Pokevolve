import sqlite3
import math

def add_pokemon(guild_id, user_id, region, pokemon, level):
    xp = 0
    pokemon_id = id_gen(guild_id, user_id, region)

    if pokemon_id is None:
        return 0
    
    connection = sqlite3.connect('./util/pokemon.db')
    cursor = connection.cursor()

    level_up_xp = (2 * level ** 2 + 7 * level + 15) - (2 * (level-1) ** 2 + 7 * (level-1) + 15)

    cursor.execute('INSERT INTO Caught (guild_id, user_id, region, pokemon, xp, level_up_xp, level, pokemon_id) VALUES (?,?,?,?,?,?,?,?)', (guild_id, user_id, region, pokemon, xp, level_up_xp, level, pokemon_id))

    connection.commit()
    connection.close()

    return 1

def id_gen(guild_id, user_id, region):
    connection = sqlite3.connect('./util/pokemon.db')
    cursor = connection.cursor()

    cursor.execute('SELECT pokemon_id FROM Caught WHERE guild_id = ? AND user_id = ? AND region = ? ORDER BY pokemon_id', (guild_id, user_id, region))

    id_data = cursor.fetchall()

    match region:
        case 'kantos':
            region_mod = 1000
        case 'johto':
            region_mod = 2000
        case 'hoenn':
            region_mod = 3000
        case 'sinnoh':
            region_mod = 4000
        case 'unova':
            region_mod = 5000

    if id_data == []:
        tag = 1

    most_recent = 0

    for i in range(0, len(id_data)):
        temp_id = id_data[i][0] - region_mod
        if temp_id == i + 1:
            most_recent = temp_id
            continue
        else:
            break

    tag = most_recent + 1

    if tag == 1000:
        return None

    pokemon_id = region_mod + tag

    connection.close()

    return pokemon_id

def poke_fetch(guild_id, user_id, region=None, level=None, pokemon=None, id=None):
    connection = sqlite3.connect('./util/pokemon.db')
    cursor = connection.cursor()

    conditions = []
    parameters = [guild_id, user_id]

    if region is not None:
        conditions.append('region = ?')
        parameters.append(region)

    if pokemon is not None:
        conditions.append('pokemon = ?')
        parameters.append(pokemon)

    if level is not None:
        conditions.append('level = ?')
        parameters.append(level)

    if id is not None:
        conditions.append('pokemon_id = ?')
        parameters.append(id)

    query = 'SELECT * FROM Caught WHERE guild_id = ? AND user_id = ?'

    if conditions:
        query += ' AND ' + ' AND '.join(conditions)

    cursor.execute(query, parameters)
    results = cursor.fetchall()

    connection.close()

    return results

def release_pokemon(guild_id, user_id, id):
    connection = sqlite3.connect('./util/pokemon.db')
    cursor = connection.cursor()

    cursor.execute('DELETE FROM Caught WHERE guild_id = ? AND user_id = ? AND pokemon_id = ?', (guild_id, user_id, id))

    connection.commit()
    connection.close()

def set_companion(guild_id, user_id, id):
    connection = sqlite3.connect('./util/pokemon.db')
    cursor = connection.cursor()

    cursor.execute('UPDATE Users SET companion_id = ? WHERE guild_id = ? AND user_id = ?', (id, guild_id, user_id))
    
    connection.commit()
    connection.close()

def fetch_companion(guild_id, user_id):
    connection = sqlite3.connect('./util/pokemon.db')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Users WHERE guild_id = ? AND user_id = ?', (guild_id, user_id))

    results = cursor.fetchone()

    if results is None:
        return None
    
    companion_id = results[2]

    poke_data = poke_fetch(guild_id, user_id, id=companion_id)

    connection.close()

    return poke_data

def create_trainer(guild_id, user_id):
    companion_id = 0
    trainer_level = 1
    trainer_xp = 0
    level_up_xp = 100
    region = 'kantos'

    parameters = [guild_id, user_id, companion_id, trainer_level, trainer_xp, level_up_xp, region]

    connection = sqlite3.connect('./util/pokemon.db')
    cursor = connection.cursor()

    cursor.execute('INSERT INTO Users (guild_id, user_id, companion_id, trainer_level, trainer_xp, level_up_xp, region) VALUES (?,?,?,?,?,?,?)', parameters)

    connection.commit()
    connection.close()

def push_update(guild_id, user_id, id, pokemon=None, xp=None, level_up_xp=None, level=None):
    connection = sqlite3.connect('./util/pokemon.db')
    cursor = connection.cursor()

    conditions = []
    parameters = []

    if pokemon is not None:
        conditions.append('pokemon = ?')
        parameters.append(pokemon)

    if xp is not None:
        conditions.append('xp = ?')
        parameters.append(xp)

    if level_up_xp is not None:
        conditions.append('level_up_xp = ?')
        parameters.append(level_up_xp)

    if level is not None:
        conditions.append('level = ?')
        parameters.append(level)

    parameters += [guild_id, user_id, id]

    query = 'UPDATE Caught SET ' + ', '.join(conditions) + ' WHERE guild_id = ? AND user_id = ? AND pokemon_id = ?'

    cursor.execute(query, parameters)
    connection.commit()
    connection.close()

def push_channel(guild_id, channel):
    connection = sqlite3.connect('./util/pokemon.db')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Servers WHERE guild_id = ?', (guild_id,))

    result = cursor.fetchone()

    if result is None:
        cursor.execute('INSERT INTO Servers (guild_id, bot_channel) VALUES (?,?)', (guild_id, channel))

    else:
        cursor.execute('UPDATE Servers SET bot_channel = ? WHERE guild_id = ?', (channel, guild_id))
    
    connection.commit()
    connection.close()

def get_channel(guild_id):
    connection = sqlite3.connect('./util/pokemon.db')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Servers WHERE guild_id = ?', (guild_id,))

    result = cursor.fetchone()

    connection.close()

    if result is None:
        return None
    else:
        return result[1]
    

def reset_channel(guild_id):
    connection = sqlite3.connect('./util/pokemon.db')
    cursor = connection.cursor()

    cursor.execute('DELETE FROM Servers WHERE guild_id = ?', (guild_id,))

    connection.commit()
    connection.close()

def trainerxp_add(guild_id, user_id, amount):
    connection = sqlite3.connect('./util/pokemon.db')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Users WHERE guild_id = ? AND user_id = ?', (guild_id, user_id))

    result = cursor.fetchone()

    trainer_level = result[3]
    current_xp = result[4]
    level_up_xp = result[5]
    flag = 0

    new_xp = current_xp + amount

    if new_xp >= level_up_xp:
        trainer_level += 1
        new_xp = new_xp - level_up_xp
        level_up_xp = math.ceil(0.5 * trainer_level ** 2 + 75 * trainer_level + 15)

        cursor.execute('UPDATE Users SET trainer_level = ?, trainer_xp = ?, level_up_xp = ? WHERE guild_id = ? AND user_id = ?', (trainer_level, new_xp, level_up_xp, guild_id, user_id))
        flag = 1

    cursor.execute('UPDATE Users SET trainer_xp = ? WHERE guild_id = ? AND user_id = ?', (new_xp, guild_id, user_id))

    connection.commit()
    connection.close()

    return flag

def fetch_trainer(guild_id, user_id):
    connection = sqlite3.connect('./util/pokemon.db')
    cursor = connection.cursor()
    
    cursor.execute('SELECT * FROM Users WHERE guild_id = ? AND user_id = ?', (guild_id, user_id))

    result = cursor.fetchone()

    connection.close()

    return result

def push_region(guild_id, user_id, new_region):
    connection = sqlite3.connect('./util/pokemon.db')
    cursor = connection.cursor()

    cursor.execute('UPDATE Users SET region = ? WHERE guild_id = ? AND user_id = ?', (new_region, guild_id, user_id))

    connection.commit()
    connection.close()