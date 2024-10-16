import sys, csv, math
from collections import defaultdict
#import heapq
import time as time_module
class MinHeap:
    def __init__(self):
        self.heap = []

    def parent(self, i):
        return (i - 1) // 2

    def left_child(self, i):
        return 2 * i + 1

    def right_child(self, i):
        return 2 * i + 2

    def swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def push(self, key):
        self.heap.append(key)
        self._sift_up(len(self.heap) - 1)

    def pop(self):
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        min_val = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._sift_down(0)
        return min_val

    def _sift_up(self, i):
        parent = self.parent(i)
        if i > 0 and self.heap[i] < self.heap[parent]:
            self.swap(i, parent)
            self._sift_up(parent)

    def _sift_down(self, i):
        min_index = i
        left = self.left_child(i)
        right = self.right_child(i)
        if left < len(self.heap) and self.heap[left] < self.heap[min_index]:
            min_index = left
        if right < len(self.heap) and self.heap[right] < self.heap[min_index]:
            min_index = right
        if i != min_index:
            self.swap(i, min_index)
            self._sift_down(min_index)

class Hilberts:

    def __init__(self):
        self.channels = {1: 2, 2: 3, 3: 5, 4: 7, 5: 11}
        self.guests_per_channel = defaultdict(int)
        self.manual_rooms = set()
        self.manual_room_info = {}  # To store additional info for manual rooms
        self.function_times = {}
        self.highest_occupied_room = 0
        self.removed_rooms = set()

    def track_time(func):
        def wrapper(self, *args, **kwargs):
            start_time = time_module.perf_counter()
            result = func(self, *args, **kwargs)
            end_time = time_module.perf_counter()
            execution_time = end_time - start_time
            self.function_times[func.__name__] = self.function_times.get(func.__name__, 0) + execution_time
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
        self.highest_occupied_room = max(
            max(self.manual_rooms) if self.manual_rooms else 0,
            max(
                self.channels[channel] ** self.guests_per_channel[channel]
                for channel in self.channels
                if self.guests_per_channel[channel] > 0
            ) if any(self.guests_per_channel.values()) else 0
        )
    # @track_time
    # def remove_room(self, room_number):
    #     room_number = int(room_number)
    #     # Check manual rooms first (O(1) operation)
    #     if room_number in self.manual_rooms:
    #         self.manual_rooms.remove(room_number)
    #         del self.manual_room_info[room_number]
    #         if room_number == self.highest_occupied_room:
    #             self.recalculate_highest_occupied_room()
    #         return f"Room {room_number} removed from manual rooms"
        
    #     # Check channel rooms efficiently
    #     for channel, base in self.channels.items():
    #         if room_number % base == 0:
    #             exponent = int(math.log(room_number, base))
    #             if exponent <= self.guests_per_channel[channel]:
    #                 self.guests_per_channel[channel] -= 1
    #                 if room_number == self.highest_occupied_room:
    #                     self.recalculate_highest_occupied_room()
    #                 return f"Room {room_number} removed from channel {channel}. Remaining guests in channel {channel}: {self.guests_per_channel[channel]}"
    #             # If exponent is greater, we know it's not in this channel, so break early
    #             break
    #     return f"Room {room_number} is unoccupied or empty room. No action needed."
    @track_time
    def remove_room(self, room_number):
        room_number = int(room_number)

        # Check if the room has already been removed
        if room_number in self.removed_rooms:
            return f"Room {room_number} was already removed. No action needed."

        # Check manual rooms first (O(1) operation)
        if room_number in self.manual_rooms:
            self.manual_rooms.remove(room_number)
            del self.manual_room_info[room_number]
            self.removed_rooms.add(room_number)
            if room_number == self.highest_occupied_room:
                self.recalculate_highest_occupied_room()
            return f"Room {room_number} removed from manual rooms"
        
        # Check channel rooms efficiently
        for channel, base in self.channels.items():
            if room_number % base == 0:
                exponent = int(math.log(room_number, base))
                if exponent <= self.guests_per_channel[channel]:
                    self.guests_per_channel[channel] -= 1
                    self.removed_rooms.add(room_number)
                    if room_number == self.highest_occupied_room:
                        self.recalculate_highest_occupied_room()
                    return f"Room {room_number} removed from channel {channel}. Remaining guests in channel {channel}: {self.guests_per_channel[channel]}"
                break  # If exponent is greater, it's not in this channel, so break early

        # If we reach here, the room was not occupied
        self.removed_rooms.add(room_number)  # We still mark it as removed
        return f"Room {room_number} was unoccupied. Marked as removed."
    # def is_valid_room(self, room_number):
    #     if room_number in self.manual_rooms:
    #         return True
    #     return any(room_number == base ** exp for base in self.channels.values() 
    #                for exp in range(1, int(math.log(room_number, min(self.channels.values())) + 1)))
    @track_time
    def is_room_occupied(self, room_number):
        if room_number in self.manual_rooms:
            return True
        for channel, base in self.channels.items():
            if room_number % base == 0:
                exponent = int(math.log(room_number, base))
                if exponent <= self.guests_per_channel[channel]:
                    return True
        return False

    @track_time
    def find_room(self, room_number):
        room_number = int(room_number)
        if room_number <= 0:
            return f"Error: Invalid room number {room_number}. Room numbers must be positive integers."
        # if not self.is_valid_room(room_number):
        #     return f"Error: Room {room_number} is an empty room in this hotel."
        if room_number in self.manual_rooms:
            guest_info, channel = self.manual_room_info[room_number]
            return f"Room {room_number}: Occupied by guest ---> {guest_info} : {channel}"
        for channel, base in self.channels.items():
            if room_number % base == 0:
                exponent = int(math.log(room_number, base))
                if exponent <= self.guests_per_channel[channel]:
                    return f"Room {room_number}: Occupied by guest from channel {channel}"
        return f"Room {room_number} is a valid room but currently unoccupied"

    @track_time
    def update_highest_occupied_room(self, room_number):
        self.highest_occupied_room = max(self.highest_occupied_room, room_number)
    @track_time
    def add_initial_guests(self, num_guests):
        self.guests_per_channel[1] = num_guests
        return f"Added {num_guests} initial guests to channel 1"


    @track_time
    def add_new_guests(self, channel, num_guests):
        # highest_room = self.channels[channel] ** self.guests_per_channel[channel]
        # self.removed_rooms = {room for room in self.removed_rooms if room > highest_room}
        # if channel not in self.channels:
        #     return f"Error: Invalid channel number {channel}"
        # try:
        #     num_guests = int(num_guests)
        #     self.guests_per_channel[channel] += num_guests
        #     return f"Added {num_guests} new guests to channel {channel}. Total guests in channel {channel}: {self.guests_per_channel[channel]}"
        # except ValueError:
        #     return "Error: Invalid number of guests"
        #         if channel not in self.channels:
        #     return f"Error: Invalid channel number {channel}"
        
        try:
            num_guests = int(num_guests)
            if num_guests <= 0:
                return "Error: Number of guests must be positive"

            base = self.channels[channel]
            old_highest_room = base ** self.guests_per_channel[channel]
            self.guests_per_channel[channel] += num_guests
            new_highest_room = base ** self.guests_per_channel[channel]

            # Update removed_rooms
            self.removed_rooms = {room for room in self.removed_rooms 
                                  if room <= old_highest_room or room > new_highest_room}

            # Update highest_occupied_room if necessary
            if new_highest_room > self.highest_occupied_room:
                self.highest_occupied_room = new_highest_room

            return f"Added {num_guests} new guests to channel {channel}. Total guests in channel {channel}: {self.guests_per_channel[channel]}"
        
        except ValueError:
            return "Error: Invalid number of guests"


    @track_time
    def sort_rooms(self, start=0, count=20):
        def room_generator():
            yield from self.manual_rooms
            for channel, base in self.channels.items():
                exponent = 1
                while exponent <= self.guests_per_channel[channel]:
                    yield base ** exponent
                    exponent += 1

        heap = MinHeap()
        for i, room in enumerate(room_generator()):
            if i < start:
                continue
            if len(heap.heap) < count:
                heap.push(-room)  # Use negative for max-heap behavior
            elif -room > heap.heap[0]:
                heap.pop()
                heap.push(-room)
            if len(heap.heap) == count and i >= start + count - 1:
                break

        return sorted(-room for room in heap.heap)

    # @track_time
    # def sort_rooms(self, start=0, count=20):
    #     all_rooms = list(self.manual_rooms)
    #     for channel, base in self.channels.items():
    #         all_rooms.extend(base ** i for i in range(1, self.guests_per_channel[channel] + 1))
    #     all_rooms.sort()
    #     end = min(start + count, len(all_rooms))
    #     return all_rooms[start:end]

    # @track_time
    # def count_empty_rooms(self):
    #     # Find the highest occupied room number
    #     highest_manual = max(self.manual_rooms) if self.manual_rooms else 0
    #     highest_channel = max(
    #         self.channels[channel] ** self.guests_per_channel[channel]
    #         for channel in self.channels
    #         if self.guests_per_channel[channel] > 0
    #     ) if any(self.guests_per_channel.values()) else 0

    #     highest_occupied = max(highest_manual, highest_channel)

    #     # Count occupied rooms
    #     total_occupied = sum(self.guests_per_channel.values()) + len(self.manual_rooms)

    #     # Calculate empty rooms
    #     return highest_occupied - total_occupied
    @track_time
    def count_empty_rooms(self):
        total_occupied = sum(self.guests_per_channel.values()) + len(self.manual_rooms)
        return max(0, self.highest_occupied_room - total_occupied) #always return positive num

    def suggest_rooms(self, count):
        count = int(count)  # Ensure count is an integer
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
    
    
    # @track_time
    # def write_to_file(self, filename):
    #     # Use the sort_rooms method to get all rooms in sorted order
    #     all_rooms = self.sort_rooms(start=0, count=float('inf'))  # Get all rooms
        
    #     with open(filename, 'w', newline='') as file:
    #         writer = csv.writer(file)
    #         writer.writerow(["Room Number", "Channel/Info"])
    #         for room in all_rooms:
    #             if room in self.manual_rooms:
    #                 guest_info, channel = self.manual_room_info[room]
    #                 info = f"manual - {guest_info}"
    #             else:
    #                 for channel, base in self.channels.items():
    #                     if room % base == 0 and base ** (math.log(room, base)) == room:
    #                         info = f"channel {channel}"
    #                         break
    #             writer.writerow([room, info])
        
    #     return f"Data written to {filename}"

    @track_time
    def write_to_file(self, filename):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Room Number", "Channel"])
            for channel, base in self.channels.items():
                for i in range(1, self.guests_per_channel[channel] + 1):
                    writer.writerow([base ** i, f"channel {channel}"])
            for room in self.manual_rooms:
                writer.writerow([room, "manual"])
        return f"Data written to {filename}"
    
    @track_time
    def get_hotel_status(self):
        total_guests = sum(self.guests_per_channel.values()) + len(self.manual_rooms)
        occupied_channels = sum(1 for guests in self.guests_per_channel.values() if guests > 0)
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


def process_command(hotel, command, args):
    operations = {
        'A': hotel.add_new_guests,
        'M': hotel.add_room_manual,
        'R': hotel.remove_room,
        'F': hotel.find_room,
        'S': hotel.sort_rooms,
        'C': hotel.count_empty_rooms,
        'W': hotel.write_to_file,
        'U': hotel.memory_usage,
        # 'SR': hotel.suggest_rooms,
    }
    
    op = command[0]
    if op not in operations:
        return f"Invalid command: {op}"
    
    try:
        if op == 'A':
            channel, num_guests = int(command.split()[1]), int(args[0])
            return operations[op](channel, num_guests)
        elif op in ['M', 'R', 'F', 'W']:
            return operations[op](*args)
        elif op == 'S':
            start, count = map(int, args)
            return operations[op](start, count)
        # elif op == 'SR':
        #     count = args[0] if args else "10"  # Use "10" as a string if no count is provided
        #     suggested = operations[op](count)
        #     return f"Suggested unoccupied rooms: {', '.join(map(str, suggested))}"
        
        else:
            return operations[op]()
    except Exception as e:
        return f"Error: {str(e)}"
    
def main():
    hotel = Hilberts()
    
    while True:
        print("---------------------------------------------------------------------------------------------------------")
        print("\n*** Hilbert's Infinite Hotel Management System ***")
        print("1. Initialize hotel with guests")
        print("2. Add guests to channels")
        print("3. Add room manually")
        print("4. Remove room")
        print("5. Find a room")
        print("6. Sort and display rooms")
        print("7. Count empty rooms")
        print("8. Write room data to file")
        print("9. Show memory usage")
        print("10. Show function execution times")
        print("11. Show hotel status")
        
        print("0. Exit")
        try:
            choice = input("Enter your choice (0-11): ")
            print("---------------------------------------------------------------------------------------------------------")
            start_time = time_module.perf_counter()
            if choice == '0':
                print("Thank you for using Hilbert's Infinite Hotel Management System. Goodbye!")
                break
            
            elif choice == '1':
                num_guests = input("Enter the number of initial guests: ")
                print(process_command(hotel, "A 1", [num_guests]))
            
            elif choice == '2':
                guests_input = input("Enter guests for channels 2-5 (comma-separated): ").split(',')
                for i, num in enumerate(guests_input, start=2):
                    if i > 5:
                        break
                    print(process_command(hotel, f"A {i}", [num]))
            
            elif choice == '3':
                args = input("Enter room number, guest info, and channel (space-separated): ").split()
                if len(args) != 3:
                    print("Error: Please provide room number, guest info, and channel.")
                else:
                    room_number, guest_info, channel = args
                    print(hotel.add_room_manual(int(room_number), guest_info, channel))
            
            elif choice == '4':
                room_number = input("Enter room number to remove: ")
                print(process_command(hotel, "R", [room_number]))
            
            elif choice == '5':
                room_number = input("Enter room number to find: ")
                print(process_command(hotel, "F", [room_number]))
            
            elif choice == '6':
                args = input("Enter start and count (space-separated): ").split()
                print(process_command(hotel, "S", args))
            
            elif choice == '7':
                print(process_command(hotel, "C", []))
            
            elif choice == '8':
                filename = input("Enter filename to save room data: ")
                print(process_command(hotel, "W", [filename]))
            
            elif choice == '9':
                print(f"Current memory usage: {process_command(hotel, 'U', [])} bytes")
            
            elif choice == '10':
                function_times = hotel.get_function_times()
                for func, time in function_times.items():
                    print(f"{func}: {time} seconds")
            
            # elif choice == '11':
            #     count = input("Enter the number of rooms to suggest (default 10): ")
            #     count = count if count else "10"  # Use "10" as a string if no input is provided
            #     print(process_command(hotel, "SR", [count]))
            elif choice == '11':
                print(hotel.get_hotel_status())
            
            else:
                print("Invalid choice. Please try again.")

            end_time = time_module.perf_counter()
            print(f"\nOperation completed in {end_time - start_time:.6f} seconds")
            print(f"Current memory usage: {hotel.memory_usage()} bytes")
        except Exception as e:
            print(f"An error occurred: {e}")
if __name__ == "__main__":
    main()