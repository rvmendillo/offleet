package common;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.List;

public class TreeNode {
    public int val;
    public TreeNode left, right;

    public TreeNode() {}
    public TreeNode(int val) { this.val = val; }
    public TreeNode(int val, TreeNode left, TreeNode right) { this.val = val; this.left = left; this.right = right; }

    public static TreeNode of(List<Object> vals) {
        if (vals.isEmpty() || vals.get(0) == null) return null;
        TreeNode root = new TreeNode(((Number) vals.get(0)).intValue());
        Deque<TreeNode> q = new ArrayDeque<>();
        q.add(root);
        int i = 1;
        while (!q.isEmpty() && i < vals.size()) {
            TreeNode n = q.poll();
            if (i < vals.size() && vals.get(i) != null) { n.left = new TreeNode(((Number) vals.get(i)).intValue()); q.add(n.left); }
            i++;
            if (i < vals.size() && vals.get(i) != null) { n.right = new TreeNode(((Number) vals.get(i)).intValue()); q.add(n.right); }
            i++;
        }
        return root;
    }
}
