# An approximation of python IR/impl for the tictactoe example ???

# Runtime-provided functions:
# BinaryRel type needs a __getitem__, __setitem__, .onchange
import sys
import itertools
from v3 import Entities, Event, BinaryRel, Var, Engine

entities = Entities()
eng = Engine()

Blank = entities.new()
X = entities.new()
O = entities.new()
Mark = set([Blank, X, O])
Side = set([X, O])

event_Win = Event("Win", "side")
event_Turn = Event("Turn", "side")
event_Main = Event("Main")

# Convert "forall" type rules to materialized sets/relations
# Note that materializing ValidCellPos is unneeded as CellValue subsumes it

ValidCellPos = set([
    (0, 0), (0, 1), (0, 2),
    (1, 0), (1, 1), (1, 2),
    (2, 0), (2, 1), (2, 2),
])

CellValue = BinaryRel(
    ((0, 0), Blank),
    ((0, 1), Blank),
    ((0, 2), Blank),
    ((1, 0), Blank),
    ((1, 1), Blank),
    ((1, 2), Blank),
    ((2, 0), Blank),
    ((2, 1), Blank),
    ((2, 2), Blank)
)

# Convert "for-some" type rules to functions

def HorizontalLine(p1, p2, p3):
    return p1[0] == p2[0] and p2[0] == p3[0]

def VerticalLine(p1, p2, p3):
    return p1[1] == p2[1] and p2[1] == p3[1]

def UpDiagonalLine(p1, p2, p3):
    return (
        p2[0] == p1[0] + 1 and p2[1] == p1[1] + 1 and
        p3[0] == p2[0] + 1 and p3[1] == p2[1] + 1
    )

def DownDiagonalLine(p1, p2, p3):
    return (
        p2[0] == p1[0] - 1 and p2[1] == p1[1] - 1 and
        p3[0] == p2[0] - 1 and p3[1] == p2[1] - 1
    )


def Win(side):
    # Very un-optimized, of course.
    # The naive implementation is a self-join / cross-product times 3
    # We can be slightly smarter and use combinations since order doesn't matter, since we return result sets
    for i, j, k in itertools.combinations(ValidCellPos, 3):
        if CellValue[i] == side and CellValue[j] == side and CellValue[k] == side:
            if HorizontalLine(i, j, k) or VerticalLine(i, j, k) or UpDiagonalLine(i, j, k) or DownDiagonalLine(i, j, k):
                return True
    return False


def when_Turn(side):
    move = input("Player {} -- enter x,y: ".format(side))
    _tmp1 = move.strip()
    x, y = _tmp1.split(",")
    x = int(x)
    y = int(y)
    if not (x, y) in ValidCellPos:
        print("Invalid move")
    else:
        CellValue[(x, y)] = side

    if side == X:
        eng.do(event_Turn, O)
    else:
        eng.do(event_Turn, X)

def when_Win(side):
    print("Player {} wins!".format(side))
    sys.exit()

def check_Win():
    for side in Side:
        if Win(side):
            eng.do(event_Win, side)

def when_Main():
    eng.do(event_Turn, X)

CellValue.onchange(check_Win)

eng.handle(event_Win, when_Win)
eng.handle(event_Turn, when_Turn)
eng.handle(event_Main, when_Main)

if __name__ == "__main__":
    eng.do(event_Main)
