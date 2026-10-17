# Changelog (Fire TV / API 22 port builds)

* **v16** - Pausing music keeps the Now Playing card (album art / title) on screen instead of going black.
* **v15** - Remote Fast-forward / Rewind send next / previous track (Fire TV remote has no Next/Prev keys).
* **v14** - iOS pause (`TEARDOWN` of the audio stream only) no longer ends the AirPlay session; resume re-adds the stream.
* **v13** - Logs every key event seen by the activity; tolerant DACP service-name matching.
* **v12** - Reverted the 30 fps hint / small queue experiment (it froze the picture). Behaves like v10.
* **v10** - `/fp-setup2` -> 421, 4 MiB RTSP body limit, video-URL/HLS feature bits cleared.
* **v9** - RTSP request body limit raised (fixes audio sessions killed by large artwork/metadata requests).
* **v7** - Logger forwarded to logcat.
* **v6** - `__register_atfork` stub for `libalac.so` / `libplayfair.so`.
* **v5** - SysV `DT_HASH` added to the native libs (Android 5.1 linker).
* **v2-v4** - API 22 compatibility: shims for API 23+ calls, dex 035, locale/notification fixes.
