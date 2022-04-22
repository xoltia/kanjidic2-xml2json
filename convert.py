import json
import sys

from bs4 import BeautifulSoup

def make_pascal_case(s: str) -> str:
    """
    This function transform a string to PascalCase
    """
    return s.replace('_', ' ').title().replace(' ', '')

def make_camel_case(s: str) -> str:
    """
    This function transform a string to camelCase
    """
    pascal_case_str = make_pascal_case(s)
    return pascal_case_str[0].lower() + pascal_case_str[1:]

def enforce_name_policy(d: dict, policy: str) -> dict:
    """
    This function transform dict keys to match a certain naming standard
    (camelCase, snake_case, etc.)
    """

    # Do nothing by default
    key_creater = lambda x: x

    if policy == 'camel':
        key_creater = make_camel_case
    elif policy == 'pascal':
        key_creater = make_pascal_case

    for key in list(d.keys()):
        new_key = key_creater(key)
        d[new_key] = d.pop(key)

    return d

if len(sys.argv) < 2:
    print('Too few arguments, please specify a file to be converted')
    sys.exit(1)

# Open and parse the file
FILE_NAME = sys.argv[1]
NAME_POLICY = sys.argv[3] if len(sys.argv) > 3 else 'none'

with open(FILE_NAME, encoding='utf8') as f:
    soup = BeautifulSoup(f.read().strip(), 'xml')

# Empty characters array
characters = []

# Iterate over dict items
# TODO: break the code into functions
for character in soup.find_all('character'):
    character_data = {}
    
    #
    # Only add the most important info (for now)
    #

    # Character literal
    character_data['literal'] = character.literal.text

    # Readings and meanings object
    rmgroup_present = True
    try:
        rm = character.reading_meaning.rmgroup
    except AttributeError:
        rmgroup_present = False

    # Readings
    if rmgroup_present:
        character_data['onyomi'] = [
            yomi.text for yomi in rm.find_all('reading') 
                if yomi['r_type'] == 'ja_on'
        ]
        character_data['kunyomi'] = [
            yomi.text for yomi in rm.find_all('reading') 
                if yomi['r_type'] == 'ja_kun'
        ]
        if len(character_data['onyomi']) == 0:
            del character_data['onyomi']
        if len(character_data['kunyomi']) == 0:
            del character_data['kunyomi']

    # Nanori readings
    if character.reading_meaning is not None:
        nanori = character.reading_meaning.find_all('nanori')
        if len(nanori) > 0:
            character_data['nanori'] = [
                yomi.text for yomi in nanori
            ]

    # English meanings
    if rmgroup_present:
        character_data['meanings'] = [
            meaning.text for meaning in rm.find_all('meaning') 
                if not meaning.has_attr('m_lang')
        ]
        if len(character_data['meanings']) == 0:
            del character_data['meanings']

    # JLPT level
    misc_data = character.misc

    if misc_data.jlpt:
        character_data['jlpt'] = int(character.misc.jlpt.text)

    # Grade
    if misc_data.grade:
        character_data['grade_level'] = int(character.misc.grade.text)

    # And finally...
    characters.append(enforce_name_policy(character_data, NAME_POLICY))


# Save to a file
OUTPUT_NAME = sys.argv[2] if len(sys.argv) >= 3 else 'kanjidic2.json'

with open(OUTPUT_NAME, 'w', encoding='utf8') as f:
    json.dump(characters, f, ensure_ascii=False)
