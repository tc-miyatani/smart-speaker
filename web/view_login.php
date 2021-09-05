<!DOCTYPE html><html lang="ja">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0 , minimum-scale=1.0, maximum-scale=2.0">
        <meta name="theme-color" content="#dff">
        <title>遠隔 ログイン</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0-beta/css/materialize.min.css">
        <style>
            .main {
                padding: 0 10%;
            }
            .main-title {
                font-size: 25px;
            }
            .err-msg {
                padding: 10px;
                background: pink;
                color: red;
            }
            .submit-btn {
                width: 100%;
            }
        </style>
    </head>
    <body class="grey lighten-2">
        <main class="main center-align">
            <h1 class="main-title cyan-text text-accent-4">遠隔操作 ログイン</h1>
            <?php if($login_err): ?>
            <p class="err-msg">ログインに失敗しました</p>
            <?php endif; ?>
            <form method="post" action="./index.php">
                <p class="input-field">
                    <input type="hidden" name="ctl" value="login">
                    <input type="password" name="pass" class="validate">
                    <label for="pass">Password</label>
                </p>
                <p>
                     <button type="submit" class="submit-btn waves-effect waves-light btn-large">ログイン</button>
                </p>
            </form>
        </main>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0-beta/js/materialize.min.js"></script>
    </body>
</html>
