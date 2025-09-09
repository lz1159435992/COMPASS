size_t mutant(size_t size, size_t alignment) {
  if (likely(size <= 4096)) {
    return sz_s2u_lookup(size);}
  if (unlikely(size > 8070450532247928832)) {
    return 0;} ...
  size_t x = (size<<1) - 1;
  |^size_t ctlz = __builtin_clzll(x);^|
  |^size_t num = 8 * sizeof(x) - 1; ^|// 63 
  |^x = (unsigned)( (ctlz | num) - (ctlz & num) );^| @\label{code:example1mutant:l1}@
  size_t lg_delta = x < 7 ? LG_QUANTUM : x - @\Suppressnumber@
                        SC_LG_NGROUP - 1; ...@\Reactivatenumber{11}@ 
}