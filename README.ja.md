# agentic-ide-demo

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md)

## 概要

`agentic-ide-demo` は、安定した1つの JVM コードベースで4つのエージェント型 IDE の作業方法を比較するため、意図的に小さく作った Kotlin・Spring Boot のノートアプリケーションである。Thymeleaf ダッシュボードと JSON API は、ノートドメイン、サービス、Spring Data JPA リポジトリ、H2 データベース、テストを共有する。アプリケーションを固定したまま、Kiro、VS Code の GitHub Copilot、Google Antigravity、JetBrains Junie で異なるエージェントハーネスを試せる。

使用技術は次のとおりだ。

- Kotlin 1.9.25、Java 21
- Spring Boot 3.5.6、Spring Data JPA
- Thymeleaf、H2、Gradle Kotlin DSL、JUnit 5

比較対象は次の4つである。

- Kiro
- VS Code の GitHub Copilot
- Google Antigravity
- JetBrains Junie

![プロジェクト概要](docs/readme/ja/project-overview.svg)

## リポジトリ構成

![リポジトリ構成](docs/readme/ja/repository-structure.svg)

```text
src/main/kotlin/com/seonology/demo/
  AgenticIdeDemoApplication.kt
  note/   # entity, repository, service, Thymeleaf controller, REST controller
  stats/  # statistics service and JSON controller
src/main/resources/
  application.properties
  data.sql
  templates/  # index, new, detail, and shared header
src/test/kotlin/com/seonology/demo/
  AgenticIdeDemoApplicationTests.kt
  note/  # REST and service tests
```

`src/main` は本番コードと実行時リソース、`src/test` はテストを収める。リポジトリ運用の設定は `.gitea/`、`gitea-settings.json`、`apply-gitea-settings.sh` にある。発表用プロンプトは `DEMO.ko.md` と `DEMO.ja.md` に残している。移行前の英語文書は `docs/README.original.en.md` にバイト単位で保存し、`README_STRUCTURE.md` に文書契約を記録している。

## クイックスタート

Java 21 と Git が必要だ。両方を確認してから、リポジトリをクローンして作業ディレクトリへ移動する。

```bash
java -version
git --version
git clone https://git.seonology.com/seon-labs/agentic-ide-demo.git
cd agentic-ide-demo
```

Gradle Wrapper でアプリケーションを起動する。

```bash
./gradlew bootRun
```

## ビルドとデプロイ

実行可能なアーカイブを作る前にテストを実行する。

```bash
./gradlew test
./gradlew clean bootJar
java -jar build/libs/agentic-ide-demo-0.0.1-SNAPSHOT.jar
```

サーバーは `http://localhost:8090` で待ち受ける。ダッシュボードは `/`、ノート作成画面は `/notes/new`、REST コレクションは `/api/notes`、統計情報は `/api/stats`、H2 コンソールは `/h2-console` で利用できる。H2 コンソールの JDBC URL は `jdbc:h2:mem:notes` だ。

コンテナイメージ、インフラ定義、ホスト環境用プロファイル、自動デプロイワークフローはない。`bootRun` と実行可能な Spring Boot JAR は、どちらもポート `8090` でローカルの単一プロセスを起動する。外部環境への公開は、このリポジトリの対象外である。

## リクエストフロー

![ノートのリクエストフロー](docs/readme/ja/request-flow.svg)

`AgenticIdeDemoApplication` が Spring Boot を起動する。`NoteService` は `NoteRepository` を通じてノートの作成、参照、更新、削除を担当する。`NoteController` は Thymeleaf ページを描画し、`NoteApiController` は JSON エンドポイントを公開する。`StatsService` はノート総数（`total`）、当日作成されたノート数（`today`）、色別のノート数（`byColor`）を `StatsController` に渡す。

起動時には JPA モデルからデータベースを作成する。`src/main/resources/data.sql` がダッシュボードに表示するサンプルノートを登録する。`spring.jpa.open-in-view=false` により、永続化層へのアクセスをサービス境界内に保つ。

## 設定

![実行時設定の構成](docs/readme/ja/configuration-structure.svg)

`src/main/resources/application.properties` が唯一の実行時設定ファイルである。リポジトリ内にプロファイルや環境変数による上書きはない。

| キー | リポジトリの既定値 | 役割 |
| --- | --- | --- |
| `spring.application.name` | `agentic-ide-demo` | Spring アプリケーション名を設定する |
| `spring.datasource.url` | `jdbc:h2:mem:notes;MODE=PostgreSQL;DB_CLOSE_DELAY=-1` | PostgreSQL 互換モードのインメモリ H2 を作成する |
| `spring.datasource.driver-class-name` | `org.h2.Driver` | H2 JDBC ドライバを選ぶ |
| `spring.datasource.username` | `sa` | ローカルデータベースのユーザーを設定する |
| `spring.datasource.password` | 空 | ローカル H2 のパスワードを設定しない |
| `spring.jpa.hibernate.ddl-auto` | `create-drop` | プロセスの起動と終了に合わせてスキーマを作成・削除する |
| `spring.jpa.open-in-view` | `false` | View 描画時の永続化アクセスを止める |
| `spring.jpa.defer-datasource-initialization` | `true` | シード SQL より先に JPA スキーマを作る |
| `spring.h2.console.enabled` | `true` | H2 ブラウザコンソールを有効にする |
| `spring.h2.console.path` | `/h2-console` | コンソールのパスを設定する |
| `spring.sql.init.mode` | `always` | 起動時に `data.sql` を読み込む |
| `server.port` | `8090` | HTTP の待ち受けポートを設定する |

## セキュリティとシークレット

このアプリケーションには認証・認可の依存関係がない。そのため、HTML ルート、JSON API、H2 コンソールは、信頼できるローカルデモ環境だけで使う。テンプレートは `https://cdn.tailwindcss.com` から Tailwind CSS を読み込むため、UI の実行時には外部スクリプトにも依存する。

アプリケーションのシークレット値はコミットされていない。`spring.datasource.password` は、ローカル H2 用に意図して空にしている設定である。`apply-gitea-settings.sh` は実行時に `TOK` というシークレット名を要求し、値がなければ終了する。この値をリポジトリやコマンド履歴へ書き込んではならない。ライブ環境では Gitea Actions と GitHub Actions のシークレットおよび変数が0件だった。Gitea Actions は無効で、どちらのリモートにもワークフローはない。

## 概念図

![エージェント型 IDE 比較の概念図](docs/readme/ja/demo-scenarios.svg)

スクリプトでは同じアプリケーションを使って4つの作業方法を比較する。

- Kiro: タグ機能を仕様主導で追加する流れ
- GitHub Copilot: 1つの作業で Agent mode、Inline、Next Edit Suggestions、Cloud agent を組み合わせる流れ
- Google Antigravity: Manager View から独立した3つの変更を委任する流れ
- JetBrains Junie: Auto、Think、Brave の各モードで同じリファクタリングを比較する流れ

1回の比較では4つのツールに同じモデルを使う。これにより、観察した差をモデルの変更ではなく、モデルを動かすツール側の実行基盤（エージェントハーネス）の差として比較できる。共通のベース課題では、複数ファイルの編集、データベーススキーマの変更、サービスの分割、Thymeleaf UI の変更、互換性を破る REST API の変更を扱う。

スクリプトには、4つのツールで共通して行うお気に入り機能の課題と評価表も含まれる。そのまま使えるプロンプトは [DEMO.ko.md](DEMO.ko.md) または [DEMO.ja.md](DEMO.ja.md) にある。

## アプリケーションアーキテクチャ

![アプリケーションアーキテクチャ](docs/readme/ja/application-architecture.svg)

`AgenticIdeDemoApplication` が1つの Spring Boot プロセスを起動する。Web アダプターは `NoteService` または `StatsService` を呼び出す。`NoteService` は `NoteRepository` を通じて変更を保存し、`StatsService` は同じノートから集計値を算出する。JPA は `Note` から `notes` テーブルを作り、`data.sql` はスキーマ作成後に6件のサンプル行を追加する。データベースはメモリ上にあり、スキーマモードが `create-drop` のため、プロセスを再起動するとデータが初期化される。

## HTTP エンドポイント

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | ノートダッシュボードを描画 |
| `GET` | `/notes/new` | ノート作成画面を描画 |
| `POST` | `/notes` | ノートを作成してダッシュボードへ戻る |
| `GET` | `/notes/{id}` | 1件のノートを描画 |
| `POST` | `/notes/{id}/delete` | ノートを削除してダッシュボードへ戻る |
| `GET` | `/api/notes` | すべてのノートを JSON で返す |
| `GET` | `/api/notes/{id}` | 1件のノートを JSON で返す |
| `POST` | `/api/notes` | JSON からノートを作成 |
| `PUT` | `/api/notes/{id}` | JSON からノートを更新 |
| `DELETE` | `/api/notes/{id}` | ノートを削除 |
| `GET` | `/api/stats` | ノート数を `total`、`today`、`byColor` で返す |

## GitHub と Gitea

作業用のソースは `https://git.seonology.com/seon-labs/agentic-ide-demo` の `main` ブランチにある。Gitea は `sync_on_commit=true` と8時間の補助間隔で、`https://github.com/seonNoh/agentic-ide-demo` へ push ミラーを送る。両リモートの `main` ブランチは現在同じ最新コミットを指している。GitHub から取得した最初のソース基準点は `b1dd56bc2045d54a4f1af43958753843e38be883` である。

ライブ環境にはブランチ保護も、Gitea Actions の実行、ランナー、シークレット、変数もなかった。GitHub は `workflows=0`、`runs=0`、`secrets=0`、`variables=0`、`environments=0` で、両リポジトリとも `tags=0` だった。このリポジトリでは Gitea Actions を無効にしている。文書を保守するときは、どちらの Actions も開始しない。

## 運用

変更時のゲートには `./gradlew test` を使う。ポート `8090` を別のプロセスが使用している場合は、そのプロセスを停止するか、ローカル実行時に一時的な Spring プロパティを指定する。アプリケーションは `Ctrl+C` で停止する。再起動すると6件のシードノートが戻り、前回のプロセスで作ったノートは消える。

## 関連パス

- [DEMO.ko.md](DEMO.ko.md) — そのまま使える韓国語の発表用スクリプト
- [DEMO.ja.md](DEMO.ja.md) — そのまま使える日本語の発表用スクリプト
- [元の英語 README](docs/README.original.en.md) — バイト単位で保存した移行元の文書
- [README 構成契約](README_STRUCTURE.md) — セクション、事実、図の対応関係
- [コントリビューションガイド](CONTRIBUTING.md) — 変更とレビューの手順
- [Gitea Issues](https://git.seonology.com/seon-labs/agentic-ide-demo/issues) — 質問と問題の報告先
- [Spring Boot documentation](https://docs.spring.io/spring-boot/)
- [Kotlin documentation](https://kotlinlang.org/docs/home.html)
- [Gradle Kotlin DSL documentation](https://docs.gradle.org/current/userguide/kotlin_dsl.html)
