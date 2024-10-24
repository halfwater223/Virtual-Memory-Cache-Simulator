# Author: Xiaohao Xia

import numpy as np
from collections import OrderedDict


class CacheSystem:
    def __init__(self, levels_size=None, levels=3, line_size=64, n_way=2):
        if levels_size is None:
            # Example sizes: 32KiB for L1, 256KiB for L2, 2MiB for L3
            levels_size = [32 * 1024, 256 * 1024, 2 * 1024 * 1024]
        self.cache_levels = [
            SetAssociativeCache(i+1, size, line_size, n_way) for i, size in enumerate(levels_size)]

        self.n_way = n_way
        self.number_levels = levels
        self.levels_size = levels_size
        self.line_size = line_size

    def configure_cache(self, l1_size, l2_size, l3_size, n_way):
        self.levels_size = [l1_size, l2_size, l3_size]
        self.n_way = n_way
        self.reset_caches()

    def reset_caches(self):
        self.cache_levels = [
            SetAssociativeCache(i+1, size, self.line_size, self.n_way) for i, size in enumerate(self.levels_size)]

    def check_hit(self, address):
        for level, cache in enumerate(self.cache_levels):
            is_hit, levrl = cache.check_hit(address)
            if is_hit:
                return is_hit, levrl
        return None, None

    def read_data(self, address):
        for level, cache in enumerate(self.cache_levels):
            # check each level of caches
            data = cache.read_data(address)
            if data is not None:
                print(f"Address{address:#x} hits in L{level+1}")
                for upper_level in range(level):
                    self.cache_levels[upper_level].write_data(address, data)  # Update L1 Cache
                return data
            else:
                print(f"Address{address} misses in L{level+1}")
        return None

    def write_data(self, address, data):
        # Write to all levels of cache and memory
        for level in self.cache_levels:
            level.write_data(address, data)

    def load_block(self, address, block):
        for level, cache in enumerate(self.cache_levels):
            cache.write_block(address, block)


class CacheSet:
    def __init__(self, n_way, block_size=16):
        self.entries = OrderedDict()  # Assume that each cache line is managed with an OrderedDict
        self.n_way = n_way
        self.block_size = block_size

    def check_hit(self, tag):
        return tag in self.entries

    def access(self, tag):
        if tag in self.entries:
            # Move the recently accessed item to the end (mark it as recently used)
            self.entries.move_to_end(tag)
            return self.entries[tag]  # Cache hit
        else:
            return None  # Cache miss

    def add_or_update(self, tag, block):
        if not isinstance(block, dict):
            raise ValueError("Block data must be a dictionary")
        if len(block) > self.block_size:
            raise ValueError("Block data exceeds allowed size")
        if tag in self.entries:
            # If the cache line already exists, update the data and move it to the end of the ordered dictionary
            self.entries[tag] = block
            self.entries.move_to_end(tag)
        else:
            # If the cache line does not exist, add a new cache line
            # If maximum capacity has been reached, remove the oldest cache line (LRU policy)
            if len(self.entries) >= self.n_way:
                self.entries.popitem(last=False)
            self.entries[tag] = block

    def get_block(self, tag):
        return self.entries.get(tag, None)

    def write_data(self, tag, block_offset, data):
        if tag in self.entries:
            self.entries[tag][block_offset] = data
        else:
            return False

    def read_data(self, tag, offset):
        return self.entries[tag].get(offset, None)

class SetAssociativeCache:
    def __init__(self, level, size, line_size, n_way, block_size=16, cache_type="set_associative"):
        self.n_way = n_way
        self.line_size = line_size
        self.num_sets = 1 if cache_type == "fully_associative" else size // (line_size * n_way)
        self.block_size = block_size
        self.cache_sets = [CacheSet(n_way, block_size) for _ in range(self.num_sets)]
        self.cache_type = cache_type  # "direct_mapped", "fully_associative", "set_associative"
        self.offset_bits = self.block_size.bit_length() - 1
        self.index_bits = self.num_sets.bit_length() - 1
        self.level = level

    def _get_set_index(self, address):
        if self.cache_type in ["direct_mapped", "set_associative"]:
            index = (address >> self.offset_bits) & ((1 << self.index_bits) - 1)
            return index
        else:  # "fully_associative"
            return 0

    def get_tag(self, address):
        if self.cache_type == "fully_associative":
            return address // self.line_size
        else:  # "direct_mapped" or "set_associative"
            set_index = self._get_set_index(address)
            tag = address >> (set_index.bit_length() + self.block_size.bit_length() - 1)
            return tag

    def get_offset(self, address):
        print(f"offset = {address % self.block_size}")
        return address % self.block_size

    def get_set(self, address):
        set_index = self._get_set_index(address)
        return {hex(key): value for key, value in self.cache_sets[set_index].entries.items()}

    def check_hit(self, address):
        set_index = self._get_set_index(address)
        tag = self.get_tag(address)
        return self.cache_sets[set_index].check_hit(tag), self.level

    def write_block(self, address, block):
        if not isinstance(block, dict) or len(block) > self.block_size:
            raise ValueError("Invalid block size or type")
        set_index = self._get_set_index(address)
        tag = self.get_tag(address)
        self.cache_sets[set_index].add_or_update(tag, block)

    def read_data(self, address):
        data = None
        if self.check_hit(address):
            set_index = self._get_set_index(address)
            tag = self.get_tag(address)

            block_offset = self.get_offset(address)

            data = self.cache_sets[set_index].read_data(tag, block_offset)
        return data

    def write_data(self, address, data):
        set_index = self._get_set_index(address)
        tag = self.get_tag(address)
        block_offset = self.get_offset(address)
        # 更新缓存行中特定偏移量的数据

        self.cache_sets[set_index].write_data(tag, block_offset, data)

    def get_block(self, address):
        set_index = self._get_set_index(address)
        tag = self.get_tag(address)
        return self.cache_sets[set_index].get_block(tag)
