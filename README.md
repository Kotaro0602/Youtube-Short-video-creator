# わせだや YouTube ショート動画 台本生成システム

YouTubeチャンネル「わせだや」の「時代別あるある」ショート動画の台本を、Claude Codeスキルで全自動生成するシステム。

## クイックスタート

### 台本を作る（最も多い使い方）

Claude Codeで以下のように話しかけるだけ:

```
転職ネタで書いて
```

または

```
/wasedaya-orchestrator 時代別、飲み会の断り方
```

orchestratorが以下を全自動実行:
1. ネタ5案を開発 → ベスト案を自動選定
2. 選定ネタの時代別リサーチ
3. 台本執筆
4. レビュー＆自動修正（最大2回）
5. Google Driveに保存

### エピソードから台本を作る

面白いエピソードを投げるだけ:

```
この前上司に転職考えてるって言ったら翌日めっちゃ優しくなってて草、これで台本作って
```

episode-orchestratorが以下を全自動実行:
1. エピソード分析（面白さの核を抽出、最適な年代を判定）
2. 時代別リサーチ（エピソードとの対比を重視）
3. 台本執筆（エピソードを配置年代の口調に変換）
4. レビュー＆自動修正（最大2回）
5. Google Driveに保存

### チャンネル戦略を更新する（週1目安）

```bash
# 1. YouTubeデータを取得
export YOUTUBE_API_KEY="your-api-key"
export YOUTUBE_CHANNEL_ID="your-channel-id"
python wasedaya-skills/scripts/fetch_youtube_data.py

# 2. Claude Codeで戦略分析を実行
# /channel-strategist
```

## スキル一覧

| スキル | コマンド | 役割 |
|--------|----------|------|
| wasedaya-orchestrator | `/wasedaya-orchestrator` | テーマ→完成台本の一気通貫実行 |
| episode-orchestrator | `/episode-orchestrator` | エピソード→完成台本の一気通貫実行 |
| neta-developer | `/neta-developer` | ネタ5案の開発 |
| episode-analyzer | `/episode-analyzer` | エピソード分析＆テーマ抽出 |
| jidai-researcher | `/jidai-researcher` | 選定ネタの時代別リサーチ |
| script-writer | `/script-writer` | 台本執筆 |
| script-reviewer | `/script-reviewer` | 台本レビュー＆修正 |
| channel-strategist | `/channel-strategist` | チャンネルデータ分析＆戦略更新 |

## ディレクトリ構成

```
.claude/
├── skills/                        # Claude Codeスキル
│   ├── wasedaya-orchestrator/     # 統括（全自動パイプライン）
│   ├── neta-developer/            # ネタ開発
│   ├── jidai-researcher/          # 時代リサーチ（+ 基礎データ）
│   ├── script-writer/             # 台本執筆（+ サンプル台本）
│   ├── script-reviewer/           # 台本レビュー
│   ├── channel-strategist/        # 戦略分析（+ テンプレート）
│   ├── episode-orchestrator/      # エピソードベース統括
│   └── episode-analyzer/          # エピソード分析
├── mcp.json                       # Google Drive MCP設定（※git管理外・各自作成）
├── settings.local.json            # 許可設定（※git管理外・各自作成）
wasedaya-skills/
├── scripts/
│   └── fetch_youtube_data.py      # YouTube Data API取得
├── data/
│   └── youtube_data.json          # 取得データ（git管理外推奨）
CLAUDE.md                          # プロジェクト説明
```

## セットアップ

### 前提条件

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) がインストール済み
- Node.js（npx が使える状態）
- Google Cloud Platformのプロジェクト（OAuth 2.0クライアントID発行済み）

### 1. リポジトリのクローンと依存パッケージ

```bash
git clone <このリポジトリのURL>
cd Youtube-Short-video-creator
npm install
```

### 2. Google Drive MCP の設定

台本の保存・戦略ドキュメントの読み込みに Google Drive MCP を使用する。

#### 2-1. GCPでOAuth 2.0クライアントIDを作成

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを開く
2. 「APIとサービス」→「認証情報」→「認証情報を作成」→「OAuthクライアントID」
3. アプリケーションの種類: 「デスクトップアプリ」
4. JSONをダウンロードし、プロジェクトルートに `gcp-oauth.keys.json` として保存

#### 2-2. `.mcp.json` を作成

プロジェクトルートに `.mcp.json` を作成し、パスを自分の環境に合わせて設定:

```json
{
  "mcpServers": {
    "gdrive": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-gdrive"],
      "env": {
        "GDRIVE_CREDENTIALS_PATH": "/your/path/to/Youtube-Short-video-creator/.gdrive-server-credentials.json",
        "GDRIVE_OAUTH_PATH": "/your/path/to/Youtube-Short-video-creator/gcp-oauth.keys.json"
      }
    }
  }
}
```

#### 2-3. Google Drive認証

```bash
npx -y @modelcontextprotocol/server-gdrive auth
```

ブラウザが開くのでGoogleアカウントで認証する。成功すると `.gdrive-server-credentials.json` が自動生成される。

#### 2-4. Google Driveにフォルダを作成

Google Driveに以下のフォルダ構造を手動で作成:

```
わせだや/
├── 台本/
│   ├── レビュー待ち/
│   ├── 撮影OK/
│   └── アーカイブ/
└── 戦略/
```

### 3. 許可設定（推奨）

スキル実行時にツールの許可確認が毎回出るのを防ぐため、`.claude/settings.local.json` を作成:

```json
{
  "permissions": {
    "allow": [
      "WebSearch",
      "WebFetch",
      "MCP",
      "Bash(python3 *)",
      "Bash(npm *)",
      "Bash(npx *)",
      "Bash(ls *)"
    ]
  }
}
```

### 4. YouTube Data API（チャンネル戦略分析を使う場合のみ）

```bash
pip install google-api-python-client
export YOUTUBE_API_KEY="your-api-key"
export YOUTUBE_CHANNEL_ID="your-channel-id"
```

## Google Drive フォルダ構造

```
わせだや/
├── 台本/
│   ├── レビュー待ち/    ← 新規台本の保存先
│   ├── 撮影OK/
│   └── アーカイブ/
└── 戦略/
    └── strategy.md      ← チャンネル戦略ドキュメント
```
