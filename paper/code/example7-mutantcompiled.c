unsigned char mutant_opt(unsigned val){
  return |^((val/10) * 6) + val^|;
}