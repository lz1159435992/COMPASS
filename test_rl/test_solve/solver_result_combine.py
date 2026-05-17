from test_rl.test_script.utils import load_dictionary
import config

info_dict = load_dictionary(os.path.join(config.TEST_RL_ROOT, 'test_solve', 'info_dict.txt'))
print(len(info_dict))
info_dict_bingxing = load_dictionary('/test_rl/test_solve/info_dict_bingxing.txt')
print(len(info_dict_bingxing))

for k,v in info_dict.items():
    if k not in info_dict_bingxing:
        print(k,v)