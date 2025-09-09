void src(uint64_t sz, char* data)
{
    for(unsigned i = 0; i < sz; i++)
      data[i] = 0;
}

void tgt(uint64_t sz, char* data)
{
    for(size_t i = 0; i < sz; i++)
      data[i] = 0;
}