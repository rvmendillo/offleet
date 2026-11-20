package common;

import java.util.ArrayList;
import java.util.List;

/** Graph node (clone-graph style problems). */
public class Node {
    public int val;
    public List<Node> neighbors;

    public Node() { this(0); }
    public Node(int val) { this.val = val; this.neighbors = new ArrayList<>(); }
    public Node(int val, List<Node> neighbors) { this.val = val; this.neighbors = neighbors; }

    public static Node of(List<Object> adj) {
        if (adj.isEmpty()) return null;
        List<Node> nodes = new ArrayList<>();
        for (int i = 0; i < adj.size(); i++) nodes.add(new Node(i + 1));
        for (int i = 0; i < adj.size(); i++)
            for (Object j : (List<?>) adj.get(i)) nodes.get(i).neighbors.add(nodes.get(((Number) j).intValue() - 1));
        return nodes.get(0);
    }
}
