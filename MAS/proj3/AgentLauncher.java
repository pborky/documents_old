package massim.agent.implementation;

import massim.agent.framework.AbstractDamaSyncAgent;

import java.util.HashMap;
import java.util.LinkedList;

/**
 * Launcher of the agents in the simulation
 */
public class AgentLauncher {

    static LinkedList<AbstractDamaSyncAgent> agents = new LinkedList<AbstractDamaSyncAgent>();
    static HashMap<String, Integer> usernamesIDs = new HashMap<String, Integer>();
    static HashMap<Integer, String> IDsUsernames = new HashMap<Integer, String>();

    /**
     * Return number ID (priority) of the agent
     * 
     * @param un User name
     * @return Number ID
     */
    public static Integer username2ID(String un) {
        return usernamesIDs.get(un);
    }

    /**
     * Return username of the agent with a given number ID (priority)
     * 
     * @param id Number ID (priority)
     * @return User name
     */
    public static String ID2username(Integer id) {
        return IDsUsernames.get(id);
    }

    /**
     * Main method
     */
    public static void main(String[] args) {

        if (args.length != 1) {

            // number of agents parameter is missing
            System.out.println("Parameter missing!\nUSAGE: AgentLauncher <numberOfAgents>");
        } else {

            // get the number of agents
            String numberOfAgents = args[0];
            System.out.println("Number of agents: '" + numberOfAgents + "'");
            int n = Integer.parseInt(numberOfAgents);
            String[] usernames = {"", "b1", "a1", "b2", "a2", "b3", "a3", "b4", "a4"};

            // create agents
            for (int i = 1; i <= n; i++) {
                agents.add(new DamaSyncAgent(usernames[i], "1", i));
            }

            // run the agents
            LinkedList<Thread> threads = new LinkedList<Thread>();
            for (AbstractDamaSyncAgent agent : agents) {
                usernamesIDs.put(agent.getUsername(), agent.getPriority());
                IDsUsernames.put(agent.getPriority(), agent.getUsername());
                Thread thread = new Thread(agent);
                threads.add(thread);
                thread.start();
            }
            for (Thread thread : threads) {
                try { thread.join(); }
                catch (InterruptedException ex) {  ex.printStackTrace(); }
            }
            System.exit(0);
        }
    }
}
