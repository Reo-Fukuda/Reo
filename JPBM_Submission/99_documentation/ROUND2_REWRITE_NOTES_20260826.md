# Round 2 全面改稿ノート(2026-08-26)

対象ファイル: `01_manuscript/working/JPBM_Manuscript_round2.tex`
準拠文書:
- `JBR_Submission/JPBM_paragraph_design_revised_0815.md`(パラグラフ設計・最新版)
- `99_documentation/JPBM_MANUSCRIPT_TERMINOLOGY_AUDIT_20260810.md`(用語監査)
- `99_documentation/JBR_TO_JPBM_REVISION_REQUIREMENTS.md`(JBR指摘への対応要件)
- 数値ソース: `01_manuscript/baseline_JBR_20260301/`(投稿版本文+SI)と `04_analysis/` の保存出力

## 1. 設計→原稿の対応

| 設計ID | 原稿での位置 | 状態 |
|---|---|---|
| I1–I8 | §1 Introduction(8段落+Key Terms表) | 反映 |
| T1–T4 | §2.1 Attribution Theory in Consumer Research | 反映 |
| T5–T11 (H1, H2) | §2.2 Consumer Responses to Initial Price and Distribution Information | 反映 |
| T12–T15 (H3a) | §2.3 Displayed Buyer and Market-Value Information and Failure Inference | 反映 |
| T16–T19 (H3b, H3c) | §2.4 Specific Presentation Conditions in Studies 3b and 3c | 反映 |
| O1–O3 | §3 Overview(+ Table 2「Conditions as Implemented」新設) | 反映 |
| F1–F7 | §4 Preliminary Field Study | 反映 |
| S1-1–S1-6 | §5 Study 1 | 反映 |
| S2-1–S2-8 | §6 Study 2 | 反映 |
| S3a-1–S3a-8 | §7 Study 3a | 反映 |
| S3b-1–S3b-7 | §8 Study 3b | 反映 |
| S3c-1–S3c-9 | §9 Study 3c | 反映 |
| C1–C4+meta | §10 Cross-Study Synthesis(+Study 4開示段落) | 反映 |
| D1–D13 | §11 General Discussion | 反映 |
| SS4-1–SS4-6 | 本文では§10末尾に要約1段落のみ。本体はSI改稿時に執筆 | **未着手(次工程)** |

## 2. 設計から意図的に変えた点(要共著者確認)

1. **H2の文言**: 設計は "lower perceived product luxuriousness" だが、保存尺度名ルール(監査§5)に合わせ "increase scores on Loss of Product Luxuriousness" と方向を尺度に揃えた。
2. **H3b/H3cの条件名**: 設計はどちらも "complimentary magazine-gift condition" と書くが、SI(投稿版A-4/A-5)で確認した実装は
   - Study 3b: **"Free (complimentary with a fan book)"**(fan-book gift)
   - Study 3c: **"Distributed for free"**(plain free)
   のため、H3b は complimentary fan-book-gift、H3c は free condition と実装通りに表記。設計S3c-3の「fan-book bonus vs implemented condition」の事前登録逸脱は§9で開示済み。
3. **Overviewに Table 2(各Studyの実装条件文言一覧)を新設**: O2/監査「implemented condition labels」の要求を表で満たすため。
4. **Study 3b/3cに総効果(PROCESS Model 1)を追記**: 3bのGGロゴ条件で総効果が正(b=0.54, p=.038)、3cのofficial siteで正の点推定(b=0.25, ns)という「保護効果が一様でない」証拠をC4/D7の根拠として明示。数値は保存出力 `研究S3b_PROCESS結果.txt` / `研究3c_PROCESS結果.txt`(N=281/282、投稿版と同一ラン)から。
5. **Study 1にTOST結果を追記**: `study1_tost_summary_d030.txt`(N=670)より、free vs comparable は d=±0.30で等価性不成立(upper p=.074)。「非有意≠等価」を本文で明示(設計S1-4/S1-6)。
6. **Study 3cのチェック項目の限界を明記**: 画像用に作られた単一項目(flagship product item)をsource操作のチェックに流用している点を§9でlimitationとして開示(旧稿は無言だった)。
7. **旧Figure 1(intro概念図)を削除**: 旧フレーミング(zero-price 3リスク図)のため。Figure番号を繰り上げ(1=overview, 2=Study1, 3=Study2, 4=Study3b)。

## 3. 数値の出所と系譜上の注意

- 全統計値は**JBR投稿版(baseline_JBR_20260301の本文+SI)を正**とした。
- フィールド分析の既知の系譜問題(`DATA_AND_REPRODUCIBILITY_GAPS.md`)はtex内に`%TODO(lineage)`/`%TODO(reanalysis)`コメントで位置づけ:
  - OpenSea: 6,209行→65コレクションの導出未文書化(2月アーカイブはN=63の別イテレーション)
  - X: official/projectアカウント未除外(F4/F6で本文開示済み)、collection単位クラスタリング未実施(F6で開示済み)
  - 「Walking Dead」「Dumb Ways to Die」のVADER語彙バイアス除外の扱いはクエリマップのメモと32ブランド表が不整合の可能性→監査対象(本文では言及せず)
- 実験N合計: 670+280+138+281+282+273 = **1,924**(投稿版と一致することを確認済み)。

## 4. 用語監査チェック(納品前監査項目 §7 対応状況)

- [x] 新規造語 0(16群の未承認ラベルすべて不使用を目視確認)
- [x] 理論語彙は4系統のみ(attribution theory / brand extension feedback effects / accessibility–diagnosticity perspective / digital brand extension)
- [x] zero-price effect は Study 1 の low vs free に限定
- [x] 尺度は保存済み尺度名(Failure Inference / Loss of Brand Luxuriousness / Loss of Product Luxuriousness / Perceived Brand Luxury / Behavioral Intention / Inferred Cost)
- [x] 操作は実装条件の完全表記(Table 2)
- [ ] タイトル: 暫定(要共著者承認)
- [ ] Figure内ラベル: 旧ラベルのまま(%TODO、再作図が必要)
- [ ] Keywords: 暫定6語(要承認)

## 5. 残タスク(優先順)

1. **Supplementary round 2 の全面改稿**(SS4本体、A-1〜A-6条件文言の用語整合、SI C(SPM)のmoderator名の付け替え=flagshipness→presentation-condition coding、SI D、SI E/F/G)
2. **図の再作成**: overview(Fig2.png)、Study 2/3bパス図(尺度名・条件名を監査語彙で)
3. **参考文献のEmerald(Harvard)スタイル変換**(現状はJBR時代のAPA併記のまま)
4. データ系譜の解消(gaps文書の解決順1–6)→ 解消後に数値を最終確定
5. Cover letter / Author bios / Highlights のJPBM向け新規作成
6. 用語監査の再実施(§7チェックリスト全項目)と共著者承認記録の記入

## 6. ワードカウント目安

本文(§1–§11、表・図・文献除く)約8,600語。設計の目安(Intro 850–950語、Theory 1,500–1,750語)に概ね収まる。JPBMの上限に対しては余裕あり。
