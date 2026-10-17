package patch.fn;

/** Stand-in for java.util.function.BiFunction (API 24); only the abstract method. */
public interface BiFunction<T, U, R> {
    R apply(T t, U u);
}
