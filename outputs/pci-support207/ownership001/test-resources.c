#include <stdio.h>
#include "resource-tests.h"
int main(void)
{
    int line=run_tests();
    printf("{\"cases\":%u,\"failure_line\":%d,\"passed\":%s}\n",cases,line,line ? "false" : "true");
    return line ? 1 : 0;
}
