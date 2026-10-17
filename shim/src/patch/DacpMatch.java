package patch;

public final class DacpMatch {
    private DacpMatch() {}

    private static String norm(String s) {
        return s.toUpperCase().replaceFirst("^ITUNES_CTRL_", "").replaceFirst("^0+", "");
    }

    /** Replacement for Intrinsics.areEqual(foundServiceName, targetName): tolerant of case / leading zeros. */
    public static boolean match(Object found, Object want) {
        if (found == null || want == null) return false;
        String a = found.toString();
        String b = want.toString();
        android.util.Log.w("iMirror", "DACP service seen: " + a + " (want " + b + ")");
        return norm(a).equals(norm(b));
    }
}
