import argparse, sys, os
import requests, random, hashlib, json


class Config:
    config_files = {'settings': 'config/settings.json', 'api': 'config/api.json'}
    dicts = {'settings': {}, 'api': {}}

    def __init__(self):
        with open(self.config_files['settings'], 'r') as f:
            self.dicts['settings'] = json.loads(f.read())
        with open(self.config_files['api'], 'r') as f:
            self.dicts['api'] = json.loads(f.read())

    def read(self, file, key):
        return self.dicts[file][key]


def translate(query, target, source='en'):
    app_id = config.read('api', 'appid')
    key = config.read('api', 'key')
    salt = str(random.randint(1000000000, 9999999999))
    sign = app_id + query + salt + key
    sign = hashlib.md5(sign.encode('utf-8')).hexdigest()

    api = 'https://fanyi-api.baidu.com/api/trans/vip/translate?q={}&from={}&to={}&appid={}&salt={}&sign={}'.format(
        query, source, target, app_id, salt, sign)
    r = requests.get(api)
    j = json.loads(r.text)
    # print(j)
    return j['trans_result'][0]['dst']


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('prompt', type=str, nargs='?', action='store')
    parser.add_argument('--conversation', action='store_true', help='完善prompt以适应[对话]场景')
    parser.add_argument('--sentence', action='store_true',
                        help='丢弃生成的文本中最后一个出现的句点后面的内容（如果生成的文本中不存在句点则会尝试继续生成直到它出现）')
    parser.add_argument('--auto', action='store_true', help='自动继续生成')
    parser.add_argument('--no-lf', action='store_true', help='丢弃生成的文本中所有的换行符')
    parser.add_argument('--trans-ipt', type=str, nargs="?", action='store', choices=['zh', 'cht', 'jp', 'kor'],
                        help='调用WebAPI将输入的文本从[指定语言]翻译为英语（使用百度翻译，需在脚本中填写您的APPID和密钥）')
    parser.add_argument('--trans-opt', type=str, nargs="?", action='store', choices=['zh', 'cht', 'jp', 'kor'],
                        help='调用WebAPI翻译生成的文本为[指定语言]（使用百度翻译，需在脚本中填写您的APPID和密钥）')

    option = parser.parse_args()
    print(option)

    if option.trans_ipt is None:
        prompt = option.prompt
    else:
        print(":: Translating...")
        prompt = translate(option.prompt, 'en', option.trans_ipt)
        print(prompt)
    if option.conversation:
        prompt = "My friend asked me \"{}\", I answered: \"".format(prompt)

    from transformers import pipeline
    print(":: Loading model, it takes time...")
    generator = pipeline('text-generation', model='model')

    i = 0
    while True:
        i = i + 1
        print(":: Generating...")
        length = 24
        min_length = length * i
        max_length = length * 2 * i
        result = generator(prompt, do_sample=True, min_length=min_length, max_length=max_length)
        txt = result[0]['generated_text']

        if option.sentence:
            last_dot = txt.rfind('.')
            if last_dot == -1:
                prompt = txt
                continue
            txt = txt[0:last_dot + 1]

        if option.no_lf:
            txt = txt.replace('\n', '')

        if option.trans_opt is not None:
            print(":: Translating...")
            t_lang = option.trans_opt
            txt_trans = translate(txt, t_lang)

        if sys.platform == 'win32':
            os.system('cls')
        else:
            os.system('clear')

        if option.trans_opt is None:
            print(txt)
        else:
            print(txt_trans)

        print('\n')
        if not option.auto:
            input('::Press any key to generate more...\n')
        prompt = txt


if __name__ == '__main__':
    config = Config()
    # print(translate('hello world', 'zh'))
    main()
