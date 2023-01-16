# CyberWaifu Server - <u>TTS</u>

(Currently it's only support tacotron2 pytorch model with HiFiGAN, not support VITS pytorch model or VITS ONNX model)

## Getting Started

### download model

### configure model

```shell
mkdir -p model/tacotron2
mkdir -p model/hifigan
# mkdir -p model/vits.torch
# mkdir -p model/vits.onnx
mkdir static
```

#### tacotron2 pytorch model

```shell
# tacotron2 model
ln -s <path/to/tacotron2/model.ckpt> TTS/model/tacotron2/model.ckpt

# hifigan model
# rename to model.ckpt
mv <path/to/hifigan/model.ckpt> <path/to/hifigan/model.ckpt>
ln -s <path/to/hifigan/folder> TTS/model/hifigan
```

#### vits pytorch model

<-- To be continued.

#### vits onnx model

<-- To be continued.

### create venv & install pip dependencies

Before create venv, you have to install **python3.7** first. (or using conda environment)

```shell
cd TTS
python3.7 -m venv venv
source venv/bin/activate

# Update
python -m pip install --upgrade setuptools wheel pip

# install pip dependencies
pip install -r requirements.txt
```

### RUN TTS SERVER

```shell
# conda deactivate

cd CyberWaifu/Server/TTS
source venv/bin/activate

python main.py
# http://127.0.0.1:7211
```

## API Manual

请求

```
# GET or POST
# 需要进行百分号转义，别忘了百分号转义的保留字也要转义
http://127.0.0.1:7211/<prompt>

# e.g.
http://127.0.0.1:7211/%E5%AE%9F%E3%81%AF%E3%80%81%E3%81%9A%E3%81%A3%E3%81%A8%E5%A5%BD%E3%81%8D%E3%81%A0%E3%81%A3%E3%81%9F
```

返回

```
# redirect to generated wav file
http://127.0.0.1:7211/static/<uuid1>.wav

# e.g.
http://127.0.0.1:7211/static/341e2fb0-87e3-11ed-9b59-a08069f51b76.wav
```

## References

**[GitHub - luoyily/MoeTTS: Speech synthesis model /inference GUI repo for galgame characters based on Tacotron2, Hifigan and VITS](https://github.com/luoyily/MoeTTS)**

[快速上手 &#8212; Flask 中文文档 (2.1.2)](https://dormousehole.readthedocs.io/en/2.1.2/quickstart.html)

[learn-python3/do_flask.py at master · michaelliao/learn-python3 · GitHub](https://github.com/michaelliao/learn-python3/blob/master/samples/web/do_flask.py)

(https://gitee.com/jieran233/live2d_waifu)

......and more, thanks.

*I am because we are.*
