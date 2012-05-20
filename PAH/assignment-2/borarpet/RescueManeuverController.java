package pah.borarpet;

import tacv.universe.environment.actuator.GoToWaypointCarActuator;
import tacv.universe.environment.sensor.CarSensor;
import tacv.util.Point;
import tacv.util.Vector;

import java.util.Random;

/**
 * Controller that manges car jam.
 */
public class RescueManeuverController {
    private boolean active;
    private GoToWaypointCarActuator actuator;
    private Point prevWaypoint;
    private Point currentWaypoint;
    private Point currentPos;
    private Point myWaypoint;
    private CarSensor sensor;
    private Random rng;

    private final double GO_BACK_BY = 10;
    private final double FUZZ = 10;
    private final double SPEED = 30;

    /**
     * constructor creates controller class and needs som APIs.
     * @param actuator car actuator
     * @param sensor car sensor
     * @param rng random numer genereator
     */
    public RescueManeuverController(GoToWaypointCarActuator actuator, CarSensor sensor, Random rng) {
        this.actuator = actuator;
        this.sensor = sensor;
        myWaypoint = null;
        this.rng = rng;
    }

    /**
     * If the rescue is active.
     * @return true if rescue is in progress
     */
    public boolean isActive() {
        return active;
    }

    /**
     * Activates rescue based on points of current path segment
     * @param prev passed path point
     * @param current next path point to be reached
     */
    public void activate(Point prev, Point current) {
        Logging.warn(this, "Rescue maneuver activated.");
        active = true;
        prevWaypoint = prev;
        currentWaypoint = current;
        currentPos = sensor.senseMyPosition();
        returnBy(GO_BACK_BY, FUZZ, SPEED);
    }

    /**
     * reverts the car backwards
     * @param dist ammount to go back
     * @param fuzz the random spread on the dist and also to the sides
     * @param speed backward speed
     */
    private void returnBy(double dist, double fuzz, double speed) {
        Vector a = VectUtils.vectProjection(prevWaypoint, currentPos, prevWaypoint, currentWaypoint );
        double side = (.5-rng.nextDouble())*fuzz;
        double direct = dist + (.5-rng.nextDouble())*fuzz;
        a = VectUtils.shorten(a, direct, side);
        a.add(prevWaypoint);
        myWaypoint = new Point(a);
        actuator.actGoToWaypoint(myWaypoint, (float)speed, false);
    }

    /**
     * return to normal
     */
    public void deactivate() {
        Logging.info(this, "Rescue maneuver deactivated.");
        active = false;
        myWaypoint = null;
    }

    /**
     * Called to check if any progress occured. If not new random path point is generated
     * @param velocity detected velocity (should be >1)
     */
    public void timeoutCallback(float velocity) {
        if (Math.abs(velocity) < 1) {
            // replan waypoint
            currentPos = sensor.senseMyPosition();
            returnBy(GO_BACK_BY, FUZZ, SPEED);
        }
    }

    /**
     * Called if car reaches the waypoint. If so we can deactivate.
     * @param wayPoint reached waypoint
     */
    public void waypointCallback(Point wayPoint) {
        if (myWaypoint == null || myWaypoint.equals(wayPoint)) {
            deactivate();
        }
    }
}
