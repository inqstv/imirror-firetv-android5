#!/usr/bin/env python3
"""v2: resolve through app class hierarchy; report refs absent in API22 but present in API25."""
import sys, os, re, json, collections
sys.path.insert(0, "/home/claude/scripts")
import importlib.util, zipfile, struct

def load_api(jar):
    spec = importlib.util.spec_from_file_location("a", "/home/claude/scripts/apiscan.py")
    src = open("/home/claude/scripts/apiscan.py").read().split("classes = {}")[0]
    ns = {}
    # reuse parse_class only
    exec(src.split("JAR, SMALI_ROOT, OUT")[0] + "\n" + "def parse_class" + src.split("def parse_class")[1], ns)
    classes = {}
    with zipfile.ZipFile(jar) as z:
        for nm in z.namelist():
            if nm.endswith(".class"):
                try:
                    c = ns["parse_class"](z.read(nm)); classes[c["name"]] = c
                except Exception: pass
    return classes

SMALI = sys.argv[1]
api22 = load_api("/home/claude/tools/android22.jar")
api25 = load_api("/home/claude/tools/android25.jar")

# app classes
app = {}
cls_re = re.compile(r"^\.class\s+(.*?)(L[^;]+;)\s*$")
for r, _, fs in os.walk(SMALI):
    for f in fs:
        if not f.endswith(".smali"): continue
        path = os.path.join(r, f)
        name = None; sup = None; ifs = []; methods = set(); fields = set()
        for line in open(path, encoding="utf-8", errors="replace"):
            if line.startswith(".class"): name = line.split()[-1][1:-1]
            elif line.startswith(".super"): sup = line.split()[-1][1:-1]
            elif line.startswith(".implements"): ifs.append(line.split()[-1][1:-1])
            elif line.startswith(".method"):
                m = re.search(r"(\S+)\((.*?)\)(\S+)\s*$", line.strip())
                if m: methods.add((m.group(1), "(" + m.group(2) + ")" + m.group(3)))
            elif line.startswith(".field"):
                m = re.search(r"\.field\s+(?:[a-z]+\s+)*([^:\s]+):", line)
                if m: fields.add(m.group(1))
        if name: app[name] = dict(super=sup, ifs=ifs, methods=methods, fields=fields, path=path)

def resolve(cn, name, desc, api, seen=None):
    """True/False/None(unknown)"""
    seen = seen if seen is not None else set()
    if cn in seen: return False
    seen.add(cn)
    if cn in app:
        c = app[cn]
        if (name, desc) in c["methods"]: return True
        for s in ([c["super"]] if c["super"] else []) + c["ifs"]:
            if resolve(s, name, desc, api, seen): return True
        return False
    c = api.get(cn)
    if c is None: return None
    if (name, desc) in c["methods"]: return True
    for s in ([c["super"]] if c["super"] else []) + c["ifs"]:
        if resolve(s, name, desc, api, seen): return True
    return False

inv = re.compile(r"(invoke-[a-z\-/]+)\s+\{[^}]*\},\s+(L[^;]+;)->([^(\s]+)(\([^)]*\)\S+)")
out = collections.defaultdict(set)
for cn, c in app.items():
    for ln, line in enumerate(open(c["path"], encoding="utf-8", errors="replace"), 1):
        m = inv.search(line)
        if not m: continue
        kind, cls, name, desc = m.groups()
        cn2 = cls[1:-1]
        if cn2.startswith("android/support/"): pass
        in_app_chain = cn2 in app
        r22 = resolve(cn2, name, desc, api22)
        if r22 is None or r22: continue
        r25 = resolve(cn2, name, desc, api25)
        if r25 is False: continue   # missing on 25 too -> guarded / absent anyway
        out[(kind, cls, name, desc)].add(cn)
res = [{"kind": k[0], "cls": k[1], "name": k[2], "desc": k[3], "owners": sorted(v)} for k, v in out.items()]
json.dump(res, open(sys.argv[2], "w"), indent=1)
print("distinct unresolved-on-22 method refs (present on 25):", len(res))
via_app = [r for r in res if r["cls"][1:-1] in app]
print("of which referenced through an app/androidx class:", len(via_app))
for r in via_app: print("  ", r["cls"], r["name"], r["desc"], "<-", r["owners"][:3])
