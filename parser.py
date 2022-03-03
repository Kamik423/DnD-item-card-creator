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
from shutil import copy, move, rmtree
from typing import Dict, List

import yaml
from jinja2 import Template

LATEX_TEMPLATE_NAME = os.path.join(os.path.dirname(__file__), "template.tex")
LATEX_TEMPORARY_DIR = os.path.expanduser("~/latextmp")
LATEX_TEMPORARY_TXT = "tmp.tex"


class YAMLKeys:
    """Constant keys in the yaml file."""

    # pylint: disable=too-few-public-methods
    #
    # The point of this class is to store data
    # I'd use a struct if Python had any

    bonus = "bonus"
    item_type = "type"
    time = "time"
    rarity = "rarity"
    description = "description"

    all_keys: List[str] = [bonus, item_type, time, rarity, description]


class Item:
    """Data structure to hold items."""

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    #
    # The point of this class is to store data
    # I'd use a struct if Python had any

    bonus: str = ""
    item_type: str = ""
    time: str = ""
    name: str = ""
    rarity: str = ""
    description: str = ""

    options: Dict[str, any] = {}

    def __init__(self):
        self.options = {}


def load(input_file_name: str) -> List[Dict[str, str]]:
    """Load a YAML coded item file and return it as dictionary structure

    Args:
        input_file_name (str): Name of the file to lad

    Returns:
        List[any]: The YAML coded content of the file
    """
    with open(input_file_name, "r") as input_file:
        input_file_contents = input_file.read()
        return yaml.safe_load(input_file_contents)
    assert False, "Input file does not exist"


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
        if YAMLKeys.bonus in item:
            new_item.bonus = item[YAMLKeys.bonus]
        if YAMLKeys.rarity in item:
            new_item.rarity = item[YAMLKeys.rarity]
        if YAMLKeys.item_type in item:
            new_item.item_type = item[YAMLKeys.item_type]
        if YAMLKeys.time in item:
            new_item.time = item[YAMLKeys.time]
        if YAMLKeys.description in item:
            new_item.description = item[YAMLKeys.description].replace("\n", "\n\n")
        for key in item:
            if key not in YAMLKeys.all_keys:
                new_item.options[key] = item[key]
        return_list.append(new_item)
    return return_list


def generate_source(items: List[Item]):
    """Fill in the Jinja2 LaTeX template with items

    Args:
        items (List[Item]): The Items to be filled in
    """
    os.makedirs(LATEX_TEMPORARY_DIR)
    with open(LATEX_TEMPLATE_NAME, "r") as template_in:
        template = Template(template_in.read())
        temporary_file = "{}/{}".format(LATEX_TEMPORARY_DIR, LATEX_TEMPORARY_TXT)
        rendered_text = template.render(items=items)
        with open(temporary_file, "w") as template_out:
            template_out.write(rendered_text)
            return
        assert False, "Could not write output file"
    assert False, "Template not found"


def build_latex():
    """Builds the LaTeX from source"""
    proc = subprocess.Popen(
        ["pdflatex {}".format(LATEX_TEMPORARY_TXT)],
        cwd=LATEX_TEMPORARY_DIR,
        shell=True,
        stdout=subprocess.PIPE,
    )
    (_, _) = proc.communicate()


def move_pdf(destination: str):
    """Moves the PDF to the desired output location

    Args:
        destination (str): the destination to be moved to
    """
    output_pdf_name = LATEX_TEMPORARY_TXT.rstrip(".tex") + ".pdf"
    move("{}/{}".format(LATEX_TEMPORARY_DIR, output_pdf_name), destination)


def copy_tex(pdf_destination: str):
    """Copys the .tex file next to the PDF. Use for debugging

    Args:
        pdf_destination (str): the destination of the PDF
    """
    tex_destination = pdf_destination.rstrip(".pdf") + ".tex"
    copy("{}/{}".format(LATEX_TEMPORARY_DIR, LATEX_TEMPORARY_TXT), tex_destination)


def cleanup():
    """Deletes the LaTeX temporary directory"""
    if os.path.exists(LATEX_TEMPORARY_DIR):
        rmtree(LATEX_TEMPORARY_DIR)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Parse items list")
    parser.add_argument("input", help="The input file to be parse")
    parser.add_argument("output", help="The output file")
    parser.add_argument(
        "-x", "--tex", help="Copy .tex file to destination", action="store_true"
    )
    args = parser.parse_args()

    file_input: str = args.input
    file_output: str = args.output
    do_copy_tex: bool = args.tex

    items_dict = load(file_input)
    cleanup()
    items = generate_item_objects(items_dict)
    generate_source(items)
    if do_copy_tex:
        copy_tex(file_output)
    build_latex()
    move_pdf(file_output)
    cleanup()


if __name__ == "__main__":
    main()
