package patch;

import android.content.Context;
import android.content.res.ColorStateList;
import android.graphics.Bitmap;
import android.graphics.PorterDuff;
import android.graphics.drawable.BitmapDrawable;
import android.graphics.drawable.Drawable;
import android.net.Uri;

/** Stand-in for android.graphics.drawable.Icon (API 23) on Android 5.1; keeps what the icon was made from. */
public final class Icon {
    public static final int TYPE_BITMAP = 1;
    public static final int TYPE_RESOURCE = 2;
    public static final int TYPE_DATA = 3;
    public static final int TYPE_URI = 4;
    public static final int TYPE_ADAPTIVE_BITMAP = 5;
    public static final int TYPE_URI_ADAPTIVE_BITMAP = 6;

    private final int mType;
    private Bitmap mBitmap;
    private String mResPackage;
    private int mResId;
    private byte[] mData;
    private int mDataOffset;
    private int mDataLength;
    private String mUriString;
    private ColorStateList mTintList;
    private PorterDuff.Mode mTintMode;

    private Icon(int type) {
        mType = type;
    }

    public static Icon createWithBitmap(Bitmap bitmap) {
        if (bitmap == null) {
            throw new IllegalArgumentException("Bitmap must not be null.");
        }
        Icon i = new Icon(TYPE_BITMAP);
        i.mBitmap = bitmap;
        return i;
    }

    public static Icon createWithAdaptiveBitmap(Bitmap bitmap) {
        if (bitmap == null) {
            throw new IllegalArgumentException("Bitmap must not be null.");
        }
        Icon i = new Icon(TYPE_ADAPTIVE_BITMAP);
        i.mBitmap = bitmap;
        return i;
    }

    public static Icon createWithResource(String resPackage, int resId) {
        if (resPackage == null) {
            throw new IllegalArgumentException("Resource package name must not be null.");
        }
        Icon i = new Icon(TYPE_RESOURCE);
        i.mResPackage = resPackage;
        i.mResId = resId;
        return i;
    }

    public static Icon createWithResource(Context context, int resId) {
        return createWithResource(context.getPackageName(), resId);
    }

    public static Icon createWithData(byte[] data, int offset, int length) {
        if (data == null) {
            throw new IllegalArgumentException("Data must not be null.");
        }
        Icon i = new Icon(TYPE_DATA);
        i.mData = data;
        i.mDataOffset = offset;
        i.mDataLength = length;
        return i;
    }

    public static Icon createWithContentUri(String uri) {
        if (uri == null) {
            throw new IllegalArgumentException("Uri must not be null.");
        }
        Icon i = new Icon(TYPE_URI);
        i.mUriString = uri;
        return i;
    }

    public static Icon createWithContentUri(Uri uri) {
        if (uri == null) {
            throw new IllegalArgumentException("Uri must not be null.");
        }
        return createWithContentUri(uri.toString());
    }

    public static Icon createWithAdaptiveBitmapContentUri(Uri uri) {
        if (uri == null) {
            throw new IllegalArgumentException("Uri must not be null.");
        }
        Icon i = new Icon(TYPE_URI_ADAPTIVE_BITMAP);
        i.mUriString = uri.toString();
        return i;
    }

    public int getType() {
        return mType;
    }

    public int getResId() {
        return mResId;
    }

    public String getResPackage() {
        return mResPackage;
    }

    public Uri getUri() {
        return mUriString == null ? null : Uri.parse(mUriString);
    }

    public Bitmap getBitmap() {
        return mBitmap;
    }

    public Icon setTintList(ColorStateList tint) {
        mTintList = tint;
        return this;
    }

    public Icon setTintMode(PorterDuff.Mode mode) {
        mTintMode = mode;
        return this;
    }

    public Drawable loadDrawable(Context context) {
        Drawable d = null;
        switch (mType) {
            case TYPE_BITMAP:
            case TYPE_ADAPTIVE_BITMAP:
                d = new BitmapDrawable(context.getResources(), mBitmap);
                break;
            case TYPE_RESOURCE:
                try {
                    Context c = context.getPackageName().equals(mResPackage)
                            ? context : context.createPackageContext(mResPackage, 0);
                    d = c.getResources().getDrawable(mResId);
                } catch (Throwable t) {
                    d = null;
                }
                break;
            case TYPE_DATA:
                try {
                    Bitmap b = android.graphics.BitmapFactory.decodeByteArray(mData, mDataOffset, mDataLength);
                    d = b == null ? null : new BitmapDrawable(context.getResources(), b);
                } catch (Throwable t) {
                    d = null;
                }
                break;
            default:
                d = null;
        }
        if (d != null) {
            if (mTintList != null) {
                d.mutate().setTintList(mTintList);
            }
            if (mTintMode != null) {
                d.mutate().setTintMode(mTintMode);
            }
        }
        return d;
    }
}
