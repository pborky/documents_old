package pah.borarpet;

import cz.agents.alite.vis.element.Line;
import cz.agents.alite.vis.element.implemetation.LineImpl;
import tacv.universe.environment.actuator.GoToWaypointCarActuator;
import tacv.universe.environment.sensor.AlarmSensor;
import tacv.universe.environment.sensor.CarSensor;
import tacv.universe.environment.sensor.callback.AlarmCallback;
import tacv.universe.environment.sensor.callback.WaypointReachedCallback;
import tacv.util.Point;
import tacv.vis.VisualPlanLayer;

import java.util.*;

/**
 * controller
 */
public class WaypointControl {
    private GoToWaypointCarActuator actuator;
    private VisibilityGraph2D visibilityGraph;
    private List<Point> waypoints;
    private Map<Point,List<Point>> path;
    private int currentWaypoint;
    private int currentPathElement;
    private CarSensor sensor;
    private int jam;
    private AlarmSensor alarm;
    private Set<GoalReachedEvent> goalReachedSet;
    private RescueManeuverController rescue;

    private static final long ALARM_CALLBACK_DELAY = 200;

    /**
     * constructor takes some important APIs and creates some (e.g. RescueManeuverController)
     * @param graph visibility graph
     * @param goToWaypointCarActuator car actuator
     * @param carSensor car sensor
     * @param alarmSensor alarm sensor
     * @param rng random number generator
     */
    public WaypointControl(VisibilityGraph2D graph,
                           GoToWaypointCarActuator goToWaypointCarActuator,
                           CarSensor carSensor,
                           AlarmSensor alarmSensor,
                           Random rng) {
        alarm = alarmSensor;
        sensor = carSensor;
        actuator = goToWaypointCarActuator;
        visibilityGraph = graph;
        waypoints = new ArrayList<Point>();
        path = new HashMap<Point, List<Point>>();
        goalReachedSet = new HashSet<GoalReachedEvent>();
        rescue = new RescueManeuverController(actuator, sensor, rng);

        alarm.registerAlarmCallback(ALARM_CALLBACK_DELAY, getAlarmCallback());
        sensor.registerWaypointReachedCallback(getWaypointReachedCallback());
    }

    /**
     * Inteface for goal reached callback
     */
    public interface GoalReachedEvent {
        /**
         * callback is invoked if last waypoint in sequence is reached
         */
        void goalReachedCallback();
    }

    /**
     * register GoalReachedEvent callback
     * @param goalReached the callback to register
     * @return true if sucessfull
     */
    public boolean registerGoalReachedEvent(GoalReachedEvent goalReached) {
        return goalReachedSet.add(goalReached);
    }

    /**
     * unregister GoalReachedEvent callback
     * @param goalReached the callback to unregister
     * @return true if sucessfull
     */
    public boolean unregisterGoalReachedEvent(GoalReachedEvent goalReached) {
        return goalReachedSet.remove(goalReached);
    }

    /**
     * Gets callback for alarm event. After callback is invoked new callback is registered with delay returned by alarmCallback
     * method.
     * @return new instance of the AlarmCallback
     */
    public AlarmCallback getAlarmCallback() {
        return new AlarmCallback() {
            @Override
            public void senseAlarm(long simulationTime) {
                alarm.registerAlarmCallback(alarmCallback(simulationTime), getAlarmCallback());
            }
        };
    }

    /**
     * Gets callback for waypoint reached event. Method waypointReachedCallback is invoked by callback.
     * @return new instance of  the WaypointReachedCallback
     */
    public WaypointReachedCallback getWaypointReachedCallback() {
        return new WaypointReachedCallback() {
            @Override
            public void waypointReached(Point wayPoint) {
                waypointReachedCallback(wayPoint);
            }
        };
    }

    /**
     * Method to add new sequence of hte waypoints.
     * Waypoints are added to visibility graph and connections are created. Next the A* search is invoked and car`s goal
     * is set.
     * @param points sequence of the waypoints.
     */
    public void addWaypoints(List<Point> points) {
        this.waypoints.clear();
        this.path.clear();

        waypoints.addAll(points);

        visibilityGraph.addWaypoints(points);
        path.putAll(visibilityGraph.path(points));

        currentWaypoint = 0;
        while (path.get(waypoints.get(currentWaypoint)).size() == 0) {
            if (++currentWaypoint >= points.size()) {
                Logging.info(this, "No goal.");
                return;
            }
        }
        currentPathElement = 0;

        actuator.setVisualPlan(new VisualPlanLayer.VisualPlan(getPath()));
        act();
    }

    /**
     * Return the list of the waypoint for the visual layer. (RED dots)
     * @return waypoints
     */
    public List<Point> getWaypoints() {
        return new LinkedList<Point>(waypoints);
    }

    /**
     * Returns path - all vertices based on visibility graph.
     * @return path
     */
    public List<Point> getPath() {
        List<Point> result = new LinkedList<Point>();
        for (Point p : waypoints) {
            if (path.containsKey(p)) {
                if (path.get(p).size() == 0) {
                    result.add(p);
                } else {
                    result.addAll(path.get(p));
                }
            }
        }
        return result;
    }

    /**
     * Return path - GREEN lines connection all vertices.
     * @return path lines
     */
    public List<? extends Line> getPathLines() {
        List<Line> lines = new LinkedList<Line>();
        Iterator<Point> it = getPath().iterator();
        if (it.hasNext()) {
        Point prev = it.next();
            while (it.hasNext()) {
                Point next = it.next();
                lines.add(new LineImpl(prev, next));
                prev = next;
            }
        }
        return lines;
    }

    /**
     * Returs path lines for current segment (between two waypoints) that shows up in ORANGE.
     * @return current path lines
     */
    public List<? extends Line> getPathCurrentSegment() {
        List<Line> lines = new LinkedList<Line>();
        if (path != null
                && path.size() > 0
                && waypoints.size() > 0
                && waypoints.size() > currentWaypoint
                && path.containsKey(waypoints.get(currentWaypoint))) {
            Iterator<Point> it = path.get(waypoints.get(currentWaypoint)).iterator();
            if (it.hasNext()) {
                Point prev = (currentWaypoint>0)?waypoints.get(currentWaypoint-1):it.next();
                while (it.hasNext()) {
                    Point next = it.next();
                    lines.add(new LineImpl(prev, next));
                    prev = next;
                }
            }
        }
        return lines;
    }

    /**
     * Returns waypoint in plan by iterating from current waypoint by steps elements.
     * @param steps how many steps to do from current goal (negative value staps back)
     * @return waypoint relative to current
     */
    private Point waypoint(int steps)  {
        int i = currentPathElement;
        int j = currentWaypoint;
        while (steps > 0) {
            if (++i >= path.get(waypoints.get(j)).size()) {
                i = 0;
                if (++j >= waypoints.size()) {
                    return null;
                }
            }
            steps--;
        }
        while (steps < 0) {
            if (--i < 0) {
                if (--j < 0) {
                    return null;
                }
                i = path.get(waypoints.get(j)).size()-1;
            }
            steps++;
        }
        return (i == -1) ? waypoints.get(j) : path.get(waypoints.get(j)).get(i);

    }

    /**
     * Invoked when there is no more points on path. Halts the car and calls the callbacks.
     */
    private void goalReached() {
        Logging.info(this, "Goal reached.");
        halt();
        for (GoalReachedEvent cb : goalReachedSet) {
            cb.goalReachedCallback();
        }

    }

    /**
     * Callback that is called by provided engine when car reaches waypoint.
     * @param wayPoint point that has been reached
     */
    private void waypointReachedCallback(Point wayPoint) {
        if (rescue.isActive()) {
            rescue.waypointCallback(wayPoint);
            if (!rescue.isActive()) {
                jam = -20;
                // go to last active goal
                act();
            }
        } else {
            if (++currentPathElement >= path.get(waypoints.get(currentWaypoint)).size()) {
                currentPathElement = 0;

                if (++currentWaypoint >= waypoints.size()) {
                    goalReached();
                    return;
                }
                while (path.get(this.waypoints.get(currentWaypoint)).size() == 0) {
                    if (++currentWaypoint >= waypoints.size()) {
                        goalReached();
                        return;
                    }
                }
            }
            act();
        }
    }

    /**
     * This callback is called in regural manner and manages situations if car is jammed. Returning value is used to
     * delay next callback.
     * @param simulationTime time when event occured
     * @return dealy for next invocation
     */
    private long alarmCallback(long simulationTime) {

        if (sensor.senseSpeed() < 1) {
            if (rescue.isActive()) {
                rescue.timeoutCallback(sensor.senseSpeed());
                return 5*ALARM_CALLBACK_DELAY;
            } else {
                if (jam==0) {
                    jam = -10;
                    Point myPos = sensor.senseMyPosition();
                    Logging.warn(this, "Jam detected at X = %f, Y = %f.", myPos.getX(), myPos.getY());
                    rescue.activate(waypoint(-1), waypoint(0));
                    return 5*ALARM_CALLBACK_DELAY;
                } else {
                    jam++;
                    return ALARM_CALLBACK_DELAY;
                }
            }
        } else {
            if (rescue.isActive()) {
                rescue.timeoutCallback(sensor.senseSpeed());
            }
            return ALARM_CALLBACK_DELAY;
        }
    }

    /**
     * Halts the car.
     */
    private void halt() {
        actuator.actHalt();
    }

    /**
     * Navigates to next waypoint.
     */
    private void act() {
        actuator.actGoToWaypoint(path.get(this.waypoints.get(currentWaypoint)).get(currentPathElement), 40f, true);
    }


    private void checkNext() {
        Point current = waypoint(0);
        Point next = waypoint(1);
    }


}
