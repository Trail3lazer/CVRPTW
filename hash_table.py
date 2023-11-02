from typing import List, Generic
from models import KT, VT, Entry


class Dictionary(Generic[KT, VT]):
    def __init__(self, capacity=7):
        '''Creates a new dictionary with the given capacity O(n)

        Args:
            capacity: The initial capacity of the dictionary. Defaults to 7.
        Returns:
            Dictionary[KT,VT]): A new dictionary with the given capacity

        '''
        self._table: List[List[Entry[KT, VT]]] = [[] for i in range(0, capacity)]



    @property
    def entries(self) -> List[Entry[KT, VT]]:
        '''Returns a list of all entries in the dictionary O(n)

        Returns:
            (List[Entry[KT, VT]]): A list of all entries in the dictionary

        '''
        return [e for b in self._table if b for e in b]



    @property
    def values(self) -> List[VT]:
        '''Returns a list of all values in the dictionary O(n)

        Returns:
            (List[VT]): A list of all values in the dictionary

        '''
        return [e.value for e in self.entries]



    @property
    def keys(self) -> List[KT]:
        '''Returns a list of all keys in the dictionary O(n)

        Returns:
            (List[KT]): A list of all keys in the dictionary

        '''
        return [e.key for e in self.entries]



    def __str__(self):
        '''Returns a string representation of the dictionary O(n*log(n))
        
        Returns:
            (str): A string representation of the dictionary

        '''
        result = "{"

        # Sort the entries by key to order the values in the output string.
        # For each entry add the key and value indented on a new line.
        for e in sorted(self.entries, key=lambda e: e.key): # O(n*log(n))
            result += f'\n\r    {e.key}: "{e.value}",'
        
        # Add a closing brace on a new line.
        result += "\n}"
        return result



    def __getitem__(self, key: KT) -> VT:
        '''Returns the value associated with the given key O(n)
        
        Args:
            key: The key to search for
        Returns:
            (VT): The value associated with the given key
        
        '''
        for e in self._get_bucket(key):
            if e.key == key:
                return e.value



    def __setitem__(self, key: KT, value: VT):
        '''Sets the value associated with the given key O(n)
        
        Args:
            key: The key to set
            value: The value to set
            
        '''
        bucket = self._get_bucket(key)

        # If the bucket length is greater than the table length, 
        # grow the dictionary and try again.
        if len(bucket) >= len(self._table):
            self._grow()
            self[key] = value

        # Otherwise set the entry.
        else:
            # If the bucket already contains the key, update the value.
            for i, e in enumerate(bucket): # O(n)
                if e.key == key:
                    bucket[i].value = value
                    return
                
            # Otherwise, add the entry.
            bucket.append(Entry(key, value))



    def __len__(self):
        '''Returns the number of entries in the dictionary O(1)
        
        Returns:
            (int): The number of entries in the dictionary

        '''
        return len(self.entries)



    def __contains__(self, key: KT):
        '''Returns whether or not the dictionary contains the given key O(1)
        
        Args:
            key: The key to search for
        Returns:
            (bool): Whether or not the dictionary contains the given key
        
        '''
        # Try to get the key, if it fails, return false.
        try:
            self[key]
            return True
        except:
            return False



    def __delitem__(self, key: KT):
        '''Deletes the entry with the given key O(n)
        
        Args:
            key: The key to delete

        '''
        b = self._get_bucket(key)

        # If the bucket contains the key, delete it.
        for i, e in enumerate(b): # O(n)
            if e.key == key:
                del b[i]
                return



    def _bucket_idx(self, key: KT):
        '''Returns the index of the bucket for the given key O(1)
        
        Args:
            key: The key to search for
        Returns:
            (int): The index of the bucket for the given key
        
        '''
        # Hash the key and mod it by the table length to clamp it to less than the number of buckets.
        return hash(key) % len(self._table) # O(1)



    def _get_bucket(self, key: KT):
        '''Returns the bucket for the given key O(1)
        
        Args:
            key: The key to search for
        Returns:
            (List[Entry[KT, VT]]): The bucket for the given key
        
        '''
        idx = self._bucket_idx(key)
        return self._table[idx]



    def _grow(self):
        '''Grows the dictionary to the next prime number O(n)'''
        
        cur_cap = len(self._table)
        capacity = self._next_prime(cur_cap)

        # Create a new table with the number of buckets being equal to the new capacity
        self._table = [[] for i in range(0, capacity)]

        # Reassign all entries into the new table
        for e in self.entries: # O(n)
            self[e.key] = e.value



    def _next_prime(self, current_capacity: int):
        '''Returns the next prime number after the given capacity O(n)
        
        Args:
            current_capacity: The current capacity of the dictionary
        Returns:
            (int): The next prime number after the given capacity
        
        '''
        n = (current_capacity * 2) + 1

        # If the number is not prime, increment it until it is.
        while not self._is_prime(n):
            n += 1
        return n



    def _is_prime(self, n: int):
        '''Returns whether or not the given number is prime O(sqrt(n))
        
        Args:
            n: The number to check
        Returns:
            (bool): Whether or not the given number is prime
            
        '''
        divisor = 2
        inc = 1

        # Check if the number is divisible by any number less than it's square root.
        while divisor**2 <= n:

            # If the number is divisible by the divisor, it is not prime.
            if n % divisor == 0:
                return False
            
            # Otherwise, increment the divisor by 2 (or 1 in the first case to make the divisor odd thereafter).
            divisor = divisor + inc
            inc = 2
            
        return n > 1
