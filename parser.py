#!/usr/bin/env python3
"""Parse D&D Item file

Attributes:
    LATEX_TEMPLATE_NAME (str): Name of the LaTeX Template file
    LATEX_TEMPORARY_DIR (str): Temporary directory for buildig LaTeX
    LATEX_TEMPORARY_TXT (str): Filename of the temporary file


The input file hast to be in YAML and have the format demonstrated below.
The order of those arguments is irrelevant. Some, but not all, are optional,
in case they do not make any sense: Most swords for example don't benefit the
Armor Class.

(For example)

Toothpick of great Power:
  attack bonus:         +5
  rarity:               vary rare
  type:                 Toothpick
  AC bonus:             +42
  DC:                   Animal handling 15/ Arcana 3
  advantages:           Wisdom SS
  time:                 Once per day
  description:          |
                        What it says on the box:
                        Just your everyday magical toothpick.
                        It helps you out with all things.
Other Item:
  ...
"""

import argparse
import os
import subprocess

from shutil import move, rmtree
from typing import Dict, List

from jinja2 import Template
import yaml


LATEX_TEMPLATE_NAME = os.path.join(os.path.dirname(__file__), 'template.tex')
LATEX_TEMPORARY_DIR = os.path.expanduser('~/latextmp')
LATEX_TEMPORARY_TXT = 'tmp.tex'


class Item:
    """Data structure to hold items.
    """

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    #
    # The point of this class is to store data
    # I'd use a struct if Python had any

    armor_class: str = ''
    attack_bonus: str = ''
    difficulty_class: str = ''
    advantages: str = ''
    item_type: str = ''

    time: str = ''
    name: str = ''
    rarity: str = ''
    description: str = ''


def load(input_file_name: str) -> List[Dict[str, str]]:
    """Load a YAML coded item file and return it as dictionary structure

    Args:
        input_file_name (str): Name of the file to lad

    Returns:
        List[any]: The YAML coded content of the file
    """
    with open(input_file_name, 'r') as input_file:
        input_file_contents = input_file.read()
        return yaml.load(input_file_contents)
    assert False, 'Input file does not exist'


def generate_item_objects(dictionary: List[Dict[str, str]]) -> List[Item]:
    """Create Item objects from the dictonary structure

    Args:
        dictionary (List[Dict[str, str]]): The dictionary to be converted

    Returns:
        List[Item]: The list of Items
    """

    return_list = []
    for item_title in dictionary:
        item = dictionary[item_title]
        new_item = Item()
        new_item.name = item_title
        if 'attack bonus' in item:
            attack_bonus = item['attack bonus']
            if isinstance(attack_bonus, int) and attack_bonus >= 0:
                attack_bonus = '+{}'.format(attack_bonus)
            new_item.attack_bonus = attack_bonus
        if 'rarity' in item:
            new_item.rarity = item['rarity']
        if 'type' in item:
            new_item.item_type = item['type']
        if 'AC' in item:
            new_item.armor_class = item['AC']
        if 'DC' in item:
            new_item.difficulty_class = item['DC'].replace('/', '\\newline')
        if 'advantages' in item:
            new_item.advantages = item['advantages']
        if 'description' in item:
            new_item.description = item['description'].replace('\n', '\n\n')
        if 'time' in item:
            new_item.time = item['time']
        return_list.append(new_item)
    return return_list


def generate_source(items: List[Item]):
    """Fill in the Jinja2 LaTeX template with items

    Args:
        items (List[Item]): The Items to be filled in
    """
    os.makedirs(LATEX_TEMPORARY_DIR)
    with open(LATEX_TEMPLATE_NAME, 'r') as template_in:
        template = Template(template_in.read())
        temporary_file = '{}/{}'.format(
            LATEX_TEMPORARY_DIR,
            LATEX_TEMPORARY_TXT)
        rendered_text = template.render(items=items)
        with open(temporary_file, 'w') as template_out:
            template_out.write(rendered_text)
            return
        assert False, 'Could not write output file'
    assert False, 'Template not found'


def build_latex():
    """Builds the LaTeX from source
    """
    proc = subprocess.Popen(['pdflatex {}'.format(
        LATEX_TEMPORARY_TXT)], cwd=LATEX_TEMPORARY_DIR, shell=True, stdout=subprocess.PIPE)
    (_, _) = proc.communicate()


def move_pdf(destination: str):
    """Moves the PDF to the desired output location

    Args:
        destination (str): the destination to be moved to
    """
    output_pdf_name = LATEX_TEMPORARY_TXT.rstrip('.tex') + '.pdf'
    move('{}/{}'.format(
        LATEX_TEMPORARY_DIR,
        output_pdf_name),
         destination
        )


def cleanup():
    """Deletes the LaTeX temporary directory
    """
    if os.path.exists(LATEX_TEMPORARY_DIR):
        rmtree(LATEX_TEMPORARY_DIR)


def main():
    """Main function
    """
    parser = argparse.ArgumentParser(description='Parse items list')
    parser.add_argument('input', help='The input file to be parse')
    parser.add_argument('output', help='The output file')
    args = parser.parse_args()
    file_input = args.input
    file_output = args.output
    items_dict = load(file_input)
    cleanup()
    items = generate_item_objects(items_dict)
    generate_source(items)
    build_latex()
    move_pdf(file_output)
    cleanup()

if __name__ == '__main__':
    main()
