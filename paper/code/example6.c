char trunc(int v) {return v;}

void seed(size_t extra_digits,
              bool has_leftover_value,
              Buffer* out,
              int* exp_out) {...
  bool needs_to_round_up = [\&] {...
    int sext_digit = (int)out->last_digit();
    return sext_digit %{\%}% 2 == 1;
  }(); ...
}

void mutant(size_t extra_digits,
              bool has_leftover_value,
              Buffer* out,
              int* exp_out) { ...
  bool needs_to_round_up = [\&] { ...
  int sext_digit = (int)out->last_digit();
  return trunc(sext_digit) %{\%}% trunc(2) == 1;
  }(); ...
}
