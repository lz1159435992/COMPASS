// Before              // After
return a;              int stack, *p = &stack;
                       *p = a;
                       return *p;

