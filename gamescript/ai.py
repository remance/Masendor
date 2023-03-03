from time import sleep
import threading
import pygame


class PathfindingAI:
    def __init__(self, battle):
        self.input_list = []
        self.battle = battle

        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while True:
            # Check for commands
            sleep(0.01)  # Limit the logic loop running to every 10ms

            if self.input_list:
                subunit = self.input_list[0]
                move_array = self.battle.map_move_array
                int_base_target = (int(subunit.follow_target[0]), int(subunit.follow_target[1]))
                int_base_pos = (int(subunit.base_pos[0]), int(subunit.base_pos[1]))

                # start point of new smaller array
                start_point = (min((max(0, int_base_pos[0] - 5), max(0, int_base_target[0] - 5))),
                               min((max(0, int_base_pos[1] - 5), max(0, int_base_target[1] - 5))))
                # end point of new array
                end_point = (max((min(999, int_base_pos[0] + 5), min(999, int_base_target[0] + 5))),
                             max((min(999, int_base_pos[1] + 5), min(999, int_base_target[1] + 5))))

                move_array = move_array[start_point[1]: end_point[1]]  # cut 1000x1000 array into smaller one by row
                move_array = [this_array[start_point[0]: end_point[0]] for this_array in move_array]  # cut by column

                grid = subunit.Grid(matrix=move_array)
                grid.cleanup()

                start = grid.node(int_base_pos[0] - start_point[0], int_base_pos[1] - start_point[1])  # start point
                end = grid.node(int_base_target[0] - start_point[0], int_base_target[1] - start_point[1])  # end point

                finder = subunit.AStarFinder(diagonal_movement=subunit.DiagonalMovement.always)
                path, runs = finder.find_path(start, end, grid)
                path = [pygame.Vector2(this_path[0] + start_point[0], this_path[1] + start_point[1]) for this_path in
                        path]  # remake pos into actual map pos

                subunit.move_path = path
                self.input_list = self.input_list[1:]
