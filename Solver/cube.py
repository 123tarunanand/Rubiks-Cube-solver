import colorama
from colorama import Fore, Back, Style
import sys
import random
import parser

DEFAULT_CONFIG = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5] 
class Color:
    RED = 0
    BLUE = 1
    ORANGE = 2
    GREEN = 3
    WHITE = 4
    YELLOW = 5

class Side(object):
    F = 0
    R = 1
    B = 2
    L = 3
    U = 4
    D = 5

class Face(object):
    def __init__(self, side, color, *attached):
        self.side = side
        self.color = color
        self.attached = list(attached)

class Cube(object):
    def __init__(self, size=3, config = DEFAULT_CONFIG):
        self.size = size
        self.colors = config
        self.faces = {
                Side.F: Face(
                        Side.F, Color.RED,
                        self.bottom_line(Side.U),
                        self.left_column(Side.R),
                        self.top_line(Side.D, True),
                        self.right_column(Side.L, True)
                    ),
                Side.R: Face(
                        Side.R, Color.BLUE,
                        self.right_column(Side.U, True),
                        self.left_column(Side.B),
                        self.right_column(Side.D, True),
                        self.right_column(Side.F, True)
                    ),
                Side.B: Face(
                        Side.B, Color.ORANGE,
                        self.top_line(Side.U),
                        self.left_column(Side.L, True),
                        self.bottom_line(Side.D, True),
                        self.right_column(Side.R)
                    ),
                Side.L: Face(
                        Side.L, Color.GREEN,
                        self.left_column(Side.U),
                        self.left_column(Side.F),
                        self.left_column(Side.D),
                        self.right_column(Side.B, True)
                    ),
                Side.U: Face(
                        Side.U, Color.WHITE,
                        self.top_line(Side.B),
                        self.top_line(Side.R),
                        self.top_line(Side.F),
                        self.top_line(Side.L)
                    ),
                Side.D: Face(
                        Side.D, Color.YELLOW,
                        self.bottom_line(Side.F),
                        self.bottom_line(Side.R),
                        self.bottom_line(Side.B),
                        self.bottom_line(Side.L)
                    )
                }

    def coord(self, side, line, sticker):
        return self.size * (side * self.size + line) + sticker

    def top_line(self, side, invert=False):
        if invert:
            return (self.coord(side, 0, 2), self.coord(side, 0, 1), self.coord(side, 0, 0))
        else:
            return (self.coord(side, 0, 0), self.coord(side, 0, 1), self.coord(side, 0, 2))

    def middle_line(self, side):
        return (self.coord(side, 1, 0), self.coord(side, 1, 1), self.coord(side, 1, 2))

    def bottom_line(self, side, invert=False):
        if invert:
            return (self.coord(side, 2, 2), self.coord(side, 2, 1), self.coord(side, 2, 0))
        else:
            return (self.coord(side, 2, 0), self.coord(side, 2, 1), self.coord(side, 2, 2))

    def right_column(self, side, invert=False):
        if invert:
            return (self.coord(side, 2, 2), self.coord(side, 1, 2), self.coord(side, 0, 2))
        else:
            return (self.coord(side, 0, 2), self.coord(side, 1, 2), self.coord(side, 2, 2))

    def left_column(self, side, invert=False):
        if invert:
            return (self.coord(side, 2, 0), self.coord(side, 1, 0), self.coord(side, 0, 0))
        else:
            return (self.coord(side, 0, 0), self.coord(side, 1, 0), self.coord(side, 2, 0))

    def assign_line(self, src, target, invert=False):
        for i in range(len(src)):
            if invert:
                self.colors[target[i]] = self.colors[src[::-1][i]]
            else:
                self.colors[target[i]] = self.colors[src[i]]

    def assign_line_values(self, values, target_coords):
        for i in range(len(values)):
            self.colors[target_coords[i]] = values[i]

    def get_line(self, line):
        return [self.colors[i] for i in line]

    def make_2d(self, side):
        result = []
        for i in range(self.size):
            result.append([])
            for j in range(self.size):
                result[i].append(self.colors[self.coord(side, i, j)])
        return result

    def turn(self, side):
        f = self.faces[side]
        face_array = self.make_2d(side)

        rotated = list(zip(*face_array[::-1]))
        for i in range(self.size):
            for j in range(self.size):
                self.colors[self.coord(side, i, j)] = rotated[i][j]

        tmp = self.get_line(f.attached[0])
        self.assign_line(f.attached[3], f.attached[0])
        self.assign_line(f.attached[2], f.attached[3])
        self.assign_line(f.attached[1], f.attached[2])
        self.assign_line_values(tmp, f.attached[1])
    
    def turn_back(self, side):
        f = self.faces[side]
        face_array = self.make_2d(side)

        rotated = list(zip(*face_array))[::-1]
        for i in range(self.size):
            for j in range(self.size):
                self.colors[self.coord(side, i, j)] = rotated[i][j]

        tmp = self.get_line(f.attached[0])
        self.assign_line(f.attached[1], f.attached[0])
        self.assign_line(f.attached[2], f.attached[1])
        self.assign_line(f.attached[3], f.attached[2])
        self.assign_line_values(tmp, f.attached[3])

    def turn_double(self, side):
        #TODO: non-lazy (and more optimal) implementation
        self.turn(side)
        self.turn(side)
    
    def cchar(self, c):
        table = {
                    Color.GREEN: Back.GREEN,
                    Color.RED: Back.RED,
                    Color.BLUE: Back.BLUE,
                    Color.ORANGE: Back.MAGENTA,
                    Color.WHITE: Back.WHITE,
                    Color.YELLOW: Back.YELLOW
                }
        return table[c] + "  " + Back.RESET

    def display(self):
        colorama.init(autoreset=True)

        indices = self.top_line(Side.U) + self.middle_line(Side.U) + self.bottom_line(Side.U)
        print("       {}{}{}\n       {}{}{}\n       {}{}{}".format(*[self.cchar(self.colors[c]) for c in indices]))
        print()
        indices = self.top_line(Side.L) + self.top_line(Side.F) + self.top_line(Side.R) + self.top_line(Side.B)
        for c in indices:
            sys.stdout.write(self.cchar(self.colors[c]))
            if indices.index(c) % 3 == 2 and indices.index(c):
                sys.stdout.write(" ")
        print()

        indices = self.middle_line(Side.L) + self.middle_line(Side.F) + self.middle_line(Side.R) + self.middle_line(Side.B)
        for c in indices:
            sys.stdout.write(self.cchar(self.colors[c]))
            if indices.index(c) % 3 == 2 and indices.index(c):
                sys.stdout.write(" ")
        print()

        indices = self.bottom_line(Side.L) + self.bottom_line(Side.F) + self.bottom_line(Side.R) + self.bottom_line(Side.B)
        for c in indices:
            sys.stdout.write(self.cchar(self.colors[c]))
            if indices.index(c) % 3 == 2 and indices.index(c):
                sys.stdout.write(" ")
        print()
        print()
        indices = self.top_line(Side.D) + self.middle_line(Side.D) + self.bottom_line(Side.D)
        print("       {}{}{}\n       {}{}{}\n       {}{}{}".format(*[self.cchar(self.colors[c]) for c in indices]))

        colorama.deinit()

    def execute(self, scramble, reset=False, display=False):
        if reset: self.__init__()
        items = scramble.split(' ')
        for step in items:
            if len(step) == 1:
                side = getattr(Side, step)
                self.turn(side)
            elif len(step) == 2:
                side = getattr(Side, step[0])
                if (step[1] == "'"):
                    self.turn_back(side)
                elif (step[1] == "2"):
                    self.turn_double(side)
                else:
                    raise Exception("Invalid scramble!")
            else:
                raise Exception("Invalid scramble!")

        if display: self.display()

    def reset(self):
        self.__init__()

    def getConfig(self):
        return self.colors
    def setConfig(self, conf):
        self.colors = conf
 
    def scrambler(self,moves):
        items=str(moves)
        items = items.split(' ')
        items.reverse()
        newmoves=''
        for i in items: #reverse
            if i[len(i)-1]!='2':
                if i[len(i)-1]=="'":
                    i=i[:1]
                    print(i)
                else:
                    i=i+"'"
            newmoves=newmoves+' '+i

        newmoves=newmoves[1:]
        
        self.execute(newmoves)

if __name__ == '__main__':
    c = Cube()
    c.scrambler(20)
    c.display()
    w = video.Webcam()
    w.scan()

