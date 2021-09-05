# -*- coding: utf-8 -*-
# python3

import os, sys, re, time, datetime
import threading
import signal

# ---------------------------------------------------------------
# Config
# ---------------------------------------------------------------

# for snowboy -----------------------------

# dir path for models and voices
RESOURCE_DIR = '/usr/local/pi/py/resources/'

# model files and sensivitys(default:0.5)
MODELS = (
      ('snowboy.umdl', 0.85)
    # , ('alexa.umdl', 0.5)
    # , ('apeiria_00.pmdl', 0.5)
    , ('apeiria_01.pmdl', 0.55) # 0.46
    # , ('apeiria_02.pmdl', 0.5) # < 0.65
    # , ('Raspi.pmdl', 0.5)# < 0.57
    , ('raspberrypi_01.pmdl', 0.55) # 0.49
    # , ('raspberrypi_02.pmdl', 0.65)
)
AUDIO_GAIN = 1.0 # 音声入力増幅率(default:1.0)

# for google assistant -----------------------------

DEVICE_MODEL_ID = 'miyahei-raspberrypi3-01'

# server -----------------------------

# raspberry pi zero
HOST = '192.168.10.181'
PORT = 58100

# 効果音、ボイス

voice_files = [
      'ding.wav'
    , 'apeiria_roger.wav'
    , 'apeiria_positive_send_success.wav'
    , 'apeiria_negative.wav'
    , 'apeiria_negative_err.wav'
    # , 'rospeex_timeout.wav'
    # , 'rospeex_cancel.wav'
    , 'yukari_timeout.wav'
    , 'yukari_cancel.wav'
    , 'yukari_kasituki.wav'
    , 'yukari_itterassai.wav'

    , 'yukari_site_down.wav'
    , 'yukari_bot_down.wav'
    , 'yukari_not_down.wav'

    , 'alarm18.wav'
    , 'runa_ohayo.wav'
    , 'runa_oyasumi.wav'

    , 'raspi.wav'
    , 'weather.wav'
    , 'fan_off.wav'
]

# ---------------------------------------------------------------
# 設計
# ---------------------------------------------------------------

# 【方針】
# ★ `Wakeword Engine`の変更、及び、`AIアシスタント`の追加(複数同居)
#    が簡単に出来るように設計する。

# 【詳細】
# ★ `Wakeword Engine`を親、`AIアシスタント`を子とする
# ★ 子は勝手に終了しない、親に終了処理を依頼する。
#   親は全ての子を終了させてから、自身も停止する。
# ★ 複数のウェイクワードを登録し、`管理用`と`AIアシスタント呼び出し用`に分ける。
#    `管理用`により、`AIアシスタント呼び出し用`のON/OFFを行う。
#    `管理用`には、特に誤反応のしにくいウェイクワードを設定する。

# 【ToDo】
# ★ 音声合成エンジンを組み込む(WebAPIでOK)
# ★ ボイスコマンドで、プログラムの終了・再起動をできるようにする
# ★ 不具合が起きたら、自動で再起動するようにする
# ★ スマートディスプレイのライブラリが出たら、組み込みたい(要小型ディスプレイ)

# ---------------------------------------------------------------
# Wakeword Engine (snowboy)
# ---------------------------------------------------------------

class WakewordEngine(threading.Thread):
    def __init__(self):
        super(WakewordEngine, self).__init__()

        self.is_pause = False # AIアシスタント呼び出し用ウェイクワードのON/OFF用(一時停止フラグ)
        self.last = 0 # 最後にウェイクワードに反応した日時(誤反応対処用)

        # signalのコードはサンプルコードにあったから入れてるけど、本当に必要か微妙
        self.interrupted = False
        signal.signal(signal.SIGINT, self.signal_handler)

        # AIアシスタント
        # google assistant
        self.google_assistant = GoogleAssistant(self)
        self.google_assistant.start()

        # 他のAIアシスタントを入れるならここ

        # wakeword engine
        from snowboy import snowboydecoder
        _MODELS, sensitivitys = map(list, zip(*MODELS))
        models = [RESOURCE_DIR + x for x in _MODELS]
        print(len(models), len(sensitivitys))
        self.callbacks = [(lambda m: lambda: self.on_wake(m))(x.split('.').pop(0)) for x in _MODELS]
        self.detector = snowboydecoder.HotwordDetector(models, # Wake word(Hot word)の設定
            sensitivity=sensitivitys, audio_gain=AUDIO_GAIN)
            # 感度の調節: sensitivityとaudio_gainの説明(公式ドキュメント原文まま)
            # When sensitiviy is higher, the hotword gets more easily triggered.
            #      But you might get more false alarms.
            # audio_gain controls whether to increase (>1) or decrease (<1) input volume.

    def run(self): #start
        print('start WakewordEngine')
        play_voice('runa_ohayo')
        self.detector.start(detected_callback=self.callbacks,
                        interrupt_check=self.interrupt_callback,
                        sleep_time=0.03) # sleep_time(default:0.03)
        print('finish WakewordEngine')

    def kill(self):
        print('start kill all')
        #子(AIアシスタント)を終了
        self.google_assistant.kill()
        #自身(ウェイクワードエンジン)の停止
        self.detector.stream_in.stop_stream()
        self.detector.terminate()
        print('killed all')
        #プロセスを強制終了
        # sys.exit(0)
        os.kill(os.getpid(), signal.SIGKILL)

    def start_stream(self):
        self.detector.stream_in.start_stream()
        self.interrupted = False

    def stop_stream(self):
        self.detector.stream_in.stop_stream()
        self.interrupted = True

    def signal_handler(self, signal, frame):
        self.interrupted = True

    def interrupt_callback(self):
        return self.interrupted

    def on_wake(self, model):
        #誤反応の対処
        if time.time() - self.last < 3:
            return print('skip!', model) # 3秒以内に連続でWakeWordを認識させない

        #管理用ウェイクワードが呼び出された
        if model == 'snowboy':
            self.is_pause = not self.is_pause
            if self.is_pause:
                play_voice('runa_oyasumi')
                print('change to pause')
            else:
                play_voice('runa_ohayo', is_wait=True)
                print('change to active')
                self.google_assistant.start_conversation() # Assistantの音声認識開始
                play_voice('ding')
                self.last = time.time()
            return

        #管理用ウェイクワードにより、AIアシスタント呼び出し用がOFFになっているか
        if self.is_pause:
            return print('pause中', model)

        #AIアシスタント呼び出し用ウェイクワードが呼び出された
        print('wake!', model)
        self.google_assistant.start_conversation() # Assistantの音声認識開始
        play_voice('ding', [x in model for x in ['apeiria', 'asp', 'alexa', 'snowboy']].index(True))
        print('wake-end!', model)
        self.last = time.time()

# ---------------------------------------------------------------
# Google Assistant API
# ---------------------------------------------------------------

class GoogleAssistant(threading.Thread):
    def __init__(self, wakeword_engine):
        super(GoogleAssistant, self).__init__()

        self.wakeword_engine = wakeword_engine # 親
        self.is_kill = False # 終了フラグ(イベントループ脱出用)

        import json
        import google.oauth2.credentials
        from google.assistant.library import Assistant
        from google.assistant.library.event import EventType
        # from google.assistant.library.file_helpers import existing_file

        self.EventType = EventType # ライブラリ提供の定数群

        # 認証
        f = open('/home/pi/.config/google-oauthlib-tool/credentials.json', 'r')
        credentials = google.oauth2.credentials.Credentials(token=None, **json.load(f))
        # アシスタント起動準備
        self.assistant = Assistant(credentials, DEVICE_MODEL_ID)
        print(self.assistant.device_id)

        # テスト用、メソッド一覧の確認用
        # import inspect
        # for x in inspect.getmembers(assistant._lib, inspect.ismethod):
        #     print(x[0])

    #AIアシスタント起動(待機)
    def run(self):
        for event in self.assistant.start(): # イベントループのジェネレーター(無限ループ)
            res = self.process_event(event) # イベントが発生した
            if res == 'exit' or self.is_kill:
                break # 終了
        print('finish GoogleAssistant')

    #AIアシスタント終了
    def kill(self):
        self.is_kill = True
        self.stop_conversation()
        self.assistant.__exit__(0,0,0)

    #音声認識開始
    def start_conversation(self):
        self.assistant.start_conversation()

    #音声認識停止、認識後のイベント処理中断
    def stop_conversation(self):
        self.assistant.stop_conversation()

    #音声認識イベント(ボイスコマンド待機→認識→応答)
    def process_event(self, event):
        if event.type == self.EventType.ON_CONVERSATION_TURN_STARTED:
            print('conversation start! -------------')

        # print(event)

        # 音声認識終了 (正常終了)
        if (event.type == self.EventType.ON_CONVERSATION_TURN_FINISHED and
                event.args and not event.args['with_follow_on_turn']):
            print('-------------- conversation finish!')

        # 音声認識終了 (タイムアウト)
        if event.type == self.EventType.ON_CONVERSATION_TURN_TIMEOUT:
            print('-------------- conversation timeout!')
            play_voice('yukari_timeout')

        # GoogleAssistantのイベント処理に介入（独自処理）
        if type(event.args) == type({}) and 'text' in event.args:
            text = event.args['text']

            # 電気操作
            if re.search('(電気|でんき|デンキ|ライト)', text):
                self.stop_conversation()
                play_voice('apeiria_roger')
                if re.search('(点けて|付けて|着けて|つけて)', text):
                    print('light turn on !!!!!!!!!!!!!')
                    res = send_raspi('on')
                elif re.search('(消して|けして)', text):
                    print('light turn off !!!!!!!!!!!!!')
                    res = send_raspi('off')
                else:
                    print('you say light !!!!!!!!!!!!!')
                    res = send_raspi('toggle')
                play_voice('apeiria_positive_send_success' if 'success' in res else 'apeiria_negative')

            # エアコン操作
            if re.search('(エアコン|クーラー|暖房|だんぼう)', text):
                self.stop_conversation()
                play_voice('apeiria_roger')
                if re.search('(点けて|付けて|着けて|つけて)', text):
                    print('aircon turn on !!!!!!!!!!!!!')
                    res = send_raspi('aircon_on')
                elif re.search('(消して|けして)', text):
                    print('aircon turn off !!!!!!!!!!!!!')
                    res = send_raspi('aircon_off')
                else:
                    print('you say aircon !!!!!!!!!!!!!')
                    res = send_raspi('aircon_toggle')
                # play_voice('apeiria_positive_send_success' if 'success' in res else 'apeiria_negative')

            # エアコン操作
            if re.search('(扇風機|せんぷうき)', text):
                self.stop_conversation()
                play_voice('apeiria_roger')
                if re.search('(点けて|付けて|着けて|つけて)', text):
                    print('fan turn on !!!!!!!!!!!!!')
                    res = send_raspi('ifttt fan_on')
                elif re.search('(消して|けして)', text):
                    print('fan turn off !!!!!!!!!!!!!')
                    res = send_raspi('ifttt fan_off')
                else:
                    pass
                # play_voice('apeiria_positive_send_success' if 'success' in res else 'apeiria_negative')

            is_kill = False
            is_restart = False

            # PC起動(WOL)
            if re.search('(PC|パソコン)', text):
                self.stop_conversation()
                res = send_raspi('pc')
                play_voice('apeiria_roger')

            # モバマスBOTチェック
            if re.search('(BOT|ボット|サイト)', text) and re.search('(チェック|check)', text):
                self.stop_conversation()
                res = check_my_site()
                if not res:
                    play_voice('yukari_not_down', 1)

            # スマートスピーカーに対する操作
            if re.search('(キャンセル|きゃんせる|ストップ|すとっぷ)', text):
                play_voice('yukari_cancel')
            elif re.search('(バルス|ばるす|おやすみ|ばいばい|さよなら)', text):
                is_kill = True
            elif re.search('(リスタート|りすたーと|さいき|再起動|再起|サイキ|佐伯)', text) and re.search('(パイ|ぱい)'):
                is_kill = True
                is_restart = True
            else:
                pass # 介入無し (google assistantが応答)

            # log text
            if len(text) > 2:
                fp = open('voice_log.txt', 'a')
                fp.write(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S '))
                fp.write(text)
                fp.write("\n")
                fp.close()

                check_my_site()

            if is_kill:
                if is_restart:
                    os.system('/usr/local/pi/py/smart_speaker.sh restart')
                self.wakeword_engine.kill()

# ---------------------------------------------------------------
# 音声再生
# ---------------------------------------------------------------

import pygame.mixer
pygame.mixer.init()

# 予めロードしてすぐ再生できるように準備する
voices = {voice_file.replace('.wav', '') : pygame.mixer.Sound(RESOURCE_DIR + voice_file) for voice_file in voice_files}

def play_voice(key, num=0, is_wait=False):
    voices[key].play(num) # num+1回再生、-1は無限ループ
    if is_wait and num >= 0: time.sleep(voices[key].get_length() * (num + 1)) # 再生終了まで待機

# ---------------------------------------------------------------
# 別のRaspberry PiのTCPサーバーに接続してコマンドを送信
# ---------------------------------------------------------------

import socket

def send_raspi(cmd=b'test'):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT)) # 接続
    except ConnectionRefusedError:
        play_voice('apeiria_negative_err')
        return 'failure'
    client.send(cmd.encode())
    response = client.recv(1024).decode()
    print(response)
    return response

# ---------------------------------------------------------------
# 音声合成 (rospeex)
# ---------------------------------------------------------------

import urllib.request
import urllib.response
import urllib.error
import urllib.parse

import base64
import string
import wave
import mmap
import pyaudio

class VoiceSynthesis():
    def __init__(self):
        pass

    def speech(self, text, is_thread=False):
        return
        # if is_thread: return threading.Thread(target=self.speech, args=(text,)).start() # 別スレッドで実行
        data = self.make_voice(text)
        self.play(data)
        # self.save(data)

    def make_voice(self, text):
        tts_url ="http://rospeex.nict.go.jp/nauth_json/jsServices/VoiceTraSS"
        #音声合成
        tts_command = {
            'method':'speak',
            'params':[
                '1.1',
                {'language':'ja','text':text,'voiceType':"*",'audioType':"audio/x-wav"}
            ]
        }

        obj_command = json.dumps(tts_command).encode('utf-8') # string to json object
        req = urllib.request.Request(tts_url, obj_command)
        response = urllib.request.urlopen(req)
        received = response.read().decode('utf-8')  # conv bytes to str by decode()
        # extract wav file
        obj_received = json.loads(received)
        data = base64.decodestring(obj_received['result']['audio'].encode('utf-8'))
        return data

    def play(self, data):
        # 音声データをファイルに保存せずにそのまま再生
        speechMap = mmap.mmap(-1,len(data))
        speechMap.write(data)
        speechMap.seek(0)

        wf = wave.open(speechMap, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                      channels=wf.getnchannels(),
                      rate=wf.getframerate(),
                      output=True)

        chunk = 1024
        while 1:
            data = wf.readframes(chunk)
            if len(data) == 0: break
            stream.write(data)
        stream.close()
        p.terminate()
        speechMap.close()

    def save(self, data, filename='maked_voice.wav'):
        f = open (filename,'wb')
        f.write(data)
        f.close()
        # os.system('aplay %s' % filename)


# ---------------------------------------------------------------
# 朝アラーム
# ---------------------------------------------------------------
import schedule
def good_morning():
    # 電気付ける
    send_raspi('on')

    # 扇風機消す
    send_raspi('ifttt fan_off')

    # アラーム
    play_voice('runa_ohayo', 5, is_wait=True)
    # check_my_site()

    # 扇風機消す
    # play_voice('raspi', is_wait=True)
    # time.sleep(1)
    # play_voice('fan_off', is_wait=True)

    # time.sleep(10)

    # # 天気予報
    # play_voice('raspi', is_wait=True)
    # time.sleep(1)
    # play_voice('weather', is_wait=True)

def my_schedule(timer, target, is_thread=True):
    if is_thread: return threading.Thread(target=my_schedule, args=(timer, target, False)).start()

    while 1:
        now = datetime.datetime.now()
        today_h18_str = now.strftime('%Y-%m-%d xxx:%S'.replace('xxx', timer))
        today_h18 = datetime.datetime.strptime(today_h18_str, '%Y-%m-%d %H:%M:%S')
        tomorrow_h18 = today_h18 + datetime.timedelta(days=1)
        if float(today_h18.strftime('%s')) - float(now.strftime('%s')) > 0:
            t = float(today_h18.strftime('%s')) - float(now.strftime('%s'))
        else:
            t = float(tomorrow_h18.strftime('%s')) - float(now.strftime('%s'))
        print('schedule sleep', t)
        time.sleep(t)
        target()
        time.sleep(60 * 5)

# ---------------------------------------------------------------
# サイト用BOT稼働状況チェッカー
# ---------------------------------------------------------------
# 起床時や、その他アクション時に並行してチェックさせる

import json
SITE_DOWN_CNT = 0
def check_my_site(is_thread=True):
    global SITE_DOWN_CNT
    return False
    if is_thread: return threading.Thread(target=check_my_site, args=(False,)).start()

    url = 'https://imcgdb.info/api.php?ctrl=check-bot'

    is_down = False
    try:
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req)
        received = response.read().decode('utf-8')
        res = json.loads(received)
        SITE_DOWN_CNT = 0
    except urllib.error.HTTPError as e:
        if e.code >= 400 and e.code <= 599:
            pass
        is_down = true
        play_voice('yukari_site_down', 2)
        return is_down
    except:
        SITE_DOWN_CNT += 1
        #if SITE_DOWN_CNT >= 3:
        play_voice('yukari_site_down', 2)
        is_down = True
        return is_down

    print(res)

    now = datetime.datetime.now()
    for key in ['get-for-status-bot', 'set-for-new-card-bot2', 'get-for-bot']:
        if key in res:
            last = datetime.datetime.strptime(res[key], '%Y-%m-%d %H:%M:%S')
            delta = now - last
            if delta.total_seconds() > 60 * 60 * 6: is_down = True
    # if 'status-bot' in res:
    #     dt_status = datetime.datetime.strptime(res['status-bot'], '%Y-%m-%d %H:%M:%S')
    #     delta_status = now - dt_status
    #     if delta_status.total_seconds() > 60 * 60 * 6: is_down = True
    # if 'new-card-bot' in res:
    #     dt_new_card = datetime.datetime.strptime(res['new-card-bot'], '%Y-%m-%d %H:%M:%S')
    #     delta_new_card = now - dt_new_card
    #     if delta_new_card.total_seconds() > 60 * 60 * 6: is_down = True
    # if 'trade-history-bot' in res:
    #     dt_trade_history = datetime.datetime.strptime(res['trade-history-bot'], '%Y-%m-%d %H:%M:%S')
    #     delta_trade_history = now - dt_trade_history
    #     if delta_trade_history.total_seconds() > 60 * 60 * 6: is_down = True

    print(is_down)

    if is_down:
        play_voice('yukari_bot_down', 2)

    return is_down

# ---------------------------------------------------------------
# start
# ---------------------------------------------------------------

def main():
    print('start')

    my_schedule('07:35', lambda: play_voice('runa_ohayo', 2))
    my_schedule('07:55', good_morning)
    my_schedule('08:40', lambda: play_voice('yukari_itterassai', 10))
    my_schedule('18:00', lambda: play_voice('alarm18', 5))

    wakeword_engine = WakewordEngine()
    wakeword_engine.start()
    while 1:
        if input('exit?>') in ['exit', 'y']:
            break
    print('end')
    wakeword_engine.kill()

if __name__ == '__main__':
    main()
