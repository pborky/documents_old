package massim.agent.implementation;

import massim.agent.framework.AbstractDamaSyncAgent;
import massim.agent.framework.MessageContent;
import massim.agent.framework.Pair;
import org.w3c.dom.Element;

import java.util.*;

import static java.lang.Math.abs;

public class DamaSyncAgent extends AbstractDamaSyncAgent {


    private final boolean   SEND_TARGET_REACHED_MESSAGES = true; // send the Ok(0,0) and NG(0,0) messages if local solution reached
    private final int       GLOBAL_SOLUTION_STEPS = 350; // terminate agent after certain amount of inactivity
    private final int       LOCAL_SOLUTION_STEPS = 40; // mark bTargetReached after certain amount of inactivity
    public final Integer    SLEEP_TO_SLOW_DOWN = 500; //Sleep time for the agent's control loop
    public final Integer    SLEEP_BEFORE_INBOX_READ = 50; //  we wait for other messages to read them in the right order

    // data
    public Boolean bSimFinished = false; //Simulation has finished
    public Boolean bTargetReached = false; // We have reached target destination
    public Boolean bInitialized = false; //Initialization has been done

    private long lastActivityStep; // step when last moved or received message
    private long lastNGReceveStep; // step when nogood hes been received
    private Map<Integer,Pair<Integer,Integer>> agentView; // agent view
    private Map<Integer,Boolean> otherTargetsReached; // agent view (bTargetReached flag of other agents)
    private Set<List<Pair<Integer,Integer>>> noGoods; // nogood list
    private Map<Integer,List<Pair<Integer,Integer>>> noGoodsOut; // nogoods awaiting for submission
    private Set<Integer> noGoodsConfirmation;   // agents awaiting Ok handle after sending nogoods
    public Integer targetX = -1;   // target X coordination
    private boolean sentOk; // send after reach targetX
    private int agentsCount; // number of agents (not known at begining)
    private boolean sendTargetReached; // send bTargetReached when changed ( OK:0,0 or NG:0,0 )

    // inherited
    /**
     * Dama agent constructor
     * 
     * @param username User name
     * @param password Password
     * @param priority Agent's priority (unique integer number)
     */
    public DamaSyncAgent(String username, String password, Integer priority) {
        super(username, password, priority);
    }

    // The main entry point into the agent deliberation loop
    @Override
    public void run() {
        run("localhost", 12300);
        runSyncAgent();
    }

    /**
     * Called as soon as agent logged in successfully
     */
    @Override
    public void processLogIn() {
        super.processLogIn();
    }

    /**
     * React on simulation start
     */
    @Override
    public void processSimulationStart(Element perception, long currenttime) {
        super.processSimulationStart(perception, currenttime);
    }

    /**
     * React on simulation end
     */
    @Override
    public void processSimulationEnd(Element perception, long currenttime) {
        super.processSimulationEnd(perception, currenttime);
        bSimFinished = true;
    }

    /**
     * Main control loop of the agent
     */
    @Override
    protected void runSyncAgent() {

        try {
            Boolean bSimEnd = false;
            while (!bSimEnd) { // until the end of the simulation

                // MAIN CONTROL LOOP //

                // initialization
                init();

                // perception of location, read messages, deliberate
                perceiveAndDeliberate();

                // slow down the control loop
                sleep(SLEEP_TO_SLOW_DOWN);

                // act (move/send messages)
                act();

                // check if it is not the end of the simulation
                boolean allTargetsReached = (bTargetReached && !sendTargetReached && getOtherTargetsReached());
                synchronized (this) {
                    bSimEnd = bSimFinished || allTargetsReached || ((getSimStep()- lastActivityStep) > GLOBAL_SOLUTION_STEPS);
                }
            }
        } finally {
            if (bTargetReached) {
                System.out.println(String.format("FINAL_POSITION_AGENT%d:%d,%d", priority, currentX, currentY ));
            }
        }
    }

    // my
    private void
    init() {
        if (!bInitialized) {
            //////////////////////////////
            targetX = (new Random (System.currentTimeMillis())).nextInt(priority)+1;
            sentOk = false;
            agentView = new HashMap<Integer, Pair<Integer,Integer>>();
            otherTargetsReached = new HashMap<Integer, Boolean>();
            noGoods = new HashSet<List<Pair<Integer,Integer>>>();
            noGoodsOut = new HashMap<Integer, List<Pair<Integer,Integer>>>();
            noGoodsConfirmation = new HashSet<Integer>();
            setAgentsCount(priority); // update the value upon receiving Ok? messages
            //////////////////////////////

            // initialization is done

            bInitialized = true;
        }
    }

    private void
    perceiveAndDeliberate() {

        // LOCATION //
        // Position of the agent is automatically stored in variables currentX and currentY
        //System.out.println("PERCEPTION of agent" + priority + ": step #" + getSimStep() + " currentX:" + currentX + " currentY:" + currentY);

        // READ NEW MESSAGES IN MAILBOX //
        if (!isEmptyInbox()) {
            // WAIT //
            // Wait for receiving other messages to be able to read them in the right order
            sleep(SLEEP_BEFORE_INBOX_READ);

            // PERCEIVE //
            // Pop a message from inbox
            MessageContent msg = popInboxMessage();

            // Debug info
            //System.out.println("RECEIVED by agent" + priority + " step=#" + getSimStep() + " timestamp=" + msg.getTimestamp() + " MSG='" + msg.toString() + "'");

            // DELIBERATE //
            processMsg(msg.toString());
            //////////////////////////////
        }
    }

    private void
    act() {

        // SEND MESSAGES //
        sendOks();
        sendNoGoods();

        // MOVE //
        if (currentX == targetX) {
            actNothing();
            if (getSimStep() > (lastActivityStep + LOCAL_SOLUTION_STEPS)) {
                setbTargetReached(true);
            }
        } else {
            lastActivityStep = getSimStep();
            if (currentX < targetX) {
                actRight();
            } else if (currentX > targetX) {
                actLeft();
            }
        }
        //////////////////////////////
    }

    private void
    setbTargetReached(boolean val) {
        if (val != bTargetReached) {
            sendTargetReached = true;
            if (val)
                System.out.format("LOG SET agent=%d step=#%d Target Reached\n", priority, getSimStep());
            else
                System.out.format("LOG SET agent=%d step=#%d Target NOT Reached\n", priority, getSimStep());
        }
        bTargetReached = val;
    }

    private void
    setAgentsCount(int val) {
        if (val > agentsCount) {
            agentsCount = val;
            System.out.format("LOG SET agent=%d step=#%d agentsCount=%d\n", priority, getSimStep(), agentsCount);
        }
    }

    private void
    processMsg(String msg) {
        String[] parts = msg.split(":");

        if (parts[0].equals("HandleOK")) {
            try {
                int alien = Integer.parseInt(parts[1]);
                String[] pos = parts[2].split(",");
                int alienX = Integer.parseInt(pos[0]);
                int alienY = Integer.parseInt(pos[1]);

                onReceiveOk(alien, new Pair<Integer,Integer>(alienX,alienY));

            } catch (NumberFormatException e) {
                e.printStackTrace();
            }
        } else if (parts[0].equals("HandleNoGood")) {
            try {
                int alien = Integer.parseInt(parts[1]);
                List<Pair<Integer,Integer>> noGood = new Vector<Pair<Integer,Integer>>(parts.length-2);
                for (int i = 2; i < parts.length; i++) {
                    String[] p = parts[i].split(",");
                    int noGoodX = Integer.parseInt(p[0]);
                    int noGoodY = Integer.parseInt(p[1]);
                    noGood.add(new Pair<Integer,Integer> (noGoodX, noGoodY));
                }
                onReceiveNoGood(alien, noGood);
            } catch (NumberFormatException e) {
                e.printStackTrace();
            }
        }
    }

    private void
    onReceiveOk(int alien, Pair<Integer,Integer> pos) {
        if (pos.equals(new Pair<Integer, Integer>(0,0))) {
            // agent <alien> is thinking that he reached the goal
            otherTargetsReached.put(alien,true);
            System.out.format("LOG SET agent=%d step=#%d Agent #%d Reached Target\n", priority, getSimStep(), alien);
        } else {
            // update count of agents
            setAgentsCount(alien);
            // update agent view
            agentView.put(alien, pos);
            if (!otherTargetsReached.containsKey(alien)) {
                otherTargetsReached.put(alien, false);
            }
        }
        // check
        checkView();
    }

    private void
    onReceiveNoGood(int alien, List<Pair<Integer,Integer>> noGood) {
        if (noGood.get(0).equals(new Pair<Integer, Integer>(-1,-1))) {
            bTargetReached = false;
            bSimFinished = true;
            lastActivityStep = getSimStep();
            if (priority == 1) System.out.println("FINAL_SOLUTION:NONE");
        } else if (noGood.get(0).equals(new Pair<Integer, Integer>(0,0))) {
            // agent <alien> is loose his goal
            otherTargetsReached.put(alien, false);
            System.out.format("LOG SET agent=%d step=#%d Agent #%d NOT Reached Target\n", priority, getSimStep(), alien);
        } else {
            noGoodsConfirmation.add(alien);
            noGoods.add(noGood);
            lastNGReceveStep = getSimStep();
            checkView();
        }
    }

    private Pair<Set<Integer>,Map.Entry<Integer,Pair<Integer,Integer>>>
    getConsistentSet() {
        Set<Integer> danger = new HashSet<Integer>();
        Set<Integer> consitent = new HashSet<Integer>();
        Map.Entry<Integer,Pair<Integer,Integer>> leastAlien = null;
        for (Map.Entry<Integer,Pair<Integer,Integer>> entry : agentView.entrySet()) {
            int alien = entry.getKey();
            int alienX = entry.getValue().getLeft();
            int alienY = entry.getValue().getRight();
            if (alien > priority) {
                int diffY = currentY - alienY;
                for (int k = -1 ; k <=1; k++) {
                    int d = alienX + k * diffY;
                    if (d >= 1 && d <= agentsCount) {
                        danger.add(d);
                        if (leastAlien == null || leastAlien.getKey() > alien) {
                            leastAlien = entry;
                        }
                    }
                }
            }
        }
        for (int i = 1; i <= agentsCount; i++) {
            boolean r = false;
            for (List<Pair<Integer,Integer>> noGood : noGoods) {
                r = true;
                for (Pair<Integer,Integer> p : noGood) {
                    if (p.getRight() == priority) {
                        r &= (p.getLeft() == i);
                    } else {
                        r &= agentView.containsKey(p.getRight()) &&  agentView.get(p.getRight()).equals(p);
                    }
                    if (!r) break;
                }
                if (r) break;
            }
            if (!danger.contains(i) && !r ) {
                consitent.add(i);
            }
        }
        return new Pair(consitent, leastAlien);
    }

    private boolean
    getOtherTargetsReached() {
        // have we all agents` reponses ?
        if (!(otherTargetsReached.size() + 1 == agentsCount) || !(agentsCount > 1)) {
            return false;
        }

        boolean all = true;
        for (boolean value : otherTargetsReached.values()) {
            all &= value;
        }

        return all;
    }

    private void
    checkView() {
        Pair<Set<Integer>,Map.Entry<Integer,Pair<Integer,Integer>>> r = getConsistentSet();

        Set<Integer> consitent = r.getLeft();
        Map.Entry<Integer,Pair<Integer,Integer>> leastAlien = r.getRight();

        if (!consitent.contains(currentX)) {
            lastActivityStep = getSimStep();
            if (bTargetReached) {
                setbTargetReached(false);
            }
            if (consitent.isEmpty()) {
                backTrack(leastAlien);
            } else {
                int x = Integer.MAX_VALUE;
                for (int i : consitent) {
                    if (abs(i - currentX) < abs(x - currentX)) {
                        x = i;
                    }
                }
                assert x != -1;
                targetX = x;
                sentOk = false;
            }
        }
    }

    private void
    backTrack(Map.Entry<Integer,Pair<Integer,Integer>> leastAlien) {
        if (leastAlien == null) {
            for (int i = 1; i <= agentsCount; i++) {
                if (i == priority) continue;
                noGoodsOut.put(i, null);
            }
            bSimFinished = true;
            setbTargetReached(false);
            if (priority == 1) System.out.println("FINAL_SOLUTION:NONE");
        } else {
            Vector<Pair<Integer,Integer>> set = new Vector<Pair<Integer, Integer>>();
            for (int i = leastAlien.getKey(); i <= agentsCount; i++) {
                if (agentView.containsKey(i)) {
                    set.add(agentView.get(i));
                }
            }
            noGoodsOut.put(leastAlien.getKey(), set);
            agentView.remove(leastAlien.getKey());
            checkView();
        }
    }

    private void
    sendOks() {
        if (currentX.equals(targetX)) {
            if (!sentOk) {
                sentOk = true;
                for (int i = priority-1; i > 0; i--) {
                    sendHandleOK(i);
                    Thread.yield();
                    noGoodsConfirmation.remove(i);
                }
                agentView.put(priority, new Pair<Integer, Integer>(currentX,currentY));
                System.out.println(String.format("CURRENT_POSITION_AGENT%d:%d,%d", priority, currentX, currentY ));
            } else if (!noGoodsConfirmation.isEmpty() && lastNGReceveStep +5 < getSimStep()) {
                // if for some odd reasons no response has been given
                for (Iterator<Integer> it = noGoodsConfirmation.iterator() ; it.hasNext(); ) {
                    int i = it.next();
                    it.remove();
                    sendHandleOK(i);
                    Thread.yield();
                }
            }
            if (sendTargetReached && bTargetReached && SEND_TARGET_REACHED_MESSAGES) {
                sendTargetReached = false;
                for (int i =1; i <= agentsCount; i++) {
                    if (i == priority) continue;
                    // this is ugly, but it provides faster termination of algorithm
                    // by commenting out this section algorithm still works, but takes a lot of time
                    // (agent terminates after 250 steps after last activity)
                    //
                    // this will send information to other agents that local solution hes been found
                    // agent terminates when all local solutions are found
                    /*       */
                    int x = currentX, y = currentY;
                    currentX = currentY = 0;
                    sendHandleOK(i);
                    currentX = x; currentY = y;
                    Thread.yield();
                }
            }
        }
    }

    private void
    sendNoGoods() {
        if (!noGoodsOut.isEmpty()) {
            for (Map.Entry<Integer, List<Pair<Integer, Integer>>> entry : noGoodsOut.entrySet()) {
                if (entry.getValue() == null) {
                    sendHandleNoGood(entry.getKey(), "-1,-1");
                } else {
                    boolean f = true;
                    StringBuilder s = new StringBuilder();
                    for (Pair<Integer,Integer> p : entry.getValue()) {
                        if (f) {
                            f = false;
                        } else {
                            s.append(':');
                        }
                        s.append(p.getLeft());
                        s.append(',');
                        s.append(p.getRight());
                    }
                    sendHandleNoGood(entry.getKey(), s.toString());
                }
                Thread.yield();
            }
            noGoodsOut.clear();
            if (sendTargetReached && !bTargetReached && SEND_TARGET_REACHED_MESSAGES) {
                sendTargetReached = false;
                for (int i =1; i <= agentsCount; i++) {
                    if (i == priority) continue;
                    sendHandleNoGood(i, "0,0");
                }
            }
        }
    }
}
