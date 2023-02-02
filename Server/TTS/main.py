print(":: Importing module...")
import os, sys, json, uuid

from PIL import Image
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.colors import LinearSegmentedColormap
from scipy.io.wavfile import write

import g2p.jp.japanese_g2p as jp_g2p
import g2p.zh.chinese_g2p as zh_g2p

import numpy as np
import torch
from tacotron2.hparams import create_hparams
from tacotron2.train import load_model
from hifigan.models import Generator

from flask import Flask
from flask import redirect
from flask import url_for
from flask import request
from markupsafe import escape

# text to sequence
taco_default_symbols = ["_", "-", "!", "'", "(", ")", ",", ".", ":", ";", "?", " ", "A", "B", "C", "D", "E", "F", "G",
                        "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
                        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s",
                        "t", "u", "v", "w", "x", "y", "z", "@AA", "@AA0", "@AA1", "@AA2", "@AE", "@AE0", "@AE1", "@AE2",
                        "@AH", "@AH0", "@AH1", "@AH2", "@AO", "@AO0", "@AO1", "@AO2", "@AW", "@AW0", "@AW1", "@AW2",
                        "@AY", "@AY0", "@AY1", "@AY2", "@B", "@CH", "@D", "@DH", "@EH", "@EH0", "@EH1", "@EH2", "@ER",
                        "@ER0", "@ER1", "@ER2", "@EY", "@EY0", "@EY1", "@EY2", "@F", "@G", "@HH", "@IH", "@IH0", "@IH1",
                        "@IH2", "@IY", "@IY0", "@IY1", "@IY2", "@JH", "@K", "@L", "@M", "@N", "@NG", "@OW", "@OW0",
                        "@OW1", "@OW2", "@OY", "@OY0", "@OY1", "@OY2", "@P", "@R", "@S", "@SH", "@T", "@TH", "@UH",
                        "@UH0", "@UH1", "@UH2", "@UW", "@UW0", "@UW1", "@UW2", "@V", "@W", "@Y", "@Z", "@ZH"]
vits_default_symbols = ['_', ',', '.', '!', '?', '-', 'A', 'E', 'I', 'N', 'O', 'Q', 'U', 'a', 'b', 'd', 'e', 'f', 'g',
                        'h', 'i', 'j', 'k', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'w', 'y', 'z', 'ʃ', 'ʧ', '↓',
                        '↑', ' ']


def text_to_sequence(text, symbols=None):
    print('text_to_sequence')
    _symbol_to_id = {s: i for i, s in enumerate(symbols)}
    seq = [_symbol_to_id[c] for c in text if c in symbols]
    return seq


class Tacotron2:
    def __init__(self, tts_model, hifigan_model):
        print(":: Initializing...")
        siblings = os.cpu_count()
        torch.set_num_threads(siblings)
        torch.set_num_interop_threads(siblings)

        device = torch.device('cpu')

        self.symbols = taco_default_symbols

        hparams = create_hparams()
        hparams.n_symbols = len(self.symbols)
        hparams.sampling_rate = 22050

        print(":: Loading tacotron2 model...")
        self.model = load_model(hparams)
        self.model.load_state_dict(torch.load(tts_model, map_location='cpu')['state_dict'])
        _ = self.model.cpu().eval()

        # sys.path.append('hifigan/')
        class AttrDict(dict):
            def __init__(self, *args, **kwargs):
                super(AttrDict, self).__init__(*args, **kwargs)
                self.__dict__ = self

        def load_checkpoint(filepath, device):
            assert os.path.isfile(filepath)
            # print("Loading '{}'".format(filepath))
            print(":: Loading hifigan model...")
            checkpoint_dict = torch.load(filepath, map_location=device)
            # print("Complete.")
            return checkpoint_dict

        hifigan_cfg = '/'.join(hifigan_model.split('/')[:-1])
        config_file = (hifigan_cfg + '/config.json')
        with open(config_file) as f:
            data = f.read()
        json_config = json.loads(data)
        self.h = AttrDict(json_config)

        torch.manual_seed(self.h.seed)

        self.generator = Generator(self.h).to(device)
        state_dict_g = load_checkpoint(hifigan_model, device)
        self.generator.load_state_dict(state_dict_g['generator'])
        self.generator.eval()
        self.generator.remove_weight_norm()

    def inference_taco(self, target_text):
        text_list = [target_text]
        for n, tar_text in enumerate(text_list):
            text = tar_text
            sequence = np.array(text_to_sequence(text, self.symbols))[None, :]
            sequence = torch.autograd.Variable(torch.from_numpy(sequence)).cpu().long()

            mel_outputs, mel_outputs_postnet, _, alignments = self.model.inference(sequence)

            with torch.no_grad():
                raw_audio = self.generator(mel_outputs.float())
                audio = raw_audio.squeeze()
                audio = audio * 32768.0
                audio = audio.cpu().numpy().astype('int16')
                wav_path = os.path.join(wav_folder, str(uuid.uuid1()) + '.wav')
                write(wav_path, self.h.sampling_rate, audio)
                return wav_path


def main():
    taco = Tacotron2(tts_model='model/tacotron2/model.ckpt', hifigan_model='model/hifigan/model.ckpt')
    app = Flask(__name__)

    global wav_folder
    wav_folder = 'static'

    # 清理缓存
    print(":: Cleaning cache...")
    for i in os.listdir(wav_folder):
        print(i)
        try:
            os.remove(os.path.join(wav_folder, i))
        except Exception as e:
            print(e.args)

    # 创建缓存文件夹
    try:
        os.mkdir(wav_folder)
    except Exception as e:
        print(e.args)

    @app.route("/<prompt>")
    def receive_request(prompt):
        print(":: Getting romaji...")
        txt = jp_g2p.get_romaji_with_space(prompt)
        print(":: Generating...")
        wav_path = taco.inference_taco(txt)
        url_for('static', filename=wav_path)
        return redirect(wav_path)

    app.run(host='127.0.0.1', port=7211)


if __name__ == '__main__':
    main()
