# わせだや YouTube ショート動画 台本生成システム

YouTubeチャンネル「わせだや」の「時代別あるある」ショート動画の台本を全自動生成するClaude Codeスキル群。

## スキル一覧

| スキル | コマンド | 役割 |
|--------|----------|------|
| wasedaya-orchestrator | `/wasedaya-orchestrator` | テーマ→完成台本の一気通貫実行 |
| neta-developer | `/neta-developer` | ネタ5案の開発 |
| jidai-researcher | `/jidai-researcher` | 選定ネタの時代別リサーチ |
| script-writer | `/script-writer` | 台本執筆 |
| script-reviewer | `/script-reviewer` | 台本レビュー＆修正 |
| channel-strategist | `/channel-strategist` | チャンネルデータ分析＆戦略更新 |

## 基本的な使い方

### 台本生成（最も多い使い方）
テーマを一言投げるだけ → orchestratorが全自動で台本を生成しGoogle Driveに保存:
- 「転職ネタで書いて」
- 「時代別、飲み会の断り方 で台本作って」
- 「今週の1本作って」

### チャンネル戦略更新（週1目安）
1. `python wasedaya-skills/scripts/fetch_youtube_data.py` でデータ取得
2. `/channel-strategist` で strategy.md を更新

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

## 環境変数（チャンネル戦略分析に必要）

```bash
export YOUTUBE_API_KEY="your-api-key"
export YOUTUBE_CHANNEL_ID="your-channel-id"
```
