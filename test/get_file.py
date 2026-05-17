import os
directory = os.environ.get('SMT_QF_FP_DIR', '/tmp/smt_data/QF_FP')
for dirpath, dirnames, filenames in os.walk(directory):
    for filename in filenames:
        # 构造完整的文件路径
        file_path = os.path.join(dirpath, filename)
        print(file_path)  # 或者进行其他操作