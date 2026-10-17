package patch;

import android.media.AudioAttributes;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;

/** Stand-in for android.media.AudioTrack.Builder (API 23), built on the API 21 AudioTrack constructor. */
public final class AudioTrackBuilder {
    private AudioAttributes mAttributes;
    private AudioFormat mFormat;
    private int mBufferSize = 0;
    private int mMode = AudioTrack.MODE_STREAM;
    private int mSessionId = AudioManager.AUDIO_SESSION_ID_GENERATE;

    public AudioTrackBuilder() {
    }

    public AudioTrackBuilder setAudioAttributes(AudioAttributes attributes) {
        if (attributes == null) {
            throw new IllegalArgumentException("Illegal null AudioAttributes argument");
        }
        mAttributes = attributes;
        return this;
    }

    public AudioTrackBuilder setAudioFormat(AudioFormat format) {
        if (format == null) {
            throw new IllegalArgumentException("Illegal null AudioFormat argument");
        }
        mFormat = format;
        return this;
    }

    public AudioTrackBuilder setBufferSizeInBytes(int bufferSizeInBytes) {
        if (bufferSizeInBytes <= 0) {
            throw new IllegalArgumentException("Invalid buffer size " + bufferSizeInBytes);
        }
        mBufferSize = bufferSizeInBytes;
        return this;
    }

    public AudioTrackBuilder setTransferMode(int mode) {
        if (mode != AudioTrack.MODE_STATIC && mode != AudioTrack.MODE_STREAM) {
            throw new IllegalArgumentException("Invalid transfer mode " + mode);
        }
        mMode = mode;
        return this;
    }

    public AudioTrackBuilder setSessionId(int sessionId) {
        mSessionId = sessionId;
        return this;
    }

    public AudioTrack build() {
        if (mAttributes == null) {
            mAttributes = new AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_MEDIA)
                    .setContentType(AudioAttributes.CONTENT_TYPE_UNKNOWN)
                    .build();
        }
        if (mFormat == null) {
            throw new UnsupportedOperationException("Cannot create AudioTrack without an AudioFormat");
        }
        int size = mBufferSize;
        if (size <= 0) {
            size = AudioTrack.getMinBufferSize(mFormat.getSampleRate(), mFormat.getChannelMask(), mFormat.getEncoding());
            if (size <= 0) {
                size = 4096;
            }
        }
        return new AudioTrack(mAttributes, mFormat, size, mMode, mSessionId);
    }
}
