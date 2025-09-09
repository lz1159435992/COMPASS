size_t seed(size_t size, size_t alignment) {
    if (likely(size <= 4096)) {
		return sz_s2u_lookup(size);
	}
    
    if (unlikely(size > 8070450532247928832)) {
		return 0;
	}

    // ...
    
	{
        size_t x = (size<<1)-1;
        x = (unsigned)((8 * sizeof(x) - 1) ^ __builtin_clzll(x));
	    size_t lg_delta = (x < 7 ? LG_QUANTUM : x - SC_LG_NGROUP - 1);
        // ...
	}
    
    // ...
}

size_t seed_opt(size_t size, size_t alignment) {
    if (likely(size <= 4096)) {
		return sz_s2u_lookup(size);
	}
    
    if (unlikely(size > 8070450532247928832)) {
		return 0;
	}

    // ...
    
	{
        size_t x = (size<<1)-1;
        x = (unsigned)(63 ^ __builtin_clzll(x));
	    size_t lg_delta = (x < 7 ? LG_QUANTUM : x - SC_LG_NGROUP - 1);
        // ...
	}
    
    // ...
}

size_t mutant(size_t size, size_t alignment) {
    if (likely(size <= 4096)) {
		return sz_s2u_lookup(size);
	}
    
    if (unlikely(size > 8070450532247928832)) {
		return 0;
	}

    // ...
    
	{
        size_t x = (size<<1)-1;
        size_t ctlz = __builtin_clzll(x);
        size_t num = 8 * sizeof(x) - 1; // 63
        x = (unsigned)( (ctlz | num) - (ctlz & num) );
	    size_t lg_delta = (x < 7 ? LG_QUANTUM : x - SC_LG_NGROUP - 1);
        // ...
	}
    
    // ...
}

size_t mutant_opt(size_t size, size_t alignment) {
    if (likely(size <= 4096)) {
		return sz_s2u_lookup(size);
	}
    
    if (unlikely(size > 8070450532247928832)) {
		return 0;
	}

    // ...
    
	{
        size_t x = (size<<1)-1;
        x = (unsigned)((63 - __builtin_clzll(x)));
	    size_t lg_delta = x - SC_LG_NGROUP - 1;
        // ...
	}
    
    // ...
}