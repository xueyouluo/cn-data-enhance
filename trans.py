import argparse
import json
import time

from translation_apis import sogou_translate,baidu_translate,youdao_translate,google_translate,tencent_translate

TRANS_APIS = [youdao_translate,sogou_translate,baidu_translate,google_translate,tencent_translate]
api_num = len(TRANS_APIS)
tran_idx = 0
translate_apis = {api.__name__:api for api in TRANS_APIS}
translate_gap = {api.__name__:time.time() for api in TRANS_APIS}
translate_fail = {api.__name__:0 for api in TRANS_APIS}

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='translation')
    parser.register("type", "bool", lambda v: v.lower() == "true")
    parser.add_argument("--match", type='bool', nargs="?", const=True, default=False, help="Whether need to match api")
    parser.add_argument("--data_file", type=str, default=None, help="data file", required=True)
    parser.add_argument("--source", type=str, default='zh', help="source language", required=True)
    parser.add_argument("--target", type=str, default='en', help="target language", required=True)
    parser.add_argument("--out_file", type=str, default=None, help="output data file", required=True)
    parser.add_argument("--start", type=int, default=0, help="start index")
    parser.add_argument("--end", type=int, default=0, help="end index")

    flags, unparsed = parser.parse_known_args()

    print("# Load data from {0}...".format(flags.data_file))
    data = [json.loads(line) for line in open(flags.data_file,encoding='utf8')]
    data = data[flags.start:flags.end]
    print("# Translation from {0} to {1}".format(flags.source,flags.target))
    print("# Start to translation file {0} from index {1} to {2}, size={3}".format(flags.data_file,flags.start,flags.end,flags.end-flags.start))
    
    def translation(content,from_lang='zh', to='en', old_api_name=None):
        global tran_idx
        global translate_gap
        global translate_fail
        global api_num 
        global translate_apis

        retry = api_num
        while retry > 0:
            try:
                if old_api_name is not None and translate_fail[old_api_name]<10:
                    api = translate_apis[old_api_name]
                else:
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
                print("# Warning - {0} api not working... Try next api".format(api.__name__))
                translate_fail[api.__name__] += 1
                translate_gap[api.__name__] = time.time()
                old_api_name = None
                tran_idx += 1
                retry -= 1
        print("# Error: All apis are not working...")
        return None, None

    start_trans_time = time.time()
    size = flags.end - flags.start
    with open(flags.out_file,'w',encoding='utf8') as f:
        for i,item in enumerate(data):
            print("# Process item {0} of {1}, ratio {2:.3%}...".format(i,size,(i+1)/size))
            if '{0}_content'.format(flags.source) in item:
                content = item['{0}_content'.format(flags.source)]
            else:
                content = item['content']
            new_item = item.copy()
            start = time.time()
            old_api_name = new_item.get("{0}_api".format(flags.source),None)
            new_content,api_name = translation(content,flags.source,flags.target, old_api_name)
            end = time.time()
            if new_content is None:
                print("# No result, stop early")
                break
            print("# Finishing processing {0} with api {1} in {2:.2f} seconds, total time {3:.2f} min...".format(i,api_name,(end-start),(end-start_trans_time)/60))
            new_item['{0}_content'.format(flags.target)] = new_content
            new_item['{0}_api'.format(flags.target)] = api_name
            f.write(json.dumps(new_item,ensure_ascii=False) + '\n')
            f.flush()

    print("# Done!")

if __name__ == "__main__":
    main()
