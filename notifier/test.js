

//google home test
const googlehome = require('./google-home-notifier');

const deviceName = 'メイン';
const language = 'ja';
const ip = '192.168.10.101';

googlehome
    .device(deviceName, language)
    .ip(ip, language)
    .accent(language)
    ;

async function gh_send_msg(msg) {
    return new Promise(function(resolve, reject) {
        googlehome.notify(msg, function(res) {
          console.log(res);
          resolve();
        });
    });
}

//音声を再生 第1引数:ファイルPATH or URL
async function gh_send_mp3(mp3) {
    return new Promise(function(resolve, reject) {
        googlehome.play(mp3, function(res) {
          console.log(res);
          resolve();
        });
    });
}

async function sleep(msec) {
    return new Promise(function (resolve, reject) {
        setTimeout(function() {
            resolve();
        }, msec);
    });
}


(async function() {
    // await gh_send('Hello World');
    // await sleep(1000);
    await gh_send_msg('はいどーも、キズナアイです。');
})();


