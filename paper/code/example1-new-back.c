bool input_prog(unsigned a) {
    if (a <= 50)
        return (63 - a) < 13;
    else
        return false;
}

bool compiled_prog(unsigned a) {
    return false;
}

bool optimized_prog(unsigned a) {
    if (a <= 50)
        return (a ^ 63) < 13;
    else
        return false;
}