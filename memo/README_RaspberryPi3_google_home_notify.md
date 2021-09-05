
sudo apt-get install -y nodejs
sudo npm -g install n
sudo n lts
シェルに入り直す
node -v

sudo apt-get install git-core libnss-mdns libavahi-compat-libdnssd-dev
git clone https://github.com/noelportugal/google-home-notifier
cd google-home-notifier
npm install

node test.js
