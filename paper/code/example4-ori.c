#define BIT_ULL(nr) (1ULL << (nr))
bool vhost_svq_valid_features(
        uint64_t features, Error **errp) {

    unsigned s = c ? a & 24 : b & 25;
    // unsigned s1 = c ? a & 24 : b & 25;
    use(s & 8);
    use(s & 16);
----------------------
    uint64_t svq_features = features;
    ...

    if (!(svq_features & BIT_ULL(30))) {
        svq_features &= ~BIT_ULL(30);
        ...
    }
    if (!(svq_features & BIT_ULL(31))) {
        svq_features &= ~BIT_ULL(31);
        ...
    }
}

void mutant_real(bool c, unsigned a, 
        unsigned b) {
    if (!(svq_features & BIT_ULL(30))) {
        svq_features &= ~BIT_ULL(30);
        ...
    }
    if (!(svq_features & BIT_ULL(30))) {
        svq_features &= ~BIT_ULL(30);
        ...
    }
    if (!(svq_features & BIT_ULL(31))) {
        svq_features &= ~BIT_ULL(31);
        ...
    }
}

void mutant(bool c, unsigned a, 
        unsigned b) {
    unsigned s = c ? (a + 1 - 1) & 
        24 : b & 25;
    unsigned s1 = c ? a & 24 : b & 25;
    use(s & 8);
    use(s1 & 16);
}