// Before
int a = 10, b = 20, c = 0, d = a + b;
for(int i = 0; i < 100; i++) c += d;
// After
int a = 10, b = 20, c = 0;
for(int i = 0; i < 100; i++) c += a + b;