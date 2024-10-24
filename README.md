# Virtual Memory and Cache Simulator

This project provides a **Virtual Memory and Cache Simulator** built using **Python** and **Streamlit**. The simulator supports the configuration and demonstration of virtual memory management and cache systems, including an N-Way Set Associative Cache with Least Recently Used (LRU) replacement policy.

## Features

- **Virtual Memory to Physical Memory Translation**: Map 64-bit virtual addresses to physical addresses using a page table.
- **Cache System Simulation**: Configure L1, L2, and L3 cache sizes, block size, and associativity for N-Way Set Associative caches.
- **Write-Through Cache Policy**: Implemented for both data read and write operations.
- **LRU (Least Recently Used) Cache Replacement Policy**: Simulate the behavior of LRU in different associativity settings.
- **Interactive GUI**: Built with **Streamlit**, allowing real-time configuration and operation demonstration.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Simulator Demos](#simulator-demos)
  - [Data Operations](#data-operations)
  - [Virtual to Physical Address Mapping](#virtual-to-physical-address-mapping)
  - [N-Way Set Associative LRU Cache Simulator](#n-way-set-associative-lru-cache-simulator)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Python 3.x
- Pip
- Streamlit (`pip install streamlit`)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/virtual-memory-cache-simulator.git
2. Navigate into the project directory:
   ```bash
   cd virtual-memory-cache-simulator
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
4. Run the simulator:
   ```bash
   streamlit run demo_streamlit.py

## Usage
Once you have run the Streamlit app, open your browser to **localhost:8501**. The interface provides an intuitive way to explore different configurations for memory and cache simulation.

## Simulator Demos

### Data Operations
- Write Data: Simulate writing data to a virtual address and watch how it is translated to a physical address and cached.
- Read Data: Simulate reading data from a virtual address and check whether it results in a cache hit or miss.

### Virtual to Physical Address Mapping
This demo shows how virtual addresses are translated to physical addresses using a page table. You can input the page size and other configurations to view the translated results.

### N-Way Set Associative LRU Cache Simulator
Test the effectiveness of the LRU (Least Recently Used) policy by entering a sequence of memory addresses. You can configure cache sizes and the degree of associativity (N-Way).

## Project Structure

  ```
  ├── cache_system.py               # Handles the cache system and operations
  ├── demo_streamlit.py             # Main Streamlit app for the simulator
  ├── memory_management_unit.py     # Simulates the MMU and manages virtual-to-physical translation
  ├── PageTable.py                  # Page table management for virtual memory
  ├── TestNwaySetAssociativeCacheWithLRU.py  # Test file for the N-Way Cache with LRU
  ├── TestVirtualToPhysicalAddressMapping.py # Test file for virtual to physical mapping demo
  └── README.md                     # This file
  ```


## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue if you have suggestions for improvements.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

