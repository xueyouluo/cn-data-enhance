import argparse
import json
import time

from translation_apis import sogou_translate,baidu_translate,youdao_translate,google_translate,tencent_translate

TRANS_APIS = [youdao_translate,sogou_translate,baidu_translate,google_translate,tencent_translate]
api_num = len(TRANS_APIS)
tran_idx = 0
translate_gap = {api.__name__:time.time() for api in TRANS_APIS}
translate_fail = {api.__name__:0 for api in TRANS_APIS}

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='translation')
    parser.add_argument("--data_file", type=str, default=None, help="data file", required=True)
    parser.add_argument("--source", type=str, default='zh', help="source language", required=True)
    parser.add_argument("--target", type=str, default='en', help="target language", required=True)
    parser.add_argument("--out_file", type=str, default=None, help="output data file", required=True)
    parser.add_argument("--start", type=int, default=0, help="start index")
    parser.add_argument("--size", type=int, default=0, help="translation size")

    flags, unparsed = parser.parse_known_args()

    print("# Load data from {0}...".format(flags.data_file))
    data = [json.loads(line) for line in open(flags.data_file,encoding='utf8')]
    data = data[flags.start:flags.start+flags.size]
    print("# Translation from {0} to {1}".format(flags.source,flags.target))
    print("# Start to translation file {0} from index {1} to {2}, size={3}".format(flags.data_file,flags.start,flags.start+flags.size,flags.size))
    
    def translation(content,from_lang='zh', to='en'):
        global tran_idx
        global translate_gap
        global translate_fail
        global api_num 

        retry = api_num
        while retry > 0:
            try:
                api = TRANS_APIS[tran_idx%api_num]
                if translate_fail[api.__name__] >= 10:
                    TRANS_APIS.remove(api)
                    api_num -= 1
                    tran_idx += 1
                    continue
                # slow down
                while time.time() - translate_gap[api.__name__] < 3:
                    time.sleep(1)
                translated = api(content,from_lang,to)
                tran_idx += 1
                translate_gap[api.__name__] = time.time()
                translate_fail[api.__name__] = 0
                return translated,api.__name__
            except:
                print("# Warning - {0} api not working... Try next api".format(TRANS_APIS[tran_idx%api_num].__name__))
                translate_fail[TRANS_APIS[tran_idx%api_num].__name__] += 1
                translate_gap[TRANS_APIS[tran_idx%api_num].__name__] = time.time()
                tran_idx += 1
                retry -= 1
        print("# Error: All apis are not working...")
        return None, None

    with open(flags.out_file,'w',encoding='utf8') as f:
        for i,item in enumerate(data):
            print("# Process item {0} of {1}, ratio {2:.3%}...".format(i,flags.size,(i+1)/flags.size))
            if '{0}_content'.format(flags.source) in item:
                content = item['{0}_content'.format(flags.source)]
            else:
                content = item['content']
            new_item = item.copy()
            start = time.time()
            new_content,api_name = translation(content,flags.source,flags.target)
            end = time.time()
            if new_content is None:
                print("# No result, stop early")
                break
            print("# Finishing processing {0} with api {1} in {2:.2f} seconds...".format(i,api_name,(end-start)))
            new_item['{0}_content'.format(flags.target)] = new_content
            new_item['{0}_api'.format(flags.target)] = api_name
            f.write(json.dumps(item,ensure_ascii=False) + '\n')
            f.flush()

    print("# Done!")

if __name__ == "__main__":
    main()
