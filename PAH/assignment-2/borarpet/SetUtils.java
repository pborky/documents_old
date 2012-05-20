package pah.borarpet;


import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

public class SetUtils {    
    public static <U> Set<U> intersect(Set<U> a, Set<U> b) {
        return intersect(a,b,new HashSet<U>());
    }
    
    public static <U> Set<U> intersect(Set<U> a, Set<U> b, Set<U> c) {
        c.clear();
        if (a == null || b == null || a.isEmpty() || b.isEmpty()) {
            return c;
        }
        c.addAll(a);
        c.retainAll(b);
        return c;
    }
    
    public static <U> U removeOne(Set<U> set) {
        Iterator<U> it = set.iterator();
        if (it.hasNext()) {
            U result = it.next();
            it.remove();
            return result;
        } else {
            return null;
        }
    }
}
