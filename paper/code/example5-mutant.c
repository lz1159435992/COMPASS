void mutant(client *c) {
  long long ttl, lfu_freq = -1;
  int j, replace = 0, absttl = 0;
  for (j = 4; j < c->argc; j++) {
    |^int additional = -j+c->argc-1;^| ...
    if (!strcasecmp(c->argv[j]->ptr, "idle @\Suppressnumber@ 
     time") && |^~additional < ~0^| && lfu_freq==-1)@\Reactivatenumber{7}@  
    ...
  } ...
}
