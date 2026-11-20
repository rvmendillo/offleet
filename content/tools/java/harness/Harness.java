package harness;

import common.ListNode;
import common.Node;
import common.TreeNode;

import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;
import java.util.concurrent.*;

/**
 * Runs every Java solution against its tests and prints one JSON line per test:
 * {"key": ..., "i": n, "ret": ..., "args": [...], "err": ...}. Comparison happens in build.py.
 */
public final class Harness {

    @SuppressWarnings("unchecked")
    public static void main(String[] argv) throws Exception {
        String text = new String(Files.readAllBytes(Paths.get(argv[0])), StandardCharsets.UTF_8);
        List<Object> jobs = (List<Object>) Json.parse(text);
        ExecutorService pool = Executors.newCachedThreadPool(r -> {
            Thread t = new Thread(r);
            t.setDaemon(true);
            return t;
        });
        StringBuilder out = new StringBuilder();
        for (Object jo : jobs) {
            Map<String, Object> job = (Map<String, Object>) jo;
            List<Object> tests = (List<Object>) job.get("tests");
            for (int i = 0; i < tests.size(); i++) {
                Map<String, Object> res = new LinkedHashMap<>();
                res.put("key", job.get("key"));
                res.put("i", i);
                final Object test = tests.get(i);
                Future<Map<String, Object>> f = pool.submit(() -> runOne(job, test));
                try {
                    res.putAll(f.get(5, TimeUnit.SECONDS));
                } catch (TimeoutException e) {
                    f.cancel(true);
                    res.put("err", "timeout");
                } catch (ExecutionException e) {
                    Throwable c = e.getCause();
                    if (c instanceof InvocationTargetException) c = c.getCause();
                    res.put("err", String.valueOf(c));
                }
                out.append(Json.write(res)).append('\n');
            }
        }
        System.out.print(out);
        System.out.flush();
        System.exit(0);
    }

    @SuppressWarnings("unchecked")
    static Map<String, Object> runOne(Map<String, Object> job, Object test) throws Exception {
        String pkg = (String) job.get("pkg");
        Map<String, Object> r = new LinkedHashMap<>();
        if (Boolean.TRUE.equals(job.get("design"))) {
            List<Object> t = (List<Object>) test;
            List<Object> ops = (List<Object>) t.get(0);
            List<Object> args = (List<Object>) t.get(1);
            Class<?> cls = Class.forName(pkg + "." + ops.get(0));
            List<Object> a0 = (List<Object>) args.get(0);
            Constructor<?> ctor = null;
            for (Constructor<?> c : cls.getDeclaredConstructors()) if (c.getParameterCount() == a0.size()) ctor = c;
            if (ctor == null) throw new IllegalStateException("no constructor with " + a0.size() + " args");
            ctor.setAccessible(true);
            Object obj = ctor.newInstance(convertAll(ctor.getGenericParameterTypes(), a0));
            List<Object> outs = new ArrayList<>();
            outs.add(null);
            for (int k = 1; k < ops.size(); k++) {
                List<Object> av = (List<Object>) args.get(k);
                Method m = pick(cls, (String) ops.get(k), av.size());
                m.setAccessible(true);
                Object ret = m.invoke(obj, convertAll(m.getGenericParameterTypes(), av));
                outs.add(m.getReturnType() == void.class ? null : toJson(ret));
            }
            r.put("ret", outs);
        } else {
            Class<?> cls = Class.forName(pkg + "." + job.get("cls"));
            List<Object> av = (List<Object>) test;
            Method m = pick(cls, (String) job.get("method"), av.size());
            m.setAccessible(true);
            Constructor<?> c = cls.getDeclaredConstructor();
            c.setAccessible(true);
            Object inst = Modifier.isStatic(m.getModifiers()) ? null : c.newInstance();
            Object[] conv = convertAll(m.getGenericParameterTypes(), av);
            Object ret = m.invoke(inst, conv);
            r.put("ret", toJson(ret));
            List<Object> argsOut = new ArrayList<>();
            for (Object o : conv) argsOut.add(toJson(o));
            r.put("args", argsOut);
        }
        return r;
    }

    static Method pick(Class<?> cls, String name, int argc) {
        for (Method m : cls.getDeclaredMethods())
            if (m.getName().equals(name) && m.getParameterCount() == argc && Modifier.isPublic(m.getModifiers())) return m;
        for (Method m : cls.getDeclaredMethods())
            if (m.getName().equals(name) && m.getParameterCount() == argc) return m;
        throw new IllegalStateException("method " + name + "/" + argc + " not found in " + cls.getName());
    }

    static Object[] convertAll(Type[] types, List<Object> vals) {
        Object[] out = new Object[types.length];
        for (int i = 0; i < types.length; i++) out[i] = convert(vals.get(i), types[i]);
        return out;
    }

    @SuppressWarnings("unchecked")
    static Object convert(Object v, Type t) {
        if (t instanceof ParameterizedType) {
            ParameterizedType pt = (ParameterizedType) t;
            Class<?> raw = (Class<?>) pt.getRawType();
            Type[] ta = pt.getActualTypeArguments();
            if (v == null) return null;
            if (Set.class.isAssignableFrom(raw)) {
                Set<Object> s = new HashSet<>();
                for (Object x : (List<Object>) v) s.add(convert(x, ta[0]));
                return s;
            }
            if (Collection.class.isAssignableFrom(raw) || raw == Iterable.class) {
                List<Object> l = new ArrayList<>();
                for (Object x : (List<Object>) v) l.add(convert(x, ta[0]));
                return l;
            }
            if (Map.class.isAssignableFrom(raw)) {
                Map<Object, Object> m = new HashMap<>();
                for (Map.Entry<String, Object> e : ((Map<String, Object>) v).entrySet())
                    m.put(convert(ta[0] == String.class ? e.getKey() : (Object) Long.parseLong(e.getKey()), ta[0]), convert(e.getValue(), ta[1]));
                return m;
            }
            throw new IllegalArgumentException("unsupported type " + t);
        }
        Class<?> c = (Class<?>) t;
        if (v == null) {
            if (c.isPrimitive()) throw new IllegalArgumentException("null for primitive " + c);
            return null;
        }
        if (c == int.class || c == Integer.class) return ((Number) v).intValue();
        if (c == long.class || c == Long.class) return ((Number) v).longValue();
        if (c == double.class || c == Double.class) return ((Number) v).doubleValue();
        if (c == float.class || c == Float.class) return ((Number) v).floatValue();
        if (c == boolean.class || c == Boolean.class) return v;
        if (c == char.class || c == Character.class) return ((String) v).charAt(0);
        if (c == String.class) return v;
        if (c == ListNode.class) return ListNode.of((List<Object>) v);
        if (c == TreeNode.class) return TreeNode.of((List<Object>) v);
        if (c == Node.class) return Node.of((List<Object>) v);
        if (c.isArray()) {
            Class<?> comp = c.getComponentType();
            if (comp == char.class && v instanceof String) return ((String) v).toCharArray();
            List<Object> l = (List<Object>) v;
            Object arr = Array.newInstance(comp, l.size());
            for (int i = 0; i < l.size(); i++) Array.set(arr, i, convert(l.get(i), comp));
            return arr;
        }
        if (c == List.class || c == Object.class) return v;
        throw new IllegalArgumentException("unsupported type " + c);
    }

    static Object toJson(Object o) {
        if (o == null) return null;
        if (o instanceof ListNode) {
            List<Object> l = new ArrayList<>();
            Set<ListNode> seen = Collections.newSetFromMap(new IdentityHashMap<>());
            for (ListNode n = (ListNode) o; n != null && seen.add(n) && l.size() < 10000; n = n.next) l.add((long) n.val);
            return l;
        }
        if (o instanceof TreeNode) {
            List<Object> l = new ArrayList<>();
            Deque<TreeNode> q = new ArrayDeque<>();
            List<TreeNode> order = new ArrayList<>();
            order.add((TreeNode) o);
            for (int i = 0; i < order.size(); i++) {
                TreeNode n = order.get(i);
                if (n == null) { l.add(null); continue; }
                l.add((long) n.val);
                order.add(n.left);
                order.add(n.right);
            }
            while (!l.isEmpty() && l.get(l.size() - 1) == null) l.remove(l.size() - 1);
            return l;
        }
        if (o instanceof Node) {
            Map<Integer, Node> seen = new TreeMap<>();
            Deque<Node> q = new ArrayDeque<>();
            q.add((Node) o);
            seen.put(((Node) o).val, (Node) o);
            while (!q.isEmpty()) {
                Node n = q.poll();
                for (Node nb : n.neighbors) if (!seen.containsKey(nb.val)) { seen.put(nb.val, nb); q.add(nb); }
            }
            List<Object> adj = new ArrayList<>();
            for (Node n : seen.values()) {
                List<Object> nb = new ArrayList<>();
                for (Node x : n.neighbors) nb.add((long) x.val);
                adj.add(nb);
            }
            return adj;
        }
        if (o instanceof Character) return String.valueOf(o);
        if (o instanceof Number || o instanceof Boolean || o instanceof String) return o;
        if (o.getClass().isArray()) {
            List<Object> l = new ArrayList<>();
            int n = Array.getLength(o);
            for (int i = 0; i < n; i++) l.add(toJson(Array.get(o, i)));
            return l;
        }
        if (o instanceof Collection) {
            List<Object> l = new ArrayList<>();
            for (Object x : (Collection<?>) o) l.add(toJson(x));
            return l;
        }
        if (o instanceof Map) {
            Map<String, Object> m = new LinkedHashMap<>();
            for (Map.Entry<?, ?> e : ((Map<?, ?>) o).entrySet()) m.put(String.valueOf(e.getKey()), toJson(e.getValue()));
            return m;
        }
        return String.valueOf(o);
    }
}
