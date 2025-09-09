int seed(uint8_t *macaddr, const char *p)
{
    int i;
    char *last_char;
    long int offset;

    errno = 0;
    offset = strtol(p, &last_char, 0);
    if (errno == 0 && *last_char == '\0' &&
        offset >= 0 && offset <= 0xFFFFFF) {
        // ...
        return 0;
    }

    //...
}

int seed_opt(uint8_t *macaddr, const char *p)
{
    int i;
    char *last_char;
    long int offset;

    errno = 0;
    offset = strtol(p, &last_char, 0);
    if (errno == 0 && *last_char == '\0' &&
        offset >= 0 && offset <= 0xFFFFFF) {
        // ...
        return 0;
    }

    //...
}

int tgt(uint8_t *macaddr, const char *p)
{
    int i;
    char *last_char;
    long int offset;

    errno = 0;
    offset = strtol(p, &last_char, 0);
    if (errno == 0 && offset >= 0 && *last_char == '\0' && offset <= 0xFFFFFF) {
        // ...
        return 0;
    }

    //...
}

int tgt_opt(uint8_t *macaddr, const char *p)
{
    int i;
    char *last_char;
    long int offset;

    errno = 0;
    offset = strtol(p, &last_char, 0);
    if (errno == 0 && *last_char == '\0' && ((unsigned)offset) <= 0xFFFFFF) {
        // ...
        return 0;
    }

    //...
}