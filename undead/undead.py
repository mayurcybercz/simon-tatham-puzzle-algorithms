import math

puzzle = "4x4:2,3,7:aRLLLaReLc:2,4,3,5,2,3,1,3,1,3,1,2,3,2,0,3"
puzzle2 = "4x4:7,3,2:aLeLLbRd:4,1,1,1,2,0,1,1,0,1,4,0,1,1,5,1"


def get_value_of_character(c):
    return ord(c.lower())-96


def check_mirror_correctness(mirrors, boxes):
    total = 0
    for c in  mirrors:
        if c not in ['L', 'R']:
            total += get_value_of_character(c)
        else:
            total += 1
    return total == boxes


class Game:

    class Tile:
        def __init__(self, obj=None, orient=None):
            self.obj = obj
            self.orient = None

        def set_obj(self, obj):
            self.obj = obj
            return True

        def get_obj(self):
            return self.obj

        def is_mirror(self):
            return self.obj == 'mirror'

        def set_orient(self, orient):
            self.orient = orient
            return True

        def get_orientation(self):
            if self.is_mirror():
                return self.orient

        def add_object(self, obj, orient=None):
            self.obj = obj
            self.orient = orient
            return True

        def __str__(self):
            if self.get_obj() is None:
                s = 'Empty'
            else:
                s = self.get_obj()
            if self.get_orientation() is not None:
                s = s + ': ' + self.get_orientation()
            return s

    def initialize_tiles(self, tiles, mirrors):
        for tile in tiles:
            mirror = mirrors.pop(0)
            if mirror is not None:
                tile.add_object('mirror', mirror)
        return tiles

    def __init__(self, size, undeads, mirrors, visibles):
        '''
        initialize the game
        :param size: a perfect square integer, denoting number of squares
        :param undeads: a dictionary of the structure
                        { 'ghosts': count, 'vampires': count, 'zombies': count }
        :param mirrors: a list of length size containing mirrors at location it belong
                        example for a 2*2 game a valid mirrors is
                        ['L', None, None, 'R']
        :param visibles: a list of length sqrt(size)*4 denoting how many creatures are visible
                         example for a 2*2 game a valid visibles is
                         [1, 1, 2, 0, 0, 1, 1, 1]
        '''
        tiles = []
        for _ in range(size):
            tiles.append(self.Tile())
        self.tiles = self.initialize_tiles(tiles,  mirrors)
        self.zombies = undeads['zombies']
        self.vampires = undeads['vampires']
        self.ghosts = undeads['ghosts']
        self.views = visibles
        self.size = size
        self.mirror_occurrence = False

    def adjust_direction(self, direction, mirror):

        if mirror == 'L':
            if direction == 'right':
                return 'down'
            elif direction == 'left':
                return 'up'
            elif direction == 'up':
                return 'left'
            else:
                return 'right'
        else:
            if direction == 'right':
                return 'up'
            elif direction == 'left':
                return 'down'
            elif direction == 'up':
                return 'right'
            else:
                return 'left'

    def get_initial_direction(self, initial):
        initial += 1
        size = int(math.sqrt(self.size))
        if initial <= size:
            new_initial = initial - 1
            new_direction = 'down'
            if self.tiles[new_initial].get_obj() == 'mirror':
                new_direction = self.adjust_direction(new_direction, self.tiles[new_initial].get_orientation())
                self.mirror_occurrence = True
            return new_initial, new_direction
        elif initial <= 2*size:
            temp = initial - size
            new_initial = size*temp - 1
            new_direction = 'left'
            if self.tiles[new_initial].get_obj() == 'mirror':
                new_direction = self.adjust_direction(new_direction, self.tiles[new_initial].get_orientation())
                self.mirror_occurrence = True
            return new_initial, new_direction
        elif initial <= 3*size:
            temp = initial - 2 * size
            new_initial = (size**2) - temp
            new_direction = 'up'
            if self.tiles[new_initial].get_obj() == 'mirror':
                new_direction = self.adjust_direction(new_direction, self.tiles[new_initial].get_orientation())
                self.mirror_occurrence = True
            return new_initial, new_direction
        else:
            temp = initial - 3 * size
            new_initial = size * (size-temp)
            new_direction = 'right'
            if self.tiles[new_initial].get_obj() == 'mirror':
                new_direction = self.adjust_direction(new_direction, self.tiles[new_initial].get_orientation())
                self.mirror_occurrence = True
            return new_initial, new_direction

    def next_tile_helper(self, current_tile, direction):
        size = int(math.sqrt(self.size))
        if direction == 'left':
            if current_tile % size == 0:
                return None, None
            new_tile = current_tile-1
            if self.tiles[new_tile].get_obj() == 'mirror':
                if self.tiles[new_tile].get_orientation() == 'L':
                    return new_tile, 'up'
                else:
                    return new_tile, 'down'
            return new_tile, 'left'

        elif direction == 'right':
            if current_tile%size == size-1:
                return None, None
            new_tile = current_tile + 1
            if self.tiles[new_tile].get_obj() == 'mirror':
                if self.tiles[new_tile].get_orientation() == 'L':
                    return new_tile, 'down'
                else:
                    return new_tile, 'up'
            return new_tile, 'right'

        elif direction == 'up':
            if current_tile < size:
                return None, None
            new_tile = current_tile - size
            if self.tiles[new_tile].get_obj() == 'mirror':
                if self.tiles[new_tile].get_orientation() == 'L':
                    return new_tile, 'left'
                else:
                    return new_tile, 'right'
            return new_tile, 'up'

        else:
            if current_tile >= size*(size-1):
                return None, None
            new_tile = current_tile + size
            if self.tiles[new_tile].get_obj() == 'mirror':
                if self.tiles[new_tile].get_orientation() == 'L':
                    return new_tile, 'right'
                else:
                    return new_tile, 'left'
            return new_tile, 'down'

    def get_next_tile(self, current_tile, direction, start=None):
        if start is not None:
            tile_id, new_direction = self.get_initial_direction(start)
            return tile_id, new_direction
        next_tile, new_direction = self.next_tile_helper(current_tile, direction)
        # print(next_tile, new_direction)
        if next_tile is None:
            return next_tile, new_direction
        while self.tiles[next_tile].get_obj() == 'mirror':
            # print('next tile is ', next_tile)
            self.mirror_occurrence = True
            # print('next tile: ', next_tile, ' ', new_direction, ' ', current_tile)
            next_tile, new_direction = self.next_tile_helper(next_tile, new_direction)
            if next_tile is None:
                break

        return next_tile, new_direction

    def get_path(self, start):
        self.mirror_occurrence = False
        path = []
        next_tile, new_direction = self.get_next_tile(current_tile=None, direction='', start=start)
        if next_tile is None:
            return path
        path.append((next_tile, self.mirror_occurrence))
        while next_tile is not None:
            # print('get path')
            next_tile, new_direction = self.get_next_tile(current_tile=next_tile, direction=new_direction)
            path.append((next_tile, self.mirror_occurrence))
        return path
        # this will give return all the tiles that will be encountered while on that path


    def update_views(self):
        for i, view in enumerate(self.views):
            path = self.get_path(i)


    def __str__(self):
        d = ''
        for tile in self.tiles:
            d = d + tile.__str__() + ', '
        return d


def extract_puzzle(puzzle):
    datas = puzzle.split(":")
    if len(datas) != 4:
        message = "Puzzle input format not good. Proper format is mxm:G,V,Z:aRLLLaReLc:4030021203100131"
        raise Exception(message)
    if datas[0][0] != datas[0][2]:
        message = "Puzzle input format not good. Grid should be a square of shape mxm. Eg. 4x4"
        raise Exception(message)
    if not check_mirror_correctness(datas[2], int(datas[0][0])*int(datas[0][2])):
        message = "Puzzle input format not good. Mirrors + empty boxes != total boxes"
        raise Exception(message)
    size = int(datas[0][0])
    size = size*size
    undeads = {
        'ghosts': int(datas[1].split(",")[0]),
        'vampires': int(datas[1].split(",")[1]),
        'zombies': int(datas[1].split(",")[2])
    }
    mirrors = []

    for c in datas[2]:
        if c not in ['L', 'R']:
            times = get_value_of_character(c)
            mirrors.extend([None]*times)
        else:
            mirrors.append(c)
    # print('mirrors is: ', mirrors)
    visibles = list(map(int, datas[3].split(',')))
    game =  Game(size, undeads, mirrors, visibles)
    return game

# extract_puzzle(puzzle)

# solve puzzle steps
def solve(game):
    # pass
    # step 1 should be target all the views which have zero undeads. because it has only one option
    #        that whether it can be a vampire or a ghost based on the location of mirror
    # step 2 should be we should update all the views and see which new views have become zero
    #        so that we can target them. repeat step 2 until there is no new occurrence of zero in views
    # step 3 should be a sweeping step, means here we see how many ghosts, vampires and zombies are remaining
    #        and see if they can be fitted anywhere in the place. Example: 1 zombie is remaining and only 1 tile
    #        so we put the zombie there.
    # lets see how much of the puzzle is solved using this.

    views = game.views
    zero_indices = [i for i, val in enumerate(views) if val == 0]

    # step 1
    step_1 = True
    # while step_1:
    for index in zero_indices:
        path = game.get_path(index)
        for tile_index in path:
            if tile_index[0] is not None and game.tiles[tile_index[0]].get_obj() != 'mirror':
                # continue
                if tile_index[1]:
                    game.tiles[tile_index[0]].set_obj("vampire")
                else:
                    game.tiles[tile_index[0]].set_obj("ghost")
        print(game)
    game.update_views()
    # print(game)

    # step_2 = True
    # while step_2:
    #     pass
    #
    # step_3 = True
    # while step_3:
    #     pass

    print(game)

game = extract_puzzle(puzzle2)
# print(game)
print(game.get_path(8))
solve(game)
