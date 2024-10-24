# Author: Yinxuan Wu
# halfbottleofsoda@gmail.com

import streamlit as st

from PageTable import PageTable


def get_page_number(virtual_address, OFFSET_BITS):
    # Shift right to discard the offset and get the page number
    page_number = virtual_address >> OFFSET_BITS
    return page_number


def get_offset(virtual_address, PAGE_SIZE):
    # Use bitwise AND to get the offset within the page
    return virtual_address & (PAGE_SIZE - 1)


def test_virtual_to_physical_address_mapping(virtual_address=None):
    st.write("The following shows how to map from a virtual address to a physical address.")

    print(f"The following shows how to map from a virtual address to a physical address.")
    print()
    # Assume 4 KiB page size (2^12 bytes)
    PAGE_SIZE_KiB = 4  # 4 KiB pages
    PAGE_SIZE = PAGE_SIZE_KiB * 1024  # 4 KiB
    print(f"Consider that the size of each page is {PAGE_SIZE_KiB}*1024 Bytes = {PAGE_SIZE_KiB}KiB.")
    OFFSET_BITS = (PAGE_SIZE - 1).bit_length()  # 12 bits for the offset
    print(f"The number of bits required to address within a single page "
          f"is represented as OFFSET_BITS "
          f"= PAGE_SIZE.bit_length() - 1 = {PAGE_SIZE.bit_length()} - 1 = {OFFSET_BITS}")

    print()
    # Example virtual address (64 bits)
    VIRTUAL_ADDRESS_BITS = 64
    print(f"Consider {VIRTUAL_ADDRESS_BITS}-bit virtual addresses.")
    virtual_address = 0x1234567890ABCDEF
    print(f"Consider the hexadecimal address {hex(virtual_address)} as an example.")

    # Calculate the number of pages in the virtual address space
    # 2^VIRTUAL_ADDRESS_BITS total addresses / (PAGE_SIZE_KB * 1024 bytes per KiB)
    num_pages = int(2 ** VIRTUAL_ADDRESS_BITS / (PAGE_SIZE_KiB * 1024))
    print(f"Given the {VIRTUAL_ADDRESS_BITS}-bit virtual addresses and "
          f"the size of each page is {PAGE_SIZE_KiB}KiB, "
          f"we gain the number of pages "
          f"= 2^{VIRTUAL_ADDRESS_BITS} / 2^{(PAGE_SIZE_KiB * 1024).bit_length() - 1} "
          f"= {num_pages} = {size_in_different_units(int(num_pages), 'power of two')}")
    size_in_different_units(int(num_pages), 'power of two')
    # Calculate the size of the page table
    BYTES_PER_PTE = 4  # 4 bytes per page table entry
    page_table_size_bytes = num_pages * BYTES_PER_PTE

    print()

    offset = get_offset(virtual_address, PAGE_SIZE)
    print(f"Given a virtual address {hex(virtual_address)} and PAGE_SIZE {PAGE_SIZE} bytes, "
          f"we computes the offset within the page. \n"
          f"This is done by performing a bitwise AND operation between the virtual address "
          f"and (PAGE_SIZE - 1). \n "
          f"Since PAGE_SIZE is a power of two, (PAGE_SIZE - 1) "
          f"generates a bitmask for the lower bits of the address. \n"
          f"The resulting offset is {hex(offset)}, which is the position within the page "
          f"where the actual data is located.")
    print()
    # Calculate the virtual page number and offset
    virtual_page_number = get_page_number(virtual_address, OFFSET_BITS)
    print(f"Given a virtual address {hex(virtual_address)} and OFFSET_BITS = {OFFSET_BITS}, "
          f"we shifts the address right by {OFFSET_BITS} bits. \n"
          "This operation discards the page offset and extracts the virtual page number. "
          f"The resulting virtual page number is {hex(virtual_page_number)}.")
    print()
    # Map the virtual page to a hypothetical physical page number (32 bits)
    PHYSICAl_ADDRESS_BITS = 32
    physical_page_number = 0x12345
    print(f"Consider this virtual page address {hex(virtual_page_number)} "
          f"mapped to a {PHYSICAl_ADDRESS_BITS}-bit physical page address {hex(physical_page_number)}.")

    page_table = PageTable()
    page_table.add_entry(virtual_page_number, physical_page_number)

    # Retrieve the physical page number using the virtual page number
    retrieved_physical_page_number = page_table.get_physical_page_number(virtual_page_number)
    # print(f"retrieved_physical_page_number = {retrieved_physical_page_number, hex(retrieved_physical_page_number)}")

    if retrieved_physical_page_number is not None:
        physical_address = (retrieved_physical_page_number << OFFSET_BITS) | offset
        st.write(
            "The Page Offset of the virtual address is added to the physical page address "
            "to obtain the final physical address", hex(physical_address),
            "corresponding to virtual address", hex(virtual_address)
        )
    else:
        st.write(f"Physical page number for virtual page {virtual_page_number} not found in the page table.")


def size_in_different_units(size_bytes, size_type=None):
    """
    Prints the size in different units (bytes, KiB, MiB, KB, MB, 2^N, etc.).
    """
    size_bytes = int(size_bytes)
    # Constants
    KILOBYTE = 1024
    MEGABYTE = KILOBYTE * 1024
    GIGABYTE = MEGABYTE * 1024
    TERABYTE = GIGABYTE * 1024

    # Decimal units
    KB = 1000
    MB = KB * 1000
    GB = MB * 1000
    TB = GB * 1000

    if not size_type:
        # Print in different units
        print(f"Size in bytes: {size_bytes} bytes")
        print(f"Size in KiB (Kibibytes): {size_bytes / KILOBYTE} KiB")
        print(f"Size in MiB (Mebibytes): {size_bytes / MEGABYTE} MiB")
        print(f"Size in GiB (Gibibytes): {size_bytes / GIGABYTE} GiB")
        print(f"Size in TiB (Tebibytes): {size_bytes / TERABYTE} TiB")
        print(f"Size in KB (Kilobytes): {size_bytes / KB} KB")
        print(f"Size in MB (Megabytes): {size_bytes / MB} MB")
        print(f"Size in GB (Gigabytes): {size_bytes / GB} GB")
        print(f"Size in TB (Terabytes): {size_bytes / TB} TB")
        print(f"Size in power of two (2^N): 2^{size_bytes.bit_length() - 1}")
    elif size_type == 'power of two':
        # print(f"Size in power of two (2^N): 2^{size_bytes.bit_length() - 1}")
        return f"2^{size_bytes.bit_length() - 1}"


def calculate_page_info(PAGE_SIZE_KiB, BYTES_PER_PTE, virtual_address, physical_page_number):
    PAGE_SIZE = PAGE_SIZE_KiB * 1024
    OFFSET_BITS = (PAGE_SIZE - 1).bit_length()

    VIRTUAL_ADDRESS_BITS = 64
    num_pages = int(2 ** VIRTUAL_ADDRESS_BITS / PAGE_SIZE)
    num_pages_string = size_in_different_units(int(num_pages), 'power of two')

    page_table_size_bytes = num_pages * BYTES_PER_PTE
    page_table_size_bytes_string = size_in_different_units(int(page_table_size_bytes), 'power of two')

    offset = virtual_address & (PAGE_SIZE - 1)
    virtual_page_number = virtual_address >> OFFSET_BITS

    # Assuming a simple page table class for demonstration
    page_table = {"entries": {}}
    page_table["entries"][virtual_page_number] = physical_page_number
    retrieved_physical_page_number = page_table["entries"].get(virtual_page_number, None)

    physical_address = None
    if retrieved_physical_page_number is not None:
        physical_address = (retrieved_physical_page_number << OFFSET_BITS) | offset

    return PAGE_SIZE, OFFSET_BITS, num_pages_string, page_table_size_bytes_string, \
       offset, virtual_page_number, page_table, \
       retrieved_physical_page_number, physical_address


test_virtual_to_physical_address_mapping()