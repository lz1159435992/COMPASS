void seed(client *c) {
  long long ttl, lfu_freq = -1, lru_idle = -1, lru_clock = -1;
  int j, type, replace = 0, absttl = 0;
  for (j = 4; j < c->argc; j++) {//Parse additional options
    int additional = c->argc-j-1;
    if (!strcasecmp(c->argv[j]->ptr,"replace")){...} 
    else if (!strcasecmp(c->argv[j]->ptr,"absttl")){...} 
    else if (!strcasecmp(c->argv[j]->ptr,"idletime") && additional >= 1 &&)
    ...
  } ...
}

void mutant(client *c) {
  long long ttl, lfu_freq = -1, lru_idle = -1, lru_clock = -1;
  int j, type, replace = 0, absttl = 0;
  for (j = 4; j < c->argc; j++) {//Parse additional options
    int additional = -j+c->argc-1;
    if (!strcasecmp(c->argv[j]->ptr,"replace")){...}
    else if (!strcasecmp(c->argv[j]->ptr,"absttl")){...}
    else if (!strcasecmp(c->argv[j]->ptr,"idletime") && ~additional < ~0 &&)
    ...
  } ...
}