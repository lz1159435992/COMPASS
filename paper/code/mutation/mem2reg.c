// Before
int stack, *p = &stack;
*p = a;
return *p;
// After
return a;