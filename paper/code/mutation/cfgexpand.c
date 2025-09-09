// Before              // After
return c ? a : b;      if (c) return a;
                       else return b;

