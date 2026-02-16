# ErrorMate

エラー解決力を高めるための学習支援Webアプリケーション

---

## 制作目的

生成AI時代において、自ら考えて問題解決する力を育成することを目的として開発。

---

## 主な機能

- ユーザー登録 / ログイン機能
- ステップカード投稿機能
- エラーコード・修正コード保存
- 週次エラー統計表示

---

## 技術スタック

- Backend: Flask
- Database: MariaDB (AWS RDS)
- Frontend: HTML / CSS / JavaScript
- Infrastructure: AWS EC2

---

## 今後の課題

- パスワードリセット機能
- テストコード追加
- UI/UX改善

---

## 工夫した点

- Blueprintによる機能分割設計
- AWS RDSとの安全な接続設定
- 週次エラー統計APIの実装
- mysqldumpによるDBバックアップ取得
- AIタグ付け機能により検索性能、効率向上

---

## 苦労した点
- AWS RDSの接続、チーム全員のGithub,Cloud9の接続。
- JavaScript非同期処理のバグ修正
- MoodleとErrorMateのLTI接続

---

## 起動方法（VSCode）

- Python 3.9.25 をインストール
- VSCode をインストール

### ② プロジェクトを開く

1. VSCodeを起動
2. 「フォルダーを開く」から本プロジェクトを選択

### ③ 仮想環境の作成

ターミナルを開き、以下を実行

Windowsの場合...
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements_local.txt
```

### ④　環境変数の設定(SQLite)
ErrorMateの直下に.envファイルを作成し、下記のコードを書き込む。
```bash
USE_SQLITE=1  
SQLITE_PATH=errormate_local.db  
```
(AI機能を使うのならば、Gemini APIキーを作成し、下記に追加する)  
GEMINI_API_KEY=""

### ⑤ データベースの作成
```basu
python create_db_local.py
```

### ⑥ アプリケーション起動
python applicaion.py

### ⑦　ブラウザ起動

