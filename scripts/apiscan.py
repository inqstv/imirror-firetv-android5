#!/usr/bin/env python3
"""Find framework/JDK references in smali that do not exist in a given android.jar (API 22)."""
import sys, os, re, zipfile, struct, json, collections

JAR, SMALI_ROOT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
PREFIXES = ("Landroid/", "Ljava/", "Ljavax/", "Ldalvik/", "Lorg/apache/http/", "Lorg/json/",
            "Lorg/w3c/", "Lorg/xml/", "Lorg/xmlpull/", "Ljunit/")


def parse_class(data):
    p = 8
    n = struct.unpack_from(">H", data, p)[0]; p += 2
    cp = [None] * n
    i = 1
    while i < n:
        t = data[p]; p += 1
        if t == 1:
            ln = struct.unpack_from(">H", data, p)[0]; p += 2
            cp[i] = ("utf8", data[p:p + ln].decode("utf-8", "replace")); p += ln
        elif t in (3, 4):
            p += 4
        elif t in (5, 6):
            p += 8; i += 1
        elif t in (7, 8, 16, 19, 20):
            cp[i] = ("ref", struct.unpack_from(">H", data, p)[0]); p += 2
        elif t in (9, 10, 11, 12, 17, 18):
            p += 4
        elif t == 15:
            p += 3
        else:
            raise ValueError("bad cp tag %d" % t)
        i += 1
    def utf(ix): return cp[ix][1]
    def cls(ix): return utf(cp[ix][1])
    acc, this, sup = struct.unpack_from(">HHH", data, p); p += 6
    ni = struct.unpack_from(">H", data, p)[0]; p += 2
    ifs = []
    for _ in range(ni):
        ifs.append(cls(struct.unpack_from(">H", data, p)[0])); p += 2
    def members():
        nonlocal p
        cnt = struct.unpack_from(">H", data, p)[0]; p += 2
        out = []
        for _ in range(cnt):
            a, nm, ds, ac = struct.unpack_from(">HHHH", data, p); p += 8
            for _ in range(ac):
                p += 2
                ln = struct.unpack_from(">I", data, p)[0]; p += 4 + ln
            out.append((a, utf(nm), utf(ds)))
        return out
    fields = members()
    methods = members()
    return dict(name=cls(this), super=cls(sup) if sup else None, ifs=ifs, acc=acc,
                methods={(n, d) for _, n, d in methods}, fields={n for _, n, _ in fields})


classes = {}
with zipfile.ZipFile(JAR) as z:
    for nm in z.namelist():
        if nm.endswith(".class"):
            try:
                c = parse_class(z.read(nm))
                classes[c["name"]] = c
            except Exception as e:
                pass
print("api classes loaded:", len(classes), file=sys.stderr)


def has_method(cn, name, desc, seen=None):
    seen = seen if seen is not None else set()
    if cn in seen: return False
    seen.add(cn)
    c = classes.get(cn)
    if not c: return None  # unknown class
    if (name, desc) in c["methods"]: return True
    for s in ([c["super"]] if c["super"] else []) + c["ifs"]:
        r = has_method(s, name, desc, seen)
        if r: return True
    # interfaces implicitly have Object methods
    return False if cn != "java/lang/Object" else False


def has_field(cn, name, seen=None):
    seen = seen if seen is not None else set()
    if cn in seen: return False
    seen.add(cn)
    c = classes.get(cn)
    if not c: return None
    if name in c["fields"]: return True
    for s in ([c["super"]] if c["super"] else []) + c["ifs"]:
        if has_field(s, name, seen): return True
    return False


inv = re.compile(r"invoke-[a-z\-/]+\s+\{[^}]*\},\s+(\[*L[^;]+;)->([^(\s]+)(\([^)]*\)\S+)")
fld = re.compile(r"\b[is](?:get|put)[a-z\-]*\s+[^,]+,\s*(?:[^,]+,\s*)?(L[^;]+;)->([^:\s]+):(\S+)")
clsref = re.compile(r"\b(?:new-instance|check-cast|instance-of|const-class)\s+[^,]+,\s*(L[^;]+;)")
sig_class = re.compile(r"(L(?:android|java|javax|dalvik)/[^;]+;)")

res = collections.defaultdict(list)  # smali file class -> list of (kind, ref, line)
missing_classes = collections.Counter()
for root, _, files in os.walk(SMALI_ROOT):
    for f in files:
        if not f.endswith(".smali"): continue
        path = os.path.join(root, f)
        owner = None
        with open(path, encoding="utf-8", errors="replace") as fh:
            for ln, line in enumerate(fh, 1):
                if owner is None and line.startswith(".class"):
                    owner = line.split()[-1]
                s = line.strip()
                m = inv.search(s)
                if m:
                    c, name, desc = m.group(1), m.group(2), m.group(3)
                    if c.startswith("[") or not c.startswith(PREFIXES) or c.startswith("Landroid/support/"): continue
                    cn = c[1:-1]
                    r = has_method(cn, name, desc)
                    if r is None:
                        res[owner].append(("class", c, ln)); missing_classes[c] += 1
                    elif not r:
                        res[owner].append(("method", f"{c}->{name}{desc}", ln))
                    continue
                m = fld.search(s)
                if m:
                    c, name = m.group(1), m.group(2)
                    if c.startswith(PREFIXES) and not c.startswith("Landroid/support/"):
                        r = has_field(c[1:-1], name)
                        if r is None:
                            res[owner].append(("class", c, ln)); missing_classes[c] += 1
                        elif not r:
                            res[owner].append(("field", f"{c}->{name}", ln))
                    continue
                m = clsref.search(s)
                if m:
                    c = m.group(1)
                    if c.startswith(PREFIXES) and not c.startswith("Landroid/support/") and c[1:-1] not in classes:
                        res[owner].append(("class", c, ln)); missing_classes[c] += 1

json.dump({k: v for k, v in res.items()}, open(OUT, "w"), indent=1)
tot = sum(len(v) for v in res.values())
print("classes with missing refs:", len(res), "| total missing refs:", tot)
kinds = collections.Counter(k for v in res.values() for k, _, _ in v)
print("by kind:", dict(kinds))
refs = collections.Counter(r for v in res.values() for _, r, _ in v)
print("distinct missing refs:", len(refs))
for r, n in refs.most_common(60):
    print(f"{n:4d}  {r}")
