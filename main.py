from hilbert import *
import time as time_module

def process_command(hotel, command, args):
    operations = {
        'A': hotel.add_new_guests,
        'I': hotel.add_initial_guests, 
        'M': hotel.add_room_manual,
        'R': hotel.remove_room,
        'F': hotel.find_room,
        'S': hotel.sort_rooms,
        'C': hotel.count_empty_rooms,
        'W': hotel.write_to_file,
        'U': hotel.memory_usage,
        'V': hotel.move_guest,  
    }
    
    op = command[0]
    if op not in operations:
        return f"Invalid command: {op}"

    if op == 'A':
        if len(args) != 2:
            return "Error: Add new guests command requires channel name and number of guests"
        channel, num_guests = args
        return operations[op](channel, int(num_guests))
    elif op == 'I': 
        if len(args) != 1:
            return "Error: Initialize guests command requires number of guests"
        return operations[op](int(args[0]))
    elif op in ['M', 'R', 'F']:
        return operations[op](*args)
    elif op == 'W':
        return operations[op]()
    elif op == 'S':
        if len(args) != 1:
            return "Error: Sort rooms command requires chunk_size"
        return operations[op](int(args[0]))
    elif op == 'V':
        if len(args) != 2:
            return "Error: Move guest command requires from_room and to_room"
        return operations[op](int(args[0]), int(args[1]))
    else:
        return operations[op]()
    
def main():
    hotel = Hilberts()
    
    while True:
        print("\n*** Hilbert's Infinite Hotel Management System ***")
        print("1. Initialize hotel with guests (I)")
        print("2. Add guests to channels (A)")
        print("3. Add room manually (M)")
        print("4. Remove room (R)")
        print("5. Find a room (F)")
        print("6. Sort rooms (S)")
        print("7. Count empty rooms (C)")
        print("8. Write room data to file (W)")
        print("9. Show memory usage (U)")
        print("10. Show function execution times")
        print("11. Show hotel status")
        print("12. Move guest (V)")
        print("0. Exit")
        
        choice = input("Enter your choice (0-12): ")
        start_time = time_module.perf_counter()

        if choice == '0':
            print("Thank you for using Hilbert's Infinite Hotel Management System. Goodbye!")
            break
            
        elif choice == '1':
            num_guests = input("Enter the number of initial guests: ")
            print(process_command(hotel, "I", [num_guests]))
            
        elif choice == '2':
            channel = input("Enter one of these channels (Bus/Train/Plane/Ship): ")
            num_guests = input(f"Enter number of guests for {channel} channel: ")
            print(process_command(hotel, "A", [channel, num_guests]))
                
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
            chunk_size = input("Enter chunk size for sorting: ")
            print(process_command(hotel, "S", [chunk_size]))
            
        elif choice == '7':
            print(process_command(hotel, "C", []))
            
        elif choice == '8':
            filename = input("Enter filename to save room data: ")
            content = process_command(hotel, "W", [])
            if content:
                try:
                    with open(filename, 'w', newline='') as file:
                        file.write(content)
                    print(f"Data successfully written to {filename}")
                except IOError as e:
                    print(f"Error writing to file: {e}")
            else:
                print("No data to write.")

            
        elif choice == '9':
            print(f"Current memory usage: {process_command(hotel, 'U', [])} bytes")
            
        elif choice == '10':
            function_times = hotel.get_function_times()
            for func, time in function_times.items():
                print(f"{func}: {time} seconds")
 
        elif choice == '11':
            print(hotel.get_hotel_status())

        elif choice == '12':
            from_room = input("Enter the room number to move from: ")
            to_room = input("Enter the room number to move to: ")
            print(process_command(hotel, "V", [from_room, to_room]))
            
        else:
            print("Invalid choice. Please try again.")

        end_time = time_module.perf_counter()
        print(f"\nOperation completed in {end_time - start_time:.6f} seconds")
        print(f"Current memory usage: {hotel.memory_usage()} bytes")

if __name__ == "__main__":
    main()
