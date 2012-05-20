package pah;

import cz.agents.alite.vis.VisManager;
import cz.agents.alite.vis.element.Line;
import cz.agents.alite.vis.element.aggregation.LineElements;
import cz.agents.alite.vis.element.aggregation.PointElements;
import cz.agents.alite.vis.layer.VisLayer;
import cz.agents.alite.vis.layer.terminal.LineLayer;
import cz.agents.alite.vis.layer.terminal.PointLayer;
import pah.borarpet.Logging;
import pah.borarpet.VisibilityGraph2D;
import pah.borarpet.WaypointControl;
import tacv.universe.entity.PositionedEntity;
import tacv.universe.environment.AgentScoutEnvironment.AgentScoutEnvironmentHandler;
import tacv.universe.environment.actuator.GoToWaypointCarActuator;
import tacv.universe.environment.storage.PositionedEntityStorage;
import tacv.util.Point;
import tacv.vis.VisualInteractionLayer;
import tacv.vis.VisualPlanLayer;

import java.awt.*;
import java.util.*;
import java.util.List;

/**
 * Agent implements car planner based on visibilty graph.
 *
 * Visibility graph is built from the collision envelopes and from waypoints. For the envelopes the vertices of the
 * visibilty graph are set on the outside of the collision envlopes. Weight of edges of the visibility graph is set
 * to the euclidean distance plus penalty for diferences of the terain altitude. The penelty as the threshold diference
 * has been determined heauristically.
 *
 * The modified A* algorithm is used to determine best path. The G-heuritic value of next node in openset is
 * penalized if angle is sharp and collision envelope is nearby. Angle, distance of collision envelope and resulting
 * penalty is determined empirically.
 *
 * Rescue maneuver (if the car jam is detected) is based on the extra waypoint put in reverse direction on the original
 * way. The position is based on randomness and if the car is not moving backvards, waypoint is replaced with another
 * (still based on random). After reaching waypoint car original plan is resumed.
 *
 * The core of the controller is in class WaypointControl, and visibility graph is in VisibilityGraph2D. Rescue is
 * managed by class RescueManeuverController.
 */
public class BorarpetCar extends PahCarAgent{
    private WaypointControl control;
    private Random rng;
    private Set<CarReady> carReadySet;

    /**
     * Constructor creates cntroller WaypointControl and some visualisations.
     * @param name
     * @param handler
     */
    public BorarpetCar(String name, AgentScoutEnvironmentHandler handler) {
        super(name, handler);

        rng = handler.getRandom();

        control = new WaypointControl(
                new VisibilityGraph2D(
                        handler.getCollisionZone(),
                        handler.getMap().getStreetGraph().vertexSet(),
                        handler.getTerrain()),
                this.handler.addAction(GoToWaypointCarActuator.class, this),
                carSensor,
                alarmSensor,
                rng);

        VisManager.registerLayer(VisualInteractionLayer.create(new VisualInteractionLayer.VisualInteractionListener() {
            @Override
            public void interact(double x, double y) {
                clickOnMap((float) x, (float) y);
            }
        }));
        VisManager.registerLayer(PointLayer.create(new PointElements() {
            @Override
            public Iterable<? extends cz.agents.alite.vis.element.Point> getPoints() {
                return control.getWaypoints();
            }

            @Override
            public Color getColor() {
                return Color.RED;
            }

            @Override
            public int getStrokeWidth() {
                return 7;
            }
        }));
        VisManager.registerLayer(LineLayer.create(new LineElements() {
            @Override
            public Iterable<? extends Line> getLines() {
                return control.getPathLines();
            }

            @Override
            public Color getColor() {
                return Color.GREEN;
            }

            @Override
            public int getStrokeWidth() {
                return 2;
            }
        }));
        VisManager.registerLayer(LineLayer.create(new LineElements() {
            @Override
            public Iterable<? extends Line> getLines() {
                return control.getPathCurrentSegment();
            }

            @Override
            public Color getColor() {
                return Color.ORANGE;
            }

            @Override
            public int getStrokeWidth() {
                return 2;
            }
        }));
        
        control.registerGoalReachedEvent(new WaypointControl.GoalReachedEvent() {
            @Override
            public void goalReachedCallback() {
                ready();
            }
        });
        carReadySet = new HashSet<CarReady>();
    }

    @Override
    void submitPlan(List<Point> points) {

        Point from = carSensor.senseMyPosition();
        points.add(0, new Point(from.getX(), from.getY(), 0));

        control.addWaypoints(points);
    }

    @Override
    VisLayer getPlanLayer() {
        return VisualPlanLayer.create(
                new VisualPlanLayer.VisualPlanProvidingEntity() {
                    @Override
                    public String getName() {
                        return "BorarpetCar";
                    }

                    @Override
                    public VisualPlanLayer.VisualPlan getVisualPlan() {
                        return new VisualPlanLayer.VisualPlan(control.getPath());
                    }
                },
                new PositionedEntityStorage() {
                    @Override
                    public Map<String, ? extends PositionedEntity> getPositionedEntities() {
                        Map<String, PositionedEntity> map = new HashMap<String, PositionedEntity>();
                        map.put("BorarpetCar", new PositionedEntity() {
                            @Override
                            public Point getPosition() {
                                return carSensor.senseMyPosition();
                            }
                        });
                        return map;
                    }
                },
                new Color(191, 162, 136),
                1
        );
    }

    @Override
    protected void ready() {
        for (CarReady cb: carReadySet)  {
            cb.carReadyCallback();
        }
    }


    /**
     * Helper API to announce my car creator
     */
    public interface CarReady {
        void carReadyCallback();
    }

    /**
     * Helper API to announce my car creator
     */
    public boolean registerCarReadyCallback(CarReady carReady) {
        return carReadySet.add(carReady);
    }

    /**
     * Dummy but usefull callback to log the altitude of terain under click.
     * @param x
     * @param y
     */
    private void clickOnMap(float x, float y) {
        Logging.info(this, "Click on X = %f, Y = %f, alt = %f.", x, y, handler.getAltitude(x, y));
    }


}
