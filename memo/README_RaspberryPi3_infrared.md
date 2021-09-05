
■ 赤外線リモコン

● インストール
git clone git://git.drogon.net/wiringPi
cd wiringPi
./build

gcc scanir.c -o scanir -lwiringPi
gcc sendir.c -lm -o sendir -lwiringPi

● 学習、送信
gpio readall
#赤外線スキャン 第1引数:データ保存先, 第2引数:wPi(WiringPi)番号
./scanir light_on.data 7
#赤外線スキャン 第1引数:データ保存先, 第2引数:連続送信回数, 第3引数:wPi(WiringPi)番号
./sendir light_on.data 1 0


./scanir aircon_on.data 7
./scanir aircon_off.data 7

cd /usr/local/raspberrypi/infrared/c
./sendir aircon_on.data 1 0
./sendir aircon_off.data 1 0


cd /usr/local/pi/infrared
./sendir light_on.data 1 0


