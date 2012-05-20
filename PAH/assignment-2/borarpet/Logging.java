package pah.borarpet;


import java.io.PrintStream;
import java.util.Calendar;

/**
 * Class for managing standard output.
 */
public class Logging {

    final static private PrintStream out = System.out;

    enum Type {WARN, INFO, ERROR, DEBUG}

    public static void output (Type type, Class<?> caller, String fmt, Object... data) {
        String f = fmt.endsWith("\n") ? "%1$tF %1$tT [%2$s] (%3$s): %4$s" : "%1$tF %1$tT [%2$s] (%3$s): %4$s\n";
        out.printf(f,
                Calendar.getInstance(),
                caller.getName(),
                type.name(),
                String.format(fmt, data));
    }

    public static void info(String fmt, Object... data) {
        info(Logging.class, fmt, data);
    }

    public static void info(Class<?> caller, String fmt, Object... data) {
        output(Type.INFO, caller, fmt, data);
    }

    public static void info(Object caller, String fmt, Object... data) {
        info(caller.getClass(), fmt, data);
    }

    public static void warn(String fmt, Object... data) {
        info(Logging.class, fmt, data);
    }

    public static void warn(Object caller, String fmt, Object... data) {
        warn(caller.getClass(), fmt, data);
    }

    public static void warn(Class<?> caller, String fmt, Object... data) {
        output(Type.WARN, caller, fmt, data);
    }

    public static void debug(String fmt, Object... data) {
        info(Logging.class, fmt, data);
    }

    public static void debug(Object caller, String fmt, Object... data) {
        debug(caller.getClass(), fmt, data);
    }

    public static void debug(Class<?> caller, String fmt, Object... data) {
        output(Type.DEBUG, caller, fmt, data);
    }

    public static void error(String fmt, Object... data) {
        info(Logging.class, fmt, data);
    }

    public static void error(Object caller, String fmt, Object... data) {
        error(caller.getClass(), fmt, data);
    }

    public static void error(Class<?> caller, String fmt, Object... data) {
        output(Type.ERROR, caller, fmt, data);
    }

}
