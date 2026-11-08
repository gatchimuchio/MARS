# MARS — 公開資料に基づく再現・検証プロジェクト

**日本の鉄道座席予約システム MARS の設計を、一次資料に遡って復元し、再現の成立範囲を検証する独立研究。**

> Independent research and reproduction of publicly documented engineering principles behind Japan's MARS railway reservation systems. **Not an official JR or Hitachi project.** English summary below.

## 目的と境界

本プロジェクトの目的は、MARS と同じ画面を持つ予約アプリを作ることではない。**各世代の原設計が、どの要求・制約・根拠からどの構造を導出したか**を調べ、確認できた実装原理を再現し、その同一性と成立条件を検証する。

研究上の第一目的は、**当時の日本の工業・情報工学が残した設計思想と判断の知見を、史料照合と実験を通じて吸収・記録すること**。使用言語や現代実装方式を史料の確認前に先決しない。

- **歴史的再現**：MARS-1、101、105、301、501、505をそれぞれ独立した世代として扱い、当時の機械構成・制御・データ形式・言語を一次資料で特定する。
- **再構成実験**：原資料に対応する機構だけをモデル化し、史料の欠落を推測で埋めた場合は明示する。
- **多言語比較**：確定した言語非依存の同一仕様を複数言語で実装し、実行環境を固定して性能・信頼性・保守性などを比較する。**原機の再現とは別の実験**とする。

MARS-1 は固定論理回路、MARS-101 はプログラム内蔵方式であり、両者を同一ソフトウェアとして扱わない。2000年代初頭の業務ロジックにCOBOLが多数使用された史料はあるが、それを MARS-101 や現行 MARS-505 全体の使用言語に無断で拡張しない。

## 現在の成果

| 対象 | 状態 | 主張できる範囲 |
|---|---|---|
| MARS-101 論理実験 | 稼働・検証済み | 区間ビットマップ、予約・取消、二系統照合、操作記録・再生監査を部分再構成 |
| MARS-101 実機の命令体系・端局プロトコル | 未再現 | 史料整理と実装境界の確定が必要 |
| MARS-105以降 | 複数世代の原著・証言を一次整理済み | 原構造・時点の特定前に実装方式を固定しない |
| 多言語比較 | 検証契約を準備 | 歴史的再現と独立して実施 |

### 史料調査・分析レポート

**[2026-11-09 MARS史料総合監査：失われつつある設計知の再構成](docs/research/HISTORICAL_ENGINEERING_AUDIT_2026-11-09.md)**

1964年の日立評論MARS-101特集**全9論文**、1961年のMARS-1原著、MARS-105の信頼性・拡張設計、301の端局設計、後年の501/505、開発当事者の証言などを統合。出典ごとの事実、要求→技術選択の因果、故障・停止・復旧、現場試運転、年代・能力値の齟齬、原機再現に必要な追加資料を整理した。本文未取得の関連論文も区別して登録している。

- [史料登録簿と未取得資料一覧](docs/SOURCE_REGISTER.md)
- [原理を再現する際の同一性と未確定事項](docs/RECONSTRUCTION_BOUNDARIES.md)

### 最初の通し実験

```bash
cd experiments/mars101-logical
python3 mars101_lab.py demo
python3 -m unittest discover -s tests -v
```

外部ライブラリ不要。Python は **論理検証用ホスト処理系**であり、MARS-101の原機言語として選んだものではない。実験データは架空で、発券結果は実券ではない。現在11件の検証を整備済み。

- [実験の説明と動作範囲](experiments/mars101-logical/README.md)
- [原設計・再現・推定の区別](docs/RECONSTRUCTION_BOUNDARIES.md)
- [一次資料と確認事項の登録簿](docs/SOURCE_REGISTER.md)
- [資料分析・工学的知見・次の研究課題](docs/research/HISTORICAL_ENGINEERING_AUDIT_2026-11-09.md)
- [言語非依存の検証契約](docs/CONFORMANCE_CONTRACT.md)
- [多言語比較の実験方法](docs/MULTILANGUAGE_PROTOCOL.md)
- [設計判断の記録](docs/DECISIONS.md)

## 運用原則

1. 要求・原資料・確認事実・推論・仮定・未確認を混同しない。
2. 再現の同一性は **対象世代・機能・入力・状態遷移・出力・運用条件**ごとに示す。
3. 実装は入力から出力・記録・監査までを通し、その後に局所の性能・故障条件を検証する。
4. 言語・フレームワーク・工程は設計に従属する。歴史的再現に使用する言語を先に決めない。
5. 実験の差異・欠陥・未再現項目を隠さず、根拠の更新とともに記録する。

## English summary

This repository is an **independent, source-grounded reconstruction study** of the MARS railway reservation system family. The work intentionally separates (1) historical fidelity, (2) runnable logical experiments, and (3) cross-language comparisons. The first experiment models selected MARS-101 concepts, using a modern host-language harness only for verification. The original HITAC-3030 instruction set, original programming language, terminal protocol, scheduling, and hardware are **not yet reproduced**. No real trains, railway reservations, payment systems, or tickets are accessed or issued.

The name MARS refers to the historical railway system and is used here for identification and research. It is a trademark of Railway Information Systems Co., Ltd. This project has no affiliation with JR Group, Railway Information Systems, or Hitachi.

## License / ライセンス

本プロジェクトが独自に作成した成果物は、既存の研究リポジトリと同様に**種類別のライセンス**を適用する。

- **ソースコード・テスト・CI**：Apache License 2.0（`Apache-2.0`）
- **仕様・設計・研究記述・README**：Creative Commons Attribution 4.0 International（`CC-BY-4.0`）

Copyright 2026 がっちむち♂。適用範囲・帰属表示・原典の権利留保は [LICENSE](LICENSE)、[LICENSE-APACHE-2.0](LICENSE-APACHE-2.0)、[LICENSE-CC-BY-4.0](LICENSE-CC-BY-4.0)、[NOTICE](NOTICE) を参照。これは全ファイルに対してどちらかのライセンスを任意に選べる二重ライセンスではない。

Historical papers, source quotations, diagrams, third-party code and the rights in the original MARS systems are **not** relicensed by this repository. These licenses apply only to this project's independently authored works.

