import random
import math
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from copy import deepcopy


@dataclass
class Activity:
    name: str
    enrollment: int
    preferred_facilitators: List[str]
    other_facilitators: List[str]

@dataclass
class Room:
    name: str
    capacity: int

@dataclass
class ScheduleItem:
    activity: str
    room: str
    time: str
    facilitator: str

"""
A complete schedule with multiple scheduled items 
and methods for fitness evaluation.
"""
class Schedule:
    # Initialize the schedule with a list of ScheduleItems.
    def __init__(self, items: List[ScheduleItem]):
        self.items = items
        self.fitness_score = None

    def __lt__(self, other):
        # For heap operations, comparing by fitness score
        return self.fitness_score < other.fitness_score

    # Calculate the fitness score of the schedule based on various constraints.
    def calculate_fitness(self, activities: Dict[str, Activity], rooms: Dict[str, Room]) -> float:
        score = 0
        facilitator_counts = {}
        time_room_pairs = set()
        facilitator_time_counts = {}
        
        # Track time slots for SLA101 and SLA191 sections
        sla101_times = []
        sla191_times = []
        
        # Initialize facilitator counts
        for item in self.items:
            if item.facilitator not in facilitator_counts:
                facilitator_counts[item.facilitator] = 0
            facilitator_counts[item.facilitator] += 1
            
            time_key = f"{item.facilitator}_{item.time}"

            # Track the number of activities each facilitator is assigned at the same time slot.
            if time_key not in facilitator_time_counts:
                facilitator_time_counts[time_key] = 0
            facilitator_time_counts[time_key] += 1

            if item.activity in ["SLA100A", "SLA100B"]:
                sla101_times.append(item.time)
            elif item.activity in ["SLA191A", "SLA191B"]:
                sla191_times.append(item.time)

        # Process each scheduled item
        for item in self.items:
            # Room time conflicts. Penalize if multiple activities are scheduled in the same room at the same time.
            time_room_pair = (item.time, item.room)
            if time_room_pair in time_room_pairs:
                score -= 0.5
            time_room_pairs.add(time_room_pair)
            
            # Room size checks
            activity = activities[item.activity]
            room = rooms[item.room]

            # Penalize if the assigned room is too small for the expected enrollment.
            if room.capacity < activity.enrollment:
                score -= 0.5
            # Penalize if the room capacity is significantly larger than required    
            elif room.capacity > 6 * activity.enrollment:
                score -= 0.4
            elif room.capacity > 3 * activity.enrollment:
                score -= 0.2
            else:
                score += 0.3
                
            # Reward if the activity is overseen by a preferred facilitator. otherwise, giving penalty.
            if item.facilitator in activity.preferred_facilitators:
                score += 0.5
            elif item.facilitator in activity.other_facilitators:
                score += 0.2
            else:
                score -= 0.1
                
            # Facilitator load checks
            time_key = f"{item.facilitator}_{item.time}"
            # Reward for only one activity at the given time slot. otherwise, giving penalty
            if facilitator_time_counts[time_key] == 1:
                score += 0.2
            elif facilitator_time_counts[time_key] > 1:
                score -= 0.2

            # Penalize if the facilitator is assigned more than 4    
            if facilitator_counts[item.facilitator] > 4:
                score -= 0.5
            # Penalize if the facilitator has fewer than 3 activities (except for Tyler)
            elif facilitator_counts[item.facilitator] < 3 and item.facilitator != "Tyler":
                score -= 0.4

        # Time slot specific times
        time_slots = ["10 AM", "11 AM", "12 PM", "1 PM", "2 PM", "3 PM"]
        
        # SLA101 sections timing
        if len(sla101_times) == 2:
            if sla101_times[0] == sla101_times[1]:
                score -= 0.5
            elif abs(time_slots.index(sla101_times[0]) - time_slots.index(sla101_times[1])) > 4:
                score += 0.5
                
        # SLA191 sections timing
        if len(sla191_times) == 2:
            if sla191_times[0] == sla191_times[1]:
                score -= 0.5
            elif abs(time_slots.index(sla191_times[0]) - time_slots.index(sla191_times[1])) > 4:
                score += 0.5

        """
        Consecutive sections checks
        Iterate over all times for SLA101 sections and SLA191 sections to evaluate their relative timing.
        Reward if these sections in consecutive or 2 hours apart, and to penalize if they are scheduled at same time.
        
        """
        for sla101_time in sla101_times:
            for sla191_time in sla191_times:
                time_diff = abs(time_slots.index(sla101_time) - time_slots.index(sla191_time))
                if time_diff == 1:
                    score += 0.5
                    sla101_item = next(item for item in self.items if item.activity in ["SLA100A", "SLA100B"] and item.time == sla101_time)
                    sla191_item = next(item for item in self.items if item.activity in ["SLA191A", "SLA191B"] and item.time == sla191_time)
                    
                    is_sla101_in_roman_beach = "Roman" in sla101_item.room or "Beach" in sla101_item.room
                    is_sla191_in_roman_beach = "Roman" in sla191_item.room or "Beach" in sla191_item.room
                    
                    if is_sla101_in_roman_beach != is_sla191_in_roman_beach:
                        score -= 0.4
                elif time_diff == 2:
                    score += 0.25
                elif time_diff == 0:
                    score -= 0.25

        self.fitness_score = score
        return score