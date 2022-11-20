# cndctl

## 必要なもの
- Python 3
- Linux(WSL) or macOS

## インストール方法

1. Git リポジトリをクローンする
2. プロジェクトルートで `pip3 install -r requirements.txt` を実行する
3. `python3 -m cndctl --help` を実行してUsageが出てきたら、インストール成功

## 使い方

### 認証情報の読み込み
認証方法は次の3通りが存在します。
また、以下の並び順で下の方ほどより優先的に読み込まれます。

1. JSONファイル
2. 環境変数
3. コマンドオプション

また、JSONファイルを利用しつつ、環境変数やコマンドオプションを利用することで、それらの設定を上書きできます。
なお、一部のオプションはコマンドオプションからのみ指定できます。

#### 1. jsonファイルを使用する
本リポジトリの[./example.json](./example.json)のようにJSONファイルを作成し、次のコマンドのように実行時に指定します。

`python3 -m cndctl --secret example.json scene get`

#### 2. 環境変数を利用する

指定された環境変数を`export`しておくことでこれらを読み込みます。
利用可能な環境変数は以下のとおりです。

- `OBS_HOST`: OBS Websocketの接続先（IPアドレスまたはドメイン名）
- `OBS_PORT`: OBS Websocketの待ち受けポート
- `OBS_PASS`: OBS Websocketの待ち受けパスワード
- `DK_URL`: Dreamkast APIの接続先ドメイン名
- `DK_CLIENT_ID`: Auth0のトークンを生成するためのクライアントID
- `DK_CLIENT_SECRETS`: Auth0のトークンを生成するためのクライアントシークレット
- `DK_AUTH0_URL`: Auth0のトークンを生成するためのAuth0サブドメイン

#### 3. コマンドオプションを利用する

指定されたコマンドオプションを利用してパラメータを指定できます。
コマンドオプションのパラメータはもっとも優先されて読み込まれます。
利用可能なオプションは以下のとおりです。

- `--secret`: 認証用のJSONファイルを指定する
- `--obs-host`: OBS Websocketの接続先（IPアドレスまたはドメイン名）
- `--obs-port`: OBS Websocketの待ち受けポート
- `--obs-password`: OBS Websocketの待ち受けパスワード
- `--dk-url`: Dreamkast APIの接続先ドメイン名
- `--dk-client-id`: Auth0のトークンを生成するためのクライアントID
- `--dk-client-secrets`: Auth0のトークンを生成するためのクライアントシークレット
- `--dk-auth0-url`: Auth0のトークンを生成するためのAuth0サブドメイン
- `--dk-talk-id`: 一部のdk操作に利用する `talk_id` を指定する
- `--sceneName`: 一部のシーン操作に利用する `シーン名` を指定する
- `--sourceName`: 一部のソース操作に利用する `ソース名` を指定する

### シーン関連の操作
#### シーンの一覧を取得
`python3 -m cndctl scene get`

#### 次のシーンに切り替え
`python3 -m cndctl scene next`

#### 指定したシーンに切り替え
`python3 -m cndctl scene change --sceneName={SCENE_NAME}`

##### fzfを利用した切り替え
`python3 -m cndctl --secret switcher01.json scene change --sceneName="$(python3 -m cndctl --secret switcher01.json scene get | fzf)"`

### メディアソース関連の操作
#### メディアソースの残り時間を取得
`python3 -m cndctl mediasource time --sourceName={SOURCE_NAME}`

### Dreamkast関連の操作
#### トークンの生成
`python3 -m cndctl dk update`
※Tokenの期限が残っている場合は実行しない

#### OnAirステータスの切り替え
`python3 -m cndctl dk onair --dk-talk-id={DK_TALK_ID}`

### Switcher初期化
`python3 -m cndctl switcher build`

```
cndctl
  # シーン関連の操作
  scene
    * get
    * next
    * set
  scenecollection
    get
  source
    get
  mediasource
    get
    * time
  streaming
    start
    stop
  recording
    start
    stop
  text
    edit
    delete
    on
    off
```