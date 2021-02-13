from typing import List, Dict, Tuple
from dataclasses import dataclass
import re
from .commands import Commands


@dataclass
class GcodeLine:
    command: Tuple[str, int]
    params: Dict[str, float]
    comment: str

    def __post_init__(self):
        if self.command[0] == 'G' and self.command[1] in (0, 1, 2, 3):
            self.type = Commands.MOVE
        elif self.command[0] == ';':
            self.type = Commands.COMMENT
        elif self.command[0] == 'T':
            self.type = Commands.TOOLCHANGE
        else:
            self.type = Commands.OTHER

    def get_param(self, param: str, return_type=None, default=None):
        """
        Returns the value of the param if it exists, otherwise it will the default value.
        If `return_type` is set, the return value will be type cast.
        """
        try:
            if return_type is None:
                return self.params[param]
            else:
                return return_type(self.params[param])
        except KeyError:
            return default

    def to_gcode(self):
        command = f"{self.command[0]}{self.command[1]}"
        params = " ".join(f"{param}{self.get_param(param)}" for param in self.params.keys())
        comment = f"; {self.comment}" if self.comment != '' else ""
        return f"{command} {params} {comment}".strip()


class GcodeParser:
    def __init__(self, gcode: str, include_comments=False):
        self.gcode = gcode
        self.lines: List[GcodeLine] = get_lines(self.gcode, include_comments)
        self.include_comments = include_comments


def get_lines(gcode, include_comments=False):
    regex = r'(?!; *.+)(G|M|T|g|m|t)(\d+)(( *(?!G|M|g|m)\w-?\d+\.?\d*)*) *\t*(; *(.*))?|; *(.+)'
    regex_lines = re.findall(regex, gcode)
    lines = []
    for line in regex_lines:
        if line[0]:
            command = (line[0].upper(), int(line[1]))
            comment = line[5]
            params = split_params(line[2])

        elif include_comments:
            command = (';', None)
            comment = line[6]
            params = {}

        else:
            continue

        lines.append(
            GcodeLine(
                command=command,
                params=params,
                comment=comment,
            ))

    return lines


def is_float(num: str):
    if re.search(r'[+-]?\d+.\d+', num):
        return True
    return False


def split_params(line):
    regex = r'((?!\d)\w+?)(-?\d+\.?\d*)'
    elements = re.findall(regex, line)
    params = {}
    for element in elements:
        element_type = float if is_float(element[1]) else int
        params[element[0].upper()] = element_type(element[1])

    return params


if __name__ == '__main__':
    with open('3DBenchy.gcode', 'r') as f:
        gcode = f.read()
    parsed_gcode = GcodeParser(gcode)
    pass
