
Wake On LAN

ipconfig /all
	物理アドレス
	1C-87-2C-74-39-CA

#DL,コンパイル
	mkdir wol
	cd wol
	wget http://www.gcd.org/sengoku/docs/wol.c
	gcc wol.c -o wol

#実行
	./wol　<IP> <MAC>
	./wol 192.168.10.105 1C-87-2C-74-39-CA


#シェルスクリプト
cat <<'EOF' > ./wol.sh
./wol 192.168.10.105 1C:87:2C:74:39:CA
EOF

	chmod 700 wol.sh
	./wol.sh
	
	
	
# windows 10 高速スタートアップを無効 (アプデで強制的に有効化される)
コントロールパネル＞電源オプション＞電源ボタンの動作を選択する
	現在利用可能ではない設定を変更します
	高速スタートアップを有効にする（推奨）のチェックを外す→変更の保存

	
	
### ??

System Configuration → Integrated NIC を Enabaled に
Power Management → Wake on LAN を LAN only に
Power Management → Deep Sleep Control を Disabled に

	