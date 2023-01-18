# CyberWaifu Client

## Getting Started - Linux

### install dependencies (ArchLinux)

```shell
# Will using Python 3.10
# QtDesigner, PyUIC, Pyrcc is included in python-pyqt6 package
sudo pacman -S python-pyqt6 python-pyqt6-webengine
```

## Config file Manual

#### config/settings.json

(注意URL末尾没有`/`)

|                     |                       |                                |
| ------------------- | --------------------- | ------------------------------ |
| `"gpt"`             | http://127.0.0.1:7210 | GPT server URL                 |
| `"tts"`             | http://127.0.0.1:7211 | TTS server URL                 |
| `"l2d"`             | http://127.0.0.1:8000 | Live2D server URL              |
| `"waifu-name"`      | 桃瀬ひより                 | 将在 mainWindow 中被显示             |
| `"waifu-pic"`       | res/hiyori.80px.png   | 将在 mainWindow 中被显示（位于窗口右下角的头像） |
| `"text-voice-sync"` | `true`or`false`       | 显示文本和播放语音同时进行（等待语音生成完毕再显示文本）   |
| `"show-both-zh-jp"` | `true`or`false`       | 同时显示中文文本和日语文本                  |

## References

[Python Examples of PyQt5.QtWebEngineWidgets.QWebEngineView](https://www.programcreek.com/python/example/97321/PyQt5.QtWebEngineWidgets.QWebEngineView)

[python 3.x - PyQt5 QWebEngineView does not show webpage - Stack Overflow](https://stackoverflow.com/questions/72346850/pyqt5-qwebengineview-does-not-show-webpage)

[Qt - Arch Linux 中文维基](https://wiki.archlinuxcn.org/wiki/Qt)

[python - How to play Wav sound samples from memory - Stack Overflow](https://stackoverflow.com/a/42387773)

https://blog.csdn.net/qq_41203622/article/details/109285700

https://blog.csdn.net/flfihpv259/article/details/52958129

......and more, thanks.

*I am because we are.*
