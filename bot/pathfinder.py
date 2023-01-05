from queue import Queue

class PathFinder:
    def find_shortest_path(self, grid, start, end):
        # check if start or end points are invalid
        if not (0 <= start[0] < len(grid) and 0 <= start[1] < len(grid[0]) and grid[start[0]][start[1]] == 1):
            return []
        if not (0 <= end[0] < len(grid) and 0 <= end[1] < len(grid[0]) and grid[end[0]][end[1]] == 2):
            return []

        # initialize a queue to store the points that need to be visited
        q = Queue()
        q.put(start)

        # initialize a 2D array to store the distances from the start point
        distances = [[float('inf') for _ in range(len(grid[0]))] for _ in range(len(grid))]
        distances[start[0]][start[1]] = 0

        # initialize a 2D array to store the predecessor of each point
        predecessors = [[None for _ in range(len(grid[0]))] for _ in range(len(grid))]

        # define the directions in which we can move
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        # perform breadth-first search to find the shortest path
        while not q.empty():
            x, y = q.get()
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < len(grid) and 0 <= new_y < len(grid[0]) and grid[new_x][new_y] != 8 and distances[new_x][new_y] == float('inf'):
                    q.put((new_x, new_y))
                    distances[new_x][new_y] = distances[x][y] + 1
                    predecessors[new_x][new_y] = (x, y)

        # check if the end point is reachable
        if distances[end[0]][end[1]] == float('inf'):
            return []

        # reconstruct the shortest path by following the predecessors from the end point
        path = [end]
        x, y = end
        while predecessors[x][y] != start:
            x, y = predecessors[x][y]
            path.append((x, y))
        path.append(start)

        # return the path in the correct order
        return path[::-1]


def test_find_shortest_path():
    pathfinder = PathFinder()

    # test a simple case with no obstacles
    grid = [[1, 0, 2],
            [0, 0, 0],
            [0, 0, 0]]
    start = (0, 0)
    end = (0, 2)
    path = pathfinder.find_shortest_path(grid, start, end)
    assert len(path) == 3
    print(path)

    # test a case with an obstacle
    grid = [[1, 0, 8, 0, 2],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]]
    start = (0, 0)
    end = (0, 4)
    path = pathfinder.find_shortest_path(grid, start, end)
    assert len(path) == 7
    print(path)

    # test a case where the end point is unreachable
    grid = [[1, 0, 0],
            [0, 8, 0],
            [0, 8, 8]]
    start = (0, 0)
    end = (2, 2)
    path = pathfinder.find_shortest_path(grid, start, end)
    assert len(path) == 0
    print(path)


if __name__ =='__main__':
    # create an instance of the class and call the plot function
    test_find_shortest_path()