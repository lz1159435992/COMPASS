size_t seed(size_t size, size_t alignment) {
  if (likely(size <= 4096)) {
    return sz_s2u_lookup(size);}
  if (unlikely(size > 8070450532247928832)) {
    return 0;} ...
  size_t x = (size<<1) - 1;@\Suppressnumber@
    @\Reactivatenumber{7}@  
  ||*x = (unsigned)((8 * sizeof(x) - 1) ^*||@\Suppressnumber@ 
                        ||*__builtin_clzll(x));*||@\Reactivatenumber{8}@  
  size_t lg_delta = x < 7 ? LG_QUANTUM : x - @\Suppressnumber@ 
                        SC_LG_NGROUP - 1; ...@\Reactivatenumber{9}@  
}