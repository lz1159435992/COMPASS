unsigned char mutant(unsigned val) {
  return ((val/10) << 4) + |^val - (val/10) * 10^|;
}