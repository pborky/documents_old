package pah;

import cz.agents.alite.creator.CreatorFactory;
import tacv.universe.map.MapPosition;
import tacv.util.Point;

import java.util.LinkedList;
import java.util.List;
import java.util.Random;

public class MyCreator extends AbstractPahCarCreator {

    private BorarpetCar car;
    private Random rng;

    @Override
    public PahCarAgent getCarAgent() {
        car = new BorarpetCar("car", universe.getEnvironment().handler());
        rng = universe.getEnvironment().handler().getRandom();
        car.registerCarReadyCallback(new BorarpetCar.CarReady() {
            @Override
            public void carReadyCallback() {
                List<Point> points = new LinkedList<Point>();
                while (points.size() < 20) {
                    Point pt = new Point(1400 * rng.nextDouble() + 50, 1400 * rng.nextDouble() + 50, 0);
                    if (!universe.getEnvironment().handler().getCollisionZone().testPoint(pt)) {
                        points.add(pt);
                    }
                }
                car.submitPlan(points);
            }
        });
        return car;
    }

    public static void main(String[] args) {
        CreatorFactory.createCreator(new String[]{MyCreator.class.getName()}).create();
    }
}
