from random import randint
from art import tprint


class BoardException(Exception):
    pass


class BoardOut(BoardException):
    def __str__(self):
        return "Клетка за пределами доски"


class DotError(BoardException):
    def __str__(self):
        return "Клетка уже отстреляна"


class ShipError(BoardException):
    pass


class Dot:  # класс точек грового поля
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, dot2):  # сравнение клеток поля
        return self.x == dot2.x and self.y == dot2.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Ship:  # класс коробля
    def __init__(self, lenght, nose, direct):
        self.lenght = lenght
        self.nose = nose
        self.direct = direct
        self.life = lenght

    @property
    def dots(self):  # свойство корабля - его клетки на поле
        ship_dots = []
        for i in range(self.lenght):
            now_x = self.nose.x
            now_y = self.nose.y

            if self.direct == 0:
                now_x += i
            elif self.direct == 1:
                now_y += i

            ship_dots.append(Dot(now_x, now_y))

        return ship_dots

    def shooten(self, shot):  # проверка попадания при выстреле
        return shot in self.dots


class Board:  # игровое поле
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size
        self.sunken_ship = 0
        self.field = [["."] * size for _ in range(size)]
        self.ships = []
        self.busy = []

    def add_ship(self, ship):  # добавление корабля на поле
        for i in ship.dots:
            if self.out(i) or i in self.busy:
                raise ShipError()

        for d in ship.dots:
            self.field[d.x][d.y] = "█"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):  # контур клетки, что бы его помечать
        near = [(-1, -1), (-1, 0), (-1, 1),
                (0, -1), (0, 0), (0, 1),
                (1, -1), (1, 0), (1, 1)]

        for i in ship.dots:
            for i1, i2 in near:
                cur = Dot(i.x + i1, i.y + i2)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "o"
                    self.busy.append(cur)

    def __repr__(self):  # вывод на экран поля
        player_field = ""
        player_field += "  | 1 | 2 | 3 | 4 | 5 | 6 |"

        for i, j in enumerate(self.field):
            player_field += f"\n{i + 1} | " + " | ".join(j) + " |"

        if self.hid:
            player_field = player_field.replace("█", ".")

        return player_field

    def out(self, out_dot):  # проверка, что клетка внутри поля
        return not ((0 <= out_dot.x < self.size) and (0 <= out_dot.y < self.size))

    def shot(self, fire):  # выстрел
        if self.out(fire):
            raise BoardOut

        if fire in self.busy:
            raise DotError

        self.busy.append(fire)
        for ship in self.ships:  # при попадании в корабль
            if ship.shooten(fire):
                ship.life -= 1
                self.field[fire.x][fire.y] = "X"
                if ship.life == 0:
                    self.sunken_ship += 1
                    self.contour(ship, verb=True)
                    print("Убит!")
                    return True
                else:
                    print("Ранен")
                    return True
        self.field[fire.x][fire.y] = "o"  # при промахе
        print("Мимо")
        return False

    def begin(self):  # обнуление занятых клеток после расстановки кораблей, перед игрой.
        self.busy = []


class Player:  # общий класс для игрока и компьютера
    def __init__(self, board, enemy_board):
        self.board = board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError

    def move(self):  # попытка хода
        while True:
            try:
                target = self.ask()
                repeat = self.enemy_board.shot(target)
                return repeat
            except BoardException as cause:
                print(cause)


class AI(Player):  # наследник класса Player с переназначеной для космпьютера функцией запроса выстрела
    def ask(self):
        ai_shot = Dot(randint(0, 5), randint(0, 5))
        print(f"Компьютер бьет по: {ai_shot.x + 1} {ai_shot.y + 1}")
        return ai_shot


class User(Player):  # наследник класса Player с переназначеной для игрока функцией запроса выстрела
    def ask(self):
        while True:
            user_shot = input("Куда будете стрелять? ").split()
            if len(user_shot) != 2:
                print("Введите две координаты! ")
                continue
            x, y = user_shot
            if not (x.isdigit()) or not (y.isdigit()):
                print("Вводите числа! ")
                continue

            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)


class Game:  # основной класс игры
    def __init__(self, size=6):
        self.size = size
        user_board = self.create_board()
        ai_board = self.create_board()
        user_board.hid = False
        ai_board.hid = True
        self.ai = AI(ai_board, user_board)
        self.user = User(user_board, ai_board)

    @staticmethod
    def rules():  # приветствие и правила
        tprint("SEA    BATTLE")
        print("Координаты выстрела вводите через пробел: x y")
        print("          x - номер строки")
        print("          у - номер столбца")

    def generate_board(self):  # генерация случайной доски с кораблями
        ships = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for i in ships:
            while True:
                attempts += 1
                if attempts > 1000:
                    return None

                ship = Ship(i, Dot(randint(0, int(self.size)), randint(0, int(self.size))), randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except ShipError:
                    pass

        board.begin()
        return board

    def create_board(self):  # пересоздание досок, пока не получатся
        board = None
        while board is None:
            board = self.generate_board()
        return board

    def loop(self):  # игровой цикл до победы
        num = 0
        while True:
            print("\nДоска игрока:\n")
            print(self.user.board)
            print("\nДоска компьютера:\n")
            print(self.ai.board)
            if num % 2 == 0:  # смена хода
                print("\nХод игрока!")
                print(f"Потоплено кораблей противника: {self.ai.board.sunken_ship}")
                if self.ai.board.sunken_ship == 7:  # проверка победы после хода
                    print("\nПобеда игрока!")
                    print("ПОЗДРАВЛЯЕМ")
                    break
                repeat = self.user.move()
            else:
                print("\nХод компьютера!")
                print(f"Потоплено ваших кораблей: {self.user.board.sunken_ship}")
                if self.user.board.sunken_ship == 7:  # проверка победы после хода
                    print("\nПобеда компьютера!")
                    print("      :(")
                    break
                repeat = self.ai.move()

            if repeat:
                num -= 1

            num += 1


g = Game()
while True:  # игровой цикл
    g.rules()
    print("\n1 - начать игру ")
    print("2 - выйти из игры ")
    s = int(input("\nВаш выбор: "))
    if s == 1:
        g.loop()
    elif s == 2:
        break
