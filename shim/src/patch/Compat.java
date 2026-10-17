package patch;

import android.app.Activity;
import android.app.AppOpsManager;
import android.app.Notification;
import android.app.NotificationManager;
import android.content.ContentProviderClient;
import android.content.Context;
import android.content.pm.PackageManager;
import android.content.res.ColorStateList;
import android.content.res.Configuration;
import android.content.res.Resources;
import android.graphics.Paint;
import android.graphics.PorterDuff;
import android.graphics.drawable.Drawable;
import android.media.AudioTrack;
import android.media.MediaDescription;
import android.net.Uri;
import android.os.Handler;
import android.os.Looper;
import android.os.Process;
import android.view.View;
import android.view.WindowInsets;
import android.view.accessibility.AccessibilityNodeInfo;
import android.widget.CompoundButton;
import android.widget.FrameLayout;
import android.widget.PopupWindow;
import android.widget.RemoteViews;
import android.widget.TextView;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Locale;

/**
 * Fallbacks for Android 6.0-7.1 (API 23-25) methods that the app's build tool stopped guarding
 * with version checks. Every method here compiles against the Android 5.1 (API 22) class library.
 * Naming: static shims take the original receiver as their first argument.
 */
public final class Compat {
    private Compat() {
    }

    // ---- boxed hashCode statics (Java 8) ----
    public static int hashZ(boolean b) {
        return b ? 1231 : 1237;
    }

    public static int hashJ(long v) {
        return (int) (v ^ (v >>> 32));
    }

    public static int hashD(double d) {
        long bits = Double.doubleToLongBits(d);
        return (int) (bits ^ (bits >>> 32));
    }

    public static int hashI(int i) {
        return i;
    }

    // ---- Context / Resources ----
    public static int ctxGetColor(Context c, int id) {
        return c.getResources().getColor(id);
    }

    public static int resGetColor(Resources r, int id, Resources.Theme theme) {
        return r.getColor(id);
    }

    public static ColorStateList resGetColorStateList(Resources r, int id, Resources.Theme theme) {
        return r.getColorStateList(id);
    }

    public static int ctxCheckSelfPermission(Context c, String permission) {
        if (permission == null) {
            throw new IllegalArgumentException("permission is null");
        }
        return c.checkPermission(permission, Process.myPid(), Process.myUid());
    }

    public static Context ctxDeviceProtected(Context c) {
        return c;
    }

    private static final HashMap<Class<?>, String> SERVICES = new HashMap<Class<?>, String>();

    static {
        SERVICES.put(android.accounts.AccountManager.class, Context.ACCOUNT_SERVICE);
        SERVICES.put(android.app.ActivityManager.class, Context.ACTIVITY_SERVICE);
        SERVICES.put(android.app.AlarmManager.class, Context.ALARM_SERVICE);
        SERVICES.put(android.app.AppOpsManager.class, Context.APP_OPS_SERVICE);
        SERVICES.put(android.app.DownloadManager.class, Context.DOWNLOAD_SERVICE);
        SERVICES.put(android.app.KeyguardManager.class, Context.KEYGUARD_SERVICE);
        SERVICES.put(android.app.NotificationManager.class, Context.NOTIFICATION_SERVICE);
        SERVICES.put(android.app.SearchManager.class, Context.SEARCH_SERVICE);
        SERVICES.put(android.app.UiModeManager.class, Context.UI_MODE_SERVICE);
        SERVICES.put(android.app.WallpaperManager.class, Context.WALLPAPER_SERVICE);
        SERVICES.put(android.app.admin.DevicePolicyManager.class, Context.DEVICE_POLICY_SERVICE);
        SERVICES.put(android.app.job.JobScheduler.class, Context.JOB_SCHEDULER_SERVICE);
        SERVICES.put(android.bluetooth.BluetoothManager.class, Context.BLUETOOTH_SERVICE);
        SERVICES.put(android.content.ClipboardManager.class, Context.CLIPBOARD_SERVICE);
        SERVICES.put(android.content.RestrictionsManager.class, Context.RESTRICTIONS_SERVICE);
        SERVICES.put(android.content.pm.LauncherApps.class, Context.LAUNCHER_APPS_SERVICE);
        SERVICES.put(android.hardware.ConsumerIrManager.class, Context.CONSUMER_IR_SERVICE);
        SERVICES.put(android.hardware.SensorManager.class, Context.SENSOR_SERVICE);
        SERVICES.put(android.hardware.camera2.CameraManager.class, Context.CAMERA_SERVICE);
        SERVICES.put(android.hardware.display.DisplayManager.class, Context.DISPLAY_SERVICE);
        SERVICES.put(android.hardware.input.InputManager.class, Context.INPUT_SERVICE);
        SERVICES.put(android.hardware.usb.UsbManager.class, Context.USB_SERVICE);
        SERVICES.put(android.location.LocationManager.class, Context.LOCATION_SERVICE);
        SERVICES.put(android.media.AudioManager.class, Context.AUDIO_SERVICE);
        SERVICES.put(android.media.MediaRouter.class, Context.MEDIA_ROUTER_SERVICE);
        SERVICES.put(android.media.projection.MediaProjectionManager.class, Context.MEDIA_PROJECTION_SERVICE);
        SERVICES.put(android.media.session.MediaSessionManager.class, Context.MEDIA_SESSION_SERVICE);
        SERVICES.put(android.media.tv.TvInputManager.class, Context.TV_INPUT_SERVICE);
        SERVICES.put(android.net.ConnectivityManager.class, Context.CONNECTIVITY_SERVICE);
        SERVICES.put(android.net.nsd.NsdManager.class, Context.NSD_SERVICE);
        SERVICES.put(android.net.wifi.WifiManager.class, Context.WIFI_SERVICE);
        SERVICES.put(android.net.wifi.p2p.WifiP2pManager.class, Context.WIFI_P2P_SERVICE);
        SERVICES.put(android.nfc.NfcManager.class, Context.NFC_SERVICE);
        SERVICES.put(android.os.BatteryManager.class, Context.BATTERY_SERVICE);
        SERVICES.put(android.os.DropBoxManager.class, Context.DROPBOX_SERVICE);
        SERVICES.put(android.os.PowerManager.class, Context.POWER_SERVICE);
        SERVICES.put(android.os.UserManager.class, Context.USER_SERVICE);
        SERVICES.put(android.os.Vibrator.class, Context.VIBRATOR_SERVICE);
        SERVICES.put(android.os.storage.StorageManager.class, Context.STORAGE_SERVICE);
        SERVICES.put(android.print.PrintManager.class, Context.PRINT_SERVICE);
        SERVICES.put(android.telecom.TelecomManager.class, Context.TELECOM_SERVICE);
        SERVICES.put(android.telephony.TelephonyManager.class, Context.TELEPHONY_SERVICE);
        SERVICES.put(android.view.LayoutInflater.class, Context.LAYOUT_INFLATER_SERVICE);
        SERVICES.put(android.view.WindowManager.class, Context.WINDOW_SERVICE);
        SERVICES.put(android.view.accessibility.AccessibilityManager.class, Context.ACCESSIBILITY_SERVICE);
        SERVICES.put(android.view.accessibility.CaptioningManager.class, Context.CAPTIONING_SERVICE);
        SERVICES.put(android.view.inputmethod.InputMethodManager.class, Context.INPUT_METHOD_SERVICE);
        SERVICES.put(android.view.textservice.TextServicesManager.class, Context.TEXT_SERVICES_MANAGER_SERVICE);
    }

    public static Object ctxGetSystemService(Context c, Class<?> cls) {
        String name = SERVICES.get(cls);
        return name != null ? c.getSystemService(name) : null;
    }

    public static String ctxGetSystemServiceName(Context c, Class<?> cls) {
        return SERVICES.get(cls);
    }

    // ---- runtime permissions: Android 5.1 grants at install time ----
    public static boolean actShouldShowRationale(Activity a, String permission) {
        return false;
    }

    public static void actRequestPermissions(final Activity a, final String[] permissions, final int requestCode) {
        new Handler(Looper.getMainLooper()).post(new Runnable() {
            public void run() {
                int[] results = new int[permissions.length];
                PackageManager pm = a.getPackageManager();
                String pkg = a.getPackageName();
                for (int i = 0; i < permissions.length; i++) {
                    results[i] = pm.checkPermission(permissions[i], pkg);
                }
                try {
                    Method m = a.getClass().getMethod("onRequestPermissionsResult",
                            int.class, String[].class, int[].class);
                    m.invoke(a, Integer.valueOf(requestCode), permissions, results);
                } catch (Throwable ignored) {
                }
            }
        });
    }

    public static int appOpsNoteProxyOp(AppOpsManager m, String op, String pkg) {
        return 0; // MODE_ALLOWED
    }

    public static String appOpsPermissionToOp(String permission) {
        return null;
    }

    // ---- notifications ----
    public static boolean nmAreNotificationsEnabled(NotificationManager nm) {
        return true;
    }

    public static int nmGetImportance(NotificationManager nm) {
        return -1000; // IMPORTANCE_UNSPECIFIED
    }

    public static Notification.Builder nbSetSmallIcon(Notification.Builder b, Icon icon) {
        if (icon != null && icon.getType() == Icon.TYPE_RESOURCE) {
            b.setSmallIcon(icon.getResId());
        }
        return b;
    }

    public static Notification.Builder nbSetLargeIcon(Notification.Builder b, Icon icon) {
        if (icon != null) {
            android.graphics.Bitmap bm = icon.getBitmap();
            if (bm != null) {
                b.setLargeIcon(bm);
            }
        }
        return b;
    }

    public static Notification.Action.Builder nabCreate(Icon icon, CharSequence title, android.app.PendingIntent pi) {
        int res = (icon != null && icon.getType() == Icon.TYPE_RESOURCE) ? icon.getResId() : 0;
        return new Notification.Action.Builder(res, title, pi);
    }

    public static Notification.Builder nbSetCustomContentView(Notification.Builder b, RemoteViews rv) {
        return b.setContent(rv);
    }

    public static Notification.Builder nbSetCustomBigContentView(Notification.Builder b, RemoteViews rv) {
        return b;
    }

    public static Notification.Builder nbSetCustomHeadsUpContentView(Notification.Builder b, RemoteViews rv) {
        return b;
    }

    public static Notification.Builder nbSetRemoteInputHistory(Notification.Builder b, CharSequence[] h) {
        return b;
    }

    public static Notification.Action.Builder nabSetAllowGeneratedReplies(Notification.Action.Builder b, boolean allow) {
        return b;
    }

    // ---- misc framework ----
    public static void cpcClose(ContentProviderClient c) {
        c.release();
    }

    public static int audioWrite(AudioTrack t, byte[] data, int offset, int size, int writeMode) {
        return t.write(data, offset, size);
    }

    public static MediaDescription.Builder mdbSetMediaUri(MediaDescription.Builder b, Uri uri) {
        return b;
    }

    public static Uri mdGetMediaUri(MediaDescription d) {
        return null;
    }

    public static boolean aniIsContextClickable(AccessibilityNodeInfo n) {
        return false;
    }

    public static boolean aniIsImportantForAccessibility(AccessibilityNodeInfo n) {
        return true;
    }

    public static WindowInsets viewGetRootWindowInsets(View v) {
        return null;
    }

    public static int viewGetScrollIndicators(View v) {
        return 0;
    }

    public static void viewSetScrollIndicators(View v, int indicators) {
    }

    public static void viewSetScrollIndicators(View v, int indicators, int mask) {
    }

    public static void viewSetForeground(View v, Drawable d) {
        if (v instanceof FrameLayout) {
            ((FrameLayout) v).setForeground(d);
        }
    }

    public static boolean paintHasGlyph(Paint p, String s) {
        return true;
    }

    public static LocaleList paintGetTextLocales(Paint p) {
        Locale l = p.getTextLocale();
        return l == null ? LocaleList.getDefault() : new LocaleList(l);
    }

    public static LocaleList cfgGetLocales(Configuration c) {
        Locale l = c.locale;
        return l == null ? LocaleList.getDefault() : new LocaleList(l);
    }

    public static void cfgSetLocales(Configuration c, LocaleList list) {
        if (list != null && list.size() > 0) {
            c.setLocale(list.get(0));
        }
    }

    // ---- TextView ----
    public static void tvSetTextLocales(TextView tv, LocaleList list) {
        if (list != null && list.size() > 0) {
            tv.setTextLocale(list.get(0));
        }
    }

    public static int tvGetBreakStrategy(TextView tv) {
        return 0;
    }

    public static void tvSetBreakStrategy(TextView tv, int s) {
    }

    public static int tvGetHyphenationFrequency(TextView tv) {
        return 0;
    }

    public static void tvSetHyphenationFrequency(TextView tv, int f) {
    }

    public static ColorStateList tvGetCompoundDrawableTintList(TextView tv) {
        return null;
    }

    public static PorterDuff.Mode tvGetCompoundDrawableTintMode(TextView tv) {
        return null;
    }

    public static void tvSetCompoundDrawableTintList(TextView tv, ColorStateList tint) {
        Drawable[] ds = tv.getCompoundDrawables();
        for (int i = 0; i < ds.length; i++) {
            Drawable d = ds[i];
            if (d != null) {
                d.mutate().setTintList(tint);
            }
        }
    }

    public static void tvSetCompoundDrawableTintMode(TextView tv, PorterDuff.Mode mode) {
        Drawable[] ds = tv.getCompoundDrawables();
        for (int i = 0; i < ds.length; i++) {
            Drawable d = ds[i];
            if (d != null) {
                d.mutate().setTintMode(mode);
            }
        }
    }

    public static Drawable cbGetButtonDrawable(CompoundButton b) {
        try {
            Field f = CompoundButton.class.getDeclaredField("mButtonDrawable");
            f.setAccessible(true);
            return (Drawable) f.get(b);
        } catch (Throwable t) {
            return null;
        }
    }

    // ---- Drawable layout direction (hidden but present on 5.1) ----
    public static int drawableGetLayoutDirection(Drawable d) {
        try {
            Method m = Drawable.class.getDeclaredMethod("getLayoutDirection");
            m.setAccessible(true);
            return ((Integer) m.invoke(d)).intValue();
        } catch (Throwable t) {
            return 0;
        }
    }

    public static boolean drawableSetLayoutDirection(Drawable d, int dir) {
        try {
            Method m = Drawable.class.getDeclaredMethod("setLayoutDirection", int.class);
            m.setAccessible(true);
            m.invoke(d, Integer.valueOf(dir));
            return true;
        } catch (Throwable t) {
            return false;
        }
    }

    // ---- PopupWindow ----
    public static int pwGetMaxAvailableHeight(PopupWindow pw, View anchor, int yOffset, boolean ignoreBottomDecorations) {
        return pw.getMaxAvailableHeight(anchor, yOffset);
    }

    public static boolean pwGetOverlapAnchor(PopupWindow pw) {
        try {
            Method m = PopupWindow.class.getDeclaredMethod("getOverlapAnchor");
            m.setAccessible(true);
            return ((Boolean) m.invoke(pw)).booleanValue();
        } catch (Throwable t) {
            return false;
        }
    }

    public static void pwSetOverlapAnchor(PopupWindow pw, boolean overlap) {
        try {
            Method m = PopupWindow.class.getDeclaredMethod("setOverlapAnchor", boolean.class);
            m.setAccessible(true);
            m.invoke(pw, Boolean.valueOf(overlap));
        } catch (Throwable ignored) {
        }
    }

    public static int pwGetWindowLayoutType(PopupWindow pw) {
        try {
            Method m = PopupWindow.class.getDeclaredMethod("getWindowLayoutType");
            m.setAccessible(true);
            return ((Integer) m.invoke(pw)).intValue();
        } catch (Throwable t) {
            return 1002; // TYPE_APPLICATION_PANEL-ish default (TYPE_APPLICATION_SUB_PANEL)
        }
    }

    public static void pwSetWindowLayoutType(PopupWindow pw, int type) {
        try {
            Method m = PopupWindow.class.getDeclaredMethod("setWindowLayoutType", int.class);
            m.setAccessible(true);
            m.invoke(pw, Integer.valueOf(type));
        } catch (Throwable ignored) {
        }
    }

    public static void pwSetEnterTransition(PopupWindow pw, android.transition.Transition t) {
    }

    public static void pwSetExitTransition(PopupWindow pw, android.transition.Transition t) {
    }
}
