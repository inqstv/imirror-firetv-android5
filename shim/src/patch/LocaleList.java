package patch;

import java.util.Locale;

/** Stand-in for android.os.LocaleList (API 24) on Android 5.1. Same method names/signatures the app uses. */
public final class LocaleList {
    private static final Locale[] NONE = new Locale[0];
    private static final LocaleList EMPTY = new LocaleList(NONE);

    private final Locale[] mList;

    public LocaleList(Locale... list) {
        if (list == null || list.length == 0) {
            mList = NONE;
        } else {
            Locale[] copy = new Locale[list.length];
            for (int i = 0; i < list.length; i++) {
                if (list[i] == null) {
                    throw new NullPointerException("list[" + i + "] is null");
                }
                copy[i] = list[i];
            }
            mList = copy;
        }
    }

    public Locale get(int index) {
        return (index >= 0 && index < mList.length) ? mList[index] : null;
    }

    public boolean isEmpty() {
        return mList.length == 0;
    }

    public int size() {
        return mList.length;
    }

    public int indexOf(Locale locale) {
        for (int i = 0; i < mList.length; i++) {
            if (mList[i].equals(locale)) {
                return i;
            }
        }
        return -1;
    }

    public String toLanguageTags() {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < mList.length; i++) {
            if (i > 0) {
                sb.append(',');
            }
            sb.append(mList[i].toLanguageTag());
        }
        return sb.toString();
    }

    public static LocaleList forLanguageTags(String languageTags) {
        if (languageTags == null || languageTags.length() == 0) {
            return EMPTY;
        }
        String[] tags = languageTags.split(",");
        Locale[] out = new Locale[tags.length];
        int n = 0;
        for (int i = 0; i < tags.length; i++) {
            String t = tags[i].trim();
            if (t.length() == 0) {
                continue;
            }
            out[n++] = Locale.forLanguageTag(t);
        }
        Locale[] exact = new Locale[n];
        System.arraycopy(out, 0, exact, 0, n);
        return new LocaleList(exact);
    }

    public static LocaleList getEmptyLocaleList() {
        return EMPTY;
    }

    public static LocaleList getDefault() {
        return new LocaleList(Locale.getDefault());
    }

    public static LocaleList getAdjustedDefault() {
        return getDefault();
    }

    public static void setDefault(LocaleList locales) {
        if (locales != null && locales.size() > 0) {
            Locale.setDefault(locales.get(0));
        }
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if (!(other instanceof LocaleList)) {
            return false;
        }
        Locale[] o = ((LocaleList) other).mList;
        if (o.length != mList.length) {
            return false;
        }
        for (int i = 0; i < mList.length; i++) {
            if (!mList[i].equals(o[i])) {
                return false;
            }
        }
        return true;
    }

    @Override
    public int hashCode() {
        int result = 1;
        for (int i = 0; i < mList.length; i++) {
            result = 31 * result + mList[i].hashCode();
        }
        return result;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < mList.length; i++) {
            if (i > 0) {
                sb.append(',');
            }
            sb.append(mList[i]);
        }
        sb.append(']');
        return sb.toString();
    }
}
