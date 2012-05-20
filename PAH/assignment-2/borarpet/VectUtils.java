package pah.borarpet;


import tacv.util.Point;
import tacv.util.Vector;

/**
 * Helper utilites for vector math
 */
public class VectUtils {

    /**
     * Returns projection of vector a on vector b. Vectors are determined by two points (a1,a2) and (b1,b2).
     * @param a1 first point of vector a
     * @param a2 second point of vector a
     * @param b1 first point of vector b
     * @param b2 second point of vector b
     * @return projection
     */
    public static Vector vectProjection(Point a1, Point a2, Point b1, Point b2) {
        Vector a = new Vector(a2);
        a.sub(a1);
        Vector b = new Vector(b2);
        b.sub(b1);
        return vectProjection(a,b);
    }

    /**
     * Returns projection of vector a on vector b
     * @param a vector which to project
     * @param b vector to project on
     * @return projection
     */
    public static Vector vectProjection(Vector a, Vector b) {
        // compute (a \dot \hat{c})\hat{c} avoiding side effects
        b = new Vector(b);
        b.normalize();
        b.scale(a.dot(b));
        return b;
    }

    /**
     * Shorten the vector by ammount of the scale.
     * @param a  vector to shorten
     * @param scale amount of the shortage
     * @return new vector shortened
     */
    public static Vector shorten(Vector a, double scale) {
        Vector b = new Vector(a);
        b.normalize();
        b.negate();
        b.scale(scale);
        b.add(a);
        return b;
    }

    /**
     * Shorten the vector by ammount of the scale and with side offset that is perpendicular to vector a.
     * @param a vector to shorten
     * @param scale amount of the shortage
     * @param sideOffset side offset
     * @return new vector shortened
     */
    public static Vector shorten(Vector a, double scale, double sideOffset) {
        Vector b = new Vector(a);
        b.normalize();
        // perpendicular
        Vector c = new Vector(-b.getY(), b.getX(), b.getZ());
        c.scale(sideOffset);
        b.negate();
        b.scale(scale);
        b.add(a);
        b.add(c);
        return b;
    }
}
