# n8n Workflow Validator

n8nワークフローJSONファイルを検証するCLIツール。

## インストール

```bash
pip install -e .
```

## 使用方法

```bash
# テキストレポート出力
n8n-validator workflow.json

# JSON出力
n8n-validator workflow.json --json
```

## 検証ルール

| ルール | 説明 |
|--------|------|
| error-handling | Error TriggerノードまたはerrorWorkflow設定の有無 |
| webhook-timeout | レスポンス待ちWebhookのタイムアウト設定 |

## 出力例

```
Validation Report: My Workflow
==================================================
Status: VALID (no errors)
Issues: 1 (0 errors, 1 warnings)

Issues Found:
------------------------------
1. [WARNING] error-handling
   Workflow has no error handling.
   Suggestion: Add an Error Trigger node to handle failures...
```

## 開発

```bash
# 開発用インストール
pip install -e ".[dev]"

# テスト実行
pytest -v
```

## プロジェクト構造

```
src/n8n_validator/
├── loader.py      # ワークフロー読み込み
├── validators.py  # 検証ロジック
├── reporter.py    # 結果出力
└── cli.py         # CLIエントリポイント
```
