<!DOCTYPE html><html lang="ja">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0 , minimum-scale=1.0, maximum-scale=2.0">
        <meta name="theme-color" content="#dff">
        <title>遠隔</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0-beta/css/materialize.min.css">
        <style>
            .main {
                padding: 0 10%;
            }
            .main-title {
                font-size: 25px;
            }
            .send-btn,
            .submit-btn
            {
                width: 100%;
            }
            .loading {
                display: none;
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 100;
                padding: 10%;
                background: rgba(50, 50, 50, 0.8);
            }
            .preloader-wrapper.custom {
                width: 300px;
                height: 300px;
            }
        </style>
    </head>
    <body class="grey lighten-2">
        <main class="main center-align">
            <h1 class="main-title cyan-text text-accent-4">遠隔操作</h1>
            <p>
                <button id="aircon_on" class="send-btn waves-effect waves-light btn-large">エアコン</button>
            </p>
            <p>
                <button id="light_on" class="send-btn waves-effect waves-light btn-large">電気</button>
            </p>

            <p>
                <button id="pc_on" class="send-btn waves-effect waves-light btn-large">PC</button>
            </p>
            <hr>
            <form method="post" action="./index.php">
                <p>
                    <input type="hidden" name="ctl" value="logout">
                    <button type="submit" class="submit-btn waves-effect waves-light btn-large">ログアウト</button>
                </p>
            </form>
        </main>
        <div class="loading center-align">
          <div class="preloader-wrapper custom active">
            <div class="spinner-layer spinner-blue-only">
              <div class="circle-clipper left">
                <div class="circle"></div>
              </div><div class="gap-patch">
                <div class="circle"></div>
              </div><div class="circle-clipper right">
                <div class="circle"></div>
              </div>
            </div>
          </div>
        </div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0-beta/js/materialize.min.js"></script>
        <script
  src="https://code.jquery.com/jquery-3.3.1.min.js"
  integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8="
  crossorigin="anonymous"></script>
        <script>
            (function () {
                var el_loading = $('.loading');
                $('.send-btn').click(function () {
                    el_loading.show();
                    $.ajax({
                        type: "POST",
                        url: "api.php",
                        data: {ctl : this.id},
                        dataType: 'json'
                    }).done(function (res, status, xhr) {
                        console.log(res);
                        alert(res.msg);
                    }).fail(function (xhr, status, err) {
                        alert("通信エラー");
                    }).always(function () {
                        el_loading.hide();
                    });
                });
            })();
        </script>
    </body>
</html>
