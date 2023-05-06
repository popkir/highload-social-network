import random

vowels = [97,101,105,111,117]
consonants = [98,99,100,102,103,104,106,107,108,109,110,112,113,114,115,116,118,119,120,121,122]

def get_character(seed):
    if seed == 'L':
        return chr(random.randint(97,122))
    elif seed == 'C':
        return chr(consonants[random.randint(0,len(consonants)-1)])
    elif seed == 'V':
        return chr(vowels[random.randint(0,len(vowels)-1)])
    else:
        return -1

def get_pseudonym(length=None, template=None):
    # enter custom values here: C for consonants, V for vowels, and L for all letters
    if template is None:
        if length is None:
            length = random.randint(5, 7)
        template = 'CVC' * (length // 3) + 'L' * (length % 3)
    
    pseudonym = ''
    for character_type in template:
        pseudonym += get_character(character_type)
    return pseudonym
