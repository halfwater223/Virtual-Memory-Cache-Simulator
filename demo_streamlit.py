# demo_streamlit.py
# Author: Yinxuan Wu
# halfbottleofsoda@gmail.com

import streamlit as st

from cache_system import CacheSystem
from memory_management_unit import MMU
from memory_management_unit import Memory
from PageTable import PageTable
from TestVirtualToPhysicalAddressMapping import test_virtual_to_physical_address_mapping
from TestVirtualToPhysicalAddressMapping import calculate_page_info
from TestNwaySetAssociativeCacheWithLRU import SetAssociativeCache

def main():
    PAGE_SIZE_KiB = 4  # 4 KiB pages

    # Initialize the page table
    page_table = PageTable(PAGE_SIZE_KiB)
    memory = Memory(size_byte=1024 * 1024 * 1024)

    # Add some entries to the page table (this would be done by the OS as part of memory management)
    page_table.add_entry(virtual_page_number=0x1111, physical_page_number=0x1101)
    page_table.add_entry(virtual_page_number=0x1112, physical_page_number=0x1102)

    # Add some entries to the page table (this would be done by the OS as part of memory management)
    page_table.add_entry(virtual_page_number=0x0001, physical_page_number=0x1001)
    page_table.add_entry(virtual_page_number=0x0002, physical_page_number=0x1002)

    cache_system = CacheSystem()
    # Initialize the MMU with the page table
    mmu = MMU(page_table, cache_system, memory)

    # Check if these variables have been initialized
    if "mmu" not in st.session_state:
        st.session_state.mmu = mmu

    demo(st.session_state.mmu)

def demo(mmu):
    # Page layout and input
    st.title("Virtual Memory and Cache Simulator")

    main_demo(mmu)

    address_translator_demo()

    n_way_cache_lru_demo()


def display_cache_operation(result):
    """
    Displays the result of the cache operation on the Streamlit interface.
    """
    if result['page_fault']:
        st.error("Page Fault occurred")
    else:
        st.success("Address translation successful")

    if result['cache_hit']:
        st.info(f"L{result['cache_hit']} Cache Hit")
    else:
        st.warning("Cache Miss")

    st.write(f"Physical Address: {hex(result['physical_address']) if result['physical_address'] is not None else 'None'}")


def main_demo(mmu):
    # Cache Configuration
    st.sidebar.header("Cache Configuration")
    # Allow user input of cache configuration
    l1_size = st.sidebar.number_input("L1 Cache Size", value=32 * 1024)
    l2_size = st.sidebar.number_input("L2 Cache Size", value=256 * 1024)
    l3_size = st.sidebar.number_input("L3 Cache Size", value=2 * 1024 * 1024)
    n_way = st.sidebar.number_input("N-Way Set Associative", value=2, min_value=1)

    if st.sidebar.button("Configure Cache"):
        # Configure the cache system
        mmu.cache_system.configure_cache(l1_size, l2_size, l3_size, n_way)
        st.sidebar.success("Cache Configured")

    st.header("Data Operations")
    # Data writing
    st.write(f"Writr Policy: Write-Through")
    st.write(f"Writr Miss Policy: Write-Allocate")
    write_address = st.text_input("Write to 64 bit Virtual Address (e.g., 0x1234567890ABCDEF)",
                                  value="0x1234567890ABCDEF")
    write_data = st.text_input("Data to Write")
    if st.button("Write Data"):
        # Check if write_data is empty
        if not write_data:
            print(f"memory={mmu.memory.storage}")
            st.error("Data to write cannot be empty.")
        else:
            try:
                # Remove the prefix 0x (if present) and convert the string to a hexadecimal number
                if write_address.startswith("0x") or write_address.startswith("0X"):
                    write_address = write_address[2:]
                write_address_hex = int(write_address, 16)
                # Use write_address_hex as address to handle write operations
                operation_result = mmu.process_virtual_address(write_address_hex, write_data)
                st.success(f"Data written to address 0x{write_address}")
                display_cache_operation(operation_result)
                st.sidebar.write("Page Table Entries:", format_page_table_entries(mmu.page_table.entries))
                # st.sidebar.write("L1 Cache:", mmu.cache_system.cache_levels[0].cache_sets)

            except ValueError:
                st.error("Please enter a valid hexadecimal address.")

    # Data reading
    read_address = st.text_input(
        "Read from 64 bit Virtual Address (e.g., 0x1234567890ABCDEF)", value="0x1234567890ABCDEF")
    if st.button("Read Data"):
        try:
            # Remove the prefix 0x (if present) and convert the string to a hexadecimal number
            if read_address.startswith("0x") or read_address.startswith("0X"):
                read_address = read_address[2:]
            read_address_hex = int(read_address, 16)
            # 使用 write_address_hex 作为地址处理写入操作
            st.write(f"Physical Address: "
                     f"{hex(mmu.translate_address(read_address_hex)) if mmu.translate_address(read_address_hex) is not None else 'None'}")
            operation_result = mmu.process_virtual_address(read_address_hex)
            if operation_result['data'] is not None:
                st.info(f"Data at address 0x{read_address}: {operation_result['data']}")
                display_cache_operation(operation_result)
            else:
                st.error("Data not found or Page Fault")
            st.sidebar.write("Page Table Entries:", format_page_table_entries(mmu.page_table.entries))
        except ValueError:
            st.error("Please enter a valid hexadecimal address.")


def address_translator_demo():
    st.header("Sub-Demo: Virtual to Physical Address Mapping Demo")
    with st.expander("Virtual to Physical Address Mapping Demo", expanded=True):
        PAGE_SIZE_KiB = st.number_input("Page Size (KiB)", min_value=1, value=4, step=1)
        BYTES_PER_PTE = st.number_input("Bytes Per Page Table Entry", min_value=1, value=4, step=1)
        virtual_address = st.text_input("Virtual Address in hexadecimal (e.g., 0x1234567890ABCDEF):",
                                        value="0x1234567890ABCDEF")
        physical_page_number = st.text_input(
            "Physical Page Number for the Virtual Address (hexadecimal, e.g., 0x12345):",
            value="0x12345")

        if st.button("Calculate"):
            try:
                va = int(virtual_address, 16)
                ppa = int(physical_page_number, 16)
                PAGE_SIZE, OFFSET_BITS, num_pages, page_table_size_bytes, offset, \
                    vpn, page_table, retrieved_ppn, physical_address = calculate_page_info(
                        PAGE_SIZE_KiB, BYTES_PER_PTE, va, ppa)

                st.write(f"PAGE_SIZE (in KiB): {PAGE_SIZE / 1024} KiB")
                st.write(f"OFFSET_BITS: {OFFSET_BITS}")
                st.write(f"Number of Pages: {num_pages}")
                st.write(f"Page Table Size (bytes): {page_table_size_bytes}")
                st.write(f"Page Offset of the Virtual Address: {hex(offset)}")
                st.write(f"Virtual Page Number (VPN): {hex(vpn)}")
                st.write("Page Table Entries:", format_page_table_entries(page_table["entries"]))
                st.write(f"Retrieved Physical Page Number: {hex(retrieved_ppn) if retrieved_ppn is not None else 'None'}")
                st.write(f"Physical Address: {hex(physical_address) if physical_address is not None else 'None'}")
            except ValueError:
                st.error("Invalid input. Please enter valid hexadecimal addresses.")

def format_page_table_entries(page_table_entries):
    return {hex(key): hex(value) for key, value in page_table_entries.items()}


def n_way_cache_lru_demo():
    st.header('Sub-Demo: N-Way Set Associative LRU Cache Simulator')

    # User input
    st.write(f"LRU Test Address: ")
    default_addrs = "0x10000000, 0x20000000, 0x30000000, 0x40000000, 0x10000000, 0x20000000, 0x50000000, 0x10000000"
    user_input = st.text_input('Enter Test Addresses (comma separated)', default_addrs)
    test_addrs = [int(addr.strip(), 16) for addr in user_input.split(',')] if user_input else default_addrs.split(',')

    st.write(f"LRU Test Address: ")
    st.write(f"\n{[hex(addr) for addr in test_addrs]}")

    cache_size = st.number_input('Cache Size (in bytes)', min_value=1024, value=2048, step=1024)
    block_size = st.number_input('Block Size (in bytes)', min_value=16, value=64, step=16)
    n1 = st.number_input('Associativity 1 (n-way)', min_value=1, value=2, step=1)
    n2 = st.number_input('Associativity 2 (n-way)', min_value=1, value=4, step=1)

    if st.button('Run LRU Test'):
        cache1 = SetAssociativeCache(cache_size, block_size, n1)
        lru_test_result1 = cache1.test_lru_effectiveness(test_addrs)
        cache2 = SetAssociativeCache(cache_size, block_size, n2)
        lru_test_result2 = cache2.test_lru_effectiveness(test_addrs)
        st.write(f"LRU Test Result: {lru_test_result1}")
        st.write(f"LRU Test Result: {lru_test_result2}")


if __name__ == '__main__':
    main()
