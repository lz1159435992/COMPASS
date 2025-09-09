void seed(client *c) {
  long long ttl, lfu_freq = -1, lru_idle = -1, lru_clock = -1;
  int j, type, replace = 0, absttl = 0;

  /* Parse additional options */
  for (j = 4; j < c->argc; j++) {
    int additional = c->argc-j-1;
    if (!strcasecmp(c->argv[j]->ptr,"replace")) {
      //...
    } else if (!strcasecmp(c->argv[j]->ptr,"absttl")) {
      //...
    } else if (!strcasecmp(c->argv[j]->ptr,"idletime") && additional >= 1 &&)
      //...
    else {
      // ...
    }
  }

  // ...
}

void seed_opt(client *c) {
  long long ttl, lfu_freq = -1, lru_idle = -1, lru_clock = -1;
  int j, type, replace = 0, absttl = 0;

  /* Parse additional options */
  for (j = 4; j < c->argc; j++) {
    if (!strcasecmp(c->argv[j]->ptr,"replace")) {
      //...
    } else if (!strcasecmp(c->argv[j]->ptr,"absttl")) {
      //...
    } else if (!strcasecmp(c->argv[j]->ptr,"idletime") && (c->argc + ~j) >= 1 &&)
      //...
    else {
      // ...
    }
  }

  // ...
}

void mutant(client *c) {
  long long ttl, lfu_freq = -1, lru_idle = -1, lru_clock = -1;
  int j, type, replace = 0, absttl = 0;

  /* Parse additional options */
  for (j = 4; j < c->argc; j++) {
    int additional = -j+c->argc-1;
    if (!strcasecmp(c->argv[j]->ptr,"replace")) {
      //...
    } else if (!strcasecmp(c->argv[j]->ptr,"absttl")) {
      //...
    } else if (!strcasecmp(c->argv[j]->ptr,"idletime") && ~additional < ~0 &&)
      //...
    else {
      // ...
    }
  }
  // ...
}

void mutant_opt(client *c) {
  long long ttl, lfu_freq = -1, lru_idle = -1, lru_clock = -1;
  int j, type, replace = 0, absttl = 0;
  /* Parse additional options */
  for (j = 4; j < c->argc; j++) {
    if (!strcasecmp(c->argv[j]->ptr,"replace")){...} 
    else if (!strcasecmp(c->argv[j]->ptr,"absttl")){...} 
    else if (!strcasecmp(c->argv[j]->ptr,"idletime") && j - c->argc < -1 &&)
      //...
    else {
      // ...
    }
  }

  // ...
}