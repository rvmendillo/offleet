import SwiftUI

/// Timed interview simulation: random problem, countdown, interview-flow checklist, progressive hints,
/// scratchpad and self-assessment that feeds the spaced-repetition queue.
struct MockInterviewView: View {
    let initialFocus: String
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var progress: ProgressStore
    @EnvironmentObject private var settings: AppSettings

    private enum Phase { case setup, running, finished }

    @State private var phase: Phase = .setup
    @State private var focus = "any"
    @State private var difficulty = "Any"
    @State private var minutes = 25
    @State private var problem: Problem?
    @State private var startedAt = Date()
    @State private var usedSeconds = 0
    @State private var hintsShown = 0
    @State private var checks: Set<Int> = []
    @State private var notes = ""
    @State private var rated = false

    private static let steps = [
        "Clarify inputs, outputs and edge cases out loud",
        "Describe a brute-force idea and its complexity",
        "Spot the pattern and optimise (window? pointers? map?)",
        "Write clean code with good names",
        "Dry-run a small example and an edge case",
        "State the final time and space complexity",
    ]

    init(focus: String) {
        initialFocus = focus
    }

    var body: some View {
        Group {
            switch phase {
            case .setup: setup
            case .running: session
            case .finished: result
            }
        }
        .navigationTitle("Mock interview")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear { if phase == .setup && focus == "any" { focus = initialFocus } }
    }

    // MARK: setup

    private struct FocusOption: Hashable {
        let id: String
        let title: String
    }

    private var focusOptions: [FocusOption] {
        var out = [FocusOption(id: "any", title: "Any topic"), FocusOption(id: "pattern:sliding-window", title: "Sliding Window"),
                   FocusOption(id: "pattern:two-pointers", title: "Two Pointers"), FocusOption(id: "cat:ai-engineering", title: "AI Engineering"),
                   FocusOption(id: "cat:system-design", title: "Senior Design")]
        for p in content.patterns where !["sliding-window", "two-pointers", "spring-boot", "angular"].contains(p.id) {
            out.append(FocusOption(id: "pattern:" + p.id, title: p.name))
        }
        return out
    }

    private var setup: some View {
        Form {
            Section {
                HStack(spacing: 14) {
                    PresenterView(presenter: settings.presenter, size: 64, owner: "none")
                    Text("\(settings.presenter.name) picks a problem and starts the clock. Think out loud, follow the checklist, then grade yourself honestly.")
                        .font(.subheadline).foregroundStyle(.secondary)
                }
            }
            Section("Setup") {
                Picker("Focus", selection: $focus) {
                    ForEach(focusOptions, id: \.id) { opt in Text(opt.title).tag(opt.id) }
                }
                Picker("Difficulty", selection: $difficulty) {
                    ForEach(["Any", "Easy", "Medium", "Hard"], id: \.self) { Text($0).tag($0) }
                }
                .pickerStyle(.segmented)
                Picker("Time", selection: $minutes) {
                    ForEach([15, 25, 35, 45], id: \.self) { Text("\($0) min").tag($0) }
                }
                .pickerStyle(.segmented)
                let pool = content.problems(focus: focus, difficulty: difficulty)
                Button {
                    start(pool)
                } label: {
                    Label("Start interview (\(pool.count) problems in pool)", systemImage: "timer")
                        .font(.headline)
                }
                .disabled(pool.isEmpty)
            }
            if !progress.data.mocks.isEmpty {
                Section("Recent attempts") {
                    ForEach(progress.data.mocks.prefix(10)) { m in
                        if let p = content.problem(m.problemId) {
                            NavigationLink(value: Route.problem(p.id)) {
                                HStack {
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(p.title).font(.subheadline.weight(.semibold))
                                        Text("\(m.date) · \(m.seconds / 60) min · \(m.hints) hints").font(.caption2).foregroundStyle(.secondary)
                                    }
                                    Spacer()
                                    Text(Self.ratingLabel(m.rating)).font(.caption.weight(.bold))
                                        .foregroundStyle(Self.ratingColor(m.rating))
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    private func start(_ pool: [Problem]) {
        let unsolved = pool.filter { !progress.isSolved($0.id) }
        problem = (unsolved.isEmpty ? pool : unsolved).randomElement()
        startedAt = Date()
        hintsShown = 0
        checks = []
        notes = ""
        rated = false
        withAnimation { phase = .running }
    }

    // MARK: session

    private var session: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                TimelineView(.periodic(from: startedAt, by: 1)) { tl in
                    let elapsed = Int(tl.date.timeIntervalSince(startedAt))
                    let remaining = minutes * 60 - elapsed
                    HStack {
                        Image(systemName: "timer").font(.title2)
                        Text(Self.clock(abs(remaining)))
                            .font(.system(size: 34, weight: .heavy, design: .monospaced))
                            .contentTransition(.numericText())
                        if remaining < 0 { Text("over").font(.caption.weight(.bold)) }
                        Spacer()
                        Button("Finish") {
                            usedSeconds = elapsed
                            withAnimation { phase = .finished }
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    .foregroundStyle(remaining < 300 ? Color.red : Color.primary)
                }
                .card()
                if let p = problem {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text(p.title).font(.brand(22, .heavy))
                            Spacer()
                            DifficultyPill(difficulty: p.diff)
                        }
                        MarkdownBlock(text: p.statement)
                        ForEach(Array(p.examples.prefix(2).enumerated()), id: \.offset) { _, ex in
                            VStack(alignment: .leading, spacing: 2) {
                                Text("In: " + ex.input).font(.system(size: 13, design: .monospaced))
                                Text("Out: " + ex.out).font(.system(size: 13, design: .monospaced)).foregroundStyle(.secondary)
                            }
                            .padding(8)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(RoundedRectangle(cornerRadius: 10).fill(Color(uiColor: .tertiarySystemFill)))
                        }
                    }
                    .card()
                    checklist
                    hints(p)
                    VStack(alignment: .leading, spacing: 6) {
                        Label("Scratchpad", systemImage: "pencil.and.scribble").font(.headline)
                        TextEditor(text: $notes)
                            .font(.system(size: 14, design: .monospaced))
                            .autocorrectionDisabled()
                            .textInputAutocapitalization(.never)
                            .scrollContentBackground(.hidden)
                            .frame(minHeight: 180)
                            .padding(8)
                            .background(CodeTheme.background, in: RoundedRectangle(cornerRadius: 12))
                            .foregroundStyle(CodeTheme.plain)
                    }
                    .card()
                }
            }
            .padding(16)
        }
        .background(Color(uiColor: .systemGroupedBackground))
    }

    private var checklist: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label("Interview flow", systemImage: "list.bullet.clipboard").font(.headline)
            ForEach(Array(Self.steps.enumerated()), id: \.offset) { i, step in
                Button {
                    checks.formSymmetricDifference([i])
                } label: {
                    HStack(alignment: .top, spacing: 10) {
                        Image(systemName: checks.contains(i) ? "checkmark.square.fill" : "square")
                            .foregroundStyle(checks.contains(i) ? Brand.mint : Color.secondary)
                        Text(step).font(.subheadline).foregroundStyle(.primary).multilineTextAlignment(.leading)
                        Spacer(minLength: 0)
                    }
                }
                .buttonStyle(.plain)
            }
        }
        .card()
    }

    private func hints(_ p: Problem) -> some View {
        let all = p.hints + ["Pattern: " + p.patterns.compactMap { content.pattern($0)?.name }.joined(separator: ", ")]
        return VStack(alignment: .leading, spacing: 8) {
            HStack {
                Label("Hints used: \(hintsShown)/\(all.count)", systemImage: "lightbulb").font(.headline)
                Spacer()
                Button("Reveal") { hintsShown = min(hintsShown + 1, all.count) }
                    .buttonStyle(.bordered)
                    .disabled(hintsShown >= all.count)
            }
            ForEach(Array(all.prefix(hintsShown).enumerated()), id: \.offset) { _, h in
                Text("• " + h).font(.subheadline).fixedSize(horizontal: false, vertical: true)
            }
        }
        .card()
    }

    // MARK: result

    private var result: some View {
        ScrollView {
            VStack(spacing: 16) {
                PresenterView(presenter: settings.presenter, size: 110, owner: "none")
                Text("Time used \(Self.clock(usedSeconds))").font(.brand(26, .heavy))
                Text("\(checks.count)/\(Self.steps.count) flow steps · \(hintsShown) hints").foregroundStyle(.secondary)
                if !rated {
                    Text("How did it go?").font(.headline)
                    ForEach([3, 2, 1, 0], id: \.self) { r in
                        Button {
                            if let p = problem {
                                progress.recordMock(problemId: p.id, seconds: usedSeconds, rating: r, hints: hintsShown)
                                if r >= 2 && !progress.isSolved(p.id) { progress.toggleSolved(p.id) }
                            }
                            rated = true
                        } label: {
                            Text(Self.ratingLabel(r))
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 12)
                                .background(RoundedRectangle(cornerRadius: 14).fill(Self.ratingColor(r).opacity(0.18)))
                                .foregroundStyle(Self.ratingColor(r))
                                .font(.headline)
                        }
                        .buttonStyle(.plain)
                    }
                } else {
                    Label("Saved. It's scheduled in your review queue.", systemImage: "checkmark.seal.fill").foregroundStyle(Brand.mint)
                    if let p = problem {
                        NavigationLink(value: Route.problem(p.id)) {
                            Label("Study the solution and walkthrough", systemImage: "play.rectangle.fill").frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    Button("Another interview") { withAnimation { phase = .setup } }
                        .buttonStyle(.bordered)
                }
            }
            .padding(20)
        }
    }

    static func clock(_ s: Int) -> String { String(format: "%02d:%02d", s / 60, s % 60) }

    static func ratingLabel(_ r: Int) -> String {
        switch r {
        case 3: return "Nailed it"
        case 2: return "Solved with help"
        case 1: return "Partly there"
        default: return "Couldn't solve"
        }
    }

    static func ratingColor(_ r: Int) -> Color {
        switch r {
        case 3: return Brand.mint
        case 2: return Color(hex: "#22D3EE")
        case 1: return Brand.amber
        default: return Color(hex: "#EF4444")
        }
    }
}
