#include <string>
#include <stdint.h>
#include <stdio.h>

main()
{
    const std::string methodName("intOverflow");
    int32_t int32 = -1;
    int16_t int16 = -1;
    uint32_t int32u = 65536;
    printf("method:%s:   signed -1 16 bits:%d, -1 32 bits=%d.\n", methodName.c_str(), int16, int32);
    printf("method:%s: unsigned -1 16 bits:%u, -1 32 bits=%u.\n", methodName.c_str(), static_cast<uint16_t>(int16), int32);
    const char* textYES = "YES";
    const char* textNO  = "NO";
    printf("method:%s: --\n"
        " signed -1 16 bits equal to %d : %s.\n"
        " signed -1 16 bits equal to direct cast %u : %s.\n"
        , methodName.c_str()
        , int32u, int16 == int32u ? textYES : textNO
        , static_cast<uint16_t>(-1), int16 == static_cast<uint16_t>(-1) ? textYES : textNO
    );
    return 0;
}
