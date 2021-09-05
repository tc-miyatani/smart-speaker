<?php

// ini_set('display_errors', 'On');
// error_reporting(E_ALL);

$is_safemode = ini_get('safe_mode');

if ($is_safemode) {
    $result = ['msg' => 'セーフモードの為、処理できませんでした。'];
} else {
    $ctl = $_POST['ctl'] ?? '';
    switch ($ctl) {
        case 'aircon_on':
            exec('/usr/local/raspberrypi/infrared/c/sendir /usr/local/raspberrypi/infrared/c/aircon_on.data 1 0', $sh);
            $result = ['msg' => 'エアコンを操作しました。', 'sh' => $sh];
            break;

        case 'light_on':
            exec('/usr/local/raspberrypi/infrared/c/sendir /usr/local/raspberrypi/infrared/c/light_on.data 1 0', $sh);
            $result = ['msg' => '電気を操作しました。', 'sh' => $sh];
            break;

        case 'pc_on':
            exec('/usr/local/raspberrypi/wol/wol.sh', $sh);
            //$sh = shell_exec('/usr/local/raspberrypi/wol/wol 192.168.10.105 1C-87-2C-74-39-CA');
            $result = ['msg' => 'PCを起動しました。', 'sh' => $sh];
            break;

        default:
            $result = ['msg' => '未定義の命令です。'];
            break;
    }

    date_default_timezone_set('Asia/Tokyo');
    $s = date('Y-m-d H:i:s') . ': ctl = ' . $ctl . "\n";
    $fp = fopen('./log.txt', 'a');
    fwrite($fp, $s);
    fclose($fp);
}

header('content-type: application/json; charset=utf-8');
echo json_encode($result);
