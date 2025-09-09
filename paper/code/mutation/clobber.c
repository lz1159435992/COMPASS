// Before              // After
*p1 = a;               *p1 = arbitrary_value;
*p2 = 0;               *p2 = 0;
*p3 = 0;               *p1 = a;
                       *p3 = 0;
