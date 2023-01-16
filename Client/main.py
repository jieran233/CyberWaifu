import os
import sys, json
import urllib.parse, requests, html, base64, uuid
import soundfile as sf
import sounddevice as sd

# 多线程
from threading import Thread
# 结束线程
import ctypes
import inspect


# PyQt6
# PyQt5 QWebEngineView has a big bug on Linux (does not show anything), so we are using PyQt6
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import *

from mainWindow import *


class Config:
    config_files = {'servers': 'config/settings.json'}
    dicts = {'servers': {}}

    def __init__(self):
        with open(self.config_files['servers'], 'r') as f:
            self.dicts['servers'] = json.loads(f.read())

    def read(self, file, key):
        return self.dicts[file][key]

    def srv(self):
        return self.dicts['servers']


class Utils:
    def url_text_encode(self, text):
        text = urllib.parse.quote(text, 'utf-8')
        reserved_replace = [['!', '%21'], ['#', '%23'], ['$', '%24'], ['&', '%26'], ['\'', '%27'], ['(', '%28'],
                            [')', '%29'], ['*', '%2A'], ['+', '%2B'], [',', '%2C'], ['/', '%2F'], [':', '%3A'],
                            [';', '%3B'], ['=', '%3D'], ['?', '%3F'], ['@', '%40'], ['[', '%5B'], [']', '%5D']]
        for i in reserved_replace:
            text = text.replace(i[0], i[1])
        return text

    def base64_decode(self, text):
        text = base64.urlsafe_b64decode(text.encode('UTF-8')).decode('UTF-8')
        # print(text)
        return text

    def test_connection(self, url):
        try:
            r = requests.get(url=url)
            return 'OK'
            # return r.status_code
        except Exception as e:
            return e.args

    def get_gpt_json(self, txt):
        txt = self.url_text_encode(txt)
        url = srv['gpt'] + '/' + txt
        try:
            r = requests.get(url=url)
        except Exception as e:
            print(e.args)
            return ""
        txt = html.unescape(r.text)  # HTML反转义
        j = json.loads(txt)  # json str to dict
        return j

    def get_tts_wav(self, txt):
        txt = self.url_text_encode(txt)
        url = srv['tts'] + '/' + txt
        try:
            r = requests.get(url=url)
        except Exception as e:
            print(e.args)
            return ""
        wav_data = r.content  # 因为wav为流媒体文件，所以这里使用的是content，将它转为二进制
        wav_path = os.path.join(wav_folder, str(uuid.uuid1()) + '.wav')
        with open(wav_path, 'wb') as f:  # wb 写二进制
            f.write(wav_data)
        return wav_path

    def playsound(self, wav_file):
        if os.path.isfile(wav_file) is False:
            print('wav_file doe not exist')
            return
        sd.stop()
        samples, samplerate = sf.read(wav_file)
        sd.play(samples, samplerate)
        # sd.wait()

    def _async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def stop_thread(self, thread):
        self._async_raise(thread.ident, SystemExit)

class Ui_MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Ui_MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.current_wav_path = ''

    def setupUi(self, MainWindow):
        super(Ui_MainWindow, self).setupUi(MainWindow)

        # QWebEngienView -> self.widget
        webview = QWebEngineView(self.widget)
        l2d_url = srv['l2d']
        webview.load(QUrl(l2d_url))  # 加载Live2D页面
        # self.setCentralWidget(self.browser)
        webview.resize(800, 380)
        webview.show()

        # QLabel -> self.widget_2
        label = QLabel(self.widget_2)
        pixmap = QPixmap('res/hiyori.80px.png')
        label.setPixmap(pixmap)
        label.setToolTip('Click to replay voice')  # 设置悬停提示

        # 单击触发绑定的槽函数
        self.pushButton.clicked.connect(self.button_clicked)

        self.setFixedSize(MainWindow.width(), MainWindow.height())  # 禁止最大化和调整窗口大小
        self.label.setWordWrap(True)  # Label自动换行
        self.textEdit.setFocus()  # 输入文本框获取焦点

        self.tabWidget.setTabText(0, srv['waifu-name'])

        # 服务器连接状况
        status = ":: GPT Server | {} | {}".format(srv['gpt'], util.test_connection(srv['gpt'])) + '\n' + \
                 ":: TTS Server | {} | {}".format(srv['tts'], util.test_connection(srv['tts'])) + '\n' + \
                 ":: Live2D Server | {} | {}".format(srv['l2d'], util.test_connection(srv['l2d'])) + '\n'
        print(status)
        self.label.setText(status)

    def button_clicked(self):
        sender = self.sender()
        name = sender.objectName()
        # print(name)

        if name == 'pushButton':  # 发送请求按钮被点击
            if self.textEdit.toPlainText() == '':
                return
            self.pushButton.setDisabled(True)
            self.pushButton.setText('Please wait')
            self.label.setText('')
            thread_01 = Thread(target=self.do)
            thread_01.start()


    def do(self):  # 请求
        ipt = self.textEdit.toPlainText()
        def show_text():
            if srv['show-both-zh-jp'] is True:
                self.label.setText(opt['zh'] + '\n\n' + opt['jp'])
            else:
                self.label.setText(opt['zh'])

        status = ':: Now waiting GPT...'
        print(status)
        self.setWindowTitle("CyberWaifu {}".format(status))
        opt = {}
        try:
            o_dic = util.get_gpt_json(ipt)  # GPT
        except Exception as e:
            print(e.args)
        opt['zh'] = util.base64_decode(o_dic['zh'])
        opt['jp'] = util.base64_decode(o_dic['jp'])

        if srv['text-voice-sync'] is not True:
            show_text()  # 显示中文文本

        status = ':: Now waiting TTS...'
        print(status)
        self.setWindowTitle("CyberWaifu {}".format(status))
        try:
            self.current_wav_path = util.get_tts_wav(opt['jp'])  # TTS, 语音 日语
        except Exception as e:
            print(e.args)
        print(self.current_wav_path)

        print(':: Done')
        self.setWindowTitle("CyberWaifu")
        if srv['text-voice-sync'] is True:
            show_text()  # 显示中文文本
        try:
            util.playsound(self.current_wav_path)  # 播放语音
        except Exception as e:
            print(e.args)

        self.pushButton.setText('Send')
        self.pushButton.setDisabled(False)
        return

    def get_current_wav_path(self):
        return self.current_wav_path


class QLabel(QtWidgets.QLabel):
    """
    重写QLabel的事件函数
    Ref. https://blog.csdn.net/qq_41203622/article/details/109285700
    """
    def mouseReleaseEvent(self, QMouseEvent):  # 重播音频按钮被点击
        wav_path = mainWindow.get_current_wav_path()
        print('replay ' + wav_path)
        util.playsound(wav_path)


if __name__ == '__main__':
    global conf, util, srv, mainWindow
    conf = Config()
    util = Utils()
    srv = conf.srv()

    global wav_folder
    wav_folder = '.cache'

    # 创建缓存文件夹
    try:
        os.mkdir(wav_folder)
    except Exception as e:
        print(e.args)

    # 清理缓存
    print(":: Cleaning cache...")
    for i in os.listdir(wav_folder):
        print(i)
        try:
            os.remove(os.path.join(wav_folder, i))
        except Exception as e:
            print(e.args)

    app = QApplication(sys.argv)
    mainWindow = Ui_MainWindow()

    global thread_01

    mainWindow.show()

    sys.exit(app.exec())
