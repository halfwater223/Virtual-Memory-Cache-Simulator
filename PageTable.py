# Author: Yinxuan Wu
# halfbottleofsoda@gmail.com

"""
The PageTable class supports mapping between 64-bit virtual addresses and 32-bit physical addresses.
In this class, the length of page numbers is not specifically restricted to 32 or 64 bits.
Python's dictionary keys can be any immutable (hashable) type, including long integers,
allowing for easy handling of 64-bit values.

The actual length of the page number depends on the size of the virtual address space and the page size.
For example, a 64-bit virtual address does not mean that the page number itself occupies 64 bits.
The page number is only a part of the virtual address, with the other part being the page offset.
The number of bits used for the page number will vary depending on the page size.
For instance, if the system has a page size of 4 KiB (2^12 bytes),
the number of bits used for the page number in a 64-bit virtual address would be 64 minus 12 bits for the page offset,
resulting in 52 bits.

When dealing with specific address mappings,
ensure that the size of the page number and physical page number matches your system architecture.
The PageTable class does not need to know the specific size of the page number,
as it simply maps a virtual page number to a physical page number without concern for their bit sizes.

In practical use, extracting page numbers based on the system's page table structure usually involves bit operations such as shifts and masks.
Below is a simple example demonstrating how to extract page numbers and page offsets from a 64-bit virtual address:
"""

class PageTable:
    def __init__(self, PAGE_SIZE_KiB=4):
        # Initialize an empty dictionary to hold the page table entries.
        # The keys are virtual page numbers, and the values are physical page numbers.
        self.entries = {}
        self.PAGE_SIZE_KiB = PAGE_SIZE_KiB
        self.page_size = PAGE_SIZE_KiB * 1024

    def add_entry(self, virtual_page_number, physical_page_number):
        # Adds an entry to the page table, mapping a virtual page number to a physical page number.
        self.entries[virtual_page_number] = physical_page_number

    def get_physical_page_number(self, virtual_page_number):
        # Retrieves the physical page number for a given virtual page number.
        # Returns None if the virtual page number is not in the page table.
        return self.entries.get(virtual_page_number, None)

    def remove_entry(self, virtual_page_number):
        # Removes the entry for the given virtual page number from the page table.
        if virtual_page_number in self.entries:
            del self.entries[virtual_page_number]

    def update_entry(self, virtual_page_number, new_physical_page_number):
        # Updates the physical page number for a given virtual page number.
        if virtual_page_number in self.entries:
            self.entries[virtual_page_number] = new_physical_page_number
        else:
            raise KeyError(f"No entry found "
                           f"for virtual page number: {virtual_page_number}")

    def get_page_table_entries(self):
        return {hex(key): hex(value) for key, value in self.entries.items()}

    def clear(self):
        # Clears all entries from the page table.
        self.entries.clear()


def test():
    # Example usage of the PageTable class
    PAGE_SIZE_KiB = 4
    page_table = PageTable(PAGE_SIZE_KiB)
    page_table.add_entry(0x01, 0xA0)  # Map virtual page 0x01 to physical page 0xA0

    physical_page = page_table.get_physical_page_number(0x01)  # Should return 0xA0
    print(f"The physical page for virtual page 0x01 is: {physical_page}")

    page_table.update_entry(0x01, 0xB0)  # Update mapping for virtual page 0x01 to physical page 0xB0
    page_table.remove_entry(0x01)  # Remove the entry for virtual page 0x01

    page_table.clear()  # Clear the page table


# Example functions to demonstrate extracting page numbers and offsets from virtual addresses


def get_page_number_and_offset(virtual_address, OFFSET_BITS, PAGE_SIZE):
    # The page number is the higher part of the virtual address
    page_number = hex(virtual_address >> OFFSET_BITS)
    # The page offset is the lower part of the virtual address
    offset = hex(virtual_address & (PAGE_SIZE - 1))
    return page_number, offset


def get_page_number(virtual_address, OFFSET_BITS):
    # Shift right to discard the offset and get the page number
    page_number = virtual_address >> OFFSET_BITS
    return page_number

def get_offset(virtual_address, PAGE_SIZE):
    # Use bitwise AND to get the offset within the page
    return virtual_address & (PAGE_SIZE - 1)

def test__():

    # Assume 4 KiB page size (2^12 bytes)
    PAGE_SIZE_KiB = 4
    PAGE_SIZE = PAGE_SIZE_KiB * 1024  # 4 KiB
    OFFSET_BITS = PAGE_SIZE.bit_length() - 1  # 12 bits for the offset

    # Example usage of the PageTable class
    page_table = PageTable(PAGE_SIZE_KiB)

    # Example virtual address (64 bits)
    virtual_address = 0x0000123456789ABC

    # Calculate the virtual page number and offset
    virtual_page_number = get_page_number(virtual_address, OFFSET_BITS)
    offset = get_offset(virtual_address, PAGE_SIZE)

    # Map the virtual page to a hypothetical physical page number (32 bits)
    physical_page_number = 0x00005678
    page_table.add_entry(virtual_page_number, physical_page_number)

    # Retrieve the physical page number using the virtual page number
    retrieved_physical_page_number = page_table.get_physical_page_number(virtual_page_number)
    print(f"Physical page number for virtual page {virtual_page_number}: {retrieved_physical_page_number}")

    # Combine the physical page number with the offset to get the physical address
    physical_address = (retrieved_physical_page_number << OFFSET_BITS) | offset
    print(f"Physical address corresponding to virtual address {hex(virtual_address)}: {hex(physical_address)}")

def test_virtual_to_physical_address_mapping():
    print(f"The following shows how to map from a virtual address to a physical address.")
    print()
    # Assume 4 KiB page size (2^12 bytes)
    PAGE_SIZE_KiB = 4  # 4 KiB pages
    PAGE_SIZE = PAGE_SIZE_KiB * 1024  # 4 KiB
    print(f"Consider that the size of each page is {PAGE_SIZE_KiB}*1024 Bytes = {PAGE_SIZE_KiB}KiB.")
    OFFSET_BITS = OFFSET_BITS = (PAGE_SIZE - 1).bit_length()  # 12 bits for the offset
    print(f"The number of bits required to address within a single page "
          f"is represented as OFFSET_BITS "
          f"= PAGE_SIZE.bit_length() - 1 = {PAGE_SIZE.bit_length()} - 1 = {OFFSET_BITS}")

    page_table = PageTable(PAGE_SIZE_KiB)

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
          f"= 2^{VIRTUAL_ADDRESS_BITS} / 2^{(PAGE_SIZE_KiB * 1024).bit_length()-1} "
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

    page_table.add_entry(virtual_page_number, physical_page_number)

    # Retrieve the physical page number using the virtual page number
    retrieved_physical_page_number = page_table.get_physical_page_number(virtual_page_number)
    # print(f"retrieved_physical_page_number = {retrieved_physical_page_number, hex(retrieved_physical_page_number)}")
    if retrieved_physical_page_number is not None:
        # Combine the physical page number with the offset to get the physical address
        # Use the Bitwise Operator (Bitwise OR, '|')
        physical_address = (retrieved_physical_page_number << OFFSET_BITS) | offset
        # or Use the Addition ('+'):
        physical_address_ = (retrieved_physical_page_number << OFFSET_BITS) + offset
        print(
            f"The Page Offset of the virtual address is added to the physical page address \n"
            f"to obtain the final physical address {hex(physical_address)} "
            f"corresponding to virtual address {hex(virtual_address)}: "
            # f", {hex(physical_address_)}"
        )
    else:
        print(f"Physical page number for virtual page {virtual_page_number} not found in the page table.")


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


if __name__ == '__main__':
    # test()
    # print()
    # test_()
    # print()
    # test__()
    # print()
    test_virtual_to_physical_address_mapping()


"""
To understand the code OFFSET_BITS = PAGE_SIZE.bit_length() - 1, it's important to comprehend the relationship 
between the page size (PAGE_SIZE) and the offset within the page (OFFSET_BITS):

1. Page Size (PAGE_SIZE):
In virtual memory systems, the page size is the fundamental unit of memory paging. For example, 
4 KiB (4096 bytes) is a common page size. The page size determines the amount of data each page can hold. 
In a page of 4 KiB, the addresses range from 0x000 to 0xFFF.

2. Bit Width of Page Offset (OFFSET_BITS):
Page offset refers to the displacement within the page to locate specific data. For instance, in a 4 KiB page, 
12 bits are needed to represent any number from 0 to 4095, as 2^12 equals 4096. In the address, 
the page offset is represented by the lowest bits, indicating the specific position within the page.
How to calculate the bit width of the page offset:
PAGE_SIZE.bit_length() returns the number of bits needed to represent the page size in bytes. 
For example, for 4096 (4 KiB), bit_length() returns 12 because 2^12 equals 4096. 
Since the range of the page offset is from 0 to one less than the page size (0x000 to 0xFFF in this example), 
we subtract 1 from the result of bit_length() to get the actual number of bits required for the offset.

In summary, the code OFFSET_BITS = PAGE_SIZE.bit_length() - 1 calculates the number of bits 
required to represent the page offset. This is crucial for correctly extracting the page number 
and page offset from a virtual address. In the case of a 4 KiB page, this means that 
the page offset occupies the lowest 12 bits of the address.
"""
