import json
import sys

from bs4 import BeautifulSoup


if len(sys.argv) < 2:
    print('Too few arguments, please specify a file to be converted')
    sys.exit(1)

# Open and parse the file
FILE_NAME = sys.argv[1]

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
    characters.append(character_data)


# Save to a file
OUTPUT_NAME = sys.argv[2] if len(sys.argv) >= 3 else 'kanjidic2.json'

with open(OUTPUT_NAME, 'w', encoding='utf8') as f:
    json.dump(characters, f, ensure_ascii=False)
