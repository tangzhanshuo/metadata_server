import hashlib
from typing import List, Dict, Optional, Tuple

def deterministic_hash(data: Tuple) -> int:
    """
    A deterministic hash function that will produce consistent results across different runs.
    
    Args:
        data: A tuple containing the data to hash
        
    Returns:
        A 64-bit integer hash value
    """
    # Convert all elements to strings and join with a delimiter
    # that won't appear in the data to avoid collisions
    str_data = "|".join(str(item) for item in data)
    
    # Use SHA-256 for a cryptographically secure hash
    hash_obj = hashlib.sha256(str_data.encode('utf-8'))
    
    # Convert to a 64-bit integer (8 bytes)
    # We use big-endian byte order for consistency
    return int.from_bytes(hash_obj.digest()[:8], byteorder='big')

def generate_block_hashes(token_sequence: List[int], block_size: int) -> List[int]:
    # Calculate how many full blocks we have
    num_full_blocks = len(token_sequence) // block_size
    
    # Initialize the list to store block hashes
    block_hashes = []
    
    # Process each full block
    prev_block_hash = None
    for i in range(num_full_blocks):
        # Get tokens for the current block
        start_idx = i * block_size
        end_idx = start_idx + block_size
        cur_block_tokens = token_sequence[start_idx:end_idx]
        
        # Determine if this is the first block
        is_first_block = (i == 0)
        
        # Handle None case for first block
        if is_first_block and prev_block_hash is None:
            prev_block_hash = 0  # Use a consistent value for None
        
        # Create a tuple and hash it deterministically
        block_hash = deterministic_hash((is_first_block, prev_block_hash, *cur_block_tokens, None))
        
        # Add the hash to our list
        block_hashes.append(block_hash)
        
        # Update prev_block_hash for the next iteration
        prev_block_hash = block_hash
    
    return block_hashes

class BlockPool:

    def __init__(self, num_blocks: int, block_size: int):
        self.num_blocks = num_blocks
        self.block_size = block_size
        self.blocks = []
        self.active_blocks = []

    def sync_status(self, blocks: Dict[int, int]) -> None:
        assert len(self.blocks) <= len(blocks) <= self.num_blocks

        self.blocks = list(blocks.keys())
        self.active_blocks = [block_id for block_id, status in blocks.items() if status != 0]

    def get_unused_blocks(self) -> int:
        return self.num_blocks - len(self.blocks)

    def get_free_blocks(self) -> int:
        return self.num_blocks - len(self.active_blocks)

    def get_hits(self, seq: List[int]) -> int:
        hashes = generate_block_hashes(seq, self.block_size)
        print(f"Tokens: {seq}, Hashes: {hashes}, blocks: {self.blocks}")
        for i in range(len(hashes)):
            if hashes[i] not in self.blocks:
                return i
        return len(hashes)