import hashlib
import math
import random
import time

import requests

import js2py

__all__ = ['youdao_translate', 'tencent_translate', 'sogou_translate', 'baidu_translate', 'google_translate','LANGS']

LANGS = ['zh','en']

def youdao_translate(content, from_lang='zh',to='en'):
    '''
    language support:
        中文 - zh-CHS
        英文 - en
        日文 - ja
        韩文 - ko
        法文 - fr
        德文 - de
    Return:  string
    '''
    langs_mapping = {"zh":'zh-CHS','en':'en'}
    from_lang = langs_mapping[from_lang]
    to = langs_mapping[to]
    headers = {
        "Cookie":'OUTFOX_SEARCH_USER_ID=-2022895048@10.168.8.76;',
        "Referer":'http://fanyi.youdao.com/',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
    content = content.replace("\n",' ')
    salt = random.randint(0, 10) + int(time.time() * 1000)
    sign = 'fanyideskweb'+content+str(salt)+'ebSeFb%=XZ%T[KZ)c(sy!'
    sign = hashlib.md5(sign.encode(encoding='UTF-8')).hexdigest()   
    data = {
        "i":content,
        "from":from_lang,
        'to':to,
        "smartresult":'dict',
        'client':'fanyideskweb',
        'salt':salt,
        'sign':sign,
        'doctype':'json',
        'version':'2.1',
        'keyfrom':'fanyi.web',
        'action':'FY_BY_CLICKBUTTION',
        'typoResult':'false'
    }
    ret = requests.post('http://fanyi.youdao.com/translate_o',data=data,headers=headers,timeout=10).json()
    trans = []
    for item in ret['translateResult'][0]:
        trans.append(item['tgt'])
    return ''.join(trans)

def tencent_translate(content,from_lang='zh',to='en'):
    """
    support languages:
        中文 - zh
        英文 - en
        日文 - jp
        韩文 - kr
        法文 - fr
        德文 - de
    Return: list of string
    """
    langs_mapping = {"zh":'zh','en':'en'}
    from_lang = langs_mapping[from_lang]
    to = langs_mapping[to]
    data = {
        "source":from_lang,
        "target":to,
        "sourceText":content,
        "sessionUuid":"translate_uuid" + str(int(time.time() * 1000))
    }
    t_headers = {
        "Cookie":"fy_guid=d4480e20-1644-4a47-a98d-787cfa244fd2; qtv=bbbc7118b32d7a9a; qtk=DTmfpOAn6b6HWTGtjW7w5a/FOommFjJPAre3GpaRUzPCQSaqY3gOSzKYEFyRYwKnjUN3M9D0V59LVNGDKchtj+RBld2oqSAVvEaAQVVLApTHDB52kdQYQYKAsa2NLnl4lIUbr6pYKN5469mS5hjcmQ==;",
        "Origin":"http://fanyi.qq.com"
    }
    ret = requests.post('https://fanyi.qq.com/api/translate',data=data,headers=t_headers,timeout=10).json()
    trans = []
    for item in ret['translate']['records']:
        trans.append(item['targetText'])
    return ''.join(trans)

def _sogou_token():
    def t():
        return hex(math.floor(65536 * (1 + random.random())))[3:]
    return t() + t() + t() + t() + t() + t() + t() + t()

def sogou_translate(content, from_lang='zh-CHS',to='en'):
    '''
    support language:
        中文 - zh-CHS
        英文 - en
        日文 - ja
        韩文 - ko
        法文 - fr
        德文 - de
    Return: string
    '''
    langs_mapping = {"zh":'zh-CHS','en':'en'}
    from_lang = langs_mapping[from_lang]
    to = langs_mapping[to]
    data = {
        "from":from_lang,
        "to":to,
        'client':'pc',
        'fr':'browser_pc',
        'text':content,
        'useDetect':'on',
        "useDetectResult":"off",
        "needQc":"1",
        "uuid":_sogou_token(),
        "oxford":"on",
        "isReturnSugg": "off"
    }
    ret = requests.post('http://fanyi.sogou.com/reventondc/translate',data=data,timeout=10).json()
    return ret['translate']['dit']

_baidu_js = """
function a(r, o) {
    for (var t = 0; t < o.length - 2; t += 3) {
        var a = o.charAt(t + 2);
        a = a >= "a" ? a.charCodeAt(0) - 87 : Number(a),
        a = "+" === o.charAt(t + 1) ? r >>> a: r << a,
        r = "+" === o.charAt(t) ? r + a & 4294967295 : r ^ a
    }
    return r
}
var C = null;
var token = function(r, _gtk) {
    var o = r.length;
    o > 30 && (r = "" + r.substr(0, 10) + r.substr(Math.floor(o / 2) - 5, 10) + r.substring(r.length, r.length - 10));
    var t = void 0,
    t = null !== C ? C: (C = _gtk || "") || "";
    for (var e = t.split("."), h = Number(e[0]) || 0, i = Number(e[1]) || 0, d = [], f = 0, g = 0; g < r.length; g++) {
        var m = r.charCodeAt(g);
        128 > m ? d[f++] = m: (2048 > m ? d[f++] = m >> 6 | 192 : (55296 === (64512 & m) && g + 1 < r.length && 56320 === (64512 & r.charCodeAt(g + 1)) ? (m = 65536 + ((1023 & m) << 10) + (1023 & r.charCodeAt(++g)), d[f++] = m >> 18 | 240, d[f++] = m >> 12 & 63 | 128) : d[f++] = m >> 12 | 224, d[f++] = m >> 6 & 63 | 128), d[f++] = 63 & m | 128)
    }
    for (var S = h,
    u = "+-a^+6",
    l = "+-3^+b+-f",
    s = 0; s < d.length; s++) S += d[s],
    S = a(S, u);

    return S = a(S, l),
    S ^= i,
    0 > S && (S = (2147483647 & S) + 2147483648),
    S %= 1e6,
    S.toString() + "." + (S ^ h)
}
"""

_baidu_token = js2py.eval_js(js=_baidu_js)

def baidu_translate(content,from_lang='zh',to='en'):
    '''
    support language:
        中文 - zh
        英文 - en
        日文 - jp
        韩文 - kor
        法文 - fra
        德文 - de
    Return: string
    '''
    langs_mapping = {"zh":'zh','en':'en'}
    from_lang = langs_mapping[from_lang]
    to = langs_mapping[to]
    content = content.replace('\n',' ')
    data = {
        "from":from_lang,
        'to':to,
        'query':content,
        'transtype':'translang',
        'simple_means_flag':'3',
        'sign': _baidu_token(content, "320305.131321201"),
        "token":"7b35624ba7fe34e692ea909140d9582d"
    }
    b_headers = {
        "Cookie":"BAIDUID=16FFA1EAAF1A387C647A22DB9FC81DAE:FG=1; BIDUPSID=16FFA1EAAF1A387C647A22DB9FC81DAE; PSTM=1514024118; __cfduid=d2f7fd3a024d1ee90b8a817ddd866d9bc1514812370; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; BDUSS=E83bFplYnBRen5hV3FKNDZCM3ZSZldWMVBjV1ZGbW9uTTVwcjFYVDQzTGVFTlJhQVFBQUFBJCQAAAAAAAAAAAEAAADnIjgkcG9obG9ndTQxNTA3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN6DrFreg6xaS; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; H_PS_PSSID=1429_21103_18559_22075; PSINO=3; locale=zh; Hm_lvt_64ecd82404c51e03dc91cb9e8c025574=1525654866,1525657996,1525658015,1525671031; Hm_lpvt_64ecd82404c51e03dc91cb9e8c025574=1525671031; to_lang_often=%5B%7B%22value%22%3A%22en%22%2C%22text%22%3A%22%u82F1%u8BED%22%7D%2C%7B%22value%22%3A%22zh%22%2C%22text%22%3A%22%u4E2D%u6587%22%7D%5D; from_lang_often=%5B%7B%22value%22%3A%22zh%22%2C%22text%22%3A%22%u4E2D%u6587%22%7D%2C%7B%22value%22%3A%22en%22%2C%22text%22%3A%22%u82F1%u8BED%22%7D%5D",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
    }
    ret = requests.post('https://fanyi.baidu.com/v2transapi',data=data,headers=b_headers,timeout=10).json()
    return ret['trans_result']['data'][0]['dst']


_google_js = """
function token(a) {
    var k = "";
    var b = 406644;
    var b1 = 3293161072;

    var jd = ".";
    var sb = "+-a^+6";
    var Zb = "+-3^+b+-f";

    for (var e = [], f = 0, g = 0; g < a.length; g++) {
        var m = a.charCodeAt(g);
        128 > m ? e[f++] = m: (2048 > m ? e[f++] = m >> 6 | 192 : (55296 == (m & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (m = 65536 + ((m & 1023) << 10) + (a.charCodeAt(++g) & 1023), e[f++] = m >> 18 | 240, e[f++] = m >> 12 & 63 | 128) : e[f++] = m >> 12 | 224, e[f++] = m >> 6 & 63 | 128), e[f++] = m & 63 | 128)
    }
    function RL(a, b) {
        var t = "a";
        var Yb = "+";
        for (var c = 0; c < b.length - 2; c += 3) {
            var d = b.charAt(c + 2),
            d = d >= t ? d.charCodeAt(0) - 87 : Number(d),
            d = b.charAt(c + 1) == Yb ? a >>> d: a << d;
            a = b.charAt(c) == Yb ? a + d & 4294967295 : a ^ d
        }
        return a
    }
    a = b;
    for (f = 0; f < e.length; f++) a += e[f],
    a = RL(a, sb);
    a = RL(a, Zb);
    a ^= b1 || 0;
    0 > a && (a = (a & 2147483647) + 2147483648);
    a %= 1E6;
    return a.toString() + jd + (a ^ b)
};
"""

_google_token = js2py.eval_js(js=_google_js)

def google_translate(content, from_lang='zh-CN',to='en'):
    """
    support languages:
        中文 - zh-CN
        英文 - en
        日文 - ja
        韩文 - ko
        法文 - fr
        德文 - de
    Return: list of string
    """
    langs_mapping = {"zh":'zh-CN','en':'en'}
    from_lang = langs_mapping[from_lang]
    to = langs_mapping[to]
    data = {
        "client":"t",
        "sl":from_lang,
        "tl":to,
        "hl":"zh-CN",
        "dt":"at",
        "dt":"bd",
        "dt":"ex",
        "dt":"ld",
        "dt":"md",
        "dt":"qca",
        "dt":"rw",
        "dt":"rm",
        "dt":"ss",
        "dt":"t",
        "ie":"UTF-8",
        "oe":"UTF-8",
        "source":"btn",
        "ssel":"0",
        "tsel":"0",
        "kc":"0",
        "tk":_google_token(content),
        "q":content,
    }
    ret = requests.get("https://translate.google.cn/translate_a/single",params=data,timeout=10).json()
    trans = []
    for item in ret[0]:
        trans.append(item[0])
    return ''.join(trans)
