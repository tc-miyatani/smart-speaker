<?php

function checkPass($pass) {
    return hash_hmac('sha256', $pass, false) == 'de3d8f455481f104a7465e298a13f470065a31cf36dc55817a2407fc89f8462b';
}

if (!isset($_POST['ctl']) &&
     isset($_COOKIE['login']) &&
     checkPass($_COOKIE['login'])) {
    //ログイン済み
    require_once 'view_main.php';
    exit;
}

$login_err = false;
switch ($_POST['ctl']) {
    case 'login':
        //ログイン処理
        if (checkPass($_POST['pass'])) {
            //パスワード一致
            setcookie('login', $_POST['pass']);
            header('Location: ./');
            exit;
        }
        //パスワード不一致
        $login_err = true;
        break;

    case 'logout':
        //ログアウト処理
        setcookie('login', '', time() - 1);
        header('Location: ./');
        exit;

    default:
        break;
}
require_once 'view_login.php';
