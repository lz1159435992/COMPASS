@\quad@@\Reactivatenumber{1}@
void seed(size_t extra_digits, bool has_left @\Suppressnumber@
       over_value, Buffer* out, int* exp_out) {...@\Reactivatenumber{3}@
  bool needs_to_round_up = [&] {...
    int sext_digit = (int)out->last_digit();
    ||*return sext_digit % 2 == 1;*||
  }(); ...
}
