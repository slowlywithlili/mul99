#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把「源泉注音圓體」切成子集放進 fonts/，並把多音字的選擇子表寫進 index.html。

用法：

    pip install fonttools brotli
    python3 make-font.py ~/Downloads/BpmfGenSenRounded-M.ttf ~/Downloads/BpmfGenSenRounded-B.ttf

第一個是內文用的字重（Medium），第二個是粗體用的（Bold）；只給一個也可以，
那粗體就讓瀏覽器自己合成（會比較糊）。

原始字型一個字重 8 MB，整套 24.6 MB，所以不放進 repo。
到 https://github.com/ButTaiwan/bpmfvs/releases 下載 BpmfGenSenRounded.zip 解開就有。

它會做三件事：
  1. 拿 zhuyin.txt 的讀音跟字型的預設讀音對一遍，不一樣的地方印出來
  2. 把需要「異體字選擇子」的字和詞寫進 index.html 的 ZY-TABLE 區塊
  3. 只留 index.html 真的用到的字，輸出 fonts/bpmf-gensen-{m,b}.woff2
"""
import io, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
TXT  = os.path.join(HERE, 'zhuyin.txt')
HTML = os.path.join(HERE, 'index.html')
FONTS = os.path.join(HERE, 'fonts')
HAN  = re.compile(r'[㐀-鿿豈-﫿]')
VS0  = 0xE01E0          # 這個選擇子 = 這個字不要標注音
VSN  = 5                # E01E1~E01E5 = 第 2~6 個讀音

# ---- 注音 → 漢語拼音（字型裡的 z_xxxN 字符名用的就是拼音＋聲調） ----
INI = {'ㄅ':'b','ㄆ':'p','ㄇ':'m','ㄈ':'f','ㄉ':'d','ㄊ':'t','ㄋ':'n','ㄌ':'l',
       'ㄍ':'g','ㄎ':'k','ㄏ':'h','ㄐ':'j','ㄑ':'q','ㄒ':'x',
       'ㄓ':'zh','ㄔ':'ch','ㄕ':'sh','ㄖ':'r','ㄗ':'z','ㄘ':'c','ㄙ':'s'}
EMPTY = {'ㄓ':'zhi','ㄔ':'chi','ㄕ':'shi','ㄖ':'ri','ㄗ':'zi','ㄘ':'ci','ㄙ':'si'}
MED = {'ㄧ':'i','ㄨ':'u','ㄩ':'v'}
FIN = {'ㄚ':'a','ㄛ':'o','ㄜ':'e','ㄝ':'ê','ㄞ':'ai','ㄟ':'ei','ㄠ':'ao','ㄡ':'ou',
       'ㄢ':'an','ㄣ':'en','ㄤ':'ang','ㄥ':'eng','ㄦ':'er'}
WITH_INI = {'i':'i','ia':'ia','io':'io','ie':'ie','iai':'iai','iao':'iao','iou':'iu',
            'ian':'ian','ien':'in','iang':'iang','ieng':'ing',
            'u':'u','ua':'ua','uo':'uo','uai':'uai','uei':'ui','uan':'uan','uen':'un',
            'uang':'uang','ueng':'ong',
            'v':'u','ve':'ue','van':'uan','ven':'un','veng':'iong'}
NO_INI  = {'i':'yi','ia':'ya','io':'yo','ie':'ye','iai':'yai','iao':'yao','iou':'you',
           'ian':'yan','ien':'yin','iang':'yang','ieng':'ying',
           'u':'wu','ua':'wa','uo':'wo','uai':'wai','uei':'wei','uan':'wan','uen':'wen',
           'uang':'wang','ueng':'weng',
           'v':'yu','ve':'yue','van':'yuan','ven':'yun','veng':'yong'}
JQX  = {'j', 'q', 'x'}
TONE = {'': '1', 'ˊ': '2', 'ˇ': '3', 'ˋ': '4', '˙': '5'}

def to_pinyin(zy):
    if not zy: return None
    t = ''
    if zy[-1] in 'ˊˇˋ˙': t, zy = zy[-1], zy[:-1]
    tone = TONE[t]
    if not zy: return None
    ini = ''
    if zy[0] in INI:
        if len(zy) == 1:
            return EMPTY[zy[0]] + tone if zy[0] in EMPTY else None
        ini, zy = INI[zy[0]], zy[1:]
    med = ''
    if zy and zy[0] in MED:
        med, zy = MED[zy[0]], zy[1:]
    fin = ''
    if zy:
        if zy[0] not in FIN or len(zy) > 1: return None
        fin = FIN[zy[0]]
    if not med and not fin: return None
    if not med:
        if fin == 'ê' and not ini: return 'ê' + tone
        if ini in ('b', 'p', 'm', 'f') and fin == 'o': return ini + 'o' + tone
        return ini + fin + tone
    key = med + ('e' if fin == 'ê' else fin)
    if ini:
        r = WITH_INI.get(key)
        if r is None: return None
        if med == 'v' and ini not in JQX:
            r = {'u': 'v', 'ue': 've', 'uan': 'van', 'un': 'vn'}.get(r, r)
        return ini + r + tone
    r = NO_INI.get(key)
    return r + tone if r else None

# ---- zhuyin.txt ----
def load_txt():
    words, chars, sec, bad = [], [], None, []
    for ln, raw in enumerate(io.open(TXT, encoding='utf-8'), 1):
        line = raw.split('←')[0].strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('['):
            sec = line.strip('[]'); continue
        if '=' not in line:
            bad.append('%s:%d 沒有等號：%s' % ('zhuyin.txt', ln, line)); continue
        key, val = [x.strip() for x in line.split('=', 1)]
        if sec == '詞':
            parts = val.split()
            if len(parts) != len(key):
                bad.append('zhuyin.txt:%d 「%s」注音 %d 組、字 %d 個，對不起來'
                           % (ln, key, len(parts), len(key)))
                continue
            words.append((key, parts))
        elif sec == '字':
            if len(key) != 1:
                bad.append('zhuyin.txt:%d 單字表一行只能一個字：%s' % (ln, key)); continue
            chars.append((key, val))
    return words, chars, bad

# ---- 字型 ----
def font_readings(font):
    """{字: [讀音1, 讀音2, ...]}，index 0 是不加選擇子時的預設"""
    glyf, best = font['glyf'], font['cmap'].getBestCmap()
    uvs = [t for t in font['cmap'].tables if t.format == 14]
    sel = {s: dict(v) for s, v in uvs[0].uvsDict.items()} if uvs else {}
    def bopomofo_of(gname):
        g = glyf[gname]
        if not g.isComposite(): return None
        for c in g.components:
            if c.glyphName.startswith('z_'): return c.glyphName[2:]
        return None
    out = {}
    for cp, gname in best.items():
        ch = chr(cp)
        if not HAN.match(ch): continue
        r = bopomofo_of(gname)
        if not r: continue
        lst = [r]
        for i in range(1, VSN + 1):
            gn = sel.get(VS0 + i, {}).get(cp)
            if gn:
                r2 = bopomofo_of(gn)
                if r2: lst.append(r2)
        out[ch] = lst
    return out

def main(argv):
    if len(argv) < 2:
        sys.stderr.write(__doc__ + '\n'); return 2
    ttfs = argv[1:3]
    try:
        from fontTools.ttLib import TTFont
        from fontTools import subset
    except ImportError:
        sys.stderr.write('請先 pip install fonttools brotli\n'); return 2

    words, chars, bad = load_txt()
    if bad:
        sys.stderr.write('\n'.join(bad) + '\n'); return 1

    font = TTFont(ttfs[0])
    reads = font_readings(font)

    # ---- 對照 ----
    char_sel, miss, diff = {}, [], []
    for ch, zy in chars:
        py = to_pinyin(zy)
        if py is None:
            diff.append('%s=%s 這個注音我轉不出拼音，請檢查有沒有打錯' % (ch, zy)); continue
        lst = reads.get(ch)
        if not lst:
            miss.append('%s=%s 字型裡沒有這個字（會用原本的圓體顯示，沒有注音）' % (ch, zy)); continue
        if py == lst[0]: continue
        if py in lst:
            char_sel[ch] = lst.index(py)
        else:
            char_sel[ch] = -1          # -1 = 這個字不要標注音
            miss.append('%s=%s 字型只有 %s，不標注音' % (ch, zy, '／'.join(lst)))

    word_sel = {}
    for w, parts in words:
        row, used = [], False
        for ch, zy in zip(w, parts):
            py, lst = to_pinyin(zy), reads.get(ch)
            if py is None or not lst:
                row.append(0); continue
            if py == lst[0]: idx = 0
            elif py in lst:  idx = lst.index(py)
            else:
                idx = -1
                miss.append('%s 的「%s」=%s 字型只有 %s，不標注音' % (w, ch, zy, '／'.join(lst)))
            row.append(idx)
            if idx != char_sel.get(ch, 0): used = True
        if used: word_sel[w] = row

    for m in miss + diff:
        sys.stderr.write('注意：' + m + '\n')

    # ---- 寫進 index.html ----
    html = io.open(HTML, encoding='utf-8').read()
    def enc(i):                       # 0 = 不用選擇子；寫成 JS 的 \uXXXX 才不會變成看不見的字元
        if i == 0: return ''
        cp = VS0 if i < 0 else VS0 + i
        v = cp - 0x10000
        return '\\u%04X\\u%04X' % (0xD800 + (v >> 10), 0xDC00 + (v & 0x3FF))
    cs = ','.join(ch + enc(i) for ch, i in sorted(char_sel.items()))
    ws = ','.join(w + '=' + ''.join(c + enc(i) for c, i in zip(w, row))
                  for w, row in sorted(word_sel.items()))
    block = ('/* ZY-TABLE-START  這一段是 make-font.py 產生的，不要手改 */\n'
             '/* 字型自己會畫注音，這裡只放「預設讀音不對」的字：字後面那個看不見的\n'
             '   異體字選擇子（U+E01E0~5）會挑出正確的讀音，E01E0 代表不標注音 */\n'
             'const ZY_CHAR_SRC = "%s";\n'
             'const ZY_WORD_SRC = "%s";\n'
             '/* ZY-TABLE-END */') % (cs, ws)
    html, n = re.subn(r'/\* ZY-TABLE-START.*?/\* ZY-TABLE-END \*/', lambda m: block,
                      html, flags=re.S)
    if n != 1:
        sys.stderr.write('index.html 裡找不到 ZY-TABLE 標記\n'); return 1
    io.open(HTML, 'w', encoding='utf-8').write(html)

    # ---- 切子集 ----
    keep = set(HAN.findall(html)) | {c for c, _ in chars}
    for w, _ in words: keep |= set(w)
    codes = sorted({ord(c) for c in keep} | {VS0 + i for i in range(VSN + 1)})
    os.makedirs(FONTS, exist_ok=True)
    for ttf, tag in zip(ttfs, ('m', 'b')):
        out = os.path.join(FONTS, 'bpmf-gensen-%s.woff2' % tag)
        subset.main([ttf, '--output-file=' + out, '--flavor=woff2', '--no-hinting',
                     '--drop-tables+=vhea,vmtx,gasp', '--layout-features=',
                     '--name-IDs=0,1,2,3,4,5,6,7,13,14,16,17', '--notdef-outline',
                     '--unicodes=' + ','.join('U+%04X' % c for c in codes)])
        print('字集 %d 字 → %s（%.0f KB）'
              % (len(keep), os.path.relpath(out, HERE), os.path.getsize(out) / 1024.0))
    print('要加選擇子的字 %d 個、詞 %d 個' % (len(char_sel), len(word_sel)))
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
