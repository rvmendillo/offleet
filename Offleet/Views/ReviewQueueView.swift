import SwiftUI

/// Spaced-repetition review of solved problems and learned bites.
struct ReviewQueueView: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var progress: ProgressStore
    @State private var queue: [String] = []
    @State private var revealed = false
    @State private var reviewedCount = 0

    var body: some View {
        VStack(spacing: 16) {
            if let key = queue.first {
                ProgressView(value: Double(reviewedCount), total: Double(reviewedCount + queue.count)).tint(Brand.indigo)
                ScrollView {
                    card(key)
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
                if revealed {
                    HStack(spacing: 8) {
                        grade("Again", 0, Color(hex: "#EF4444"), key)
                        grade("Hard", 1, Brand.amber, key)
                        grade("Good", 2, Color(hex: "#22D3EE"), key)
                        grade("Easy", 3, Brand.mint, key)
                    }
                } else {
                    Button {
                        withAnimation(.spring()) { revealed = true }
                    } label: {
                        Text("Show answer").font(.headline).frame(maxWidth: .infinity).padding(.vertical, 14)
                            .background(RoundedRectangle(cornerRadius: 14).fill(Brand.gradient)).foregroundStyle(.white)
                    }
                    .buttonStyle(.plain)
                }
            } else {
                ContentUnavailableView {
                    Label("All caught up", systemImage: "checkmark.seal.fill")
                } description: {
                    Text(reviewedCount > 0 ? "You reviewed \(reviewedCount) items. Come back tomorrow." :
                            "Solve problems and mark bites as learned. They'll come back here right before you'd forget them.")
                }
            }
        }
        .padding(16)
        .background(Color(uiColor: .systemGroupedBackground))
        .navigationTitle("Review")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear { if queue.isEmpty { queue = progress.dueKeys } }
    }

    @ViewBuilder
    private func card(_ key: String) -> some View {
        let id = String(key.dropFirst(2))
        if key.hasPrefix("p:"), let p = content.problem(id) {
            VStack(alignment: .leading, spacing: 12) {
                Label("Problem recall", systemImage: "chevron.left.forwardslash.chevron.right").font(.caption.weight(.bold)).foregroundStyle(.secondary)
                Text(p.title).font(.brand(24, .heavy))
                MarkdownBlock(text: p.statement).font(.subheadline)
                Text("Which pattern solves it, and what's the key idea?").font(.headline)
                if revealed, let a = p.approaches.first {
                    VStack(alignment: .leading, spacing: 8) {
                        if let pat = content.pattern(a.pattern) { PatternBadge(pattern: pat) }
                        MarkdownBlock(text: a.idea).font(.subheadline)
                        Text("Time \(a.time) · Space \(a.space)").font(.caption.weight(.bold)).foregroundStyle(.secondary)
                        NavigationLink(value: Route.problem(p.id)) { Label("Open problem", systemImage: "arrow.right.circle") }
                    }
                    .transition(.opacity)
                }
            }
            .card()
        } else if key.hasPrefix("b:"), let pair = content.bite(id) {
            let b = pair.1
            VStack(alignment: .leading, spacing: 12) {
                Label(pair.0.title, systemImage: pair.0.icon).font(.caption.weight(.bold)).foregroundStyle(Color(hex: pair.0.color))
                Text(b.title).font(.brand(24, .heavy))
                Text("Explain it in one sentence, then check.").font(.subheadline).foregroundStyle(.secondary)
                if revealed {
                    Text(b.tldr).font(.title3.weight(.semibold)).foregroundStyle(Color(hex: pair.0.color))
                    ForEach(Array(b.points.enumerated()), id: \.offset) { _, pt in
                        Text("• " + pt).font(.subheadline).fixedSize(horizontal: false, vertical: true)
                    }
                    if let f = b.formula { Text(f).font(.system(.body, design: .serif).weight(.semibold)) }
                }
            }
            .card()
        } else {
            Text("This item is no longer available.").card()
                .onAppear { advance() }
        }
    }

    private func grade(_ label: String, _ g: Int, _ color: Color, _ key: String) -> some View {
        Button {
            progress.review(key, grade: g)
            advance()
        } label: {
            Text(label).font(.subheadline.weight(.bold)).frame(maxWidth: .infinity).padding(.vertical, 12)
                .background(RoundedRectangle(cornerRadius: 12).fill(color.opacity(0.2))).foregroundStyle(color)
        }
        .buttonStyle(.plain)
    }

    private func advance() {
        withAnimation {
            if !queue.isEmpty { queue.removeFirst() }
            reviewedCount += 1
            revealed = false
        }
    }
}

/// Activity heatmap and headline stats.
struct StatsPanel: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var progress: ProgressStore

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            heatmap
            HStack(spacing: 8) {
                ForEach(["Easy", "Medium", "Hard"], id: \.self) { d in
                    let total = content.problems.filter { $0.diff == d && $0.isAlgorithm }.count
                    let solved = content.problems.filter { $0.diff == d && progress.isSolved($0.id) }.count
                    VStack(alignment: .leading, spacing: 4) {
                        Text(d).font(.caption2.weight(.bold)).foregroundStyle(Brand.difficultyColor(d))
                        Text("\(solved)/\(total)").font(.system(size: 16, weight: .heavy, design: .rounded))
                        ProgressView(value: Double(solved), total: Double(max(total, 1))).tint(Brand.difficultyColor(d))
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
            }
            HStack {
                Label("\(progress.data.watched.count) walkthroughs", systemImage: "play.rectangle")
                Spacer()
                Label("\(progress.data.mocks.count) mocks", systemImage: "timer")
                Spacer()
                Label("\(progress.dueKeys.count) due", systemImage: "arrow.triangle.2.circlepath")
            }
            .font(.caption.weight(.semibold))
            .foregroundStyle(.secondary)
        }
    }

    private var heatmap: some View {
        let weeks = 16
        let cal = Calendar.current
        let today = Date()
        let weekday = cal.component(.weekday, from: today) - 1
        let start = cal.date(byAdding: .day, value: -(weeks - 1) * 7 - weekday, to: today) ?? today
        let maxCount = max(progress.data.activity.values.max() ?? 1, 1)
        return VStack(alignment: .leading, spacing: 4) {
            Text("Activity · last \(weeks) weeks").font(.caption.weight(.bold)).foregroundStyle(.secondary)
            HStack(alignment: .top, spacing: 3) {
                ForEach(0..<weeks, id: \.self) { w in
                    VStack(spacing: 3) {
                        ForEach(0..<7, id: \.self) { d in
                            let date = cal.date(byAdding: .day, value: w * 7 + d, to: start) ?? today
                            let count = progress.data.activity[ProgressStore.dayString(date)] ?? 0
                            RoundedRectangle(cornerRadius: 3)
                                .fill(date > today ? Color.clear : (count == 0 ? Color(uiColor: .tertiarySystemFill) :
                                        Brand.indigo.opacity(0.3 + 0.7 * Double(count) / Double(maxCount))))
                                .frame(width: 14, height: 14)
                        }
                    }
                }
            }
        }
    }
}
