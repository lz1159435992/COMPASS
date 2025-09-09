size_t seed_o(size_t size, size_t alignment) {@\Suppressnumber@ 
  ...@\Reactivatenumber{7}@  
  x = (unsigned)(63 ^ __builtin_clzll(x));
  size_t lg_delta = (x < 7 ? LG_QUANTUM : x - @\Suppressnumber@
      SC_LG_NGROUP - 1); ...@\Reactivatenumber{9}@ 
}