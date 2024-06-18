import math
import random
import copy
import os
import time
import json


class SudokuSolver:
    def __init__(self, grid):
        self.grid = grid
        self.count_prints = 0
        self.count_iterations = 0

    def print_grid(self):
        self.count_prints += 1
        clear_screen()
        for row in self.grid:
            print(row)
        time.sleep(0.1)

    def print_solved_grid(self):
        if self.solve_sudoku():
            for row in self.grid:
                print(row)
        else:
            print("No solution found for the Sudoku puzzle.")

    def is_valid(self, row, col, num):
        # Check if the number is already in the row
        if num in self.grid[row]:
            return False

        # Check if the number is already in the column
        for i in range(len(self.grid)):
            if col < len(self.grid[i]) and self.grid[i][col] == num:
                return False

        # Check if the number is already in the 3x3 subgrid
        box_size = int(len(self.grid) ** 0.5)
        start_row, start_col = box_size * (row // box_size), box_size * (col // box_size)
        for i in range(start_row, start_row + box_size):
            for j in range(start_col, start_col + box_size):
                if self.grid[i][j] == num:
                    return False

        return True

    def find_empty_location(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j] == 0:
                    return i, j
        return None

    def solve_sudoku(self):
        empty_loc = self.find_empty_location()

        if not empty_loc:
            return True  # No empty location means Sudoku is solved

        row, col = empty_loc

        for num in range(1, len(self.grid) + 1):
            if self.is_valid(row, col, num):
                self.grid[row][col] = num
                self.count_iterations += 1
                # self.print_grid()
                # print()  # Print an empty line for better visualization

                if self.solve_sudoku():
                    return True  # If recursion returns True, puzzle is solved

                self.grid[row][col] = 0  # Backtrack if solution is not found

        return False  # If no number fits, backtrack

    def shuffle_numbers(self, num_swaps=100):
        for _ in range(num_swaps):
            num1, num2 = random.sample(range(1, len(self.grid) + 1), 2)
            for i in range(len(self.grid)):
                for j in range(len(self.grid[0])):
                    if self.grid[i][j] == num1:
                        self.grid[i][j] = num2
                    elif self.grid[i][j] == num2:
                        self.grid[i][j] = num1

    def evaluate(self):
        score = 0
        for row in self.grid:
            score += len(set(row)) - row.count(0)
        for col in range(len(self.grid[0])):
            col_values = [self.grid[row][col] for row in range(len(self.grid))]
            score += len(set(col_values)) - col_values.count(0)
        box_size = int(len(self.grid) ** 0.25)
        for i in range(0, len(self.grid), box_size):
            for j in range(0, len(self.grid[0]), box_size):
                box_values = [self.grid[r][c] for r in range(i, i + box_size) for c in range(j, j + box_size)]
                score += len(set(box_values)) - box_values.count(0)
        return score

    def crossover(self, parent1, parent2):
        # Select random crossover point
        crossover_point = random.randint(0, len(self.grid) - 1)

        # Create child grid by combining parent grids
        child_grid = []
        for i in range(len(self.grid)):
            if i <= crossover_point:
                child_grid.append(parent1[i])
            else:
                child_grid.append(parent2[i])
        return child_grid

    def mutate(self, grid):
        # Select random row and column
        row, col = random.randint(0, len(self.grid) - 1), random.randint(0, len(self.grid[0]) - 1)

        # Generate random number for mutation
        new_num = random.randint(1, len(self.grid))

        # Mutate the grid
        grid[row][col] = new_num
        return grid

    def genetic_algorithm(self, population_size=100, max_generations=1000, mutation_rate=0.1):
        population = [copy.deepcopy(self.grid) for _ in range(population_size)]

        for _ in range(max_generations):
            # Evaluate fitness of each individual in population
            fitness_scores = [(self.evaluate_grid(grid), grid) for grid in population]
            fitness_scores.sort(reverse=True)

            # If we found a solution, return it
            if fitness_scores[0][0] == len(self.grid) * (
                    len(self.grid) + 1) / 2:  # Maximum possible score for a solved Sudoku
                self.grid = fitness_scores[0][1]
                return

            # Select top individuals for crossover
            top_individuals = [individual[1] for individual in fitness_scores[:10]]

            # Create next generation through crossover and mutation
            new_population = []
            for _ in range(population_size):
                parent1, parent2 = random.sample(top_individuals, 2)
                child = self.crossover(parent1, parent2)
                if random.random() < mutation_rate:
                    child = self.mutate(child)
                new_population.append(child)

            population = new_population

        # If no solution found, select the best grid from the final population
        self.grid = fitness_scores[0][1]

    def evaluate_grid(self, grid):
        score = 0
        for row in grid:
            score += len(set(row)) - row.count(0)
        for col in range(len(grid[0])):
            col_values = [grid[row][col] for row in range(len(grid))]
            score += len(set(col_values)) - col_values.count(0)
        box_size = int(len(grid) ** 0.25)
        for i in range(0, len(grid), box_size):
            for j in range(0, len(grid[0]), box_size):
                box_values = [grid[r][c] for r in range(i, i + box_size) for c in range(j, j + box_size)]
                score += len(set(box_values)) - box_values.count(0)
        return score


def clear_screen():
    if os.name == 'nt':  # for Windows
        os.system('cls')


def read_sudoku_grid(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    sudoku_grid = []
    row = 1
    while str(row) in data:
        row_values = [int(num) if num != "0" else 0 for num in data[str(row)]]
        sudoku_grid.append(row_values)
        row += 1

    return sudoku_grid


if __name__ == "__main__":
    clear_screen()

    sudoku_grid = read_sudoku_grid('sudoku1.json')

    # Convert the 2D array into JSON format
    json_data = json.dumps(sudoku_grid)

    size = len(sudoku_grid)
    start = time.time()
    solver = SudokuSolver(sudoku_grid)

    print("Initial Sudoku Grid:")
    for i in range(0, len(sudoku_grid)):
        print(f'{sudoku_grid[i]}')

    solver.solve_sudoku()  # Apply backtracking algorithm
    print("\nSolved Sudoku Grid:")
    # solver.print_grid()
    solver.print_solved_grid()
    end = time.time()

    print(
        f'Sudoku grid of {size}x{size} has been solved in {round((end - start) - (0.2 * solver.count_prints), 2)} seconds \n')
    print(f'Number of iterations: {solver.count_iterations}')
