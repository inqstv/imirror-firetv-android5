#!/usr/bin/env python3
"""Rewrite decoded smali so it runs on Android 5.1 (API 22). Idempotent: always starts from a clean copy."""
import os, re, shutil, sys, collections

SRC = "/home/claude/work/decoded"
DST = "/home/claude/work/build"
SHIM = "/home/claude/work/shim/shim_smali"

if os.path.exists(DST):
    shutil.rmtree(DST)
shutil.copytree(SRC, DST, symlinks=True)
SMALI = os.path.join(DST, "smali")

# ---------------------------------------------------------------- 1. type renames (whole-descriptor, global)
GLOBAL_RENAMES = {
    "Landroid/os/LocaleList;": "Lpatch/LocaleList;",
    "Landroid/icu/util/ULocale;": "Lpatch/ULocale;",
    "Landroid/media/AudioTrack$Builder;": "Lpatch/AudioTrackBuilder;",
    "Landroid/graphics/drawable/Icon;": "Lpatch/Icon;",
}
# renames limited to the dd-plist package (m0/): BiFunction is used by the binary plist string parser
M0_RENAMES = {
    "Ljava/util/function/BiFunction;": "Lpatch/fn/BiFunction;",
}

# ---------------------------------------------------------------- 2. method call -> shim
# (class, name, desc, shim, original_is_static)
def E(cls, name, desc, shim, static=False):
    return ((cls, name, desc), (shim, static))

MAP = dict([
    E("Ljava/lang/Boolean;", "hashCode", "(Z)I", "hashZ", True),
    E("Ljava/lang/Long;", "hashCode", "(J)I", "hashJ", True),
    E("Ljava/lang/Double;", "hashCode", "(D)I", "hashD", True),
    E("Ljava/lang/Integer;", "hashCode", "(I)I", "hashI", True),
    E("Landroid/content/Context;", "getColor", "(I)I", "ctxGetColor"),
    E("Landroid/content/Context;", "getSystemService", "(Ljava/lang/Class;)Ljava/lang/Object;", "ctxGetSystemService"),
    E("Landroid/content/Context;", "getSystemServiceName", "(Ljava/lang/Class;)Ljava/lang/String;", "ctxGetSystemServiceName"),
    E("Landroid/content/Context;", "checkSelfPermission", "(Ljava/lang/String;)I", "ctxCheckSelfPermission"),
    E("Landroid/content/Context;", "createDeviceProtectedStorageContext", "()Landroid/content/Context;", "ctxDeviceProtected"),
    E("Landroid/content/res/Resources;", "getColor", "(ILandroid/content/res/Resources$Theme;)I", "resGetColor"),
    E("Landroid/content/res/Resources;", "getColorStateList", "(ILandroid/content/res/Resources$Theme;)Landroid/content/res/ColorStateList;", "resGetColorStateList"),
    E("Landroid/app/Activity;", "requestPermissions", "([Ljava/lang/String;I)V", "actRequestPermissions"),
    E("Landroid/app/Activity;", "shouldShowRequestPermissionRationale", "(Ljava/lang/String;)Z", "actShouldShowRationale"),
    E("Landroid/app/AppOpsManager;", "noteProxyOp", "(Ljava/lang/String;Ljava/lang/String;)I", "appOpsNoteProxyOp"),
    E("Landroid/app/AppOpsManager;", "noteProxyOpNoThrow", "(Ljava/lang/String;Ljava/lang/String;)I", "appOpsNoteProxyOp"),
    E("Landroid/app/AppOpsManager;", "permissionToOp", "(Ljava/lang/String;)Ljava/lang/String;", "appOpsPermissionToOp", True),
    E("Landroid/app/NotificationManager;", "areNotificationsEnabled", "()Z", "nmAreNotificationsEnabled"),
    E("Landroid/app/NotificationManager;", "getImportance", "()I", "nmGetImportance"),
    E("Landroid/app/Notification$Builder;", "setSmallIcon", "(Lpatch/Icon;)Landroid/app/Notification$Builder;", "nbSetSmallIcon"),
    E("Landroid/app/Notification$Builder;", "setLargeIcon", "(Lpatch/Icon;)Landroid/app/Notification$Builder;", "nbSetLargeIcon"),
    E("Landroid/app/Notification$Builder;", "setCustomContentView", "(Landroid/widget/RemoteViews;)Landroid/app/Notification$Builder;", "nbSetCustomContentView"),
    E("Landroid/app/Notification$Builder;", "setCustomBigContentView", "(Landroid/widget/RemoteViews;)Landroid/app/Notification$Builder;", "nbSetCustomBigContentView"),
    E("Landroid/app/Notification$Builder;", "setCustomHeadsUpContentView", "(Landroid/widget/RemoteViews;)Landroid/app/Notification$Builder;", "nbSetCustomHeadsUpContentView"),
    E("Landroid/app/Notification$Builder;", "setRemoteInputHistory", "([Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;", "nbSetRemoteInputHistory"),
    E("Landroid/app/Notification$Action$Builder;", "setAllowGeneratedReplies", "(Z)Landroid/app/Notification$Action$Builder;", "nabSetAllowGeneratedReplies"),
    E("Landroid/content/ContentProviderClient;", "close", "()V", "cpcClose"),
    E("Landroid/media/AudioTrack;", "write", "([BIII)I", "audioWrite"),
    E("Landroid/media/MediaDescription$Builder;", "setMediaUri", "(Landroid/net/Uri;)Landroid/media/MediaDescription$Builder;", "mdbSetMediaUri"),
    E("Landroid/media/MediaDescription;", "getMediaUri", "()Landroid/net/Uri;", "mdGetMediaUri"),
    E("Landroid/view/accessibility/AccessibilityNodeInfo;", "isContextClickable", "()Z", "aniIsContextClickable"),
    E("Landroid/view/accessibility/AccessibilityNodeInfo;", "isImportantForAccessibility", "()Z", "aniIsImportantForAccessibility"),
    E("Landroid/view/View;", "getRootWindowInsets", "()Landroid/view/WindowInsets;", "viewGetRootWindowInsets"),
    E("Landroid/view/View;", "getScrollIndicators", "()I", "viewGetScrollIndicators"),
    E("Landroid/view/View;", "setScrollIndicators", "(I)V", "viewSetScrollIndicators"),
    E("Landroid/view/View;", "setScrollIndicators", "(II)V", "viewSetScrollIndicators"),
    E("Landroid/view/View;", "setForeground", "(Landroid/graphics/drawable/Drawable;)V", "viewSetForeground"),
    E("Landroid/graphics/Paint;", "hasGlyph", "(Ljava/lang/String;)Z", "paintHasGlyph"),
    E("Landroid/graphics/Paint;", "getTextLocales", "()Lpatch/LocaleList;", "paintGetTextLocales"),
    E("Landroid/content/res/Configuration;", "getLocales", "()Lpatch/LocaleList;", "cfgGetLocales"),
    E("Landroid/content/res/Configuration;", "setLocales", "(Lpatch/LocaleList;)V", "cfgSetLocales"),
    E("Landroid/widget/TextView;", "setTextLocales", "(Lpatch/LocaleList;)V", "tvSetTextLocales"),
    E("Landroid/widget/TextView;", "getBreakStrategy", "()I", "tvGetBreakStrategy"),
    E("Landroid/widget/TextView;", "setBreakStrategy", "(I)V", "tvSetBreakStrategy"),
    E("Landroid/widget/TextView;", "getHyphenationFrequency", "()I", "tvGetHyphenationFrequency"),
    E("Landroid/widget/TextView;", "setHyphenationFrequency", "(I)V", "tvSetHyphenationFrequency"),
    E("Landroid/widget/TextView;", "getCompoundDrawableTintList", "()Landroid/content/res/ColorStateList;", "tvGetCompoundDrawableTintList"),
    E("Landroid/widget/TextView;", "getCompoundDrawableTintMode", "()Landroid/graphics/PorterDuff$Mode;", "tvGetCompoundDrawableTintMode"),
    E("Landroid/widget/TextView;", "setCompoundDrawableTintList", "(Landroid/content/res/ColorStateList;)V", "tvSetCompoundDrawableTintList"),
    E("Landroid/widget/TextView;", "setCompoundDrawableTintMode", "(Landroid/graphics/PorterDuff$Mode;)V", "tvSetCompoundDrawableTintMode"),
    E("Landroid/widget/CompoundButton;", "getButtonDrawable", "()Landroid/graphics/drawable/Drawable;", "cbGetButtonDrawable"),
    E("Landroid/graphics/drawable/Drawable;", "getLayoutDirection", "()I", "drawableGetLayoutDirection"),
    E("Landroid/graphics/drawable/Drawable;", "setLayoutDirection", "(I)Z", "drawableSetLayoutDirection"),
    E("Landroid/widget/PopupWindow;", "getMaxAvailableHeight", "(Landroid/view/View;IZ)I", "pwGetMaxAvailableHeight"),
    E("Landroid/widget/PopupWindow;", "getOverlapAnchor", "()Z", "pwGetOverlapAnchor"),
    E("Landroid/widget/PopupWindow;", "setOverlapAnchor", "(Z)V", "pwSetOverlapAnchor"),
    E("Landroid/widget/PopupWindow;", "getWindowLayoutType", "()I", "pwGetWindowLayoutType"),
    E("Landroid/widget/PopupWindow;", "setWindowLayoutType", "(I)V", "pwSetWindowLayoutType"),
    E("Landroid/widget/PopupWindow;", "setEnterTransition", "(Landroid/transition/Transition;)V", "pwSetEnterTransition"),
    E("Landroid/widget/PopupWindow;", "setExitTransition", "(Landroid/transition/Transition;)V", "pwSetExitTransition"),
])

INV = re.compile(r"^(\s*)invoke-(virtual|interface|static|direct)(/range)?\s+(\{[^}]*\}),\s+(L[^;]+;)->([^\s(]+)(\([^)]*\)\S+)\s*$")

# Static fields on AccessibilityNodeInfo.AccessibilityAction that only exist from API 23. AndroidX passes
# them to a constructor that already handles null (it builds its own action object), so read them as null.
MISSING_A11Y = {"ACTION_SHOW_ON_SCREEN", "ACTION_SCROLL_TO_POSITION", "ACTION_SCROLL_UP", "ACTION_SCROLL_LEFT",
                "ACTION_SCROLL_DOWN", "ACTION_SCROLL_RIGHT", "ACTION_CONTEXT_CLICK", "ACTION_SET_PROGRESS"}
SGET = re.compile(r"^(\s*)sget-object\s+([vp]\d+),\s+Landroid/view/accessibility/AccessibilityNodeInfo\$AccessibilityAction;->(ACTION_[A-Z_]+):")
a11y_count = 0

rename_count = collections.Counter()
call_count = collections.Counter()
files = []
for root, _, fs in os.walk(SMALI):
    for f in fs:
        if f.endswith(".smali"):
            files.append(os.path.join(root, f))

for path in files:
    rel = os.path.relpath(path, SMALI)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    orig = text
    for a, b in GLOBAL_RENAMES.items():
        if a in text:
            rename_count[a] += text.count(a)
            text = text.replace(a, b)
    if rel.startswith("m0" + os.sep):
        for a, b in M0_RENAMES.items():
            if a in text:
                rename_count[a] += text.count(a)
                text = text.replace(a, b)
    out = []
    for line in text.split("\n"):
        sm = SGET.match(line)
        if sm and sm.group(3) in MISSING_A11Y:
            line = f"{sm.group(1)}const/16 {sm.group(2)}, 0x0"
            a11y_count += 1
            out.append(line)
            continue
        m = INV.match(line)
        if m:
            indent, kind, rng, regs, cls, name, desc = m.groups()
            hit = MAP.get((cls, name, desc))
            if hit:
                shim, static = hit
                new_desc = desc if static else "(" + cls + desc[1:]
                line = f"{indent}invoke-static{rng or ''} {regs}, Lpatch/Compat;->{shim}{new_desc}"
                call_count[(cls, name, desc)] += 1
        out.append(line)
    text = "\n".join(out)
    if text != orig:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

# ---------------------------------------------------------------- 3. interface default methods (androidx.lifecycle ViewModelProvider.Factory)
U_C = """
.method public c(Ljava/lang/Class;)Landroidx/lifecycle/Q;
    .locals 1

    new-instance p1, Ljava/lang/UnsupportedOperationException;

    const-string v0, "Factory.create(String) is unsupported.  This Factory requires `CreationExtras` to be passed into `create` method."

    invoke-direct {p1, v0}, Ljava/lang/UnsupportedOperationException;-><init>(Ljava/lang/String;)V

    throw p1
.end method
"""
U_N = """
.method public n(Ljava/lang/Class;Lc0/c;)Landroidx/lifecycle/Q;
    .locals 0

    invoke-interface {p0, p1}, Landroidx/lifecycle/U;->c(Ljava/lang/Class;)Landroidx/lifecycle/Q;

    move-result-object p1

    return-object p1
.end method
"""
added = []
for path in files:
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    head = text.split(".method", 1)[0]
    if not re.search(r"^\.implements Landroidx/lifecycle/U;\s*$", head, re.M):
        continue
    if re.search(r"^\.class .*\binterface\b", head, re.M):
        continue
    has_c = re.search(r"^\.method [^\n]* c\(Ljava/lang/Class;\)Landroidx/lifecycle/Q;", text, re.M)
    has_n = re.search(r"^\.method [^\n]* n\(Ljava/lang/Class;Lc0/c;\)Landroidx/lifecycle/Q;", text, re.M)
    abstract = re.search(r"^\.class [^\n]*\babstract\b", head, re.M)
    add = ""
    if not has_c: add += U_C
    if not has_n: add += U_N
    if add:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("\n" + add)
        added.append((os.path.relpath(path, SMALI), bool(has_c), bool(has_n)))

# ---------------------------------------------------------------- 3b. Notification.Action.Builder(Icon, CharSequence, PendingIntent) constructor
# (a constructor can't be redirected like a method, so replace the helper's body with a factory call)
yv = os.path.join(SMALI, "y", "v.smali")
with open(yv, encoding="utf-8") as fh:
    t = fh.read()
pat = re.compile(
    r"new-instance v0, Landroid/app/Notification\$Action\$Builder;\s*(?:\.line[^\n]*\n\s*)*"
    r"invoke-direct \{v0, p0, p1, p2\}, Landroid/app/Notification\$Action\$Builder;-><init>"
    r"\(Lpatch/Icon;Ljava/lang/CharSequence;Landroid/app/PendingIntent;\)V")
t2, n = pat.subn(
    "invoke-static {p0, p1, p2}, Lpatch/Compat;->nabCreate(Lpatch/Icon;Ljava/lang/CharSequence;Landroid/app/PendingIntent;)Landroid/app/Notification$Action$Builder;\n\n"
    "    move-result-object v0", t)
print("Notification.Action.Builder constructor rewritten:", n)
with open(yv, "w", encoding="utf-8") as fh:
    fh.write(t2)

# ---------------------------------------------------------------- 3c. route the app's Timber-based Logger to logcat (release builds log nothing)
import re as _re
_lg = os.path.join(DST, "smali/dev/imirror/receiver/util/Logger.smali")
_t = open(_lg).read()
def _inj(m):
    return m.group(0) + '\n    const-string v0, "iMirror"\n    invoke-static {v0, p1}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I\n'
_t = _re.sub(r"\.method public final (?:d|e|i|v|w)\(Ljava/lang/String;(?:Ljava/lang/Throwable;)?\)V\n    \.locals \d+", _inj, _t)
open(_lg, "w").write(_t)

# ---------------------------------------------------------------- 3d. POST /fp-setup2 -> 421 Misdirected Request (as UxPlay does) instead of 501, which left iOS hanging
_rh = os.path.join(DST, "smali/dev/imirror/receiver/airplay/RtspHandler.smali")
_t = open(_rh).read()
_pat = _re.compile(r'(    const-string v4, "Not Implemented"\n)')
assert len(_pat.findall(_t)) == 1
_t = _pat.sub(lambda m: m.group(1) + '\n    const-string v5, "/fp-setup2"\n    invoke-virtual {v2, v5}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z\n    move-result v5\n    if-eqz v5, :imi_keep501\n    const/16 v3, 0x1a5\n    const-string v4, "Misdirected Request"\n    :imi_keep501\n', _t)
open(_rh, "w").write(_t)

# ---------------------------------------------------------------- 3e. RTSP request body limit 64 KiB -> 4 MiB (iOS sends ~170 KB artwork/metadata bodies; the app dropped the whole session)
_t = open(_rh).read()
_old = "    new-instance v1, Ldev/imirror/receiver/airplay/RtspRequestReader;\n\n    const/high16 v2, 0x10000\n"
if _old not in _t:
    _m = _re.search(r"(new-instance v1, Ldev/imirror/receiver/airplay/RtspRequestReader;\s+(?:\.line \d+\s+)*const/high16 v2, )0x10000", _t)
    assert _m, "RtspRequestReader ctor not found"
    _t = _t[:_m.start()] + _m.group(1) + "0x400000" + _t[_m.end():]
else:
    _t = _t.replace(_old, _old.replace("0x10000", "0x400000"))
open(_rh, "w").write(_t)

# ---------------------------------------------------------------- 3f. don't advertise AirPlay *video URL* / HLS (features bits 0 and 4): iOS 27 then starts the
# unsupported /server-info + /fp-setup2 video handshake for music/YouTube and stalls; without them it uses the audio + mirroring paths that work.
for _root, _d, _fs in os.walk(os.path.join(DST, "smali/dev/imirror")):
    for _f in _fs:
        if not _f.endswith(".smali"):
            continue
        _p = os.path.join(_root, _f)
        _t = open(_p).read()
        _n = _t.replace("0x5A7FFFF7,0x1E", "0x5A7FFFE6,0x1E").replace("0x1e5a7ffff7L", "0x1e5a7fffe6L")
        if _n != _t:
            open(_p, "w").write(_n)

# ---------------------------------------------------------------- 3h. DACP: tolerant service-name match + log every key the activity sees
_dl = os.path.join(DST, "smali/dev/imirror/receiver/airplay/DacpClient$startDiscovery$listener$1.smali")
_t = open(_dl).read()
_o = "invoke-static {v0, v1}, Lkotlin/jvm/internal/i;->a(Ljava/lang/Object;Ljava/lang/Object;)Z"
assert _t.count(_o) == 1
_t = _t.replace(_o, "invoke-static {v0, v1}, Lpatch/DacpMatch;->match(Ljava/lang/Object;Ljava/lang/Object;)Z")
open(_dl, "w").write(_t)

_ma = os.path.join(DST, "smali/dev/imirror/receiver/MainActivity.smali")
_t = open(_ma).read()
_m = _re.search(r"\.method public onKeyDown\(ILandroid/view/KeyEvent;\)Z\n    \.locals 2\n", _t)
assert _m
_t = _t[:_m.end()] + '\n    const-string v0, "iMirror"\n    invoke-static {p1}, Ljava/lang/String;->valueOf(I)Ljava/lang/String;\n    move-result-object v1\n    invoke-static {v0, v1}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I\n' + _t[_m.end():]
_t += """
.method public dispatchKeyEvent(Landroid/view/KeyEvent;)Z
    .locals 4

    invoke-virtual {p1}, Landroid/view/KeyEvent;->getKeyCode()I
    move-result v1
    invoke-virtual {p1}, Landroid/view/KeyEvent;->getAction()I
    move-result v2
    new-instance v3, Ljava/lang/StringBuilder;
    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V
    const-string v0, "dispatchKeyEvent code="
    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual {v3, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string v0, " action="
    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    const-string v1, "iMirror"
    invoke-static {v1, v0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I
    invoke-super {p0, p1}, Landroidx/appcompat/app/AppCompatActivity;->dispatchKeyEvent(Landroid/view/KeyEvent;)Z
    move-result v0
    return v0
.end method
"""
open(_ma, "w").write(_t)

# ---------------------------------------------------------------- 3i. iOS pauses audio by sending TEARDOWN for only stream 96; don't end the whole session (that dropped the AirPlay route
# and restarted mDNS). Keep the session alive so the phone can re-SETUP the audio stream on resume.
_t = open(_rh).read()
_re3 = _re.compile(r'(const-string v2, "TEARDOWN streams="(?:\s+\.line \d+)*\s+)(if-nez v1, :cond_3)')
assert len(_re3.findall(_t)) == 1, "teardown pattern"
_ins = """if-eqz v1, :imi_go
    invoke-interface {v0}, Ljava/util/Collection;->size()I
    move-result v3
    const/4 v4, 0x1
    if-ne v3, v4, :imi_go
    const/16 v3, 0x60
    invoke-static {v3}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v3
    invoke-interface {v0, v3}, Ljava/util/List;->contains(Ljava/lang/Object;)Z
    move-result v3
    if-eqz v3, :imi_go
    const/4 v1, 0x0
    :imi_go
    """
_t = _re3.sub(lambda m: m.group(1) + _ins + m.group(2), _t)
open(_rh, "w").write(_t)

# ---------------------------------------------------------------- 3j. Fire TV remote has FF/RW but no Next/Prev keys; iOS ignores DACP beginff/beginrew -> send nextitem/previtem instead
for _root, _d, _fs in os.walk(os.path.join(DST, "smali/dev/imirror")):
    for _f in _fs:
        if _f.endswith(".smali"):
            _p = os.path.join(_root, _f)
            _t = open(_p).read()
            _n = _t.replace('"beginff"', '"nextitem"').replace('"beginrew"', '"previtem"')
            if _n != _t:
                open(_p, "w").write(_n)

# ---------------------------------------------------------------- 3k. pausing music = TEARDOWN of audio stream 96 only; keep the Now Playing card (artwork/title) on screen instead of clearing it (screen went black)
_ar = os.path.join(DST, "smali/dev/imirror/receiver/airplay/AirPlayReceiver.smali")
_t = open(_ar).read()
_m = _re.search(r"\.method private final stopMirrorAudio\(\)V.*?\.end method", _t, _re.S)
assert _m
_body = _m.group(0)
_body2 = _body.replace("iput-boolean v0, p0, Ldev/imirror/receiver/airplay/AirPlayReceiver;->audioPlaying:Z", "nop")
_body2 = _body2.replace("invoke-direct {p0}, Ldev/imirror/receiver/airplay/AirPlayReceiver;->clearNowPlayingMetadata()V", "nop")
assert _body2 != _body
_t = _t[:_m.start()] + _body2 + _t[_m.end():]
open(_ar, "w").write(_t)

# 3g (30 fps hint + 30-frame queue) removed: the small queue froze the picture after an early frame drop (decoder waits for a keyframe the Mac rarely sends)

# ---------------------------------------------------------------- 4. shim classes
for root, _, fs in os.walk(SHIM):
    for f in fs:
        if f.endswith(".smali"):
            rel = os.path.relpath(os.path.join(root, f), SHIM)
            dst = os.path.join(SMALI, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(os.path.join(root, f), dst)

# ---------------------------------------------------------------- report
print("type renames:")
for k, v in rename_count.items(): print(f"  {v:4d}  {k}")
print("accessibility-action constants nulled:", a11y_count)
print("call sites rewritten to shims:", sum(call_count.values()), "across", len(call_count), "distinct methods")
unused = [k for k in MAP if k not in call_count]
print("mapping entries that matched nothing:", len(unused))
for k in unused: print("   ", k)
print("default-method copies added:")
for a in added: print("  ", a)
