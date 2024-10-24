# Author: Xiaohao Xia, Yinxuan Wu

class SetAssociativeCache:
    def __init__(self, cache_size, block_size, n):
        self.n = n  # Number of slots in each set (associativity)
        self.block_size = block_size  # Size of each block in bytes
        self.num_sets = cache_size // (self.block_size * self.n)  # Number of sets in the cache
        self.cache = [{} for _ in range(self.num_sets)]  # Cache data structure
        self.usage_order = [{} for _ in range(self.num_sets)]  # Tracks usage for LRU

    def _get_set_index(self, address):
        """ Get the index of the set for a given address. """
        # Extract the index bits from the address
        # Assuming the offset size is determined by the block size
        offset_bits = self.block_size.bit_length() - 1
        index_bits = self.num_sets.bit_length() - 1
        index = (address >> offset_bits) & ((1 << index_bits) - 1)
        return index

    def access_cache(self, address):
        """ Access the cache with the given address. """
        set_index = self._get_set_index(address)
        tag = address >> (set_index.bit_length() + self.block_size.bit_length() - 1)

        # Check if the tag is in the set
        if tag in self.cache[set_index]:
            # Cache hit: Update usage order
            self.usage_order[set_index][tag] = max(self.usage_order[set_index].values(), default=0) + 1
            return True  # Hit

        # Cache miss: Insert the tag into the cache
        if len(self.cache[set_index]) < self.n:
            # There is space in the set
            self.cache[set_index][tag] = True
        else:
            # Cache is full, replace the least recently used item
            lru_tag = min(self.usage_order[set_index], key=self.usage_order[set_index].get)
            del self.cache[set_index][lru_tag]
            del self.usage_order[set_index][lru_tag]
            self.cache[set_index][tag] = True

        # Update usage order for the new tag
        self.usage_order[set_index][tag] = max(self.usage_order[set_index].values(), default=0) + 1
        return False  # Miss

    def test_lru_effectiveness(self, test_addrs=None):
        """ Test the cache to ensure LRU is effective. """
        if not test_addrs:
            test_addrs = [0x10000000, 0x20000000, 0x30000000, 0x40000000, 0x10000000, 0x20000000, 0x50000000, 0x10000000]
        hit_miss = [self.access_cache(addr) for addr in test_addrs]
        return hit_miss


def test():

    # Testing the cache with n=2 and n=4
    cache_size = 2048  # 2KB
    block_size = 64  # 64 bytes

    # Test with n=2
    cache_2way = SetAssociativeCache(cache_size, block_size, 2)
    lru_test_2way = cache_2way.test_lru_effectiveness()

    # Test with n=4
    cache_4way = SetAssociativeCache(cache_size, block_size, 4)
    lru_test_4way = cache_4way.test_lru_effectiveness()

    print(f"lru_test_2way, lru_test_4way = \n"
          f"{lru_test_2way}, \n"
          f"{lru_test_4way}")


if __name__ == '__main__':
    test()
