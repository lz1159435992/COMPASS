import os
from test_rl.test_script.utils import load_dictionary
import config

info_dict = load_dictionary(os.environ.get('INFO_DICT_RL', os.path.join(config.TEST_RL_ROOT, 'info_dict_gai_6_normal_1110_pre_SMTimer_llama3.1:70b_1200s_info_dict_rl.txt')))
lsmod_info = info_dict[os.environ.get('TEST_SMT_FILE', '/tmp/cloud_disk/smt/buzybox_angr.tar.gz/single_test/lsmod/lsmod1111306')]
print(type(lsmod_info))
print(len(lsmod_info[7]))


# print(len(lsmod_info))
count = 0
for i in lsmod_info[7]:
    print(i)
    print(len(i))
    count += len(i)
print(count,count/len(lsmod_info[7]))









