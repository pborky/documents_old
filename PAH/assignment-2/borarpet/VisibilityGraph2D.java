package pah.borarpet;

import cz.agents.alite.vis.element.Line;
import tacv.universe.world.CollisionZone;
import tacv.universe.world.Terrain;
import tacv.util.Point;

import javax.vecmath.Vector3d;
import java.util.*;

/**
 * Class for generation visibility graph and
 */
public class VisibilityGraph2D {
    
    Set<Point> vertices;
    Map<Point,Set<VisibilityConnection>> edges;
    CollisionZone collisionZones;
    Set<? extends Point> streetPoints;
    private Terrain terrain;

    public VisibilityGraph2D(
            CollisionZone collisionZone,
            Set<? extends Point> streetPoints,
            Terrain terrain) {
        vertices = new HashSet<Point>();
        edges = new HashMap<Point, Set<VisibilityConnection>>();
        collisionZones = collisionZone;
        this.terrain = terrain;
        this.streetPoints = streetPoints;
        buildGraph();
    }

    /**
     * Add waypoints and connect it with visible part of graph
     * @param waypoints waypoints to add
     */
    public void addWaypoints(Collection<Point> waypoints) {
        for (Point point : waypoints) {
            Point current = new Point(point);
            for (Point other : new HashSet<Point>(vertexSet())) {
                if (!collisionZones.testLine(current, other)) {
                    addEdge(current, other);
                }
            }
        }
    }

    /**
     * Add waypoint and connect it with visible part of graph
     * @param current waypoint to add
     */
    public void addWaypoint(Point current) {
        for (Point other : new HashSet<Point>(vertexSet())) {
            if (!collisionZones.testLine(current, other)) {
                addEdge(current, other);
            }
        }
    }

    /**
     * Add vetrex to a graph. If vertex is already there do nothing.
     * @param vertex vertex to add
     * @return true if succeeded
     */
    public boolean addVertex(Point vertex) {
        if (vertices.contains(vertex)) {
            return false;
        }
        vertices.add(vertex);
        edges.put(vertex, new HashSet<VisibilityConnection>());
        return true;
    }

    /**
     * Add edge determined by two nodes to a graph. First add both vertices then the create edge itself.
     * Do nothing if edge is already there.
     * @param from first node
     * @param to other node
     * @return true if succeeded
     */
    private boolean addEdge(Point from, Point to) {
        if (containsEdge(from, to)) {
            return false;
        }
        if (!containsVertex(from)) {
            addVertex(from);
        }
        if (!containsVertex(to)) {
            addVertex(to);
        }
        VisibilityConnection edge = new VisibilityConnection(from, to, terrain);
        edges.get(from).add(edge);
        edges.get(to).add(edge);
        return true;
    }

    /**
     * Get set of all vertices.
     * @return set of all vertices
     */
    public Set<Point> vertexSet() {
        return new HashSet<Point>(vertices);
    }

    /**
     * Check if edge determined by two nodes is in graph.
     * @param from first node
     * @param to other node
     * @return true if edge is there
     */
    public boolean containsEdge(Point from, Point to) {
        return !SetUtils.intersect(edges.get(from),edges.get(to)).isEmpty();
    }

    /**
     * Check if vertex is in graph.
     * @param vertex node to check
     * @return true if node is there
     */
    public boolean containsVertex(Point vertex) {
        return vertices.contains(vertex);
    }

    /**
     * Get all edges incident to given node.
     * @param vertex node to check
     * @return set of incident edges
     */
    public Set<VisibilityConnection> edgesOf(Point vertex) {
        return new HashSet<VisibilityConnection>(edges.get(vertex));
    }

    /**
     * Expand convex shape denoted by using vector math and add non-colliding points to a graph.
     * The ammount of expansion is determined by parameter scale.
     * @param shape list of points
     * @param scale ammont of expansion
     */
    private void expandShapeAdd(List<Point> shape, double scale) {
        for (int i = 0; i < shape.size(); i++) {
            // first vector
            Vector3d vec = new Vector3d(shape.get((i==0)?shape.size()-1:i-1));
            vec.sub(shape.get(i));
            vec.normalize();

            // second vector
            Vector3d vecB = new Vector3d(shape.get((i == shape.size()-1)?0:i+1));
            vecB.sub(shape.get(i));
            vecB.normalize();
            // sum vectors, negate, normalize and scale

            vec.add(vecB);
            vec.negate();
            vec.normalize();
            vec.scale(scale);
            // now we have direction and size so add the origin and add to vertex list
            vec.add(shape.get(i));
            Point point = new Point(vec);
            if (!collisionZones.testPoint(point)) {
                addVertex(point);
            }
        }
    }

    /**
     * Construct visbility graph based on waypoint collision zones and streen map. The vertices from waypoints,
     * collisionZones and streetMap are added to graph, next edges are added if line represented by edge is
     * not inside collision zone. Search over vertices is performed by breadth first manner.
     */
    private void buildGraph() {
        Logging.info(this, "Building visibility graph...");
        // add points as vertices
        for (ArrayList<Line> zone : collisionZones.getLines()) {
            List<Point> points = new LinkedList<Point>();
            for (Line line : zone) {
                points.add((Point)line.getTo());
            }
            expandShapeAdd(points, (points.size() < 5 )? 15:2);
        }
        /*for (Point p: streetPoints) {
            if (!collisionZones.testPoint(p)) {
                addVertex(p);
            }
        } */
        // open set closed set
        Set<Point> open = new HashSet<Point>();
        Set<Point> closed = new HashSet<Point>();
        Set<Point> searchable = new HashSet<Point>(this.vertexSet());
        open.add(SetUtils.removeOne(searchable));
        for (Point current = SetUtils.removeOne(searchable); !open.isEmpty(); current = SetUtils.removeOne(open)) {
            closed.add(current);
            searchable.remove(current);
            for (Point other: searchable) {
                if (        !current.equals(other) &&   // not same node
                            !containsEdge(current, other) && // same edge not present
                            !collisionZones.testLine(current,other)) {  // edge not in collision zone
                    addEdge(current,other);
                    if (!closed.contains(other)) {
                        // not explored yet
                        open.add(other);
                    }
                }
            }
        }
    }

    /**
     * Return the edges.
     * @return all edges in this graph.
     */
    public Set<VisibilityConnection> edgesSet() {
        Set<VisibilityConnection> set = new HashSet<VisibilityConnection>();
        for (Set<VisibilityConnection> e : edges.values()) {
            set.addAll(e);
        }
        return set;
    }

    /**
     * A* implementation. Returns shortest path between waypoints. The G heauristic is penalized based on function penalty.
     * @param waypoints point sequence
     * @return list of path points
     */
    public Map<Point,List<Point>> path(List<Point> waypoints) {
        Map<Point,List<Point>> res = new HashMap<Point, List<Point>>();

        if (waypoints.size() < 2) {
            // only starting node
            res.put(waypoints.get(0), new LinkedList<Point>());
            return res;
        }

        waypoints = new ArrayList<Point>(waypoints);
        Set<Point> waypointSet = new HashSet<Point>(waypoints);

        int currentWaypoint = 0;

        Map<Point,Double> g = new HashMap<Point, Double>();
        Map<Point,Double> h = new HashMap<Point, Double>();
        Map<Point,Point> cameFrom = new HashMap<Point, Point>();
        Set<Point> open = new HashSet<Point>();
        Set<Point> closed = new HashSet<Point>();
        
        Point from = waypoints.get(currentWaypoint);
        Point to = waypoints.get(++currentWaypoint);

        g.put(from,0.);

        h.put(from,from.distance(to));

        open.add(from);
        res.put(from, new LinkedList<Point>());

        Point prev = from;

        while (!open.isEmpty()) {
            double fMin = Double.MAX_VALUE;
            Point current = null;
            for (Point o : open) {
                double f = g.get(o)+h.get(o);
                if (f <= fMin) {
                    current = o;
                    fMin = f;
                }
            }
            prev = current;
            assert current != null;
            if (current.equals(to)) {
                // reconstruct best path
                res.put(prev, addPath(prev, from, cameFrom));
                currentWaypoint++;
                Logging.info(this, "Planning waypoint %d. \n", currentWaypoint);
                if (currentWaypoint < waypoints.size()) {
                    prev = cameFrom.get(current);
                    // continue search for next waypoint
                    open.clear();
                    closed.clear();
                    cameFrom.clear();
                    h.clear();
                    g.clear();
                    // 
                    from = current;
                    to = waypoints.get(currentWaypoint);
                    open.add(from);
                    g.put(from,0.);
                    h.put(from,from.distance(to));
                    cameFrom.put(from, prev);
                    closed.add(prev);
                    g.put(prev, 0.);
                    h.put(prev, 0.);
                    continue;
                } else {
                    // no more waypoints
                    return res;
                }
            }

            open.remove(current);
            closed.add(current);

            for (VisibilityConnection e: edgesOf(current)) {
                Point neighbor =  (e.getFrom().equals(current))? e.getTo():e.getFrom();

                if (waypointSet.contains(neighbor) && !neighbor.equals(to)) {
                    continue;
                }

                double tentativeG = g.get(current) + e.getWeight() + penalty(current, neighbor, cameFrom);

                if (!g.containsKey(neighbor) || tentativeG < g.get(neighbor)) {
                    g.put(neighbor,tentativeG);
                    cameFrom.put(neighbor, current);
                }

                if (closed.contains(neighbor)) {
                    continue;
                }

                if (!open.contains(neighbor) || tentativeG < g.get(neighbor)) {
                    h.put(neighbor, neighbor.distance(to));
                    open.add(neighbor);
                }
            }
        }

        res.put(prev, addPath(prev, from, cameFrom));
        return res;
    }

    /**
     * Auxiliary function to reconstruct and add a path segment to the waypoint.
     * @param to current waypoint
     * @param from past waypoint
     * @param cameFrom shortest paths
     * @return path between waypoints from and to
     */
    private List<Point> addPath(Point to, Point from, Map<Point, Point> cameFrom) {
        List<Point> result = new LinkedList<Point>();
        List<Point> path = new LinkedList<Point>();
        while (!to.equals(from)) {
            path.add(0, to);
            to = cameFrom.get(to);
        }
        result.addAll(path);
        return result;
    }

    /**
     * Penalize if the vector to next proposed vertice is unde sharp angle. Penalty is based on angle and on radius to
     * nearby collision envelope.
     * @param current actual vertex
     * @param next neighbour of current vertex
     * @param cameFrom map of the traversal
     * @return penalty value
     */
    private double penalty(Point current, Point next, Map<Point,Point> cameFrom) {
        if (!cameFrom.containsKey(current)) {
            return 0;
        }
        Vector3d vec1 = new Vector3d(current);
        vec1.sub(next);
        Point prev = cameFrom.get(current);
        Vector3d vec2 = new Vector3d(current);
        vec2.sub(prev);
        double angle = vec1.angle(vec2);

        if (vec2.length() < 15 && cameFrom.containsKey(prev)) {
            Vector3d vec3 = new Vector3d(prev);
            vec3.sub(cameFrom.get(prev));
            if (vec1.angle(vec3)<angle) {
                angle = vec1.angle(vec3);
            }
        }
        angle /= Math.PI;
        if (angle > .6) {
            return 0;
        }  else if (angle < .2) {
            if (collisionNearby(current, 12)) {
                return 1E5 - angle*(1E5-1E4)/.2;
            }
        } else if (angle < .4) {
            if (collisionNearby(current, 6)) {
                return 19E3-9E3*angle/2E-1;
            }
        } else {
            if (collisionNearby(current, 2.5)) {
                return 3E3 - angle*1E3/.2;
            }
        }
        return 0;
    }

    /**
     * Determine if collision is nearby. The circle is aproximated with decahedron.
     * @param point vertice to check
     * @param radius radius in which check
     * @return true if collision envelope interects with decahedron
     */
    private boolean collisionNearby(Point point, double radius) {
        final int TEST_POINTS = 10;

        Vector3d prev = new Vector3d(Math.cos(0), Math.sin(0), 0.);
        prev.scale(radius);

        for (double i = 1; i < TEST_POINTS; i ++) {
            double phi = 2*Math.PI*i/TEST_POINTS;
            Vector3d next = new Vector3d(Math.cos(phi), Math.sin(phi), 0.);
            next.scale(radius);
            Point a = new Point(point);
            a.add(prev);
            Point b = new Point(point);
            b.add(next);
            if (collisionZones.testLine(a, b)) {
                return true;
            }
            prev = next;
        }
        return false;
    }

}
