---
name: mul99
description: 乘乘熱氣球（Chengcheng Hot Air Balloon）— 給小一到小三的九九乘法練習網頁遊戲，單一檔案 index.html，部署在 GitHub Pages。Use this skill before touching anything in ~/personal/mul99 — editing index.html, changing any on-screen Chinese copy, adjusting game rules or coin economy, writing or running tests, rebuilding the 注音 subset font, or pushing/deploying. 內含：無 emoji 規約、改字必重建字型、兒童文案六條審定標準、場景與貼紙不共用圖、存檔安全、測試矩陣指令、headless Chrome 的坑、推送帳號、上線驗證流程。
---

# 乘乘熱氣球 開發規約

| | |
|---|---|
| 程式碼 | `~/personal/mul99/index.html` — **單一檔案**，CSS / JS / SVG 全部內嵌，約 365 KB |
| 線上 | https://slowlywithlili.github.io/mul99/ |
| repo | `slowlywithlili/mul99`，分支 `main`，GitHub Pages 自動部署（約 30 秒）|
| 測試 | `~/personal/mul99-tests/`（見下方「測試」）|
| 當下進度與待討論事項 | `~/personal/mul99-HANDOFF.md` |
| 使用者 | 「利利寫生活」，一人開發，自己在真機上實測。用**繁體中文**溝通與回覆 |

受眾是**六到八歲的小孩**。任何決定有疑慮時，判準是「七歲看得懂嗎？」「這樣講會不會讓他覺得被罰？」

---

## 一、動工前必讀的六條硬規則

### 1. 全站不用 emoji

每一個符號都是**手繪的內嵌 SVG**（`ICON` 表在 index.html:1969，取用是 `ic('name')` index.html:2215）。
文案裡要寫 emoji 的話，走 `MK_IC` / `mk()` 查表換成手繪符號（index.html:2521-2522），**不要直接輸出 emoji 字元**。
使用者在需求裡寫 emoji（例如「歡迎回來🎉」）時，意思是「這裡要一個這種感覺的符號」，不是要你輸出那個字元 —— 去 `ICON` 找或新畫一個。

### 2. 改到任何畫面上的中文字 → 一定要重建注音字型

字型是從 index.html 裡出現過的漢字 subset 出來的，漏字就會掉字：

```bash
# 字型工具（venv + 原始字型檔）放在更早一個 session 的暫存區，編號每次都不一樣，
# 所以用「哪個 scratchpad 裡面有 fontenv」去找，不要寫死路徑
OLD=$(for d in /private/tmp/claude-*/*/*/scratchpad; do [ -x "$d/fontenv/bin/python3" ] && echo "$d" && break; done)
cd ~/personal/mul99
$OLD/fontenv/bin/python3 make-font.py \
  $OLD/fontdl/BpmfGenSenRounded-M.ttf $OLD/fontdl/BpmfGenSenRounded-B.ttf
```

- 目前 **1012 字**。字數只會往上，突然變少代表有東西被誤刪。
- 唯一的警告「什=ㄕㄜˊ 字型只有 shen2／shi2」是舊有的、無害。
- `$OLD` 是**更早一個 session 的暫存區，隨時可能被清掉**。清掉的話要重建 venv（fonttools + brotli）並重新下載 [ButTaiwan/bpmfvs](https://github.com/ButTaiwan/bpmfvs) 的 `BpmfGenSenRounded.zip`（SIL OFL 1.1）。多音字對照表在 `zhuyin.txt`。
- 注音**不是 `<ruby>`**，是用 Unicode 變體選擇子（U+E0100–E01EF，代理對 `\uDB40[\uDC00-\uDFFF]`）畫進漢字字形裡。`zyOne()`（index.html:1321）只對多音字插選擇子；`zySkip()`（index.html:1312）會跳過 SCRIPT/STYLE/TEXTAREA/INPUT、SVG 命名空間、和帶 `nozy` class 的節點。
- **給大人看的字要加 `nozy`**（例如頁尾 `.credit`）。

### 3. 給小孩的文案：六條審定標準

每一句玩家看得到的字都要同時過這六關。**改任何一句之前先對一遍，改完全站再抽查一遍。**

| 標準 | 具體做法 |
|---|---|
| 簡短好讀、六歲看得懂 | 一句一件事；短句優先；不用「首次通關」「熟練度」「賺取」「蒐集」這種大人詞 |
| 符合兒童心理學 | 不用「死」「失敗」「錯」這類詞；卡住要講成「正常的事」 |
| 成長型心態 | 誇**努力和方法**，不誇聰明和結果；**不預言結果**（「下次就會答對了」「再練習一下會更棒」都是壓力）；不評價人（「你好厲害」改成講他做了什麼）|
| 正向語言 | 錯誤訊息一律用「慢慢來」開頭；斷掉不歸零、改說「歡迎回來」 |
| 刪贅字贅句 | 同一個意思只留一句；跳出時間短的提示（toast）只講一件事 |
| 標點要正確 | **標題不加句號**；標題以外的敘述句結尾一定要有 `。`／`！`／`？`。說明清單（`HELP` / `INFO` 的 `li`）每一條都算敘述句 |

不算敘述句、**不加句號**的：按鈕、標籤、貼紙和場景名稱、狀態列（「還剩 5 個答案」）、難度說明的短詞（「自己慢慢走」）、小夥伴的對話泡泡、`PRAISE` 的歡呼句。

再加三條：
- 玩家看得到的字寫「**不熟**」不寫「答錯」（程式註解裡的「答錯」可以留）。
- **給大人的小字不受此限**（挑戰者頁那張卡片、`INFO` / `HELP` 的 `note` 欄位）—— 但標點一樣要對。
- 歡呼和預言要分清楚：**當下的驚嘆**（「太厲害了！」「答對了！」）可以留，**對未來的保證**（「下次就會答對」）和**對人的評價**（「你好厲害」）不可以。

改文案的時候順手**刪掉多餘和重複的句子** —— 使用者每次都會要求這件事。
`r4.html` 會掃 `HELP` / `INFO` 每一條的結尾標點，也會擋掉已經刪掉的用詞。

### 4. 解說句一律放在標題下面

小孩的視線由上往下，解說擺在畫面最底下等於沒寫。
全站的「怎麼玩」都放進標題下那塊 `helper()`（index.html:2517）。
底下**只留狀態、不留說明**（例如貪食蛇的「最長紀錄」，沒紀錄時整行不顯示）。
需要放在上面的補充狀態用 `<p class="note topnote">`。

**遊戲中的提示句同理**：尋寶的 `#hnote` 在 1~9 下面、畫的上面；貪食蛇的 `#snnote` 在題目下面、盤面上面。
兩個都掛 `.note.gnote`，它有 `min-height:2.5em`，**提示句變長時下面的畫和盤面不會被往下擠**（`r4.html` 量這個，容許 1px）。

### 5. 存檔是不可信輸入

紀錄存在 `localStorage`，**跟著 origin 走**（`https://slowlywithlili.github.io`）—— 同一個 GitHub Pages origin 下**別人的頁面也寫得進來**。所以：

- 每個欄位都要白名單驗證：`fixPlayer()`（:1470）/ `fixP()` / `okSave()`（:1519）。
- 玩家名字顯示前一定 `esc()`（:2649）。
- 新增存檔欄位 → `blankPlayer()`（:1385）和 `fixPlayer()` 兩邊都要加，否則舊存檔讀進來是 undefined。
- 刪掉存檔欄位是安全的（`fixP` 只抄 `blankP()` 有的鍵），舊資料會自動被丟掉。
- **沒有備份／還原功能**（原本有，已移除）。唯一提醒家長的地方是挑戰者頁那張卡片。

### 6. 推送要用 `ppmonkeyLiao` 這個 gh 帳號

`gh auth switch` 會被權限分類器擋下來，**助理自己切不了**。要請使用者在對話裡自己打：

```
! gh auth switch -u ppmonkeyLiao && git push origin main
```

---

## 二、標準改動流程

1. 改 `index.html`（用腳本批次替換時**每一條都加 assert**，整批成功才寫檔，避免半套）
2. 動到畫面上的中文字 → **重建注音字型**（規則 2）
3. `cd ~/personal/mul99-tests && ./run.sh` → 全部要綠
4. 本輪新行為 → **補一支回歸測試**（見下方「測試」）
5. 需要時截圖目視確認（版面、動畫、顏色）
6. 更新 `README.md`（專案慣例：每個 commit 都同步更新，而且要寫**為什麼**，不只寫改了什麼）
7. commit（中文訊息，條列）→ push → **驗證線上**

### 驗證線上

```bash
curl -s "https://slowlywithlili.github.io/mul99/?cb=$RANDOM" -o /tmp/live.html
# 然後用 python3 檢查關鍵字串「該在的在、該沒的沒了」
```

**用 Python 比對，不要用 shell 的 grep 吃中文變數** —— zsh 會丟 `character not in range`。

---

## 三、測試

```bash
cd ~/personal/mul99-tests
./run.sh              # 完整矩陣（22 支）
./run.sh r3.html      # 只跑一支
```

`run.sh` 會先跑 `rebuild.py`，把 `tails/*.txt`（測試腳本本體）接到**當下的** index.html 後面，產生 `build/*.html` 再跑。所以程式一改直接跑就好，不用手動同步。

| 檔 | 管什麼 |
|---|---|
| `audit1/2/3` | 口訣、熟練度、存檔安全、跨日重置、惡意欄位、13 個歷史 bug 回歸 |
| `rules` | 金幣規則（30 項）|
| `r3` | 金幣新規則、畫廊整理、解說句位置、音效響度、光暈、鼓勵句（55 項）|
| `r4` | 遊戲中提示句的位置與不位移、貪食蛇任務＝兩條彩虹、任務完成的一句話、光暈再縮小、鼓勵句增刪、刪畫文案、說明清單的句號、已淘汰用詞 |
| `r5` | 17 個場景的資料完整、舊場景順序沒動、場景道具不跟貼紙共用、同一場景不重複出現、回首頁氣球的圓底 |
| `r6` | 補氣站：誰會進去、何時出現、兩天才算補好、答錯歸零、金幣、訪客、首頁氣球、沒動到熟練度 |
| `r7` | 頁尾三段（連結、分隔線、最後更新）、「關於遊戲」整頁的內容與連結、回首頁、`HELP.about`、遊戲中按到會先問 |
| `rise` / `foot` | 進場動畫 / 頁尾與首頁提示 |
| `host` / `r2host` / `visual` / `drv_visual` | 版面（多畫面 × 多寬度）|
| `v_all` | 貼紙、轉蛋、畫作 |
| `v_modal×6` | 28 個彈窗 × 6 種螢幕高度都捲得到按鈕 |

新增測試：寫一支 tail 丟進 `tails/`，`run.sh` 會自動帶上。
慣例是把結果塞進 `document.title`（`XXX OK` / `XXX BAD(n) 第一條訊息`）和 `<pre id=out>`。

### headless Chrome 的坑（都踩過，不要再踩）

- `--window-size` **不影響版面**，`innerWidth` 永遠是 500。量版面一定要放進 `<iframe width=N>` 宿主。截圖才能用 `--window-size` 裁切。
- iframe 內容**不會出現在 `--dump-dom`** 裡。要嘛讓內層 `parent.postMessage()`，要嘛讓它寫 `parent.document.title`。
- **虛擬時間不會推進 CSS 動畫。** 用 `setTimeout` 等於停在 `from` 那一格。驗動畫走 Web Animations API：`el.getAnimations()`、`a.effect.getTiming()`、`a.currentTime=`、`a.finish()`、`a.playState`。
- **偽元素（`::before`）上的動畫**要 `el.getAnimations({subtree:true})` 才抓得到。
- 量版面前先把動畫 `finish()`，否則量到的是動畫起點（曾經誤判頁尾蓋住攤子 31px）。
- iframe 宿主要 `--allow-file-access-from-files --user-data-dir=/tmp/cr-mul99t`，不然 `contentDocument` 是 null。
- 彈窗那組要 `--virtual-time-budget=90000`。
- **測試 tail 裡不要用頂層 `const`** —— 會跟 index.html 的頂層宣告撞名（例如 `function num`），丟 SyntaxError 把整個 `<script>` 靜悄悄殺掉，症狀是「什麼都沒發生」。一律包 IIFE、變數加前綴。
- **比對字串前先剝掉注音的 IVS 選擇子**：
  ```js
  const clean=t=>String(t).replace(/[\uDB40][\uDC00-\uDFFF]/g,'').replace(/\s+/g,'');
  ```
- 沒有全域的 `act()` 分派函式，分派是掛在 `document` 上的 click listener。要觸發動作就造一顆暫時按鈕再 `.click()`。
- `showHelp()` **不吃參數**，它讀 `currentView`。選乘法表那個畫面的 view 名字是 `'pick'` 不是 `'reviewPick'`。

---

## 四、index.html 地圖

| 位置 | 內容 |
|---|---|
| :1006 `THEMES` / :1021 `STICKERS` | 63 張台灣主題貼紙，七個分類 |
| :1059 `STAGES` | 乘法實戰家 12 關 |
| :1067 `STAGE_CAP` / `TIMED_GOAL` / `DRAW_COST` | **金幣調校常數** |
| :1074 `SNAKE_LV` / :1082 `PAIR_LV` | 貪食蛇、配對的難度 |
| :1102 `SCENES` | 尋寶的 17 個場景（**只能往後接**，見第六節）|
| :1249 `ART_N` / :1251 `MAX_ART` | 一張畫藏 9 個答案；畫廊最多 60 張 |
| `PUMP_N` / `PUMP_DAYS` / `PUMP_MAX` | 補氣站調校常數（**要宣告在 `fixPump()` 之前**，見第六節）|
| `pumpAdd` / `pumpDue` / `pumpQueue` / `pumpHeal` | 補氣站的全部規則 |
| :1312 `zySkip` / :1321 `zyOne` | 注音選擇子 |
| :1385 `blankPlayer` / :1470 `fixPlayer` / :1519 `okSave` / :1584 `save` | 存檔 |
| :1658 `TIERS` / :1665 `TIER_QUESTS` / :1670 `COIN_MAX_DAY` | 攤子任務與每日金幣總量 |
| :1698 `ensureDaily` / :1751 `checkQuests` | 每日重置、任務達成判定 |
| :1822 `sfx` | 音效（`tone(freq,dur,type,when,vol)`）|
| :1969 `ICON` / :2215 `ic()` | 手繪符號 |
| :2021 `ART` | 手繪小物（**貼紙和場景共用這張表**，但兩邊不可以用到同一個 key）|
| :2408 `MODES` | 首頁六顆氣球 |
| :2434 `riseHome` | 首頁進場動畫的延遲排程 |
| :2451 `HELP` / :2524 `INFO` | 「我教你玩」與「金幣怎麼拿」的說明清單 |
| :2517 `helper()` | 標題下那塊說明框 |
| :2564 `BUDDY_SAY` | 陪我玩小夥伴的鼓勵句 |
| :2708 `go()` / :2725 `VIEWS` | 換頁與所有畫面 |
| :3420 `coinsLeftToday` / :3434 `playCoinsLeft` | 今天還能拿幾枚（**單一來源，不要各算各的**）|
| :4590 `fitCredit` | 量頁尾實際高度填 `--credh` |
| 最後的 `document.addEventListener('click')` | 所有 `data-act` 的分派 |

※ 行號會隨著改動飄移，用 `grep -n` 確認。

---

## 五、金幣經濟（改之前先看這段）

```
六個攤子任務各 1 枚 + 初級全完成 1 枚 + 超級全完成 2 枚      = 9
+ 乘法實戰家：過一關 1 枚、一天最多 3 枚（STAGE_CAP）        = 3
+ 比快挑戰：答對 TIMED_GOAL(10) 題，一天 1 枚                = 1
= COIN_MAX_DAY 13 枚／天      轉一次轉蛋 DRAW_COST = 3 枚
```

- **攤子以外的金幣只由 `playCoinsLeft()` 算**，首頁氣球和關卡頁都讀它。重複實作過一次就錯過一次（歷史 bug）。
- **實戰家的規則不要改回「第一次通關／重玩」兩套上限。** 舊規則的後果是：小孩第一關全對就把首次通關額度用光，接下來一關一關往下打一枚都拿不到，回頭重玩舊關卡反而有 —— 跟說明寫的正好相反。現在只剩一條「過關就 1 枚，一天 3 枚」，七歲講得出來。
- **貪食蛇的金幣＝過關＝兩條彩虹（14 個答案）**。任務目標 `{type:'snake', target:2}` 要跟 `SNAKE_WIN` 對齊，
  不要改回 1：target 1 的時候小孩吃到第 7 個就跳「可以拿金幣了」，但畫面寫的是「吃到 14 個過關」，兩邊打架。
- **不要在每一關掛金幣符號**：一天只有 3 枚，12 關全掛就是騙人。黃色底色只代表「還沒過關」＝事實，不是承諾。
- **攤子以外的金幣不要做進攤子任務裡**：攤子是「做完去領」的清單，實戰家和比快是過關當下自動入帳，混在一起小孩會去攤子找領取按鈕。

---

## 六、其他已定案、不要推翻的設計

- **連續天數斷掉不歸零顯示**，改說「歡迎回來」（`streakPill()`）。
- **全站只有一個答錯音 `sfx.wrong()`**（7 個呼叫點共用），音色和音量都一樣，不要為個別遊戲另外做一個。
- **答錯音效刻意比答對小聲**：方波的 RMS 是峰值本身、三角波只有 0.577 倍，同振幅下方波大快 5 dB。現在答錯是正弦波 0.035、答對 0.052。`r3.html` 有測試盯這個比例。
- **刪除一定先跳確認**，而且要寫清楚刪的是哪一個、「刪掉就找不回來」，預設拿到焦點的是「不要刪」（參考 `askDelete()` / `askDelArt()`）。
- **觸控目標至少 44×44**。字縮小但要保留按壓範圍時，用 `::after{position:absolute;inset:-9px -5px}` 往外撐，不影響版面高度。
  左上角的 `.logo`（＝回首頁鍵）已經這樣撐到 **47×50**（寬螢幕 120×46）：上下各 4px，
  窄螢幕再往左 8px、**右邊只給 1px**，多撐就會蓋到旁邊的「我教你玩」。`host.html` 每個寬度都在量。
- **`.logo` 有淺色圓底，不要拿掉，也不要改成加文字說明**。小孩不讀字，但學得會
  「圓圓的、有底色的＝可以按」，所以它的底色／外框／圓角跟右上角那排 `.iconbtn` 同一套。
  手機上「乘乘熱氣球」五個字本來就是因為塞不下才藏起來的，再塞一行小字只會更小更難讀。`r5.html` 盯著圓底還在不在。
- **`SCENES` 只能往後接，不能插在中間，也不能刪、不能換順序。**
  畫廊存的是場景的**索引**（`art.s`），動了順序就等於把小孩以前所有的畫換成別張。
  目前 17 個：前 8 個是舊的（小房間、小公園、海邊沙灘、廚房、外太空、恐龍島、下雪天、夜市），
  後 9 個是後來加的（海底世界、過年的家、森林好朋友、遊樂園、平溪天燈、梵谷星空、聖誕節、賽車場、中秋團圓）。
  `r5.html` 盯著前 8 個的名字和順序。
- **場景道具不可以直接用貼紙的圖。** 貼紙要花 3 枚金幣轉蛋才抽得到，場景裡到處都是就不值錢了。
  `ART` 同時給貼紙和場景用，所以很容易不小心共用 —— `r5.html` 會把每個場景的 `items` 和 `STICKERS` 對一遍。
  天燈、聖誕樹、月餅這種兩邊都要有的東西，作法是**畫進背景 SVG 裡**，不做成可以到處灑的道具。
  新場景要新道具就**新畫一個**，順手把畫風對齊既有的（24×24、扁平色塊、自帶顏色不用 `currentColor`）。
- **場景不要純隨機抽**。用 `pickScene()`：排除最近 5 次開過的，再排除畫廊最新 3 張的場景。
  純隨機的話連玩 3 張就有 34% 機率撞到同一個場景，小孩會覺得「怎麼又是這張」。
- **補氣站的錯題只掛在 `record(a,b,ok)` 一個地方**（`if(!ok) pumpAdd(a,b)`）。
  全站有對錯的遊戲都走這個函式，所以不要在各個遊戲裡各加一次；
  翻翻樂不呼叫 `record`，所以它自動不算，也不要幫它加。
- **補氣站的 `m.pump` 和熟練度 `m.facts` 不可以合併。** facts 只有 `{c,w,s}`，沒有日期，
  而且 `key()` 把 5×3 和 3×5 併成同一題；補氣站要日期、而且 7×8 和 8×7 分開算。
- **頁尾固定三段：`利利寫生活 製作｜關於遊戲｜最後更新：年.月.日`。**
  「｜」要掛在前一段的尾巴（`<span class="sep">`），不能獨立一格 —— 頁尾在 320px 會換行，
  獨立一格的話分隔線會變成下一行的開頭。日期讀 `document.lastModified`，不要手動維護。
  站內換頁用 `<button class="lk">`，外部連結才用 `<a>`，兩者共用同一條 `.credit` 樣式。
- **寫給家長的話有兩份，不要合併也不要互相取代**：頁尾進去的「關於遊戲」整頁（`VIEWS.about`，
  長版：誰做的、為什麼做、紀錄存在哪裡、iOS 要加到主畫面），和「挑戰者」頁下方那張三句卡片
  （短版，家長在切換孩子的當下才看得到）。兩條路徑不一樣，少一邊就有人看不到。
- **「關於遊戲」整頁是給大人看的，但沒有標 `nozy`**（跟「挑戰者」那張卡片一致），
  所以改它的字**一樣要重建注音字型**，「一」「不」的變調也要補進 `zhuyin.txt` 的 `[詞]` 區。
  `.about` 靠左、行高 1.8、18px，刻意跟給小孩的畫面（置中、大字、短句）長得不一樣。
  但 `m.pump` **只存日期和補氣進度**，不要再抄一份 c/w/s。
- **`PUMP_N` / `PUMP_DAYS` / `PUMP_MAX` 一定要宣告在 `fixPump()` 之前。**
  讀存檔（`migrate → fixPlayer → fixPump`）是在載入當下跑的，常數宣告晚了會丟 TDZ 例外，整個 app 打不開。
- **補氣站那一枚金幣只有「今天真的有題目可以補」才算**（`pumpCoinLeft()`）。
  無條件加 1 的話，沒有錯題的日子首頁會顯示一枚永遠拿不到的金幣。
- **`pumpDue()` 要排掉「今天已經在補氣站答對過的」**，不然「再玩一次」會一直重複同一題，
  而且那題再答對也不會有進度（同一天只算一次）。
- **補氣站不在同一回合重出錯題**。這個遊戲的用意就是隔一天再回想一次；
  其他遊戲的錯題重練不要跟著改。
- **兩個動畫搶同一個 `transform` 會打架**，後者勝。進場動畫掛外層容器、idle 漂浮動畫掛內層元素。
- `@media (prefers-reduced-motion:reduce)` 裡，進場動畫是**整個不做**（`.rise{animation:none}`），不是縮到 0.01ms。

---

## 七、回報與溝通

- **用繁體中文回覆。**
- 使用者問「你覺得適合嗎／給我一點意見」時，要給**明確建議和理由**，不要只列選項。建議「不要做」也是可接受的答案，但要給替代方案。
- 使用者回報症狀（「沒有金幣跑出來」）時，**先找根因再改文案** —— 很可能是規則本身壞了，不是說明不清楚。
- 改完要說：commit hash、線上驗證結果、測試矩陣狀態。數字用量出來的，不要用估的。
