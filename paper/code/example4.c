void use(unsigned);

void seed(bool c, unsigned a, unsigned b){
  unsigned s = c ? a & 24 : b & 25;
  unsigned s1 = c ? a & 24 : b & 25;
  use(s & 8);
  use(s1 & 16);
}

void seed_opt(bool c, unsigned a, unsigned b){
  unsigned s = c ? a & 24 : b & 25;
  use(s & 8);
  use(s & 16);
}

void mutant(bool c, unsigned a, unsigned b){
  unsigned s = c ? (a + 1 - 1) & 24 : b & 25;
  unsigned s1 = c ? a & 24 : b & 25;
  use(s & 8);
  use(s1 & 16);
}

void mutant_opt(bool c, unsigned a, unsigned b){
  unsigned s = c ? a : b;
  use(s & 8);
  use(s & 16);
}