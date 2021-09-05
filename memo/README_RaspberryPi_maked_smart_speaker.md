
# Raspberry Piにマイク・スピーカーを繋いで、自作スマートスピーカー（Google Home miniもどき）にする

## 音声関連ライブラリのインストール

	python --version # Python 2.7.13
	python3 --version # Python 3.5.3

	sudo apt install python-pyaudio python3-pyaudio sox

	ls -l /usr/bin/python3
	ls -l /usr/bin/python3.5
	sudo find / -name "python3.5" -type d
		/etc/python3.5
		/usr/share/doc/python3.5
		/usr/local/lib/python3.5
		/usr/lib/python3.5

	# python3でsnowboyを利用する場合、swig3.0.12以上が必要なのでソースインストールする
		wget http://prdownloads.sourceforge.net/swig/swig-3.0.12.tar.gz
		tar xvzf swig-3.0.12.tar.gz
		cd swig-3.0.12

		sudo apt-get install autoconf automake libtool
		sudo apt-get install libpcre3-dev
		
		./configure
		make
		make install
		swig -version
	
	pip --version
	python3 -m pip --version
	pip install pyaudio
	python3 -m pip install pyaudio

	sudo apt install libatlas-base-dev

	
--------

## サウンドデバイスの設定と動作確認

### サウンドの出力を有効にする（モニター出力がHDMIモードでないと音声が出力されない）
	sudo vim /boot/config.txt
		hdmi_driver=2 # コメントを外す
		dtparam=audio=on

### サウンドデバイスのが認識されてるか確認
	aplay -l
	arecord -l
	lsusb # 「◯◯ Audio Codec」等と表示されていたら、認識されている
	cat /proc/asound/modules
	cat /proc/asound/cards
	

### サウンドデバイスの優先順位の設定
	sudo vim /usr/share/alsa/alsa.conf
		# "~/.asoundrc" # 17行目先頭に「#」追加(コメントアウト)
		
		defaults.ctl.card 1 # 0から1へ変更
		defaults.pcm.card 1 # 0から1へ変更

### test
	aplay test.mp3
	aplay -D plughw:0,1 test.mp3 # plughw:カード番号,デバイス番号
	aplay -D plughw:1,0 test.mp3
	arecord -D plughw:1,0 test.wav
	rec test.wav

### 音量の設定
	alsamixer
	
	sudo apt-get install alsa-base alsa-utils alsa-tools
	sudo rm /etc/modprobe.d/alsa-base.conf
	sudo vim /usr/share/alsa/alsa.conf
		defaults.ctl.card 0
		defaults.pcm.card 0
	sudo vim ~/.asoundrc
	
	arecord -f S16_LE -D hw:1,0 test.wav
	arecord -f S16_LE -r 44100 -D hw:1,0
	arecord -f dat -t wav test.wav
		-f cd  # -f S16_LE -c2 -r48000 の短縮形
		-f dat # -f S16_LE -c2 -r44100 の短縮形

	arecord -f S16_LE -r 16000 -c 1 -D hw:1,0 test.wav
	arecord -D plughw:1,0 -f cd -r 16000 test.wav
	
	
	apt install pulseaudi
	mkdir -p ~/.config/pulse
	cp /etc/pulse/client.conf ~/.config/pulse
		autospawn = no
		daemon-binary = /bin/true
	 cp /etc/pulse/default.pa ~/.config/pulse
	
	
--------
	
## Snowboy

### Snowboyのinstall, test
	http://docs.kitt.ai/snowboy/
		wget https://s3-us-west-2.amazonaws.com/snowboy/snowboy-releases/rpi-arm-raspbian-8.0-1.1.1.tar.bz2
		tar -xvf rpi-arm-raspbian-8.0-1.1.1.tar.bz2
		cd rpi-arm-raspbian-8.0-1.1.0
		python demo.py resources/snowboy.umdl # 「snowboy」と話しかけるとコマンドラインにメッセージが表示されると共に確認音が再生される
	
		git clone https://github.com/Kitt-AI/snowboy.git
		cd snowboy/swig/Python3
		make
		demo.py、snowboydecoder.py及びresourcesディレクトリをmakeしたディレクトリにコピー
		python3 demo.py resources/snowboy.umdl
	
	
### 独自のWakeword(Hotword)のモデルデータを作成
	
	Snowboyウェブサイトでの登録
		ソーシャルログイン（Google, Github等）
		Create Hotword＞input title,language,comment>record＞test>Save and Donwload
	
	python demo.py resources/raspberrypi.umdl

----------	

## Google Assistant SDK
	
	
	### Google Cloudと繋いで、Google Assistant APIと接続できるようにする
		「Google Cloud Console」にログイン
		プロジェクトの作成＞プロジェクト名を入力
		「Google Assistant API」を検索して、有効にする
		認証情報を作成＞OAuth クライアントID＞同意画面を設定＞サービス名を入力して、保存
			その他＞名前を入力して、作成
			OAuthクライアントIDをダウンロード

			545448891061-5aan0erh206nussunkhjc99rf6s2mpmc.apps.googleusercontent.com
			odaMjGwI8-HDXbkB630T_p6c
	
		Google Cloudに登録したアカウントの設定を変更
		「https://myaccount.google.com/activitycontrols」にアクセスし、以下の項目をオンにします。
			ウェブとアプリのアクティビティ（「Chrome の閲覧履歴と Google サービスを使用するウェブサイトやアプリでのアクティビティを含める」にもチェック」）
			端末情報
			音声アクティビティ
	
	### インストール　（仮想環境）
		https://developers.google.com/assistant/sdk/guides/library/python/embed/install-sample
			sudo apt-get install python3-dev python3-venv
			python3 -m pip install --upgrade pip setuptools wheel

			sudo apt install portaudio19-dev libffi-dev libssl-dev
			python3 -m pip install pyasn1-modules
			python3 -m pip install --upgrade google-assistant-library
			python3 -m pip install --upgrade google-assistant-sdk[samples]
			
		
	### 端末の認証、デバイスの登録
		python3 -m pip install --upgrade google-auth-oauthlib[tool]
		google-oauthlib-tool --scope https://www.googleapis.com/auth/assistant-sdk-prototype \
          --save --headless --client-secrets client_secret_◯◯◯.apps.googleusercontent.com.json
			# authorization code: 上記コマンドで出てきたURLをコピーしてアクセスして認証コードを取得する

		https://developers.google.com/assistant/sdk/reference/device-registration/device-tool
		googlesamples-assistant-devicetool register-model --model miyahei-raspberrypi3-01 --type SWITCH --manufacturer My-Smart-Speaker --product-name My-Smart-Speaker

		
		#### 確認
		googlesamples-assistant-devicetool list --model
		googlesamples-assistant-devicetool list --device
				
				
	### テスト？
		googlesamples-assistant-pushtotalk --project-id smart-speaker-203010 --device-model-id miyahei-raspberrypi3-01 --lang ja_jp
			##### Ctrl+Zで終了
		googlesamples-assistant-hotword --project_id smart-speaker-203010 --device_model_id miyahei-raspberrypi3-01
			##### Illegal instruction　→　RaspberryPi Zeroは未対応
				wget http://node-arm.herokuapp.com/node_latest_armhf.deb
				sudo dpkg -i node_latest_armhf.deb


pythonライブラリの保存場所を調べる
import google.assistant.library
print(google.assistant.library.__file__) # /usr/local/lib/python3.5/dist-packages/google/assistant/library/__init__.py
print(google.assistant.library.__path__) # /usr/local/lib/python3.5/dist-packages/google/assistant/library

				
### AIY	

git clone https://github.com/google/aiyprojects-raspbian.git


https://github.com/warchildmd/google-assistant-hotword-raspi.git

=========================================================================

	#開発者登録
		amazon.co.jp＞アカウントサービス＞コンテンツと端末の管理＞設定＞居住国設定＞日本となってることを確認（なってなければ設定）
		Amazon 開発者ポータル（https://developer.amazon.com/ja/）にamazon.co.jpのアカウントでログイン
			アカウント情報登録の画面になるので、必須項目を入力していきます。
			Developer Console＞Alexa Voice Service＞製品を作成
	
	#インストール
		git clone https://github.com/alexa/alexa-avs-sample-app.git
		cd alexa-avs-sample-app
		vim automated_install.sh
			ProductID（デバイスID/製品ID）,　ClientID（クライアントID）,　ClientSecret（クライアントシークレット）を開発者登録で取得した値に設定
		. automated_install.sh # いくつか質問に答える、インストールは30分程かかる

		
	VNCでログインして、3つのターミナルを立ち上げてコマンドを順番に実行（順番が大事）
		（1） AVS認証用のWebサービス実行
			cd /usr/local/pi/alexa/alexa-avs-sample-app/samples/companionService && npm start

		（2） Sample App実行
			cd /usr/local/pi/alexa/alexa-avs-sample-app/samples/javaclient && mvn exec:exec
				しばらくすると、ポップアップ画面が現れてAVSへの認証を促されるのでAmazon Developerアカウントでログイン。
				device tokens readyという表示が出ればOK。

		（3） wake word engine実行
			cd /usr/local/pi/alexa/alexa-avs-sample-app/samples/wakeWordAgent/src && ./wakeWordAgent -e sensory
			cd /usr/local/pi/alexa/alexa-avs-sample-app/samples/wakeWordAgent/src && ./wakeWordAgent -e kitt_ai
		
	---------------
	
	AVS Device SDK
	https://github.com/alexa/avs-device-sdk/wiki/Raspberry-Pi-Quick-Start-Guide-with-Script
		### install
			wget https://raw.githubusercontent.com/alexa/avs-device-sdk/master/tools/Install/setup.sh && wget https://raw.githubusercontent.com/alexa/avs-device-sdk/master/tools/Install/config.txt && wget https://raw.githubusercontent.com/alexa/avs-device-sdk/master/tools/Install/pi.sh
			sudo bash setup.sh config.txt
				すぐに「enter "AGREE".」と出るのでAGREEと入力してENTER
				15分程待つと「Press RETURN to review the license agreement and update the files.」と出るので、ENTER
				スペースでライセンスをスクロールして読み進めると「Do you accept this license agreement? [yes or no]」と出るのでyesと入力してENTER
				15分ほど待つと「Completed Configuration/Build」と出る
		
		###　認証
			sudo bash startsample.sh
			「To authorize, browse to: ～」と出るので指定されたURLにアクセスし、AmazonアカウントでログインしてAllowで認証する。
			「アレクサ！」と話しかけるか「t」を入力しエンター押下すると、画面上にログが流れるので続けて、話しかける。
			startsample.shが実行されている状態で、「c」→「1」→「6」の順番でキー入力でALEXAを日本語化出来る

		3ヶ月経つと認証が切れるが、installからやり直せば復活利用できるかもしれない？


	UNRECOVERABLE CAPABILITIES API ERROR: FORBIDDEN
	

	sudo apt-get install pulseaudio

	sudo vim /etc/pulse/daemon.conf
		; resample-method = speex-float-3
		resample-method = trivial
		default-sample-rate = 48000
		; enable-remixing = yes
		; enable-lfe-remixing = no

	sudo vim /etc/pulse/client.conf

	pulseaudio -D 
	lsusb
	pactl list short sources
	pacmd set-default-source 0
	arecord -c 1 -r 16000 -f S16_LE test.wav

	#入力を探す
	pacmd list-sources | grep -e device.string -e 'name:'
	#一時設定
	pacmd "set-default-source <NAME>"
	pacmd "set-default-source alsa_input.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.analog-mono"
	#恒久的設定
	vim /etc/pulse/default.pa
		set-default-source alsa_input.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.analog-mono

	#出力ソースを探す
	pacmd list-sinks | grep -e 'name:' -e 'index'
	#一時設定
	pacmd "set-default-sink <NAME>"
	pacmd "set-default-sink alsa_output.usb-C-Media_Electronics_Inc._USB_Audio_Device-00.analog-stereo"
	pacmd "set-default-sink alsa_output.platform-soc_audio.analog-stereo"
	
	
	#恒久的設定
	sudo vim /etc/pulse/default.pa
		set-default-sink <NAME>	
	
	# 再起動
	pulseaudio -k 
	pulseaudio --start
	
	
sudo vim /etc/pulse/default.pa
	load-module module-udev-detect tsched=no
	load-module module-echo-cancel
sudo vim /etc/pulse/daemon.conf
	default-fragment-size-msec=5
	
	pacmd list-modules
	
	sudo apt-get install pavucontrol