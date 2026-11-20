import SwiftUI

// MARK: - Layout helpers

struct FlowLayout: Layout {
    var spacing: CGFloat = 6

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let maxW = proposal.width ?? .infinity
        var x: CGFloat = 0, y: CGFloat = 0, rowH: CGFloat = 0, width: CGFloat = 0
        for s in subviews {
            let sz = s.sizeThatFits(.unspecified)
            if x + sz.width > maxW && x > 0 {
                x = 0
                y += rowH + spacing
                rowH = 0
            }
            x += sz.width + spacing
            rowH = max(rowH, sz.height)
            width = max(width, x - spacing)
        }
        return CGSize(width: min(width, maxW), height: y + rowH)
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        var x = bounds.minX, y = bounds.minY, rowH: CGFloat = 0
        for s in subviews {
            let sz = s.sizeThatFits(.unspecified)
            if x + sz.width > bounds.maxX && x > bounds.minX {
                x = bounds.minX
                y += rowH + spacing
                rowH = 0
            }
            s.place(at: CGPoint(x: x, y: y), proposal: ProposedViewSize(sz))
            x += sz.width + spacing
            rowH = max(rowH, sz.height)
        }
    }
}

enum VizPalette {
    static func pointer(_ label: String) -> Color {
        let l = label.lowercased()
        if ["l", "left", "lo", "slow", "i", "prev", "start", "a", "read"].contains(l) { return Color(hex: "#22D3EE") }
        if ["r", "right", "hi", "fast", "j", "cur", "end", "b", "write"].contains(l) { return Brand.amber }
        if ["mid", "m", "k", "next", "node", "at", "you"].contains(l) { return Brand.mint }
        let colors = [Color(hex: "#F472B6"), Color(hex: "#A78BFA"), Color(hex: "#FB923C"), Color(hex: "#60A5FA")]
        let h = l.unicodeScalars.reduce(0) { ($0 &* 31 &+ Int($1.value)) & 0xFFFF }
        return colors[h % colors.count]
    }

    static let cell = Color.white.opacity(0.08)
    static let cellStroke = Color.white.opacity(0.16)
    static let label = Color.white.opacity(0.62)
}

/// Renames the visuals' labels for the language on screen (the frames are traced from the Python solution).
struct VizNames: Equatable {
    var map: [String: String] = [:]
    func callAsFunction(_ label: String) -> String { map[label] ?? label }
}

private struct VizNamesKey: EnvironmentKey { static let defaultValue = VizNames() }

extension EnvironmentValues {
    var vizNames: VizNames {
        get { self[VizNamesKey.self] }
        set { self[VizNamesKey.self] = newValue }
    }
}

private struct VizTitle: View {
    let text: String
    var body: some View {
        Text(text)
            .font(.caption.weight(.semibold))
            .foregroundStyle(VizPalette.label)
            .lineLimit(1)
    }
}

// MARK: - Stage

private struct FitHeightKey: PreferenceKey {
    static let defaultValue: CGFloat = 0
    static func reduce(value: inout CGFloat, nextValue: () -> CGFloat) { value = max(value, nextValue()) }
}

/// Lays its content out at natural height and scales it down (to `minScale`) when that is taller than the space
/// available, so a tutorial frame never hides part of its picture or text under the presenter. Anything taller
/// than that still scrolls. The closure receives the available size.
struct ShrinkToFit<Content: View>: View {
    var minScale: CGFloat = 0.62
    @ViewBuilder let content: (CGSize) -> Content
    @State private var contentHeight: CGFloat = 0

    var body: some View {
        GeometryReader { geo in
            let scale = contentHeight > geo.size.height && geo.size.height > 0 ? max(minScale, geo.size.height / contentHeight) : 1
            ScrollView(.vertical, showsIndicators: false) {
                content(geo.size)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .fixedSize(horizontal: false, vertical: true)
                    .background(GeometryReader { g in Color.clear.preference(key: FitHeightKey.self, value: g.size.height) })
                    .scaleEffect(scale, anchor: .topLeading)
                    .frame(height: contentHeight > 0 ? contentHeight * scale : nil, alignment: .top)
            }
        }
        .onPreferenceChange(FitHeightKey.self) { h in
            if contentHeight == 0 {
                contentHeight = h
            } else if abs(contentHeight - h) > 0.5 {
                withAnimation(.easeInOut(duration: 0.25)) { contentHeight = h }
            }
        }
    }
}

extension View {
    /// Top-aligned card text that shrinks (to 70%) rather than running under the presenter.
    func shrinkToFit(minScale: CGFloat = 0.7) -> some View {
        ShrinkToFit(minScale: minScale) { _ in self }
    }
}

/// Renders every component present in a frame's state.
struct VizStage: View {
    let state: VizState

    var body: some View {
        ShrinkToFit { size in
            VStack(alignment: .leading, spacing: 16) {
                ForEach(Array((state.arrays ?? []).enumerated()), id: \.offset) { _, a in
                    ArrayVizView(a: a, width: size.width - 8)
                }
                if let g = state.grid { GridVizView(g: g, isTable: false, width: size.width - 8) }
                if let g = state.table { GridVizView(g: g, isTable: true, width: size.width - 8) }
                if let l = state.linked { LinkedVizView(l: l) }
                if let t = state.tree { TreeVizView(t: t, width: size.width - 8) }
                if let g = state.graph {
                    let w = min(size.width - 8, 300)
                    GraphVizView(g: g, width: w, height: max(150, w * 0.72))
                }
                if let iv = state.intervals, !iv.isEmpty { IntervalsVizView(rows: iv, width: size.width - 8) }
                if let b = state.bits, !b.isEmpty { BitsVizView(rows: b) }
                if let s = state.stacks {
                    ForEach(Array(s.enumerated()), id: \.offset) { _, st in StackVizView(s: st) }
                }
                if let m = state.maps {
                    ForEach(Array(m.enumerated()), id: \.offset) { _, mv in MapVizView(m: mv) }
                }
                if let o = state.out { OutVizView(o: o) }
                if let v = state.vars, !v.isEmpty { VarsVizView(vars: v) }
            }
            .padding(4)
        }
        .animation(.spring(response: 0.45, dampingFraction: 0.82), value: state)
    }
}

// MARK: - Array with pointers and window

struct ArrayVizView: View {
    @Environment(\.vizNames) private var name
    let a: ArrayViz
    let width: CGFloat

    private var n: Int { max(a.v.count, 1) }
    private var gap: CGFloat { 4 }
    private var cell: CGFloat { min(46, max(26, (width - 8) / CGFloat(n) - gap)) }
    private var step: CGFloat { cell + gap }

    private struct Slot: Hashable {
        let label: String
        let index: Int
        let row: Int
    }

    private var pointerRows: [Slot] {
        var used: [Int: Int] = [:]
        var out: [Slot] = []
        for p in a.p ?? [] {
            let r = used[p.i, default: 0]
            used[p.i] = r + 1
            out.append(Slot(label: p.l, index: p.i, row: r))
        }
        return out
    }

    var body: some View {
        let rows = (pointerRows.map(\.row).max() ?? -1) + 1
        let top: CGFloat = 14
        let height = top + cell + 8 + CGFloat(rows) * 22
        VStack(alignment: .leading, spacing: 4) {
            VizTitle(text: name(a.n))
            ScrollView(.horizontal, showsIndicators: false) {
                ZStack(alignment: .topLeading) {
                    if let w = a.w, w.count == 2, w[1] >= w[0] {
                        RoundedRectangle(cornerRadius: 10, style: .continuous)
                            .fill(Brand.amber.opacity(0.16))
                            .overlay(RoundedRectangle(cornerRadius: 10, style: .continuous).stroke(Brand.amber, lineWidth: 2))
                            .frame(width: CGFloat(w[1] - w[0] + 1) * step + 4, height: cell + 8)
                            .offset(x: CGFloat(w[0]) * step - 2, y: top - 4)
                    }
                    ForEach(0..<a.v.count, id: \.self) { i in
                        Text("\(i)")
                            .font(.system(size: 9, weight: .medium, design: .monospaced))
                            .foregroundStyle(VizPalette.label)
                            .frame(width: cell)
                            .offset(x: CGFloat(i) * step, y: 0)
                        cellView(i)
                            .offset(x: CGFloat(i) * step, y: top)
                    }
                    ForEach(pointerRows, id: \.label) { p in
                        pointerChip(p.label)
                            .frame(width: max(cell, 40))
                            .offset(x: xFor(p.index) - max(cell, 40) / 2, y: top + cell + 6 + CGFloat(p.row) * 22)
                    }
                }
                .frame(width: max(CGFloat(n) * step + 8, 40), height: height, alignment: .topLeading)
                .padding(.horizontal, 2)
            }
        }
    }

    private func xFor(_ i: Int) -> CGFloat {
        let x = (CGFloat(i) + 0.5) * step - gap / 2
        return min(max(x, cell * 0.3), CGFloat(n) * step - cell * 0.3)
    }

    private func cellView(_ i: Int) -> some View {
        let marked = a.m?.contains(i) ?? false
        let inWindow: Bool = {
            guard let w = a.w, w.count == 2 else { return false }
            return i >= w[0] && i <= w[1]
        }()
        let ptr = a.p?.first { $0.i == i }
        return Text(a.v[i])
            .font(.system(size: cell > 34 ? 16 : 13, weight: .bold, design: .rounded))
            .minimumScaleFactor(0.5)
            .lineLimit(1)
            .foregroundStyle(.white)
            .frame(width: cell, height: cell)
            .background(
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .fill(marked ? Brand.mint.opacity(0.55) : (inWindow ? Brand.amber.opacity(0.22) : VizPalette.cell))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 8, style: .continuous)
                    .stroke(ptr.map { VizPalette.pointer($0.l) } ?? VizPalette.cellStroke, lineWidth: ptr == nil ? 1 : 2.5)
            )
    }

    private func pointerChip(_ label: String) -> some View {
        VStack(spacing: 0) {
            Image(systemName: "arrowtriangle.up.fill").font(.system(size: 9))
            Text(name(label)).font(.system(size: 11, weight: .heavy, design: .rounded)).lineLimit(1).minimumScaleFactor(0.6)
        }
        .foregroundStyle(VizPalette.pointer(label))
    }
}

// MARK: - Variables, maps, stacks, output

struct VarsVizView: View {
    @Environment(\.vizNames) private var name
    let vars: [KV]
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            VizTitle(text: "variables")
            FlowLayout(spacing: 6) {
                ForEach(vars, id: \.k) { v in
                    HStack(spacing: 5) {
                        Text(name(v.k)).foregroundStyle(VizPalette.label)
                        Text(v.v).fontWeight(.bold).foregroundStyle(.white).contentTransition(.numericText())
                    }
                    .font(.system(size: 13, design: .monospaced))
                    .lineLimit(1)
                    .padding(.horizontal, 10).padding(.vertical, 6)
                    .background(Capsule().fill(Color.white.opacity(0.08)))
                    .overlay(Capsule().stroke(Color.white.opacity(0.12)))
                }
            }
        }
    }
}

struct MapVizView: View {
    @Environment(\.vizNames) private var name
    let m: MapViz
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            VizTitle(text: name(m.n))
            if m.e.isEmpty {
                Text("empty").font(.caption).foregroundStyle(VizPalette.label).italic()
            }
            FlowLayout(spacing: 6) {
                ForEach(m.e, id: \.k) { e in
                    HStack(spacing: 4) {
                        Text(e.k).fontWeight(.bold)
                        if !e.v.isEmpty {
                            Image(systemName: "arrow.right").font(.system(size: 9, weight: .bold)).foregroundStyle(VizPalette.label)
                            Text(e.v)
                        }
                    }
                    .font(.system(size: 13, design: .monospaced))
                    .foregroundStyle(.white)
                    .padding(.horizontal, 9).padding(.vertical, 5)
                    .background(RoundedRectangle(cornerRadius: 8).fill(Color(hex: "#A78BFA").opacity(0.22)))
                    .transition(.scale.combined(with: .opacity))
                }
            }
        }
    }
}

struct StackVizView: View {
    @Environment(\.vizNames) private var name
    let s: StackViz
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            VizTitle(text: name(s.n) + (s.t == "stack" ? "  (top on the right)" : "  (front on the left)"))
            HStack(spacing: 4) {
                if s.v.isEmpty {
                    Text("empty").font(.caption).foregroundStyle(VizPalette.label).italic()
                }
                ForEach(Array(s.v.enumerated()), id: \.offset) { i, v in
                    Text(v)
                        .font(.system(size: 13, weight: .bold, design: .monospaced))
                        .lineLimit(1).minimumScaleFactor(0.5)
                        .foregroundStyle(.white)
                        .frame(minWidth: 30, minHeight: 30)
                        .padding(.horizontal, 4)
                        .background(RoundedRectangle(cornerRadius: 6).fill((s.t == "stack" ? Color(hex: "#F59E0B") : Color(hex: "#22D3EE")).opacity(i == (s.t == "stack" ? s.v.count - 1 : 0) ? 0.55 : 0.22)))
                        .transition(.move(edge: .trailing).combined(with: .opacity))
                }
            }
        }
    }
}

struct OutVizView: View {
    @Environment(\.vizNames) private var name
    let o: OutViz
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            VizTitle(text: name(o.n))
            FlowLayout(spacing: 5) {
                if o.v.isEmpty {
                    Text("[ ]").font(.system(size: 13, design: .monospaced)).foregroundStyle(VizPalette.label)
                }
                ForEach(Array(o.v.enumerated()), id: \.offset) { _, v in
                    Text(v)
                        .font(.system(size: 13, weight: .bold, design: .monospaced))
                        .foregroundStyle(.white)
                        .padding(.horizontal, 8).padding(.vertical, 5)
                        .background(RoundedRectangle(cornerRadius: 6).fill(Brand.mint.opacity(0.3)))
                }
            }
        }
    }
}

// MARK: - Grid / DP table

struct GridVizView: View {
    @Environment(\.vizNames) private var name
    let g: GridViz
    let isTable: Bool
    let width: CGFloat

    var body: some View {
        let cols = max(g.v.map(\.count).max() ?? 1, 1)
        let size = min(38, max(18, (width - (isTable ? 22 : 0)) / CGFloat(cols) - 2))
        let marks = Set((g.m ?? []).map { "\($0[0]),\($0[1])" })
        VStack(alignment: .leading, spacing: 4) {
            VizTitle(text: name(g.n))
            ScrollView(.horizontal, showsIndicators: false) {
                VStack(alignment: .leading, spacing: 2) {
                    if isTable && g.v.count > 1 {
                        HStack(spacing: 2) {
                            Text("").frame(width: 18)
                            ForEach(0..<cols, id: \.self) { c in
                                Text("\(c)").font(.system(size: 8, design: .monospaced)).foregroundStyle(VizPalette.label).frame(width: size)
                            }
                        }
                    }
                    ForEach(0..<g.v.count, id: \.self) { r in
                        HStack(spacing: 2) {
                            if isTable && g.v.count > 1 {
                                Text("\(r)").font(.system(size: 8, design: .monospaced)).foregroundStyle(VizPalette.label).frame(width: 18)
                            }
                            ForEach(0..<g.v[r].count, id: \.self) { c in
                                cell(r, c, size, marks.contains("\(r),\(c)"))
                            }
                        }
                    }
                }
            }
            if let ps = g.p, !ps.isEmpty {
                HStack(spacing: 10) {
                    ForEach(ps, id: \.l) { p in
                        Label("\(name(p.l)) (\(p.r), \(p.c))", systemImage: "scope")
                            .font(.caption2.weight(.semibold))
                            .foregroundStyle(VizPalette.pointer(p.l))
                    }
                }
            }
        }
    }

    private func cell(_ r: Int, _ c: Int, _ size: CGFloat, _ marked: Bool) -> some View {
        let v = g.v[r][c]
        let ptr = g.p?.first { $0.r == r && $0.c == c }
        return Text(v)
            .font(.system(size: size > 28 ? 13 : 10, weight: .bold, design: .rounded))
            .minimumScaleFactor(0.4)
            .lineLimit(1)
            .foregroundStyle(.white)
            .frame(width: size, height: size)
            .background(RoundedRectangle(cornerRadius: 5).fill(marked ? Brand.mint.opacity(0.55) : fill(v)))
            .overlay(RoundedRectangle(cornerRadius: 5).stroke(ptr.map { VizPalette.pointer($0.l) } ?? Color.clear, lineWidth: 2.5))
    }

    private func fill(_ v: String) -> Color {
        if isTable { return VizPalette.cell }
        switch v {
        case "1", "L": return Color(hex: "#16A34A").opacity(0.55)
        case "0", "W": return Color(hex: "#0EA5E9").opacity(0.28)
        case "#", "2", "X", "v", "V": return Color(hex: "#A78BFA").opacity(0.5)
        case "O": return Brand.amber.opacity(0.35)
        default: return VizPalette.cell
        }
    }
}

// MARK: - Linked list

struct LinkedVizView: View {
    @Environment(\.vizNames) private var name
    let l: LinkedViz
    private let node: CGFloat = 38
    private let hgap: CGFloat = 30
    private let vgap: CGFloat = 52
    private let top: CGFloat = 26

    private func center(_ n: LNode) -> CGPoint {
        CGPoint(x: CGFloat(n.col) * (node + hgap) + node / 2 + 8, y: top + CGFloat(n.row) * (node + vgap) + node / 2)
    }

    var body: some View {
        let byId = Dictionary(l.nodes.map { ($0.id, $0) }, uniquingKeysWith: { a, _ in a })
        let maxCol = l.nodes.map(\.col).max() ?? 0
        let maxRow = l.nodes.map(\.row).max() ?? 0
        let w = CGFloat(maxCol + 1) * (node + hgap) + 16
        let h = top + CGFloat(maxRow + 1) * (node + vgap)
        VStack(alignment: .leading, spacing: 4) {
            VizTitle(text: "linked list")
            ScrollView(.horizontal, showsIndicators: false) {
                ZStack(alignment: .topLeading) {
                    Canvas { ctx, _ in
                        for n in l.nodes where n.nx >= 0 {
                            guard let t = byId[n.nx] else { continue }
                            drawArrow(&ctx, from: center(n), to: center(t), dim: n.dim)
                        }
                    }
                    .frame(width: w, height: h)
                    ForEach(l.nodes) { n in
                        Text(n.v)
                            .font(.system(size: 14, weight: .bold, design: .rounded))
                            .foregroundStyle(.white)
                            .frame(width: node, height: node)
                            .background(Circle().fill(Color(hex: "#38BDF8").opacity(0.35)))
                            .overlay(Circle().stroke(pointerColor(n.id) ?? Color.white.opacity(0.25), lineWidth: pointerColor(n.id) == nil ? 1 : 3))
                            .opacity(n.dim ? 0.3 : 1)
                            .position(center(n))
                    }
                    ForEach(labels(byId), id: \.label) { item in
                        Text(name(item.label))
                            .font(.system(size: 10, weight: .heavy, design: .rounded))
                            .foregroundStyle(VizPalette.pointer(item.label))
                            .fixedSize()
                            .position(item.pos)
                    }
                }
                .frame(width: w, height: h, alignment: .topLeading)
            }
        }
    }

    private func pointerColor(_ id: Int) -> Color? {
        guard let p = l.p?.first(where: { $0.id == id }) else { return nil }
        return VizPalette.pointer(p.l)
    }

    private struct PtrLabel {
        let label: String
        let pos: CGPoint
    }

    private func labels(_ byId: [Int: LNode]) -> [PtrLabel] {
        var stackCount: [Int: Int] = [:]
        var out: [PtrLabel] = []
        for p in l.p ?? [] {
            guard let n = byId[p.id] else { continue }
            let k = stackCount[p.id, default: 0]
            stackCount[p.id] = k + 1
            let c = center(n)
            out.append(PtrLabel(label: p.l, pos: CGPoint(x: c.x, y: c.y - node / 2 - 8 - CGFloat(k) * 12)))
        }
        return out
    }

    private func drawArrow(_ ctx: inout GraphicsContext, from a: CGPoint, to b: CGPoint, dim: Bool) {
        let color = Color.white.opacity(dim ? 0.2 : 0.7)
        let r = node / 2 + 2
        var path = Path()
        let sameRow = abs(a.y - b.y) < 1
        let forwardNeighbour = sameRow && b.x > a.x && b.x - a.x < node + hgap + 1
        let start: CGPoint
        let end: CGPoint
        var tangent: CGPoint
        if forwardNeighbour || !sameRow {
            let dx = b.x - a.x, dy = b.y - a.y
            let len = max(sqrt(dx * dx + dy * dy), 0.001)
            start = CGPoint(x: a.x + dx / len * r, y: a.y + dy / len * r)
            end = CGPoint(x: b.x - dx / len * r, y: b.y - dy / len * r)
            path.move(to: start)
            path.addLine(to: end)
            tangent = CGPoint(x: dx / len, y: dy / len)
        } else {
            // curve above the row (backwards or long jumps)
            start = CGPoint(x: a.x, y: a.y - r)
            end = CGPoint(x: b.x, y: b.y - r)
            let ctrl = CGPoint(x: (a.x + b.x) / 2, y: a.y - r - 22 - abs(b.x - a.x) * 0.08)
            path.move(to: start)
            path.addQuadCurve(to: end, control: ctrl)
            let dx = end.x - ctrl.x, dy = end.y - ctrl.y
            let len = max(sqrt(dx * dx + dy * dy), 0.001)
            tangent = CGPoint(x: dx / len, y: dy / len)
        }
        ctx.stroke(path, with: .color(color), lineWidth: 2)
        var head = Path()
        let size: CGFloat = 7
        let left = CGPoint(x: end.x - tangent.x * size - tangent.y * size * 0.6, y: end.y - tangent.y * size + tangent.x * size * 0.6)
        let right = CGPoint(x: end.x - tangent.x * size + tangent.y * size * 0.6, y: end.y - tangent.y * size - tangent.x * size * 0.6)
        head.move(to: end)
        head.addLine(to: left)
        head.addLine(to: right)
        head.closeSubpath()
        ctx.fill(head, with: .color(color))
    }
}

// MARK: - Tree

struct TreeVizView: View {
    @Environment(\.vizNames) private var name
    let t: TreeViz
    let width: CGFloat

    var body: some View {
        let count = max(t.nodes.count, 1)
        let hstep = min(46, max(26, (width - 10) / CGFloat(count)))
        let vstep: CGFloat = 54
        let r: CGFloat = min(17, hstep * 0.42)
        let depth = (t.nodes.map(\.y).max() ?? 0) + 1
        let pos: [Int: CGPoint] = Dictionary(t.nodes.map {
            ($0.id, CGPoint(x: (CGFloat($0.x) + 0.5) * hstep + 4, y: CGFloat($0.y) * vstep + r + 16))
        }, uniquingKeysWith: { a, _ in a })
        let w = CGFloat(count) * hstep + 8
        let h = CGFloat(depth) * vstep + 10
        let marks = Set(t.m ?? [])
        VStack(alignment: .leading, spacing: 4) {
            VizTitle(text: "tree")
            if t.nodes.isEmpty {
                Text("empty tree").font(.caption).italic().foregroundStyle(VizPalette.label)
            }
            ScrollView(.horizontal, showsIndicators: false) {
                ZStack(alignment: .topLeading) {
                    Path { path in
                        for n in t.nodes {
                            guard let a = pos[n.id] else { continue }
                            for c in [n.l, n.r] where c >= 0 {
                                if let b = pos[c] {
                                    path.move(to: a)
                                    path.addLine(to: b)
                                }
                            }
                        }
                    }
                    .stroke(Color.white.opacity(0.35), lineWidth: 2)
                    ForEach(t.nodes) { n in
                        let ptr = t.p?.first { $0.id == n.id }
                        Text(n.v)
                            .font(.system(size: r > 14 ? 14 : 11, weight: .bold, design: .rounded))
                            .minimumScaleFactor(0.5)
                            .foregroundStyle(.white)
                            .frame(width: r * 2, height: r * 2)
                            .background(Circle().fill(marks.contains(n.id) ? Brand.mint.opacity(0.6) : Color(hex: "#4ADE80").opacity(0.22)))
                            .overlay(Circle().stroke(ptr.map { VizPalette.pointer($0.l) } ?? Color.white.opacity(0.3), lineWidth: ptr == nil ? 1 : 3))
                            .overlay(alignment: .top) {
                                if let ptr {
                                    Text(name(ptr.l))
                                        .font(.system(size: 9, weight: .heavy, design: .rounded))
                                        .foregroundStyle(VizPalette.pointer(ptr.l))
                                        .fixedSize()
                                        .offset(y: -13)
                                }
                            }
                            .position(pos[n.id] ?? .zero)
                    }
                }
                .frame(width: w, height: h, alignment: .topLeading)
            }
        }
    }
}

// MARK: - Graph

struct GraphVizView: View {
    let g: GraphViz
    let width: CGFloat
    var height: CGFloat? = nil

    var body: some View {
        let n = max(g.nodes.count, 1)
        let h = height ?? width
        let rx = width / 2 - 26, ry = h / 2 - 22
        let c = CGPoint(x: width / 2, y: h / 2)
        let pos: [String: CGPoint] = Dictionary(g.nodes.enumerated().map { i, k in
            let ang = Double(i) / Double(n) * 2 * Double.pi - Double.pi / 2
            return (k, CGPoint(x: c.x + rx * CGFloat(cos(ang)), y: c.y + ry * CGFloat(sin(ang))))
        }, uniquingKeysWith: { a, _ in a })
        let visited = Set(g.vis ?? [])
        VStack(alignment: .leading, spacing: 4) {
            VizTitle(text: "graph")
            ZStack {
                Canvas { ctx, _ in
                    for e in g.edges {
                        guard let a = pos[e.a], let b = pos[e.b] else { continue }
                        var p = Path()
                        let dx = b.x - a.x, dy = b.y - a.y
                        let len = max(sqrt(dx * dx + dy * dy), 0.001)
                        let end = CGPoint(x: b.x - dx / len * 18, y: b.y - dy / len * 18)
                        p.move(to: a)
                        p.addLine(to: g.dir ? end : b)
                        ctx.stroke(p, with: .color(Color.white.opacity(0.35)), lineWidth: 2)
                        if g.dir {
                            var head = Path()
                            let tx = dx / len, ty = dy / len
                            head.move(to: end)
                            head.addLine(to: CGPoint(x: end.x - tx * 8 - ty * 5, y: end.y - ty * 8 + tx * 5))
                            head.addLine(to: CGPoint(x: end.x - tx * 8 + ty * 5, y: end.y - ty * 8 - tx * 5))
                            head.closeSubpath()
                            ctx.fill(head, with: .color(Color.white.opacity(0.55)))
                        }
                    }
                }
                ForEach(Array(Set(g.nodes)).sorted(), id: \.self) { k in
                    let ptr = g.p?.first { $0.k == k }
                    Text(k)
                        .font(.system(size: 13, weight: .bold, design: .rounded))
                        .minimumScaleFactor(0.5)
                        .foregroundStyle(.white)
                        .frame(width: 32, height: 32)
                        .background(Circle().fill(visited.contains(k) ? Color(hex: "#818CF8").opacity(0.75) : Color.white.opacity(0.1)))
                        .overlay(Circle().stroke(ptr.map { VizPalette.pointer($0.l) } ?? Color.white.opacity(0.3), lineWidth: ptr == nil ? 1 : 3))
                        .position(pos[k] ?? c)
                }
            }
            .frame(width: width, height: h)
        }
    }
}

// MARK: - Intervals & bits

struct IntervalsVizView: View {
    @Environment(\.vizNames) private var name
    let rows: [IntervalRow]
    let width: CGFloat

    var body: some View {
        let all = rows.flatMap(\.v)
        let lo = all.map { $0.first ?? 0 }.min() ?? 0
        let hi = all.map { $0.last ?? 1 }.max() ?? 1
        let span = max(hi - lo, 1)
        let usable = width - 16
        VStack(alignment: .leading, spacing: 10) {
            ForEach(Array(rows.enumerated()), id: \.offset) { ri, row in
                VStack(alignment: .leading, spacing: 4) {
                    VizTitle(text: name(row.n))
                    ZStack(alignment: .leading) {
                        Rectangle().fill(Color.white.opacity(0.1)).frame(width: usable, height: 1).offset(y: 10)
                        ForEach(Array(row.v.enumerated()), id: \.offset) { i, iv in
                            let s = iv.first ?? 0, e = iv.last ?? 0
                            let x = CGFloat((s - lo) / span) * usable
                            let w = max(CGFloat((e - s) / span) * usable, 6)
                            Capsule()
                                .fill((ri == 0 ? Color(hex: "#2DD4BF") : Brand.amber).opacity(0.75))
                                .frame(width: w, height: 14)
                                .overlay(Text("\(fmt(s))–\(fmt(e))").font(.system(size: 8, weight: .bold)).foregroundStyle(.white).fixedSize().offset(y: 12))
                                .offset(x: x, y: CGFloat(i % 2) * 2)
                        }
                    }
                    .frame(width: usable, height: 28, alignment: .leading)
                }
            }
        }
    }

    private func fmt(_ d: Double) -> String { d == d.rounded() ? String(Int(d)) : String(format: "%.1f", d) }
}

struct BitsVizView: View {
    @Environment(\.vizNames) private var name
    let rows: [BitsRow]
    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            VizTitle(text: "bits")
            ForEach(rows, id: \.k) { row in
                HStack(spacing: 6) {
                    Text("\(name(row.k)) = \(row.v)").font(.system(size: 12, design: .monospaced)).foregroundStyle(VizPalette.label).frame(width: 90, alignment: .leading)
                    HStack(spacing: 2) {
                        ForEach(Array(row.b.enumerated()), id: \.offset) { _, ch in
                            Text(String(ch))
                                .font(.system(size: 12, weight: .bold, design: .monospaced))
                                .foregroundStyle(.white)
                                .frame(width: 18, height: 22)
                                .background(RoundedRectangle(cornerRadius: 4).fill(ch == "1" ? Color(hex: "#818CF8").opacity(0.7) : Color.white.opacity(0.07)))
                        }
                    }
                }
            }
        }
    }
}
