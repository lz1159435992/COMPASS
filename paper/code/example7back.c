unsigned char seed(unsigned val)
{
	return ((val / 10) << 4) + val % 10;
}

unsigned char seed_opt(unsigned val)
{
	return ((val / 10) << 4) | val % 10;
}

unsigned char mutant(unsigned val)
{
	return ((val / 10) << 4) + val - (val / 10) * 10;
}

unsigned char mutant_opt(unsigned val)
{
	return ((val / 10) * 6) + val;
}