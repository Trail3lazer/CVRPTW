from typing import List, TypeVar, Generic

KT = TypeVar('KT')
VT = TypeVar('VT')

class Entry(Generic[KT,VT]):
    key: KT
    value: VT
    
class Dictionary(Generic[KT,VT]): 
    def __init__(self, capacity=7):
        self._map: List[List[Entry[KT,VT]]] = capacity * [None]
    
    @property
    def entries(self) -> List[Entry[KT,VT]]:
        return [e for b in self._map if b for e in b]
    
    @property
    def values(self) -> List[VT]:
        return [e.value for b in self._map if b for e in b]
    
    @property
    def keys(self) -> List[KT]:
        return [e.key for b in self._map if b for e in b]
    
    def __getitem__(self, key: KT) -> VT:
        for e in self._get_bucket(key):
            if e.key == key:
                return e

    def __setitem__(self, key: KT, value: VT):
        bucket = self._get_bucket(key)
        if len(bucket) >= len(self._map):
            self._grow()
            self[key] = value
        else:
            for i,e in enumerate(bucket):
                if e.key == key: 
                    bucket[i] = value; 
                    return
            bucket.append(Entry(key, value))
            
    def __len__(self):  
        return len(self.entries)
    
    def __contains__(self, key: KT):
        entry = self[key]
        return bool(entry)
        
    def __delitem__(self, key: KT):
        b = self._get_bucket(key)
        for i,e in enumerate(b):
            if e.key == key:
                b[i] = None
    
    def _bucket_idx(self, key: KT):
        return len(self._map) % hash(key)
    
    def _get_bucket(self, key: KT):
        return self._map[self._bucket_idx(key)]
    
    def _grow(self):
        cur_cap = self.len(self._map)
        capacity = self._next_prime(cur_cap)
        old = self.entries
        self._map = capacity * [None]
        for e in [b for b in self._map]:
            self[e.key] = e.value
    
    def _next_prime(self, current_capacity: int):
        n = (current_capacity * 2) + 1 
        while not self._is_prime(n): 
            n += 1
        return n
    
    def _is_prime(self, n: int):
        divisor = 2
        inc = 1
        while divisor**2 <= n:
            if n % divisor is 0: return False
            divisor = divisor+inc
            inc = 2
        return n > 1
