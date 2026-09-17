import math


class Robot:

    def __init__(self, x=400, y=215):

        self.x = x
        self.y = y

        # Direction:
        # 0   = EAST  →
        # 90  = SOUTH ↓
        # 180 = WEST  ←
        # 270 = NORTH ↑
        self.angle = 0

    def move(self, distance):

        radians = math.radians(self.angle)

        self.x += math.cos(radians) * distance
        self.y += math.sin(radians) * distance

    def turn(self, direction):

        if direction == "RIGHT":

            self.angle += 90

        elif direction == "LEFT":

            self.angle -= 90

        self.angle %= 360

    def get_state(self):

        return {"x": round(self.x, 2), "y": round(self.y, 2), "angle": self.angle}
