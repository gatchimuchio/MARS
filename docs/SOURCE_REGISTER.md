# 一次資料登録簿

「資料の内容」と「そこから導く実験の命題」を分離する。公開資料は原典優先、外部からの説明・推測で代替しない。

**原文の再確認**：[原典取得・保全手順](../sources/README.md) ／ [取得したS01–S35の全35件のSHA-256・サイズ・原URL](../sources/originals.lock.json) ／ [主張と原文ページの突合索引](research/EVIDENCE_CROSSWALK_2026-11-09.md)。原典が正本、分析レポートは派生物。第三者原典そのものは公開GitHubに再配布しない。

| ID | 原典・発行者 | 主な確認対象 | 対象世代 |
|---|---|---|---|
| S01 | [MARS-101座席予約の実時間処理方式の基本構想](https://www.hitachihyoron.com/jp/pdf/1964/06/1964_06_18.pdf)、日立評論46巻6号、1964 | 座席の時間区間在庫、TC/FC/SC/TRC、ビットパターン、待ち行列・シミュレーション、二重照合・記録 | 101 |
| S02 | [MARS-101座席予約システム用リアルタイムプログラム](https://www.hitachihyoron.com/jp/pdf/1964/06/1964_06_19.pdf)、日立評論、1964 | 多重割込み、リアルタイム制御プログラム | 101 |
| S03 | [MARS-101座席予約中央処理装置](https://www.hitachihyoron.com/jp/pdf/1964/06/1964_06_21.pdf)、日立評論、1964 | 中央装置の物理構成 | 101 |
| S04 | [MARS-101座席予約用端局装置](https://www.hitachihyoron.com/jp/pdf/1964/06/1964_06_23.pdf)、日立評論、1964 | 20/26レターの要求と応答、端局入力の構造 | 101 |
| S05 | [MARS-101座席予約自動システム建設工事](https://www.hitachihyoron.com/jp/pdf/1964/06/1964_06_24.pdf)、日立評論、1964 | 全体の段階的試験、端局・通信・中央装置の不良と改善 | 101 |
| S06 | [国鉄の座席予約システム―マルス105システム](https://www.jstage.jst.go.jp/article/ieejjournal1888/94/2/94_2_101/_pdf)、電気学会、1974 | 専用回路依存の制約、ソフトウェア主体の再設計 | 105 |
| S07 | [MARS-101](https://museum.ipsj.or.jp/heritage/MARS-101.html)、情報処理学会 | HITAC-3030、装置構成・設置と運用時期 | 101 |
| S08 | [MARSの歴史と変遷](https://www.jrs.co.jp/guideline/mars/)、鉄道情報システム株式会社 | 1～505の世代境界、公開機能・性能値 | 全世代 |
| S09 | [JRシステムでのCOBOL–XML連携事例](https://www.cobol.gr.jp/wp-content/uploads/2024/11/05-3.pdf)、日立システムアンドサービス | 2000年代初頭の業務ロジックとCOBOL利用 | 501期前後 |
| S10 | [MARS 501構築事例](https://www.hitachi.co.jp/Prod/comp/soft1/casestudy/contents/jr/index.html)、日立製作所 | メインフレーム・UNIX・Web連携、COBOLとHiRDB等の採用箇所 | 501 |
| S11 | [HiRDB 30周年対談](https://www.hitachi.co.jp/Prod/comp/soft1/hirdb/30th_anniversary/article/index.html)、日立/JRシステム | 505のDB構成、二重系、ログ・復旧への運用要求 | 505 |
| S12 | [座席予約自動化の展望](https://www.hitachihyoron.com/jp/pdf/1964/06/1964_06_16.pdf)、日立評論46巻6号、1964 | 全国予約業務の問題設定、通信・情報処理・運用の全体像 | 101 |
| S13 | [MARS-101座席予約装置のシステムの設計](https://www.hitachihyoron.com/jp/pdf/1964/06/1964_06_17.pdf)、日立評論、1964 | 応答・精度・運行改正・経済性・信頼性・拡張の要求、全体方式 | 101 |
| S14 | [MARS-101座席予約操作プログラム](https://www.hitachihyoron.com/jp/pdf/1964/06/1964_06_20.pdf)、日立評論、1964 | 運用保守プログラム、系間ファイル差分照合、手動確認・更新 | 101 |
| S15 | [MARS-101座席予約用電信交換装置](https://www.hitachihyoron.com/jp/pdf/1964/06/1964_06_22.pdf)、日立評論、1964 | 電信交換・端局の集線、回線障害と保守試験 | 101 |
| S16 | [日立評論1964年6号目次「座席予約システム特集」](https://www.hitachihyoron.com/jp/archive/1960s/1964/06.html)、日立評論、1964 | 特集号の**全9論文**の母集団確定（S01–S05＋S12–S15） | 101 |
| S17 | [座席予約用電子計算装置MARS-1について](https://www.hitachihyoron.com/jp/pdf/1961/ex39/1961_ex_39_09.pdf)、穂坂衛・大野豊ほか、日立評論増刊、1961 | 専用座席予約機の基本方式、磁気ドラム・論理回路・運用構想 | 1 |
| S18 | [MARS-105座席予約端局装置の設計報告](https://www.hitachihyoron.com/jp/pdf/1974/02/1974_02_06.pdf)、日立評論、1974 | 端局の入力方式・カードと接点、保守・運用 | 105 |
| S19 | [MARS-105信頼性設計報告](https://www.hitachihyoron.com/jp/pdf/1974/04/1974_04_15.pdf)、日立評論、1974 | ファイル二重化、異常列車の発売停止と復旧、冗長化 | 105 |
| S20 | [MARS-105システム拡張・構成に関する報告](https://www.hitachihyoron.com/jp/pdf/1975/09/1975_09_03.pdf)、日立評論、1975 | タンデムCC/FC、共有ファイルとの比較、競合・増設と経済性 | 105 |
| S21 | [MARS-101以降の歴史](https://museum.ipsj.or.jp/computer/main/0006.html)、情報処理学会コンピュータ博物館 | MARSの世代変遷と技術遺産に関する展示 | 複数 |
| S22 | [MARS-1技術遺産記録](https://museum.ipsj.or.jp/heritage/mars-1.html)、情報処理学会 | 原機の座席予約・磁気ドラム・収蔵品情報 | 1 |
| S23 | [MARS-105端局装置の技術遺産記録](https://museum.ipsj.or.jp/heritage/mars105souchi.html)、情報処理学会 | 原端末装置・操作機構の現存記録 | 105 |
| S24 | [鉄道総研研究者によるMARS開発史の回顧](https://ethw-images.s3.us-east-va.perf.cloud.ovh.us/ethw/c/c6/Reference02_RRR_201912.pdf)、鉄道総研、2019 | 世代変化の後年の回顧。原著論文とは別証拠 | 複数 |
| S25 | [MARS-1の顕彰に関する共同発表](https://www.rtri.or.jp/eng/press/nr20250829.html)、鉄道総研、2025 | 2025年の受賞・顕彰経緯（設計史の証拠とは区別） | 1 |
| S26 | [IEEE History Center MARS-1マイルストーン](https://ethw.org/Milestones:MARS-1_%E2%80%94_First_Automated_Railway_Booking_System,_1960)、IEEE ETHW、2026 | 顕彰と式典の記録、稼働日とは別 | 1 |
| S27 | [MARS-301向け端局制御装置の技術報告](https://www.hitachihyoron.com/jp/pdf/1983/06/1983_06_10.pdf)、日立評論、1983 | 分散端局制御、端局操作・経済性・保守のトレードオフ | 301 |
| S28 | [MARS-301構成・納入に関する報告](https://www.hitachihyoron.com/jp/pdf/1986/01/1986_01_04.pdf)、日立評論、1986 | CCS/SRS/DMS、装置冗長性、システム化 | 301 |
| S29 | [オンラインシステムの動向と評価](https://www.hitachihyoron.com/jp/pdf/1975/09/1975_09_02.pdf)、日立評論、1975 | MARS各世代の主機、記憶・OS、ソフト方式、営業化時期の比較表 | 1–105 |
| S30 | [MARS-105稼働・移行に関する報告](https://www.hitachihyoron.com/jp/pdf/1974/01/1974_01_06.pdf)、日立評論、1974 | 1972年9・12月～1973年1月の段階切替 | 105 |
| S31 | [穂坂衛氏インタビュー](https://museum.ipsj.or.jp/guide/pdf/magazine/IPSJ-MGN520938.pdf)、情報処理学会誌、2011 | MARS-1から101への問題設定、窓口視察、木片入力、部門横断の開発の証言 | 1/101 |
| S32 | [大野豊氏インタビュー](https://museum.ipsj.or.jp/guide/pdf/magazine/IPSJ-MGN540722.pdf)、情報処理学会誌、2013 | MARS-1磁気ドラム同期探索、専用機の限界、101への転換の証言 | 1/101 |
| S33 | [尾関雅則氏インタビュー](https://museum.ipsj.or.jp/guide/pdf/magazine/IPSJ-MGN541015.pdf)、情報処理学会誌、2013 | 105の総合設計チーム、需要増・容量と設備増強の証言 | 103–105 |
| S34 | [穂坂衛の技術史略歴](https://museum.ipsj.or.jp/pioneer/hosaka.html)、情報処理学会 | 証言者の経歴・担当範囲の照合 | 1/101 |
| S35 | [MARS-101の博物館展示](https://www.kahaku.go.jp/exhibitions/vm/past_parmanent/rikou/computer/MARS101.html)、国立科学博物館 | 収蔵機の写真・機能・能力表記（時点明示なし） | 101 |

## 本文未取得・書誌情報のみの関連史料（調査継続）

以下は存在・書誌情報を把握した資料であり、**本文の読み込み完了には算入しない**。リンク先の閲覧条件・制限を迂回しない。

| ID | 文献と所在 | 調査上の用途 | 状態 |
|---|---|---|---|
| P01 | [穂坂衛のMARS回想（1983）](https://ipsj.ixsq.nii.ac.jp/records/6267)、情報処理学会 | 2011年の後年証言と同一人物の早期記録を照合 | 本文未取得 |
| P02 | [MARS-105設計論文（第1報、1974）](https://ipsj.ixsq.nii.ac.jp/records/7866)、情報処理学会 | 当時のシステム設計の詳細 | 本文未取得 |
| P03 | [MARS-105ソフトウェア設計論文（第2報、1974）](https://ipsj.ixsq.nii.ac.jp/records/7855)、情報処理学会 | 制御プログラム・使用言語の詳細 | 本文未取得 |
| P04 | [MARSシステム運用管理論文（1991）](https://ipsj.ixsq.nii.ac.jp/records/39826)、情報処理学会 | 実運用の変更・制御・責任境界 | 本文未取得 |
| P05 | [MARS-301基本設計の関連書誌（1983）](https://jglobal.jst.go.jp/detail?JGLOBAL_ID=200902054496932824)、J-GLOBAL | 301要求分析・信頼性の設計対象 | 本文未取得 |
| P06 | [MARS-301信頼性設計の関連書誌（1984）](https://jglobal.jst.go.jp/detail?JGLOBAL_ID=200902033358093024)、J-GLOBAL | 301故障分離・連続運転方式 | 本文未取得 |

## 分析レポート

- [2026-11-09 MARS史料総合監査：失われつつある設計知の再構成](research/HISTORICAL_ENGINEERING_AUDIT_2026-11-09.md) — 各資料の寄与、世代ごとの設計判断、史料齟齬、再現実験への変換、未解明項目を記録。
- [2026-11-09 原典・ページ・命題の突合索引](research/EVIDENCE_CROSSWALK_2026-11-09.md) — 必要な主張から原文へ戻るための索引、初回分析の誤記訂正と原因。

## 読み替え禁止の例

- S01 の数値と処理能力は **MARS-101の設計時点**に限る。505のピーク処理能力へ無断で外挿しない。
- S09 が示す「業務ロジックの多くはCOBOL」は **2000年代の事実**。MARS-101原機の言語まで証明しない。
- S10 の HiRDB 採用例は、当初は列車データ作成管理の ASTD を含む特定のサブシステム。全機能が同じDBで動くとの断定はできない。
- S11 で述べられるデュアルDB構成を、MARS-101の二重系と同一の実装として扱わない。
- S05 の総合試験の記録は、現在の開発工程にそのまま適用できるという意味ではない。確認対象は当時の方法・条件・実績。
- S29 の世代比較で使われる「ソフトウェアなし」は MARS-1 の専用論理に関する区分。MARS-101のプログラム内蔵とは矛盾しない。
- S17 と S22 の原機ビット容量は数値が一致しない。総容量・有効容量・計測時点を立証するまで、一方を原機の唯一の値にしない。
- S30 の初期切替（1972年）と S06 の全面移行期（1973年）を同じ「稼働開始」指標へ無断で統合しない。

今後、原資料の命令体系・コード・符号の正確なデータを発見した場合は、対象バージョンを付して新しい資料IDと変更判断を追記する。

