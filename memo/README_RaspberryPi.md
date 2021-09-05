
https://liginc.co.jp/261317

目次
	+ OSインストール
	+ wifi接続、パスワード変更、ホスト名変更、ip固定、デフォルトをCUIに切り替、ssh接続え
	+ vnc設定


■OSインストール
	公式HPから最も標準的なOS「Raspbian（ラズビアン）」をDLする。
	以下から必要なファイル群「NOOBS」をDL（NOOBS LiteにはOSが入っていないのでNG）
	https://www.raspberrypi.org/downloads/
	zipを解凍して中身をMicroSDに移す。

	NOOBS：New Out Of Box Software

	ラズパイにMicroSDを入れ、有線のマウス・キーボードを接続。
	HDMIでディスプレイに繋ぎ、microUSBで電源供給し、電源を入れるとインストール画面が出る。
	※電源ON：microUSBを刺したら電源がONになる。

■ OS install for Zero WH

	raspbian-stretch-liteをダウンロードして解凍、imgファイルをetcherを使ってmicroSDに焼く。（liteはデスクトップGUI環境なし）
	ファイル初期配置（これをしておけばすぐにwifi接続・SSH利用ができ、画面につなぐ必要がなくなる）
		・SSH
			すぐにSSHを利用できるようにするにはsshというファイルをrootに置いておく必要がある（ファイルの中身は空でOK）
		・WIFI
			すぐにwifiを利用できるようにするために/etc/wpa_supplicant/wpa_supplicant.confを作成

				country=JP
				ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
				update_config=1
				network={
						ssid="----Your-WiFi-SSID----"
						psk="----PLAIN-PASSPHRASE----"
				}

	sudo apt update
	sudo apt upgrade
	sudo apt dist-upgrade
	sudo rpi-update

	# nodejsのインストール
	https://nodejs.org/ja/download/package-manager/
		curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
		sudo apt-get install -y nodejs

	# nodejs for raspberry pi zero
		wget -O - https://raw.githubusercontent.com/sdesalas/node-pi-zero/master/install-node-v.last.sh | bash

	sudo npm i -g npm

	sudo apt install vim


■ネットワーク設定

●GUIで設定
	wifi接続
	設定
		システム
			パスワード　→　piユーザのパスワードを変更
			ホスト名
			Boot	→　TO CLIでデフォルトをCUI（起動時にstartxしない）に切り替え
		インターフェイス
			SSH、VNCを有効化
		パフォーマンス
		ロケーション
			ロケーション、タイムゾーン、キーボード、wifi国　→　全部日本に変更

●パスワード変更
	sudo passwd pi
	sudo passwd root
	
●ホスト名hostname変更
	sudo vim /etc/hostname
	sudo vim /etc/hosts
		127.0.1.1       raspberrypi-zero

●ローカルIPを固定
	sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.bk
	sudo vim /etc/dhcpcd.conf
		#有線：eth0、無線：wlan0
		interface wlan0
		static ip_address=192.168.x.x
		static routers=192.168.x.1
		static domain_name_servers=192.168.x.1 8.8.8.8
		
	#ipを調べる
	ifconfig
		


●VNCを有効化
	RealVNCはraspbianに標準で入ってるが、一応確認しとく（既に最新ですとなる）
	sudo apt-get install realvnc-vnc-server

	設定はGUIで
		startxして設定＞Raspberry Piの設定からVNCのところの有効にチェック。これだけで、ラズパイ起動時のサービス自動起動設定までされる。
		再起動
		右上VNCメニュー -> Options -> Troubleshooting -> Enable experimental direct capture modeにチェック
		#デフォルトではパスワードがUNIXパスワードになっているのでVNCパスワードを設定する
		右上VNCメニュー -> Security -> AuthenticationをUNIX PasswordからVNC Passwordに変更
		
		
●容量を変更
	#容量を確認すると、microSDの容量より小さい。
	df -h
	#フルに使えるようにする
	sudo raspi-config
		Advanced Options > Expand Filesystem
	#raspi-configがうまくいかない場合（Your partition layout is not currently supported by this tool）
	sudo apt-get install gparted
	startx
		sudo gparted
