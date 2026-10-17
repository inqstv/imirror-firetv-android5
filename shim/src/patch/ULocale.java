package patch;

import java.util.Locale;

/** Stand-in for android.icu.util.ULocale (API 24); only what AndroidX ICUCompat calls. */
public final class ULocale {
    private final Locale mLocale;

    private ULocale(Locale l) {
        mLocale = l;
    }

    public static ULocale forLocale(Locale l) {
        return new ULocale(l == null ? Locale.getDefault() : l);
    }

    public static ULocale addLikelySubtags(ULocale u) {
        return u;
    }

    public String getScript() {
        return mLocale.getScript();
    }
}
