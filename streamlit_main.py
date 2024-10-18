import streamlit as st
from hilbert import *
import pandas as pd

def main():
    st.set_page_config(page_title="Hilbert Nuanua Infinite Hotel", page_icon="🏨", layout="wide")
    
    st.title("🏨 Hilbert Nuanua Infinite Hotel")
    
    if 'hotel' not in st.session_state:
        st.session_state.hotel = Hilberts()
    
    hotel = st.session_state.hotel

    st.sidebar.title("Operations")
    operation = st.sidebar.radio(
        "Choose an operation:",
        ["Initialize Hotel", "Add Guests", "Manage Rooms", "Hotel Status", "File Operations"]
    )

    if operation == "Initialize Hotel":
        st.header("Initialize Hotel with Guests")
        num_guests = st.number_input("Enter the number of initial guests:", min_value=1, step=1)
        if st.button("Initialize"):
            with st.spinner("Initializing hotel..."):
                start_time = time_module.perf_counter()
                result = hotel.add_initial_guests(num_guests)
                end_time = time_module.perf_counter()
            st.success(result)
            st.info(f"Operation completed in {end_time - start_time:.6f} seconds")

    elif operation == "Add Guests":
        st.header("Add Guests to Channels")
        channels = ["Bus", "Train", "Plane", "Ship"]
        col1, col2 = st.columns(2)
        with col1:
            channel = st.selectbox("Select channel:", channels)
        with col2:
            num_guests = st.number_input(f"Number of guests for {channel} channel:", min_value=1, step=1)
        if st.button("Add Guests"):
            with st.spinner("Adding guests..."):
                start_time = time_module.perf_counter()
                result = hotel.add_new_guests(channel, num_guests)
                end_time = time_module.perf_counter()
            st.success(result)
            st.info(f"Operation completed in {end_time - start_time:.6f} seconds")

    elif operation == "Manage Rooms":
        st.header("Manage Rooms")
        action = st.radio("Choose an action:", ["Add Room Manually", "Remove Room", "Find Room", "Sort Rooms", "Move Guests"])
        
        if action == "Add Room Manually":
            col1, col2, col3 = st.columns(3)
            with col1:
                room_number = st.number_input("Room number:", min_value=1, step=1)
            with col2:
                guest_info = st.text_input("Guest info:")
            with col3:
                channel = st.text_input("Channel:")
            if st.button("Add Room"):
                with st.spinner("Adding room..."):
                    start_time = time_module.perf_counter()
                    result = hotel.add_room_manual(room_number, guest_info, channel)
                    end_time = time_module.perf_counter()
                st.success(result)
                st.info(f"Operation completed in {end_time - start_time:.6f} seconds")
        
        elif action == "Remove Room":
            room_number = st.number_input("Enter room number to remove:", min_value=1, step=1)
            if st.button("Remove Room"):
                with st.spinner("Removing room..."):
                    start_time = time_module.perf_counter()
                    result = hotel.remove_room(room_number)
                    end_time = time_module.perf_counter()
                st.success(result)
                st.info(f"Operation completed in {end_time - start_time:.6f} seconds")
        
        elif action == "Find Room":
            room_number = st.number_input("Enter room number to find:", min_value=1, step=1)
            if st.button("Find Room"):
                with st.spinner("Finding room..."):
                    start_time = time_module.perf_counter()
                    result = hotel.find_room(room_number)
                    end_time = time_module.perf_counter()
                st.success(result)
                st.info(f"Operation completed in {end_time - start_time:.6f} seconds")
        
        # elif action == "Sort Rooms":
        #     col1, col2 = st.columns(2)
        #     with col1:
        #         start = st.number_input("Start from:", min_value=0, step=1)
        #     with col2:
        #         count = st.number_input("Number of rooms to display:", min_value=1, step=1)
        #     if st.button("Sort Rooms"):
        #         with st.spinner("Sorting rooms..."):
        #             start_time = time_module.perf_counter()
        #             result = hotel.sort_rooms(start, count)
        #             end_time = time_module.perf_counter()
        #         st.write("Sorted Rooms:")
        #         st.write(result)
        #         st.info(f"Operation completed in {end_time - start_time:.6f} seconds")
        elif action == "Sort Rooms":
            st.subheader("Sort Rooms")
            col1, col2, col3 = st.columns(3)
            with col1:
                chunk_size = st.number_input("Chunk size:", min_value=1000, value=1000000, step=1000)
            with col2:
                start = st.number_input("Start from:", min_value=0, step=1)
            with col3:
                count = st.number_input("Number of rooms to display:", min_value=1, max_value=1000, value=20, step=1)
            
            if st.button("Sort Rooms"):
                with st.spinner("Sorting rooms..."):
                    start_time = time_module.perf_counter()
                    all_sorted_rooms = hotel.sort_rooms(chunk_size)
                    end_time = time_module.perf_counter()
                    total_time = end_time - start_time
                    
                    # เลือกห้องตาม start และ count
                    displayed_rooms = all_sorted_rooms[start:start+count]
                    
                    st.write(f"Sorted Rooms (showing {len(displayed_rooms)} out of {len(all_sorted_rooms)} total rooms):")
                    if displayed_rooms:
                        df = pd.DataFrame({"Room Number": displayed_rooms})
                        st.dataframe(df)
                    else:
                        st.write("No rooms to display in the specified range.")
                    
                    st.info(f"Sorting completed in {total_time:.6f} seconds")
                    st.info(f"Total rooms sorted: {len(all_sorted_rooms)}")

                # แสดงข้อมูลเพิ่มเติมเกี่ยวกับการใช้หน่วยความจำ
                memory_usage = hotel.memory_usage()
                st.info(f"Current memory usage: {memory_usage} bytes")
  
        elif action == "Move Guests":
            col1, col2 = st.columns(2)
            with col1:
                from_room = st.number_input("From room number:", min_value=1, step=1)
            with col2:
                to_room = st.number_input("To room number:", min_value=1, step=1)
            if st.button("Move Guests"):
                with st.spinner("Moving guest..."):
                    start_time = time_module.perf_counter()
                    result = hotel.move_guest(from_room, to_room)
                    end_time = time_module.perf_counter()
                st.success(result)
                st.info(f"Operation completed in {end_time - start_time:.6f} seconds")

    elif operation == "Hotel Status":
        st.header("Hotel Status")
        if st.button("Show Hotel Status"):
            with st.spinner("Fetching hotel status..."):
                start_time = time_module.perf_counter()
                status = hotel.get_hotel_status()
                end_time = time_module.perf_counter()
            st.markdown(status)
            st.info(f"Operation completed in {end_time - start_time:.6f} seconds")
        
        if st.button("Count Empty Rooms"):
            with st.spinner("Counting empty rooms..."):
                start_time = time_module.perf_counter()
                empty_rooms = hotel.count_empty_rooms()
                end_time = time_module.perf_counter()
            st.success(f"Number of empty rooms: {empty_rooms}")
            st.info(f"Operation completed in {end_time - start_time:.6f} seconds")

    elif operation == "File Operations":
        st.header("File Operations")
        if st.button("Generate File"):
            with st.spinner("Generating file..."):
                    start_time = time_module.perf_counter()
                    file_content = hotel.write_to_file()
                    end_time = time_module.perf_counter()
                
            st.success("File generated successfully")
            st.info(f"Operation completed in {end_time - start_time:.6f} seconds")

            # สร้างปุ่มดาวน์โหลด
            st.download_button(
                    label="Download CSV",
                    data=file_content,
                    file_name="hotel_rooms.csv",
                    mime="text/csv"
            )

    st.sidebar.header("System Info")
    if st.sidebar.button("Show Memory Usage"):
        memory_usage = hotel.memory_usage()
        st.sidebar.info(f"Current memory usage: {memory_usage} bytes")

    if st.sidebar.button("Show Function Execution Times"):
        function_times = hotel.get_function_times()
        st.sidebar.subheader("Function Execution Times")
        for func, time in function_times.items():
            st.sidebar.text(f"{func}: {time} seconds")

if __name__ == "__main__":
    main()
