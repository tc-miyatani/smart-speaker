
●温度センサ
DS18B20+(+がつく方は鉛フリー品、特に違いなし)
パラサイトパワーモード(寄生電源モード)というのがあり、GNDと信号線の2本だけで配線できる。
	→pullupが必要なため、電源への配線も必要（結局3本）



#1-wireを有効化、GPIO番号を指定
vim /boot/config.txt
	#ファイル末尾に追記
	dtoverlay=w1-gpio-pullup,gpiopin=20#external pullup（MOSFET pullup）する場合
	dtoverlay=w1-gpio,gpiopin=20,pullup=y#パラサイトパワーモード
reboot	

#w1-gpioとw1-thermのカーネルモジュールをロード
sudo modprobe wire
sudo modprobe w1-gpio
sudo modprobe w1-therm
cd /sys/bus/w1/devices
ls
cd 28-〇〇〇〇#〇〇〇〇の部分はデバイス毎に異なる
cat w1_slave






gpio -g mode 5 out
gpio -g mode 13 out
gpio -g write 5 1
gpio -g write 13 1
gpio -g write 5 0
gpio -g write 13 0
gpio readall
 +-----+-----+---------+------+---+---Pi 3---+---+------+---------+-----+-----+
 | BCM | wPi |   Name  | Mode | V | Physical | V | Mode | Name    | wPi | BCM |
 +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
 |     |     |    3.3v |      |   |  1 || 2  |   |      | 5v      |     |     |
 |   2 |   8 |   SDA.1 |   IN | 1 |  3 || 4  |   |      | 5v      |     |     |
 |   3 |   9 |   SCL.1 |   IN | 1 |  5 || 6  |   |      | 0v      |     |     |
 |   4 |   7 | GPIO. 7 |   IN | 1 |  7 || 8  | 0 | IN   | TxD     | 15  | 14  |
 |     |     |      0v |      |   |  9 || 10 | 1 | IN   | RxD     | 16  | 15  |
 |  17 |   0 | GPIO. 0 |  OUT | 1 | 11 || 12 | 0 | IN   | GPIO. 1 | 1   | 18  |
 |  27 |   2 | GPIO. 2 |   IN | 0 | 13 || 14 |   |      | 0v      |     |     |
 |  22 |   3 | GPIO. 3 |   IN | 0 | 15 || 16 | 1 | IN   | GPIO. 4 | 4   | 23  |
 |     |     |    3.3v |      |   | 17 || 18 | 0 | IN   | GPIO. 5 | 5   | 24  |
 |  10 |  12 |    MOSI |   IN | 0 | 19 || 20 |   |      | 0v      |     |     |
 |   9 |  13 |    MISO |   IN | 1 | 21 || 22 | 0 | IN   | GPIO. 6 | 6   | 25  |
 |  11 |  14 |    SCLK |   IN | 0 | 23 || 24 | 1 | IN   | CE0     | 10  | 8   |
 |     |     |      0v |      |   | 25 || 26 | 1 | IN   | CE1     | 11  | 7   |
 |   0 |  30 |   SDA.0 |   IN | 1 | 27 || 28 | 1 | IN   | SCL.0   | 31  | 1   |
 |   5 |  21 | GPIO.21 |  OUT | 0 | 29 || 30 |   |      | 0v      |     |     |
 |   6 |  22 | GPIO.22 |   IN | 1 | 31 || 32 | 1 | IN   | GPIO.26 | 26  | 12  |
 |  13 |  23 | GPIO.23 |  OUT | 0 | 33 || 34 |   |      | 0v      |     |     |
 |  19 |  24 | GPIO.24 |  OUT | 1 | 35 || 36 | 0 | IN   | GPIO.27 | 27  | 16  |
 |  26 |  25 | GPIO.25 |   IN | 0 | 37 || 38 | 0 | IN   | GPIO.28 | 28  | 20  |
 |     |     |      0v |      |   | 39 || 40 | 1 | IN   | GPIO.29 | 29  | 21  |
 +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
 | BCM | wPi |   Name  | Mode | V | Physical | V | Mode | Name    | wPi | BCM |
 +-----+-----+---------+------+---+---Pi 3---+---+------+---------+-----+-----+


●照度センサ
	照度(ルクス[lx])：その場所の明るさの単位
	     0.1 -  1.0 : 月明かり
		 1.0 -   10 : 常夜灯
		 150 -  500 : 住宅照明
		2500 - 3000 : 朝日を室内、コンビニ店内
	   10000 -      : 屋外
 
		デスクライト
			直下 : 1000 - 2000[lx]
			30cm : AA: 500[lx]以上、 A: 300[lx]以上
			50cm : AA: 250[lx]以上、 A: 150[lx]以上
 
 
NJL7302L-F3
 
 
 
Vc = 3V, R = 10kΩ
	暗い、明るいが分かればいい程度なので
	比較的低照度でも電圧変動が認識しやすい抵抗値で、
	その代わり、強い光を当てると当然上限の3[V]付近に達する
 
	ダイナミックレンジを大きく取る場合は、電源電圧をもっと高くし、抵抗値を下げる必要がある
	出力が小さい時はオペアンプで増幅した電圧を、出力が小さい時はそのままの出力を使用すれば、精度を高められる
	
 
	NJL7502L
		照度計算
			データシートのLux-ILグラフより		lx = 2 * IL[uA]
			出力電圧が0.14[V]の時 		lx = 2 * (0.14v / 10kΩ) =  28[lx]
						3[V]の時			lx = 2 * (3.0v  / 10kΩ) = 600[lx]
			従って、電源3.3[V]、抵抗10[kΩ]の場合、600[lx]程度までしか測定できない
				SH7262 A/D変換での予想値
				　　 28[lx] > 0.14[V] >  43
				　　380[lx] > 1.90[V] > 589
				A/D値 * 0.64516129 = lx
 
			5Vで使う分には特に壊れることは無いでしょう。
			明るいオフィスで400Lux程度らしいので、データシートのグラフ Photocurrent VS Illuminance を見てみると流せる電流は100μA程度であることがわかります。
			100μA流れるときに抵抗の両端の電圧が5Vになるには5V÷100μA=50kΩ
			室内灯に反応させるには47kΩとか使っておけば大丈夫でしょう。
			もっと暗い場所50Luxで反応させたい時には抵抗値を上げ(470kΩ)、もっと明るい場所やレーザー3000Luxに反応させたい場合は抵抗値を下げます(4.7kΩ)	
 
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.IN)
for i in range(10):
	if GPIO.input(16) == GPIO.HIGH:
		print "lightness",
	else:
		print "darkness",
print GPIO.input(16), GPIO.HIGH, GPIO.LOW
GPIO.cleanup()



SPI有効化
	sudo raspi-config
		Interfacing Options＞SPI
	reboot

SPIが有効化されてるか確認
	ls /dev/spi*
		/dev/spidev0.0 /dev/spidev0.1　#左の結果が出ればOK


import time, sys
from gpiozero import MCP3002

Vref = 3.29476

pot = MCP3002(channel=0)
while 1:
	print pot.value*Vref
	time.sleep(1)


import time, sys
import spidev

Vref = 3.29476
spi = spidev.SpiDev()
spi.open(0,0) #port 0,cs 0
adc = spi.xfer2([0x68,0x00])
data = ((adc[0] & 3) << 8) | adc[1]
print (str(Vref*data/1023) + "V")

spi.close()





