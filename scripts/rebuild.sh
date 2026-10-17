#!/bin/bash
# Full pipeline: shims -> smali -> patch -> assemble -> sign. Usage: rebuild.sh <out-name.apk>
set -e
export JAVA_TOOL_OPTIONS=""
W=/home/claude/work; T=/home/claude/tools; DX=$T/dex-tools-x/dex-tools-v2.4
cd $W/shim && rm -rf out classes.jar shim.dex shim_smali && mkdir out
javac -source 8 -target 8 -Xlint:-options -nowarn -bootclasspath $T/android22.jar -d out $(find src -name '*.java') 2>&1 | grep -v "Picked up" || true
jar cf classes.jar -C out .
$DX/d2j-jar2dex.sh -f -o shim.dex classes.jar 2>&1 | grep -E "rror|xception" || true
$DX/d2j-baksmali.sh -f -o shim_smali shim.dex 2>&1 | grep -E "rror|xception" || true
cd $W && python3 -I /home/claude/scripts/patch_smali.py
rm -f rebuilt.apk && java -jar $T/apktool.jar b -f -o $W/rebuilt.apk $W/build 2>&1 | grep -E "Built|rror|xception"
rm -rf signed4 && mkdir signed4
java -jar $T/uber.jar --apks rebuilt.apk --ks debug.jks --ksAlias key --ksPass android --ksKeyPass android --out signed4 --allowResign 2>&1 | grep -E "verified|Successfully|rror"
cp signed4/rebuilt-aligned-signed.apk /mnt/user-data/outputs/$1
ls -la /mnt/user-data/outputs/$1
