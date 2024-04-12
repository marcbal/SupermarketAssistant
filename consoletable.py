# Copyright (c) 2024 Marc Baloup
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import enum
import os
from typing import TypeVar, Generic, Any
from collections.abc import Callable

from ansi.colour import fg, fx



class TextAlignment(enum.Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2

    def apply_alignment(self, text: str, width: int):
        if self is TextAlignment.LEFT:
            return text.ljust(width)
        if self is TextAlignment.RIGHT:
            return text.rjust(width)
        if self is TextAlignment.CENTER:
            return text.center(width)
    
    @staticmethod
    def get_default():
        return TextAlignment.LEFT


R = TypeVar('R')

class ColumnDefinition(Generic[R]):

    def __init__(self, header: str, text: Callable[[R], Any], color: Callable[[R], Any] = (lambda _: ""), alignment: TextAlignment = TextAlignment.get_default()):
        self.header = header
        self.text = text
        self.color = color
        self.alignment = alignment


class ConsoleTable:

    @staticmethod
    def print_raw(cellsText: list[list[str]], cellsColor: list[list[str]] = [], cellsAlignments: list[list[TextAlignment]] = []):
        screen_w = os.get_terminal_size().columns

        if cellsText is None or len(cellsText) == 0:
            return
        
        # compute column widths
        widths = []
        for i in range(max([len(r) for r in cellsText])):
            widths.append(max([len(r[i]) if i < len(r) else 0 for r in cellsText]))
        
        # shrink widest columns
        while sum(widths) > screen_w - 2 - 2 * len(widths):
            widths[widths.index(max(widths))] -= 1
        right_pad = screen_w - sum(widths) - 2 * len(widths)
        
        # actually print
        for r in range(len(cellsText)):
            lineCellsText = cellsText[r]
            lineCellsColor = cellsColor[r] if r < len(cellsColor) else []
            lineCellsAlignment = cellsAlignments[r] if r < len(cellsAlignments) else []
            for c in range(len(lineCellsText)):
                text = lineCellsText[c]
                color = lineCellsColor[c] if c < len(lineCellsColor) else ""
                alignment = lineCellsAlignment[c] if c < len(lineCellsAlignment) else TextAlignment.get_default()
                width = widths[c]
                if (len(text) > width):
                    text = text[0:width-3] + f"{fg.gray}..."
                else:
                    text = alignment.apply_alignment(text, width)
                print(f"  {color}{text}{fx.reset}", end="")
            print()

    @staticmethod
    def print_objects(rows: list[R], columns: list[ColumnDefinition[R]]):

        texts: list[list[str]] = []
        colors: list[list[str]] = []
        alignments: list[list[TextAlignment]] = []

        texts.append([c.header for c in columns])
        colors.append([fg.boldblue] * len(columns))
        alignments.append([TextAlignment.LEFT] * len(columns))
        for r in rows:
            rowTexts: list[str] = []
            rowColors: list[str] = []
            rowAlignments: list[TextAlignment] = []
            for c in columns:
                rowTexts.append(str(c.text(r)))
                rowColors.append(str(c.color(r)))
                rowAlignments.append(c.alignment)
            texts.append(rowTexts)
            colors.append(rowColors)
            alignments.append(rowAlignments)

        ConsoleTable.print_raw(texts, colors, alignments)
