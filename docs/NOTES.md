# Technical notes

## Android 5.1 (API 22) constraints
* dex 035: no interface default/static methods, no API 23-25 framework calls without a shim.
* The bionic linker only reads `DT_HASH` (not just `DT_GNU_HASH`), and libc lacks `__register_atfork`.
  Fixed by rewriting `.gnu.hash` as a SysV hash and stubbing the symbol inside the executable segment.
* `adb screencap` returns an all-black frame on this stick; use `scrcpy` to see the screen.

## iOS 27 / macOS 27 AirPlay behaviour
* Video-URL / HLS casting (YouTube's AirPlay button) goes through `/server-info`, `/fp-setup`, `/fp-setup2`
  (+ `mlhls://` and FCUP for YouTube). `/fp-setup2` is not implemented by any open-source receiver (UxPlay answers 421).
  Clearing feature bits 0 and 4 in the mDNS/`/info` features (`0x5A7FFFF7,0x1E` -> `0x5A7FFFE6,0x1E`) makes iOS use
  Screen Mirroring (stream types 110 video / 96 audio), which works.
* Modern iOS also opens a second TCP connection for `/reverse` (PTTH 101); the app rejects second clients (not implemented).
* Audio: ALAC (ct=2) and AAC-ELD (ct=8) over RTP; pause = `TEARDOWN` of stream 96 only, resume = `SETUP`+`FLUSH`.
* The sender's `DACP-ID` / `Active-Remote` headers identify the phone's `iTunes_Ctrl_<id>` service; the TV remote
  controls playback with `GET /ctrl-int/1/<cmd>`. Note the DACP-ID can be 15 hex digits (leading zero dropped).

## Performance
* The stick's MediaTek AVC decoder struggles with 1080p60 from a Mac. `MirrorStreamServer` keeps a 90-frame queue and
  resyncs on the next IDR after a drop. Shrinking the queue froze the picture, so it is unchanged.

## Harmless log noise
`LeanbackAppCompatViewInflater` ClassNotFound, "Unknown permission ...", `AudioTrack::set : Exit`, MTK
"pcm_start fail ... Broken pipe", OMX BadParameter nBufferCount.
