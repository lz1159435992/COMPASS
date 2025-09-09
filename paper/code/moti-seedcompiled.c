unsigned optimized_compiled(unsigned int val) {
  return ((val/10) << 4) | val % 10;
}