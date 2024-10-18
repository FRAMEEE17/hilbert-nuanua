import sys
import csv
import math
import time as time_module
import os 
#import heapq
import tempfile
import io
class Hilberts:
    def __init__(self):
        self.channels = {
            "Original": 2,
            "Bus": 3,
            "Train": 5,
            "Plane": 7,
            "Ship": 11
        }
        # Stores all rooms: {room_number: {"channel": channel, "guest_info": info}}
        self.rooms = {}  
        self.guests_per_channel = {channel: 0 for channel in self.channels}
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
            self.function_times[func.__name__] = self.function_times.get(func.__name__, 0) + execution_time
            return result
        return wrapper

    @track_time
    def add_room_manual(self, room_number, guest_info, channel):
        room_number = int(room_number)
        if room_number in self.removed_rooms:
            self.removed_rooms.remove(room_number)
        if room_number in self.rooms:
            suggested_rooms = self.suggest_rooms(10)
            return f"Error: Room {room_number} is already occupied. Suggested unoccupied rooms: {', '.join(map(str, suggested_rooms))}"
        self.rooms[room_number] = {"channel": "Manual", "guest_info": guest_info, "manual_channel": channel}
        self.update_highest_occupied_room(room_number)
        return f"Room {room_number} added manually with guest info: {guest_info}"

    @track_time
    def remove_room(self, room_number):
        room_number = int(room_number)
        print(f"Attempting to remove room {room_number}")

        if room_number in self.rooms:
            print(f"Room {room_number} is occupied and cannot be removed.")
            return f"Error: Room {room_number} is occupied and cannot be removed."

        if room_number in self.removed_rooms:
            print(f"Room {room_number} has already been removed.")
            return f"Room {room_number} has already been removed. No action needed."

        # ตรวจสอบว่าห้องนี้อยู่ในช่วงที่สามารถมีอยู่ได้หรือไม่
        if room_number > self.highest_occupied_room:
            print(f"Room {room_number} is beyond the highest occupied room and doesn't need to be removed.")
            return f"Room {room_number} is beyond the highest occupied room and doesn't need to be removed."

        # ลบห้องออกจากโครงสร้างข้อมูล
        self.removed_rooms.add(room_number)
        print(f"Room {room_number} has been removed from the data structure.")
        return f"Room {room_number} has been removed from the data structure."
    
    @track_time
    def move_guest(self, from_room, to_room):
        print(f"Attempting to move guest from room {from_room} to room {to_room}")
        from_room, to_room = int(from_room), int(to_room)
        if from_room not in self.rooms:
            print(f"Error: Room {from_room} is not occupied")
            return f"Error: Room {from_room} is not occupied"
        if to_room in self.rooms:
            print(f"Error: Room {to_room} is already occupied")
            return f"Error: Room {to_room} is already occupied"
        
        guest_info = self.rooms.pop(from_room)
        self.rooms[to_room] = guest_info
        
        # ปรับปรุง guests_per_channel ถ้าจำเป็น
        if guest_info['channel'] != "Manual":
            channel = guest_info['channel']
            base = self.channels[channel]
            old_exponent = int(math.log(from_room, base))
            new_exponent = int(math.log(to_room, base))
            if old_exponent != new_exponent:
                self.guests_per_channel[channel] = max(self.guests_per_channel[channel], new_exponent)
        
        self.update_highest_occupied_room(to_room)
        print(f"Guest successfully moved from room {from_room} to room {to_room}")
        return f"Guest successfully moved from room {from_room} to room {to_room}"

    @track_time
    def find_room(self, room_number):
        room_number = int(room_number)
        if room_number <= 0:
            return f"Error: Invalid room number {room_number}. Room numbers must be positive integers."
        if room_number in self.removed_rooms:
            return f"Room {room_number} has been removed."
        if room_number in self.rooms:
            info = self.rooms[room_number]
            if info["channel"] == "Manual":
                return f"Room {room_number}: Occupied by guest ---> {info['guest_info']} : {info['manual_channel']}"
            else:
                return f"Room {room_number}: Occupied by guest from channel {info['channel']}"
        return f"Room {room_number} is an empty room, any guest can reserve this room."

    @track_time
    def add_new_guests(self, channel, num_guests):
        try:
            num_guests = int(num_guests)
            if channel not in self.channels:
                return f"Error: Invalid channel name {channel}"
            if num_guests <= 0:
                return "Error: Number of guests must be positive"
            base = self.channels[channel]
            for _ in range(num_guests):
                self.guests_per_channel[channel] += 1
                room_number = base ** self.guests_per_channel[channel]
                self.rooms[room_number] = {"channel": channel, "guest_info": f"Guest from {channel}"}
            new_highest_room = base ** self.guests_per_channel[channel]
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
            base = self.channels["Original"]
            for i in range(1, num_guests + 1):
                room_number = base ** i
                self.rooms[room_number] = {"channel": "Original", "guest_info": f"Initial Guest {i}"}
            new_highest_room = base ** num_guests
            self.update_highest_occupied_room(new_highest_room)
            return f"Added {num_guests} initial guests to the Original channel"
        except ValueError:
            return "Error: Invalid number of guests"

    def update_highest_occupied_room(self, new_room):
        self.highest_occupied_room = max(self.highest_occupied_room, new_room)

    def recalculate_highest_occupied_room(self):
        self.highest_occupied_room = max(self.rooms.keys()) if self.rooms else 0

    @track_time
    def sort_rooms(self, chunk_size=1000000):
        print(f"Sorting rooms with chunk size: {chunk_size}")
        all_rooms = set(self.rooms.keys()) - self.removed_rooms
        if len(all_rooms) < chunk_size:
            print("Using regular sorting")
            return sorted(all_rooms)
        
        print("Using External Sorting")
        temp_files = []
        
        # แบ่งข้อมูลเป็น chunks และเรียงลำดับแต่ละ chunk
        for i in range(0, len(all_rooms), chunk_size):
            print(f"Processing chunk {i // chunk_size + 1}")
            chunk = sorted(list(all_rooms)[i:i+chunk_size])
            temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+')
            for room in chunk:
                temp_file.write(f"{room}\n")
            temp_file.close()
            temp_files.append(temp_file.name)
        
        print(f"Created {len(temp_files)} temporary files")
        
        # ใช้ k-way merge สำหรับ chunks ที่เรียงลำดับแล้ว
        sorted_rooms = self._merge_sorted_files(temp_files)
        
        # ลบไฟล์ชั่วคราว
        for file in temp_files:
            os.unlink(file)
        
        print(f"Sorting complete. Total rooms sorted: {len(sorted_rooms)}")
        return sorted_rooms

    def _merge_sorted_files(self, file_list):
        heap = []
        sorted_rooms = []
        open_files = []
        
        # เปิดทุกไฟล์และเพิ่มค่าแรกลงใน heap
        for filename in file_list:
            file = open(filename, 'r')
            open_files.append(file)
            first_line = file.readline().strip()
            if first_line:
                self._heap_push(heap, (int(first_line), file))
        
        # ทำ k-way merge
        while heap:
            value, file = self._heap_pop(heap)
            sorted_rooms.append(value)
            next_line = file.readline().strip()
            if next_line:
                self._heap_push(heap, (int(next_line), file))
        
        # ปิดไฟล์ทั้งหมด
        for file in open_files:
            file.close()
        
        return sorted_rooms

    def _heap_push(self, heap, item):
        heap.append(item)
        self._sift_up(heap, len(heap) - 1)

    def _heap_pop(self, heap):
        if not heap:
            return None
        if len(heap) == 1:
            return heap.pop()
        min_val = heap[0]
        heap[0] = heap.pop()
        self._sift_down(heap, 0)
        return min_val

    def _sift_up(self, heap, i):
        parent = (i - 1) // 2
        while i > 0 and heap[i][0] < heap[parent][0]:
            heap[i], heap[parent] = heap[parent], heap[i]
            i = parent
            parent = (i - 1) // 2

    def _sift_down(self, heap, i):
        min_index = i
        left = 2 * i + 1
        right = 2 * i + 2
        if left < len(heap) and heap[left][0] < heap[min_index][0]:
            min_index = left
        if right < len(heap) and heap[right][0] < heap[min_index][0]:
            min_index = right
        if i != min_index:
            heap[i], heap[min_index] = heap[min_index], heap[i]
            self._sift_down(heap, min_index)

    @track_time
    def count_empty_rooms(self):
        if sum(self.guests_per_channel.values()) > self.extreme_input_threshold:
            return "Infinite (too large to count)"
        else:
            return max(0, self.highest_occupied_room - len(self.rooms))

    def suggest_rooms(self, count):
        count = int(count)
        suggested = []
        room = 1
        while len(suggested) < count:
            if room not in self.rooms and room not in self.removed_rooms:
                suggested.append(room)
            room += 1
        return suggested

    def memory_usage(self):
        return sum(sys.getsizeof(obj) for obj in vars(self).values())

    def get_function_times(self):
        return {func: f"{time:.6f}" for func, time in self.function_times.items()}

    # @track_time
    # def write_to_file(self, filename):
    #     with open(filename, 'w', newline='') as file:
    #         writer = csv.writer(file)
    #         writer.writerow(["Room Number", "Channel", "Status", "Guest Info"])
    #         for room, info in sorted(self.rooms.items()):
    #             status = "Removed" if room in self.removed_rooms else "Occupied"
    #             channel = info['manual_channel'] if info['channel'] == "Manual" else info['channel']
    #             writer.writerow([room, channel, status, info['guest_info']])
    #     return f"Data written to {filename}"

    def channel_to_vehicle_numbers(self, channel):
        # แปลงช่องทางเป็นรหัสยานพาหนะ
        channel_order = ["Original", "Bus", "Train", "Plane", "Ship"]
        vehicle_numbers = [1] * 5  # เริ่มต้นด้วย [1, 1, 1, 1, 1]
        if channel in channel_order:
            index = channel_order.index(channel)
            vehicle_numbers[index] = index + 1
        return f"no_{'_'.join(map(str, vehicle_numbers))}"
    @track_time
    def write_to_file(self):
        print("Preparing data for file writing")
        sorted_rooms = self.sort_rooms()
        print(f"Total rooms to write: {len(sorted_rooms)}")

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Room Number", "Channel Info"])
        
        for room in sorted_rooms:
            if room not in self.removed_rooms:
                info = self.rooms[room]
                if info['channel'] == "Manual":
                    channel_info = f"Manual - {info['manual_channel']}"
                else:
                    channel_info = self.channel_to_vehicle_numbers(info['channel'])
                writer.writerow([room, channel_info])

        print("Data preparation complete")
        return output.getvalue()


    @track_time
    def get_hotel_status(self):
        total_guests = sum(self.guests_per_channel.values())
        occupied_channels = sum(1 for guests in self.guests_per_channel.values() if guests > 0)
        empty_rooms = self.count_empty_rooms()

        status = f"""
# Hilbert's Infinite Hotel Status

## Overview
- **Total Guests:** {total_guests}
- **Occupied Channels:** {occupied_channels} out of {len(self.channels)}
- **Total Occupied Rooms:** {len(self.rooms)}
- **Highest Occupied Room:** {self.highest_occupied_room}
- **Empty Rooms** (up to highest occupied): {empty_rooms}
- **Removed Rooms:** {len(self.removed_rooms)}\n
## Guests per Channel

| Channel | Guests |
|---------|--------|
"""
        
        for channel, guests in self.guests_per_channel.items():
            if guests > 0:
                status += f"| {channel:<7} | {guests:<6} |\n"

        status += "\n## Manual Rooms\n\n"
        manual_rooms = [room for room, info in self.rooms.items() if info['channel'] == "Manual"]
        if manual_rooms:
            status += "| Room Number | Guest Info | Channel |\n"
            status += "|-------------|------------|--------|\n"
            for room in manual_rooms:
                info = self.rooms[room]
                status += f"| {room:<11} | {info['guest_info']:<10} | {info['manual_channel']:<7} |\n"
        else:
            status += "No manually added rooms.\n"

        return status
