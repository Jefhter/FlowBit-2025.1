from typing import Dict, Union
from .consts import COLOURS, LOG_COLOURS
from .convert import convert_level

class ColourPrinter:
    def __init__(self, colours:Dict[int, str]=COLOURS, log_colours:Dict[int, str]=LOG_COLOURS):
        self.colours = colours
        self.log_levels = log_colours

    def get_colour(self, colour:str=None, level:int=None,):
        if colour:
            return self.colours.get(colour.upper(), '')
        elif level:
            return self.log_levels.get(level, '')
        else:
            return ''

    def print(self, msg:str, level:Union[int, str]=None, colour:str=None) -> None:
        print(self.get_colour(colour, convert_level) + msg + self.colours['RESET'])

    def __call__(self, msg:str, colour:str=None) -> str:
        return self.get_colour(colour=colour) + msg + self.colours['RESET']

colourprinter = ColourPrinter()

