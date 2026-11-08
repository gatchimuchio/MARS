# MARS原典と分析命題の突合索引（2026-11-09）

## 規則

1. 原文の発行者URLを直接開く。PDFは `#page=N` で**ファイル先頭から数えた1始まりのページ**を指す。HTMLは原ページへ移動する。
2. 分析結果の出典IDは `../SOURCE_REGISTER.md` に対応し、実際に取得した原文ファイルは `../../sources/originals.lock.json` の同一IDのSHA-256で特定できる。
3. 以下の索引は論旨の代表的な直接確認先であって、原資料全文の代わりではない。該当ページ・本文の条件・注記まで読んで判断する。単なる数値の出現だけでは原命題を保証しない。
4. `DOCUMENTED` は原資料の記載を意味する。分析側が追加した設計思想の解釈は `DERIVED` として残す。
5. ページ確認に至っていない資料は無理にページ番号を付けず、原典全体にリンクする。

## 1964年「座席予約システム特集」全9本

| ID | 原典をすぐ開く | この資料で確認する対象 | 分析側の参照先 |
|---|---|---|---|
| S12 | [展望の原文PDF・全4ページ](https://www.hitachihyoron.com/jp/pdf/1964/06/1964_06_16.pdf) | 日本全国の座席予約問題の設定・当時の制度と技術条件 | 総合監査1.2・2.1 |
| S13 | [システム設計の原文PDF・1ページ](https://www.hitachihyoron.com/jp/pdf/1964/06/1964_06_17.pdf#page=1) | 実時間応答・保護・拡張性・業務変更という設計要件 | 総合監査2.1・3.2 |
| S01 | [実時間処理の原文PDF・3ページ](https://www.hitachihyoron.com/jp/pdf/1964/06/1964_06_18.pdf#page=3) | SC/TC/FC/TRC、占有ビットと実時間処理の役割 | 総合監査3.2・3.3 |
| S02 | [実時間プログラムの原文PDF・3ページ](https://www.hitachihyoron.com/jp/pdf/1964/06/1964_06_19.pdf#page=3) | 異常処理と再送・処理の割込み | 総合監査3.3 |
| S14 | [操作プログラムの原文PDF・3ページ](https://www.hitachihyoron.com/jp/pdf/1964/06/1964_06_20.pdf#page=3) | **F45T**の両系座席データ差分・操作者確認・補正 | 総合監査3.4、H-004 |
| S03 | [中央処理装置の原文PDF・2ページ](https://www.hitachihyoron.com/jp/pdf/1964/06/1964_06_21.pdf#page=2) | 実際の装置構成と命令語長に関する記述 | 総合監査3.2 |
| S15 | [電信交換装置の原文PDF・全5ページ](https://www.hitachihyoron.com/jp/pdf/1964/06/1964_06_22.pdf) | 回線集線、通信試験と保守 | 総合監査3.5 |
| S04 | [端局装置の原文PDF・5ページ](https://www.hitachihyoron.com/jp/pdf/1964/06/1964_06_23.pdf#page=5) | 50ボー電信伝送、端局入力記号の条件（操作工程は原文1～4ページも参照） | 総合監査3.3・3.5 |
| S05 | [建設工事の原文PDF・6ページ](https://www.hitachihyoron.com/jp/pdf/1964/06/1964_06_24.pdf#page=6) | 据付・試験・現場運用、系統間の総合成立 | 総合監査2.2・3.6 |

[1964年特集号の公式目次（S16）](https://www.hitachihyoron.com/jp/archive/1960s/1964/06.html)：9本の掲載母集団を確認する正本。

## 世代をまたぐ原文の確認位置

| 命題 | 原典の直接参照 | 史料に直接あること／こちらの分析の境界 |
|---|---|---|
| MARS-1専用機と汎用機の技術選択 | [S17・1961年原著、1ページ](https://www.hitachihyoron.com/jp/pdf/1961/ex39/1961_ex_39_09.pdf#page=1) | 原著で複数方式を比較。選択の一般化は分析者の推論 |
| MARS-1磁気ドラム40万ビットの原著記載 | [S17・6ページ](https://www.hitachihyoron.com/jp/pdf/1961/ex39/1961_ex_39_09.pdf#page=6) | **400,000ビット**との仕様記載。後年の学会資料S22の値と一致せず、未解決 |
| MARS-1の磁気ドラム装置を展示する学協会記録 | [S22・収蔵ページ](https://museum.ipsj.or.jp/heritage/mars-1.html) | 原機の収蔵品情報。S17の値と比較するときは計測単位の違いを確認 |
| MARS-105の端局による入力範囲拡大 | [S18・3ページ](https://www.hitachihyoron.com/jp/pdf/1974/02/1974_02_06.pdf#page=3) | 端末接点・カードの構造。後年の301/501端末とは別 |
| MARS-105のファイル障害・発売保留・複製復旧 | [S19・3ページ](https://www.hitachihyoron.com/jp/pdf/1974/04/1974_04_15.pdf#page=3) | 障害種別による部分停止・正常ファイルからの回復 |
| MARS-105のファイル共有とタンデム方式の比較 | [S20・2ページ](https://www.hitachihyoron.com/jp/pdf/1975/09/1975_09_03.pdf#page=2) | 拡張性と保守を含む技術選定。現在の分散DBへ無断で類推しない |
| 2CPUの処理量を単純2倍としない設計 | [S20・3ページ](https://www.hitachihyoron.com/jp/pdf/1975/09/1975_09_03.pdf#page=3) | **約1.5倍の推定**。測定済み性能と推定性能を混同しない |
| MARSのハード・OS・ソフト世代別比較 | [S29・1975年原著](https://www.hitachihyoron.com/jp/pdf/1975/09/1975_09_02.pdf) | 1→101→103/104→105の技術変更を単純化せず照合 |
| 105の稼働移行と時系列 | [S30・1974年原著](https://www.hitachihyoron.com/jp/pdf/1974/01/1974_01_06.pdf) | 1972年からの段階切替と1973年全面移行の区別 |
| 301端局制御と機能分担の評価 | [S27・1983年原著](https://www.hitachihyoron.com/jp/pdf/1983/06/1983_06_10.pdf) | 端局制御をどこへ置くかの性能・費用・保守判断 |
| 301の導入時の構成 | [S28・1986年原著](https://www.hitachihyoron.com/jp/pdf/1986/01/1986_01_04.pdf) | 1983年設計論文に対する後年の構成報告 |
| 窓口の印字活字木片と入力の一体化 | [S31・穂坂衛証言、5ページ](https://museum.ipsj.or.jp/guide/pdf/magazine/IPSJ-MGN520938.pdf#page=5) | 原文に**印刷活字の付いた木片**と入力コードを接続する証言がある |
| ドラム回転同期の設計経緯 | [S32・大野豊証言、4ページ](https://museum.ipsj.or.jp/guide/pdf/magazine/IPSJ-MGN540722.pdf#page=4) | 開発当事者の後年の証言。1961年原著S17の回路説明と突合 |
| 105を支えた複数職域の統合チーム | [S33・尾関雅則証言、3ページ](https://museum.ipsj.or.jp/guide/pdf/magazine/IPSJ-MGN541015.pdf#page=3) | 通信・計算機・ソフト・営業を一緒に設計する体制の証言 |
| 現代COBOLとXML連携の実例 | [S09・当事者の技術事例](https://www.cobol.gr.jp/wp-content/uploads/2024/11/05-3.pdf) | 101原機の使用言語を証明する資料ではない |
| MARS-501の異種基盤の接続 | [S10・日立技術事例](https://www.hitachi.co.jp/Prod/comp/soft1/casestudy/contents/jr/index.html) | 特定サブシステムの構成として扱う |
| MARS-505のDB運用要件 | [S11・日立/JR対談](https://www.hitachi.co.jp/Prod/comp/soft1/hirdb/30th_anniversary/article/index.html) | 対談内で述べられた運用方針。非公開の全実装の証明ではない |

## 取得後に顕在化した原分析の誤り

原文PDFの表題に戻ったところ、初回分析には**証言者の固有名詞の取り違え**が3件あった。

| 史料ID | 初回分析での誤表記 | PDF表紙で確認した正しい表記 | 突合箇所 |
|---|---|---|---|
| S31 | 保坂守 | **穂坂衛** | [PDF・1ページ](https://museum.ipsj.or.jp/guide/pdf/magazine/IPSJ-MGN520938.pdf#page=1) |
| S32 | 小野豊 | **大野豊** | [PDF・1ページ](https://museum.ipsj.or.jp/guide/pdf/magazine/IPSJ-MGN540722.pdf#page=1) |
| S33 | 大関正則 | **尾関雅則** | [PDF・1ページ](https://museum.ipsj.or.jp/guide/pdf/magazine/IPSJ-MGN541015.pdf#page=1) |

**根因**：先行の要約と検索結果に依存し、PDFの原表題と著者名への突合を完了条件にしていなかった。この訂正は史料保存の必要性を実証する。従前のGit履歴を残し、登録簿・分析内の誤記を今回修正した。その他の資料についても、原典精読の検査は継続する。

## 次回以降の要求

- すべての重要な主張に **資料ID＋該当ページ（または見出し）＋元の対象・時期・条件＋分析か直接事実か** を付ける。
- 原文の権利者、原文バイト列のハッシュ、URLの更新、取得失敗を個別に記録する。
- 突合していない資料を「完全に読んだ」「全事項を監査した」と宣言しない。
- 未取得P01–P06は書誌記録のみ。出典を推測で補完しない。
