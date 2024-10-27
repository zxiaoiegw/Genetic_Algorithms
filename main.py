import random
from typing import List, Tuple
from datetime import datetime
from schedule import Schedule, ScheduleItem, Activity, Room

"""
Create a random schedule for all activities
Args:
        activities: Dictionary of activities with their details.
        rooms: Dictionary of available rooms.
        times: List of available time slots.
        facilitators: List of available facilitators.

Returns: a list of scheduled items with randomly assigned room, time, and facilitator for each activity.

"""
def random_schedule(activities: dict, rooms: dict, times: List[str], facilitators: List[str]) -> List[ScheduleItem]:
    return [
        ScheduleItem(
            activity=activity_name,
            facilitator=random.choice(facilitators),
            room=random.choice(list(rooms.keys())),
            time=random.choice(times)
        )
        for activity_name in activities.keys()
    ]

"""
Create initial population of n schedules
Return a list of Schedule objects representing the initial population.
"""
def initial_population(activities: dict, rooms: dict, times: List[str], facilitators: List[str], n: int) -> List[Schedule]:
    population = []
    for _ in range(n):
        schedule = Schedule(random_schedule(activities, rooms, times, facilitators))
        schedule.calculate_fitness(activities, rooms)
        population.append(schedule)
    return population

"""
Select two best schedules as parents
Args: 
    generation: The current generation of schedules.

Returns:
    Tuple[Schedule, Schedule]: The two schedules with the highest fitness scores.
"""
def select_parents(generation: List[Schedule]) -> Tuple[Schedule, Schedule]:
    # Sort by fitness score
    sorted_generation = sorted(generation, key=lambda s: s.fitness_score, reverse=True)
    return sorted_generation[0], sorted_generation[1]

def crossover(first: Schedule, second: Schedule) -> Schedule:
    """Create offspring from two parent schedules"""
    crossover_point = random.randint(0, len(first.items))
    child_items = first.items[:crossover_point] + second.items[crossover_point:]
    return Schedule(child_items)

"""
Mutate a given schedule with a specified mutation rate.
Returns: a new Schedule object representing the mutated schedule.
"""
def mutate(schedule: Schedule, rooms: dict, times: List[str], facilitators: List[str], rate: float) -> Schedule:
    mutated_items = []
    for item in schedule.items:
        if random.random() < rate:
            mutation_type = random.choice(['room', 'time', 'facilitator'])
            if mutation_type == 'room':
                mutated_items.append(ScheduleItem(
                    activity=item.activity,
                    room=random.choice(list(rooms.keys())),
                    time=item.time,
                    facilitator=item.facilitator
                ))
            elif mutation_type == 'time':
                mutated_items.append(ScheduleItem(
                    activity=item.activity,
                    room=item.room,
                    time=random.choice(times),
                    facilitator=item.facilitator
                ))
            else:  # facilitator
                mutated_items.append(ScheduleItem(
                    activity=item.activity,
                    room=item.room,
                    time=item.time,
                    facilitator=random.choice(facilitators)
                ))
        else:
            mutated_items.append(item)
    return Schedule(mutated_items)

"""
Print schedule to console and file
"""
def print_schedule(schedule: Schedule, filename: str = None):
    output_lines = [f"\nFinal Schedule (Fitness Score: {schedule.fitness_score:.2f}):\n"]
    
    sorted_items = sorted(schedule.items, key=lambda x: (x.time, x.activity))
    
    current_time = None
    for item in sorted_items:
        if item.time != current_time:
            current_time = item.time
            output_lines.append(f"\n{current_time}")
            output_lines.append("-" * 80)
        output_lines.append(
            f"Activity: {item.activity:<8} | Room: {item.room:<12} | Facilitator: {item.facilitator}"
        )
    
    print('\n'.join(output_lines))
    
    if filename:
        with open(filename, 'w') as f:
            f.write('\n'.join(output_lines))

"""
Run genetic algorithm for schedule optimization
Returns: The best schedule found by the genetic algorithm
"""
def run_genetic_algorithm(population_size: int, initial_mutation_rate: float):
    # Initialize data
    activities = {
        "SLA100A": Activity("SLA100A", 50, ["Glen", "Lock", "Banks", "Zeldin"], ["Numen", "Richards"]),
        "SLA100B": Activity("SLA100B", 50, ["Glen", "Lock", "Banks", "Zeldin"], ["Numen", "Richards"]),
        "SLA191A": Activity("SLA191A", 50, ["Glen", "Lock", "Banks", "Zeldin"], ["Numen", "Richards"]),
        "SLA191B": Activity("SLA191B", 50, ["Glen", "Lock", "Banks", "Zeldin"], ["Numen", "Richards"]),
        "SLA201": Activity("SLA201", 50, ["Glen", "Banks", "Zeldin", "Shaw"], ["Numen", "Richards", "Singer"]),
        "SLA291": Activity("SLA291", 50, ["Lock", "Banks", "Zeldin", "Singer"], ["Numen", "Richards", "Shaw", "Tyler"]),
        "SLA303": Activity("SLA303", 60, ["Glen", "Zeldin", "Banks"], ["Numen", "Singer", "Shaw"]),
        "SLA304": Activity("SLA304", 25, ["Glen", "Banks", "Tyler"], ["Numen", "Singer", "Shaw", "Richards", "Uther", "Zeldin"]),
        "SLA394": Activity("SLA394", 20, ["Tyler", "Singer"], ["Richards", "Zeldin"]),
        "SLA449": Activity("SLA449", 60, ["Tyler", "Singer", "Shaw"], ["Zeldin", "Uther"]),
        "SLA451": Activity("SLA451", 100, ["Tyler", "Singer", "Shaw"], ["Zeldin", "Uther", "Richards", "Banks"])
    }
    
    rooms = {
        "Slater 003": Room("Slater 003", 45),
        "Roman 216": Room("Roman 216", 30),
        "Loft 206": Room("Loft 206", 75),
        "Roman 201": Room("Roman 201", 50),
        "Loft 310": Room("Loft 310", 108),
        "Beach 201": Room("Beach 201", 60),
        "Beach 301": Room("Beach 301", 75),
        "Logos 325": Room("Logos 325", 450),
        "Frank 119": Room("Frank 119", 60)
    }
    
    times = ["10 AM", "11 AM", "12 PM", "1 PM", "2 PM", "3 PM"]
    facilitators = ["Lock", "Glen", "Banks", "Richards", "Shaw", "Singer", "Uther", "Tyler", "Numen", "Zeldin"]

    # Create initial population
    population = initial_population(activities, rooms, times, facilitators, population_size)
    
    current_mutation_rate = initial_mutation_rate
    best_fitness_achieved = float('-inf') # initialize the variable best_fitness_achieved to negative infinity
    generation = 0
    avg_fitness_history = []
    
    while True:
        # Create new population
        new_population = []
        
        while len(new_population) < population_size:
            # Select parents and crossover
            parent1, parent2 = select_parents(population)
            child = crossover(parent1, parent2)
            
            # Mutate and calculate fitness
            child = mutate(child, rooms, times, facilitators, current_mutation_rate)
            child.calculate_fitness(activities, rooms)
            
            new_population.append(child)
        
        # Replace old population
        population = new_population
        
        # Calculate statistics
        current_fitness = [p.fitness_score for p in population]
        current_best_fitness = max(current_fitness)
        current_avg_fitness = sum(current_fitness) / len(current_fitness)
        avg_fitness_history.append(current_avg_fitness)
        
        # Adapt mutation rate
        if current_best_fitness > best_fitness_achieved:
            best_fitness_achieved = current_best_fitness
            current_mutation_rate /= 2
            print(f"Generation {generation}: Reducing mutation rate to {current_mutation_rate}")
        
        # Check convergence after 100 generations
        if generation >= 100:
            # Determine if the genetic algorithm is still making improvement.
            improvement = (avg_fitness_history[-1] - avg_fitness_history[-100]) / abs(avg_fitness_history[-100])
            # If the improvement is less than 1%, the algorithm stops further generations
            if improvement < 0.01:
                print(f"Converged after {generation} generations")
                break
        
        #  The program prints out progress only every 10th generation
        if generation % 10 == 0:
            print(f"Generation {generation}: Best Fitness = {current_best_fitness:.2f}, "
                  f"Avg Fitness = {current_avg_fitness:.2f}, "
                  f"Mutation Rate = {current_mutation_rate:.6f}")
        
        generation += 1
    
    return max(population, key=lambda x: x.fitness_score)

if __name__ == "__main__":
    POPULATION_SIZE = 500
    INITIAL_MUTATION_RATE = 0.01
    
    best_schedule = run_genetic_algorithm(POPULATION_SIZE, INITIAL_MUTATION_RATE)
    
    # Generate output filenames 
    schedule_file = f"schedule_output.txt"
    
    # Print and save results
    print_schedule(best_schedule, schedule_file)
    print(f"\nSchedule has been saved to {schedule_file}")
  