# 発表デモスクリプト (日本語)

このベースコードを使って4つの IDE を比較します。モデルはすべて Claude Opus 4.6 または 4.7 に統一し、差はモデルではなくエージェント・ハーネスから来ることを示します。

## 事前準備

同じコミットから4ブランチを切ります。

```bash
git checkout -b demo/kiro
git checkout -b demo/copilot
git checkout -b demo/antigravity
git checkout -b demo/junie
```

各ツールは自分のブランチでのみ作業します。

## シナリオ 1 — Kiro の強みデモ (spec-driven フルサイクル)

`tag` 機能を追加します。spec モードから開始し、生成物自体をデモに使います。

**プロンプト**

```
このプロジェクトにノートのタグ(tag)機能を追加したい。

まず spec モードに入って requirements.md、design.md、tasks.md を
順番に作成してください。次の要件を反映してください。

- ノート1件に複数のタグを付けられる
- タグでフィルタできる /api/notes?tag=xxx エンドポイント
- 既存ノートはタグが空でも動作すること
- マイグレーション + JPA エンティティ + コントローラ + Thymeleaf UI + テストまで

設計が確定してからコード生成に進みます。
コード生成完了後に ./gradlew test を自動実行する
Post Task Execution hook も設定してください。
```

**観察ポイント**
- `requirements.md` / `design.md` / `tasks.md` が実際に生成されるか
- `design.md` の項目を1つ修正したとき `tasks.md` に cascade するか
- Hook が実際に発火してテストを実行するか

## シナリオ 2 — GitHub Copilot の強みデモ (4-in-1 インターフェース)

1セッション内で Agent mode、Inline、Next Edit Suggestions、Cloud agent をすべて織り交ぜます。

**プロンプト**

```
このプロジェクトで以下の作業を進めてください。

1. (Agent mode) Note エンティティに `pinned` boolean フィールドを追加
   - マイグレーション、エンティティ、サービス、コントローラ、UI すべてに反映
   - pinned のノートは一覧の最上段に表示

2. (Inline / Ctrl+I) NoteController.kt の index メソッドで
   pinned ノートを優先ソートするように直接修正

3. (Cloud agent) README.md の Quick start セクションの下に
   "Features" 節を追加する作業を非同期で委任

作業中、Next Edit Suggestions が提案する周辺編集はそのまま採用します。
```

**観察ポイント**
- 4つのインターフェースが1つの IDE 内で自然に交差するか
- Cloud agent が実際に非同期に動くか
- Next Edit Suggestions が意味のある周辺編集を提案するか

## シナリオ 3 — Antigravity の強みデモ (並列委任 + Artifacts)

互いに独立した3つの task を Manager View で同時実行します。

**プロンプト**

```
Manager View で以下の3つの task を並列に実行してください。

Task A: NoteApiController.kt のレスポンスモデルを別の Dto ファイルに分離。
        既存テストはすべて通過すること。

Task B: ノート検索エンドポイントを追加。
        GET /api/notes/search?q=keyword (タイトル + 本文 LIKE 検索)。
        統合テスト含む。

Task C: README.md、DEMO.ko.md、DEMO.ja.md の Endpoints 表を更新。

各 task の Implementation Plan / Code Diffs / Walkthrough が出たら
レビュー依頼してください。Artifact にコメントでフィードバックしながら進めます。
```

**観察ポイント**
- 3つのエージェントが本当に同時に進むか (Manager View)
- 発表者が1〜2分席を外して戻ったとき進捗がどう可視化されているか
- Artifact にコメントを付けたときエージェントが止まらずに反映するか

## シナリオ 4 — Junie の強みデモ (3モード比較、JVM ホームグラウンド)

同じリファクタリング task を Auto → Think → Brave モードで順に進めます。

**プロンプト**

```
NoteService.kt を次のようにリファクタしてください。

- 参照系ロジックと変更系ロジックを NoteQueryService と NoteCommandService に分離
- 呼び出し側 (NoteController、NoteApiController) もそれに合わせて修正
- 既存テストはすべて通過すること
- IntelliJ refactor 機能を使って安全にシグネチャを変更すること

まず Auto Mode で進めてください。

(完了後)
同じ task を新セッションで Think Mode で再度実行してください。

(完了後)
同じ task を新セッションで Brave Mode で再度実行してください。

各モードで (a) 事前分析量 (b) ユーザー介入回数 (c) 完了時間 を測定します。
```

**観察ポイント**
- 3モードの分析量と自律性の差
- IntelliJ refactor・inspection・debugger 呼び出しが実際に効くか
- Brave Mode がリスクをどう扱うか (または扱わないか)
- JVM 環境で他の3ツール (VS Code 系) との差

## シナリオ 5 — 横断比較 (4ツール同一入力)

シナリオ1〜4で各ツールの色を見せたうえで、同じ問題1つで横断比較します。

**プロンプト (4ツール共通)**

```
このプロジェクトにノートのお気に入り(favorite)機能を追加してください。

- Note エンティティに `favorite: Boolean` フィールドを追加 (デフォルト false)
- マイグレーション (data.sql 更新)
- トグル用エンドポイント PUT /api/notes/{id}/favorite
- index.html にお気に入り星アイコン + クリックでトグル
- favorite=true のノートは一覧の最上段に表示
- ユニット + 統合テストを追加

完了まで進めてください。
```

**評価シート (聴衆配布用)**

| 項目 | Kiro | Copilot | Antigravity | Junie |
| --- | --- | --- | --- | --- |
| 完了までのターン数 |  |  |  |  |
| ユーザー介入回数 |  |  |  |  |
| テスト通過 |  |  |  |  |
| 不要なファイル変更 |  |  |  |  |
| 体感時間 |  |  |  |  |

## 測定のコツ

- 測定前に `git stash` または clean 状態を確認
- 人間が直接やった場合の「正解」を事前にメモして比較
- ツールが「完了」と宣言した時点で測定終了
- ユーザー介入はツールが明示的に質問したときだけ答え、先に割り込まない
