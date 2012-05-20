package pah.borarpet;

import tacv.universe.world.Terrain;
import tacv.util.Point;
import tacv.util.Vector;

/**
 * Edge of the visibility graph. The weight includes terrain penalty.
 */
public class VisibilityConnection {
    private Point from;
    private Point to;
    private int hash = 0;
    private Terrain terrain;
    private double weight = 0;


    public VisibilityConnection(Point from, Point to, Terrain terrain) {
        this.from = from;
        this.to = to;
        this.terrain = terrain;
    }

    /**
     * Return the weight of the edge. It is euclidean distance and penalty function.
     * @return weight
     */
    public double getWeight() {
        if (weight == 0) {
            weight = to.distance(from) + terainPenalty();// + distancePenalty();
        }
        return weight;
    }
    
    @Override
    public int hashCode() {
        int h = hash;
        if (h == 0) {
            h = 31*h + from.hashCode();
            h = 31*h + to.hashCode();
            hash = h;
        }
        return h;
    }
    
    @Override
    public boolean equals(Object other) {
        return other instanceof VisibilityConnection &&
                ((VisibilityConnection) other).from.equals(from) &&
                ((VisibilityConnection) other).to.equals(to);
    }
    
    @Override
    public String toString() {
        return String.format("(%s : %s)", from.toString(), to.toString());
    }

    /**
     * one vertex of the edge
     * @return vertex
     */
    public Point getFrom() {
        return from;
    }

    /**
     * another vertex of the edge
     * @return  vertex
     */
    public Point getTo() {
        return to;
    }

    /**
     * Distance penalty is to eleiminate long distant edges
     * @return distance penalty
     */
    private double distancePenalty() {
        Vector vec1 = new Vector(from);
        vec1.sub(to);
        double dist = vec1.length();
        if (dist > 500) {
            return Math.pow(dist - 500, 1.5);
        }
        return 0;
    }

    /**
     * Penalty if edge goes through slope terrain.
     * @return terrain penalty
     */
    private double terainPenalty() {
        Vector dir = new Vector(to);
        dir.sub(from);
        double dist = dir.length();
        dir.normalize();
        dir.scale(10);

        double maxDiff = Double.MIN_VALUE;
        double prevAlt = terrain.getAltitude((float)from.getX(), (float)from.getY());
        for (Point point = new Point(from); point.distance(from) < dist; point.add(dir) ) {
            double  alt = terrain.getAltitude((float)point.getX(), (float)point.getY());

            if (Math.abs(alt-prevAlt) > maxDiff) {
                maxDiff = Math.abs(alt-prevAlt);
            }
        }
        return (maxDiff>20)?(maxDiff-20)*50:0;
    }
}
