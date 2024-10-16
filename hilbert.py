import sys
import csv
import math
import time as time_module


class Hilberts:
    def __init__(self):
        self.channels = {"Original": 2, "Bus": 3, "Train": 5, "Plane": 7, "Ship": 11}
        self.guests_per_channel = {channel: 0 for channel in self.channels}
        self.manual_rooms = set()
        self.manual_room_info = {}
        self.function_times = {}
        self.highest_occupied_room = 0
        self.removed_rooms = set()
        self.large_input_threshold = 10**6
        self.extreme_input_threshold = 10**12

    def track_time(func):
        def wrapper(self, *args, **kwargs):
            start_time = time_module.perf_counter()
            result = func(self, *args, **kwargs)
            end_time = time_module.perf_counter()
            execution_time = end_time - start_time
            self.function_times[func.__name__] = (
                self.function_times.get(func.__name__, 0) + execution_time
            )
            return result

        return wrapper

    @track_time
    def add_room_manual(self, room_number, guest_info, channel):
        room_number = int(room_number)
        if room_number in self.removed_rooms:
            self.removed_rooms.remove(room_number)
        if self.is_room_occupied(room_number):
            suggested_rooms = self.suggest_rooms(10)
            return f"Error: Room {room_number} is already occupied. Suggested unoccupied rooms: {', '.join(map(str, suggested_rooms))}"
        self.manual_rooms.add(room_number)
        self.manual_room_info[room_number] = (guest_info, channel)
        self.update_highest_occupied_room(room_number)
        return f"Room {room_number} added manually with guest info: {guest_info}"

    @track_time
    def recalculate_highest_occupied_room(self):
        highest_manual = max(self.manual_rooms) if self.manual_rooms else 0
        highest_channel = (
            max(
                self.channels[channel] ** self.guests_per_channel[channel]
                for channel in self.channels
                if self.guests_per_channel[channel] > 0
            )
            if any(self.guests_per_channel.values())
            else 0
        )
        self.highest_occupied_room = max(highest_manual, highest_channel)

    @track_time
    def remove_room(self, room_number):
        room_number = int(room_number)
        if room_number in self.removed_rooms:
            return f"Room {room_number} was already removed. No action needed."
        if room_number in self.manual_rooms:
            self.manual_rooms.remove(room_number)
            del self.manual_room_info[room_number]
            self.removed_rooms.add(room_number)
            if room_number == self.highest_occupied_room:
                self.recalculate_highest_occupied_room()
            return f"Room {room_number} removed from manual rooms"
        for channel, base in self.channels.items():
            if room_number % base == 0:
                exponent = int(math.log(room_number, base))
                if exponent <= self.guests_per_channel.get(channel, 0):
                    self.guests_per_channel[channel] -= 1
                    self.removed_rooms.add(room_number)
                    if room_number == self.highest_occupied_room:
                        self.recalculate_highest_occupied_room()
                    return f"Room {room_number} removed from channel {channel}. Remaining guests in channel {channel}: {self.guests_per_channel[channel]}"
        self.removed_rooms.add(room_number)
        return f"Room {room_number} was unoccupied. Marked as removed."

    @track_time
    def is_room_occupied(self, room_number):
        if room_number in self.manual_rooms:
            return True
        for channel, base in self.channels.items():
            if room_number % base == 0:
                exponent = int(math.log(room_number, base))
                if exponent <= self.guests_per_channel.get(channel, 0):
                    return True
        return False

    @track_time
    def find_room(self, room_number):
        room_number = int(room_number)
        if room_number <= 0:
            return f"Error: Invalid room number {room_number}. Room numbers must be positive integers."
        if room_number in self.removed_rooms:
            return f"Room {room_number} has been removed."
        if room_number in self.manual_rooms:
            guest_info, channel = self.manual_room_info[room_number]
            return (
                f"Room {room_number}: Occupied by guest ---> {guest_info} : {channel}"
            )
        for channel, base in self.channels.items():
            if room_number % base == 0:
                exponent = int(math.log(room_number, base))
                if exponent <= self.guests_per_channel.get(channel, 0):
                    return (
                        f"Room {room_number}: Occupied by guest from channel {channel}"
                    )
        return f"Room {room_number} is an empty room, you can reserve it."

    @track_time
    def add_new_guests(self, channel, num_guests):
        try:
            num_guests = int(num_guests)
            if channel not in self.channels:
                return f"Error: Invalid channel name {channel}"
            if num_guests <= 0:
                return "Error: Number of guests must be positive"
            self.guests_per_channel[channel] += num_guests
            new_highest_room = (
                self.channels[channel] ** self.guests_per_channel[channel]
            )
            if sum(self.guests_per_channel.values()) > self.large_input_threshold:
                self.highest_occupied_room = max(
                    self.highest_occupied_room, new_highest_room
                )
            else:
                self.update_highest_occupied_room(new_highest_room)
            return f"Added {num_guests} new guests to channel {channel}. Total guests in channel {channel}: {self.guests_per_channel[channel]}"
        except ValueError:
            return f"Error: Invalid input for channel {channel} or number of guests {num_guests}"

    @track_time
    def add_initial_guests(self, num_guests):
        try:
            num_guests = int(num_guests)
            if num_guests <= 0:
                return "Error: Number of guests must be positive"
            if self.guests_per_channel["Original"] > 0:
                return "Error: Initial guests have already been added. Use 'Add guests to channels' to add more guests."
            self.guests_per_channel["Original"] = num_guests
            new_highest_room = self.channels["Original"] ** num_guests
            self.update_highest_occupied_room(new_highest_room)
            return f"Added {num_guests} initial guests to the Original channel"
        except ValueError:
            return "Error: Invalid number of guests"

    def update_highest_occupied_room(self, new_room):
        self.highest_occupied_room = max(self.highest_occupied_room, new_room)


    @track_time
    def sort_rooms(self, start=0, count=20):
        all_rooms = []
        for channel, base in self.channels.items():
            all_rooms.extend(
                base**exp for exp in range(1, self.guests_per_channel[channel] + 1)
            )
        all_rooms.extend(self.manual_rooms)

        all_rooms.sort()

        end = min(start + count, len(all_rooms))
        return all_rooms[start:end]

    @track_time
    def count_empty_rooms(self):
        if sum(self.guests_per_channel.values()) > self.extreme_input_threshold:
            return "Infinite (too large to count)"
        else:
            total_occupied = sum(self.guests_per_channel.values()) + len(
                self.manual_rooms
            )
            return max(0, self.highest_occupied_room - total_occupied)

    def suggest_rooms(self, count):
        count = int(count)
        suggested = []
        room = 1
        while len(suggested) < count:
            if not self.is_room_occupied(room):
                suggested.append(room)
            room += 1
        return suggested

    def memory_usage(self):
        return sum(sys.getsizeof(obj) for obj in vars(self).values())

    def get_function_times(self):
        return {func: f"{time:.19f}" for func, time in self.function_times.items()}

    @track_time
    def write_to_file(self, filename):
        def row_generator():
            yield ["Room Number", "Channel", "Status"]
            for channel, base in self.channels.items():
                for exp in range(1, self.guests_per_channel[channel] + 1):
                    room = base**exp
                    status = "Removed" if room in self.removed_rooms else "Occupied"
                    yield [room, channel, status]
            for room, (guest_info, channel) in self.manual_room_info.items():
                status = "Removed" if room in self.removed_rooms else "Occupied"
                yield [room, f"Manual - {guest_info}", status]

        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            for row in row_generator():
                writer.writerow(row)
        return f"Data written to {filename}"

    @track_time
    def get_hotel_status(self):
        total_guests = sum(self.guests_per_channel.values()) + len(self.manual_rooms)
        occupied_channels = sum(
            1 for guests in self.guests_per_channel.values() if guests > 0
        )
        empty_rooms = self.count_empty_rooms()

        status = f"""
# Hilbert's Infinite Hotel Status

## Overview
- **Total Guests:** {total_guests}
- **Occupied Channels:** {occupied_channels} out of {len(self.channels)}
- **Manually Added Rooms:** {len(self.manual_rooms)}
- **Highest Occupied Room:** {self.highest_occupied_room}
- **Empty Rooms** (up to highest occupied): {empty_rooms}

## Guests per Channel

| Channel | Guests |
|---------|--------|
"""
        for channel, guests in self.guests_per_channel.items():
            if guests > 0:
                status += f"| {channel:<7} | {guests:<6} |\n"

        status += "\n## Manual Rooms\n\n"
        if self.manual_rooms:
            status += "| Room Number | Guest Info | Channel |\n"
            status += "|-------------|------------|--------|\n"
            for room, (guest_info, channel) in self.manual_room_info.items():
                status += f"| {room:<11} | {guest_info:<10} | {channel:<7} |\n"
        else:
            status += "No manually added rooms.\n"

        return status
