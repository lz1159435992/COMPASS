// Before              // After
int a;                 if (cond) use(b + c);
if (cond) a = b + c;   else dummy();
else dummy();
use(a);


