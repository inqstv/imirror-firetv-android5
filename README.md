# iMirror for Fire TV Stick (Android 5.1 / API 22 port)

A patched build of [prat3ik/iMirror](https://github.com/prat3ik/iMirror) (v1.0.0, AirPlay receiver for Android TV)
that runs on an **Amazon Fire TV Stick Gen 2 ("tank", LineageOS Android 5.1.1, 32-bit ARM)**.
The upstream app targets newer Android; this repo contains the scripts that rewrite its decoded smali / native
libraries so it installs and works on API 22, plus fixes found while testing against iOS 27 / macOS 27.

Latest build: [`release/iMirror-android5-v16.apk`](release/iMirror-android5-v16.apk) (also attached to the GitHub release).

```
adb install -r iMirror-android5-v16.apk
```

## Status (tested on Fire TV Stick Gen 2 with an iPhone 15 Pro / MacBook)

| Feature | Status |
|---|---|
| iPhone / iPad screen mirroring | Works |
| MacBook screen mirroring | Works (1080p60 can lag on this SoC) |
| Audio (ALAC, AAC-ELD) | Works |
| Photos app: pictures, and videos (via mirroring) | Works |
| Now Playing card with artwork; stays on screen while paused | Works (v16) |
| Pausing music keeps the AirPlay session alive | Works (v14) |
| TV remote -> phone (DACP): Play/Pause, Fast-forward = next track, Rewind = previous track | Works (v15) |
| In-app AirPlay buttons for *video URL* streaming (YouTube etc.) | **Not working.** iOS 27 uses an `/fp-setup2` handshake that no open-source receiver implements; use Screen Mirroring instead. The video-URL/HLS feature bits are therefore not advertised so iOS falls back to mirroring. |
| PIN pairing | Untested |
| Low-latency Mac mirroring | Partial (decoder falls behind at ~60 fps; a naive smaller queue froze the picture) |

See [`docs/NOTES.md`](docs/NOTES.md) for the technical findings and [`CHANGELOG.md`](CHANGELOG.md) for per-build changes.

## What the patches do

`scripts/patch_smali.py` takes the apktool-decoded upstream APK and:

* maps API 23+ calls to small shim classes (`shim/src/patch/*.java`), renames missing framework types
  (`LocaleList`, `ULocale`, `AudioTrack.Builder`, `Icon`, `BiFunction`), and removes interface default methods (dex 035)
* routes the app's silent Timber `Logger` to `logcat` (tag `iMirror`)
* `/fp-setup2` answers `421 Misdirected Request` (like UxPlay) instead of `501`
* raises the RTSP request body limit from 64 KiB to 4 MiB (iOS sends ~170 KB artwork/metadata bodies)
* clears the video-URL / HLS feature bits so iOS uses the mirroring + audio paths that work
* DACP: tolerant `iTunes_Ctrl_<id>` service-name match (case / leading zeros), FF/Rewind -> `nextitem`/`previtem`, key logging
* audio-only `TEARDOWN` (iOS pause) keeps the session and the Now Playing card
* `scripts/addhash.py` / `scripts/addstub.py` patch the prebuilt `libalac.so` / `libplayfair.so`: add a SysV `DT_HASH`
  table (Android 5.1's linker ignores GNU hash only) and stub the missing `__register_atfork`

## Rebuilding

The scripts expect this layout (paths are hard-coded; edit the constants at the top of the scripts to relocate):

```
/home/claude/work/decoded   apktool d of the upstream armeabi-v7a release APK (apk/armeabi-v7a in upstream), with
                            lib/armeabi-v7a/libalac.so + libplayfair.so already run through addhash.py + addstub.py
/home/claude/work/shim/src  this repo's shim/src
/home/claude/work/debug.jks debug keystore (alias key, pass android) - keep the SAME key between builds so `adb install -r` works
/home/claude/tools          android22.jar, apktool.jar (2.10.0), uber-apk-signer jar, dex-tools
```

Then `scripts/rebuild.sh <out.apk>`.

The signing keystore is intentionally **not** in this repo. Uninstall the app once if you switch signing keys.

## License

GPL-3.0, inherited from upstream (see [LICENSE](LICENSE) and the upstream
[NOTICE.md](https://github.com/prat3ik/iMirror/blob/main/NOTICE.md); the FairPlay `playfair` component makes GPL-3.0
mandatory). The corresponding source of the built APK is the upstream v1.0.0 source plus the patches in this repo.
This is an unofficial modification and is not affiliated with the upstream author.
