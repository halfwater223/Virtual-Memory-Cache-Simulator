# Author: Junfei Zhang

import numpy as np
import streamlit as st

from PageTable import PageTable
from cache_system import CacheSystem


class MMU:      # Memory Management Unit
    def __init__(self, page_table, cache_system, memory, tlb=None):
        self.tlb = tlb or {}  # A simple dictionary can act as a TLB for this example
        self.page_table = page_table
        self.cache_system = cache_system
        self.memory = memory
        self.is_palt = False

    def process_virtual_address(self, virtual_address, input_data=None):
        """
        Accepts a 64-bit virtual address from the CPU, performs address translation,
        and handles data based on whether it's a read or write operation.
        """
        operation_result = {
            'cache_hit': False,
            'page_fault': False,
            'physical_address': None,
            'data': None
        }
        try:
            physical_address = self.translate_address(virtual_address)
            operation_result['page_fault'] = self.is_palt
            operation_result['physical_address'] = physical_address
            # Check if cache hits
            cache_hit, level = self.cache_system.check_hit(physical_address)
            if cache_hit:
                operation_result['cache_hit'] = level
                if input_data is None:  # Read operation
                    operation_result['data'] = self.cache_system.read_data(physical_address)
                    return operation_result
                else:   # Write operation
                    self.cache_system.write_data(physical_address, input_data)
                    self.memory.write_data(physical_address, input_data)  # Write-Through: Write to main memory
                    return operation_result
            else:   # Cache miss
                operation_result['cache_hit'] = False
                if input_data is None:  # Cache miss and read operation
                    # Load page from memory to cache
                    self.cache_system.load_block(physical_address, self.memory.get_block(physical_address))
                    operation_result['data'] = self.cache_system.read_data(physical_address)
                    return operation_result
                else:   # Cache miss and write operation
                    # Write Allocate: also load page from memory into cache, then write
                    self.cache_system.load_block(physical_address, self.memory.get_block(physical_address))
                    self.cache_system.write_data(physical_address, input_data)
                    self.memory.write_data(physical_address, input_data)    # Write-Through: Write to main memory
                    return operation_result
        except MemoryError as e:
            # Handle page fault or other memory errors
            operation_result['page_fault'] = True
            st.error(f"Page fault occurred: {e}")
            return operation_result

    def translate_address(self, virtual_address):
        # First, check in the TLB
        self.is_palt = False
        if virtual_address in self.tlb:
            return self.tlb[virtual_address]
        page_size = self.page_table.page_size
        # Calculate the offset within the page.
        offset = virtual_address & (page_size - 1)
        # Calculate the virtual page number.
        offset_bits = (page_size - 1).bit_length()
        virtual_page_number = virtual_address >> offset_bits
        print(f"virtual_page_number={hex(virtual_page_number)}")
        # Retrieve the physical page number from the page table.
        physical_page_number = self.page_table.get_physical_page_number(virtual_page_number)
        if physical_page_number is None:
            # Handle page fault if the physical page number is not found
            self.is_palt = True
            physical_page_number = self.handle_page_fault(virtual_page_number)
        # Ensure that the physical_page_number is not None before calculating physical_address
        if physical_page_number is not None:
            # Calculate the physical address by combining the physical page number with the offset.
            physical_address = (physical_page_number << offset_bits) | offset
        else:
            # Handle the case where physical_page_number is still None after handling page fault
            raise MemoryError(
                f"Failed to retrieve a valid physical page number for virtual page number: {virtual_page_number:#x}")
        # Update the TLB
        self.update_tlb(virtual_address, physical_address)
        return physical_address

    def handle_page_fault(self, virtual_page_number):
        # This function should interact with the operating system to handle page faults.
        # For the purpose of this simulation, we'll just generate a random physical page number using numpy.
        print(f"Handling page fault for virtual page number: {virtual_page_number:#x}")
        # Simulate the OS finding a free physical frame
        # For the sake of this example, let's assume physical addresses range from 0x1000 to 0xFFFF
        physical_page_number = np.random.randint(0x1000, 0xFFFFF)  # numpy's upper bound is exclusive
        print(f"OS find the physical page number {physical_page_number:#x}")
        # Simulate adding the new mapping to the page table
        self.page_table.add_entry(virtual_page_number, physical_page_number)
        return physical_page_number

    def update_tlb(self, virtual_address, physical_address):
        # This is a simplified example of updating the TLB.
        # A real TLB would have a fixed size and use a replacement policy.
        self.tlb[virtual_address] = physical_address
        return physical_address

    def lookup_tlb(self, virtual_address):
        # Check if the virtual address is in the TLB
        pass

    def manage_caches(self, physical_address):
        # Manage cache coherence after page translation
        pass

    def set_page_protection(self, virtual_page_number, protection_flags):
        # Set protection flags for a virtual page
        pass

    def share_page(self, source_virtual_address, target_virtual_address):
        # Share a virtual page between different processes or threads
        pass


class Memory:
    def __init__(self, size_byte):
        # self.data = bytearray(size_byte)
        self.size_byte = size_byte
        self.storage = {}

    def read(self, physical_address):
        data = self.storage.get(physical_address, None)
        if data is None:
            # Handle page fault
            return None
        print(f"Read Memory={self.storage}")
        return data

    def write(self, physical_address, data):
        self.storage[physical_address] = data
        print(f"Memory={self.storage}")

    def get_block(self, address, block_size=16):
        block_start_address = address - (address % block_size)
        block_data = {i: b"data" + bytes([i]) for i in range(block_size)}
        self.storage[address] = block_data
        return block_data

    def write_data(self, address, data):
        self.storage[address] = data

def test_get_physical_address():
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

    # Given a virtual address, translate it to a physical address
    try:
        virtual_address = 0x1112000  # Example virtual address

        physical_address = mmu.translate_address(virtual_address)
        print(f"physical_address={physical_address}")
        print(f"Virtual address {virtual_address:#x} maps to physical address {physical_address:#x}")
    except MemoryError as e:
        print(e)

    try:
        virtual_address = 0x0002000  # Example virtual address
        physical_address = mmu.translate_address(virtual_address)
        print(f"Virtual address {virtual_address:#x} maps to physical address {physical_address:#x}")
    except MemoryError as e:
        print(e)

    try:
        virtual_address = 0x0001000  # Example virtual address
        physical_address = mmu.translate_address(virtual_address)
        print(f"Virtual address {virtual_address:#x} maps to physical address {physical_address:#x}")
    except MemoryError as e:
        print(e)

    try:
        virtual_address = 0x0011000  # Example virtual address
        physical_address = mmu.translate_address(virtual_address)
        print(f"Virtual address {virtual_address:#x} maps to physical address {physical_address:#x}")
    except MemoryError as e:
        print(e)

    try:
        virtual_address = 0x1234567890ABCDEF  # Example virtual address
        physical_address = mmu.translate_address(virtual_address)
        print(f"Virtual address {virtual_address:#x} maps to physical address {physical_address:#x}")
    except MemoryError as e:
        print(e)


if __name__ == '__main__':
    test_get_physical_address()
