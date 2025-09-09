# RQ4 SuperVenn Analysis Summary Report

## Generated SuperVenn Diagrams

### Z3
- **Description**: Microsoft's flagship SMT solver
- **Data File**: `test_rl/test_solve/result_dict_z3solver_300s.txt`
- **SuperVenn Figure**: `supervenn-z3-comparison.pdf`
- **LaTeX Code**: `z3_supervenn_latex.txt`

### CVC5
- **Description**: Latest version of CVC solver family
- **Data File**: `test_rl/test_cvc5/cvc5_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_cvc5_0628.txt`
- **SuperVenn Figure**: `supervenn-cvc5-comparison.pdf`
- **LaTeX Code**: `cvc5_supervenn_latex.txt`

### BVParti
- **Description**: Specialized bit-vector constraint solver
- **Data File**: `test_rl/test_cvc5/bvparti_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_bvparti_0728.txt`
- **SuperVenn Figure**: `supervenn-bvparti-comparison.pdf`
- **LaTeX Code**: `bvparti_supervenn_latex.txt`

### MathSAT
- **Description**: Solver particularly effective for mathematical reasoning and optimization
- **Data File**: `test_rl/mathsat_process/info_dict_SMTimer_llama3.1:70b_1200s_info_dict_rl_mathsat_[date].txt`
- **SuperVenn Figure**: `supervenn-mathsat-comparison.pdf`
- **LaTeX Code**: `mathsat_supervenn_latex.txt`

## Usage in Paper

1. Copy the generated PDF files to your paper's figures directory
2. Use the LaTeX code from the corresponding `.txt` files
3. Update figure references in your RQ4 section

## File Structure
```
paper/pics/
├── supervenn-z3-comparison.pdf
├── supervenn-cvc5-comparison.pdf
├── supervenn-bvparti-comparison.pdf
├── z3_supervenn_latex.txt
├── cvc5_supervenn_latex.txt
└── bvparti_supervenn_latex.txt
```