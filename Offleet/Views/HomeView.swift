import SwiftUI

struct HomeView: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var progress: ProgressStore
    @EnvironmentObject private var settings: AppSettings
    @Binding var tab: AppTab

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    hero
                    stats
                    if let id = progress.data.lastProblem, let p = content.problem(id) {
                        NavigationLink(value: Route.problem(p.id)) {
                            HStack(spacing: 12) {
                                Image(systemName: "arrow.uturn.forward.circle.fill").font(.title).foregroundStyle(Brand.indigo)
                                VStack(alignment: .leading, spacing: 2) {
                                    Text("Pick up where you left off").font(.caption.weight(.bold)).foregroundStyle(.secondary)
                                    Text(p.title).font(.headline).lineLimit(1)
                                }
                                Spacer()
                                DifficultyPill(difficulty: p.diff)
                            }
                            .card()
                        }
                        .buttonStyle(.plain)
                    }
                    SectionHeader(title: "Study paths", subtitle: "Sliding Window and Two Pointers first, then everything else")
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 12) {
                            ForEach(featuredTracks) { t in
                                NavigationLink(value: Route.track(t.id)) { TrackCard(track: t) }
                                    .buttonStyle(.plain)
                            }
                        }
                    }
                    quickActions
                    if let pair = content.biteOfTheDay {
                        let s = pair.0
                        let b = pair.1
                        NavigationLink(value: Route.bite(b.id)) {
                            VStack(alignment: .leading, spacing: 6) {
                                Label("Bite of the day · \(s.title)", systemImage: "sparkles").font(.caption.weight(.bold)).foregroundStyle(Brand.amber)
                                Text(b.title).font(.headline)
                                Text(b.tldr).font(.subheadline).foregroundStyle(.secondary).lineLimit(3)
                            }
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .card()
                        }
                        .buttonStyle(.plain)
                    }
                    SectionHeader(title: "All patterns")
                    LazyVGrid(columns: [GridItem(.adaptive(minimum: 150), spacing: 10)], spacing: 10) {
                        ForEach(content.tracks.filter { $0.id.hasPrefix("pat-") }) { t in
                            NavigationLink(value: Route.track(t.id)) {
                                HStack(spacing: 8) {
                                    Image(systemName: t.icon).foregroundStyle(Color(hex: t.color)).frame(width: 22)
                                    VStack(alignment: .leading, spacing: 1) {
                                        Text(t.title).font(.subheadline.weight(.semibold)).lineLimit(1).minimumScaleFactor(0.8)
                                        Text("\(t.problems.count) problems").font(.caption2).foregroundStyle(.secondary)
                                    }
                                    Spacer(minLength: 0)
                                }
                                .padding(10)
                                .background(RoundedRectangle(cornerRadius: 12).fill(Color(uiColor: .secondarySystemGroupedBackground)))
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
                .padding(16)
            }
            .background(Color(uiColor: .systemGroupedBackground))
            .toolbar(.hidden, for: .navigationBar)
            .routes()
            .miniPlayerInset()
        }
    }

    private var featuredTracks: [Track] {
        let order = ["pat-sliding-window", "pat-two-pointers", "starter", "pat-spring-boot", "pat-angular"]
        let first = order.compactMap { content.track($0) }
        return first
    }

    private var hero: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(spacing: 10) {
                LogoTile(size: 44)
                Wordmark(size: 30)
                Spacer()
                Label("Offline", systemImage: "wifi.slash")
                    .font(.caption2.weight(.bold))
                    .padding(.horizontal, 8).padding(.vertical, 4)
                    .background(Capsule().fill(Brand.mint.opacity(0.18)))
                    .foregroundStyle(Brand.mint)
            }
            HStack(alignment: .center, spacing: 14) {
                VStack(alignment: .leading, spacing: 6) {
                    Text(greeting).font(.brand(26, .heavy))
                    Text("\(settings.presenter.name) is ready to walk you through your next problem.")
                        .font(.subheadline).foregroundStyle(.secondary)
                    Button {
                        tab = .practice
                    } label: {
                        Label("Start practicing", systemImage: "play.fill").font(.subheadline.weight(.bold))
                    }
                    .buttonStyle(.borderedProminent)
                    .padding(.top, 4)
                }
                Spacer(minLength: 0)
                PresenterView(presenter: settings.presenter, size: 96, owner: "none")
            }
            .padding(16)
            .background(RoundedRectangle(cornerRadius: 22, style: .continuous).fill(Brand.softGradient))
        }
    }

    private var greeting: String {
        let h = Calendar.current.component(.hour, from: Date())
        if h < 12 { return "Good morning!" }
        if h < 18 { return "Good afternoon!" }
        return "Good evening!"
    }

    private var stats: some View {
        let algo = content.problems.count
        let solved = progress.data.solved.count
        let bites = content.subjects.reduce(0) { $0 + $1.allBites.count }
        return HStack(spacing: 10) {
            stat("\(solved)/\(algo)", "solved", "checkmark.circle.fill", Brand.mint)
            stat("\(progress.streak)", "day streak", "flame.fill", Color(hex: "#F97316"))
            stat("\(progress.data.learned.count)/\(bites)", "bites learned", "brain.head.profile", Brand.violet)
        }
    }

    private func stat(_ value: String, _ label: String, _ icon: String, _ color: Color) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Image(systemName: icon).foregroundStyle(color)
            Text(value).font(.system(size: 18, weight: .heavy, design: .rounded)).minimumScaleFactor(0.6).lineLimit(1)
            Text(label).font(.caption2).foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(RoundedRectangle(cornerRadius: 14).fill(Color(uiColor: .secondarySystemGroupedBackground)))
    }

    private var quickActions: some View {
        HStack(spacing: 10) {
            NavigationLink(value: Route.patternQuiz) {
                action("Pattern quiz", "Spot the right technique", "puzzlepiece.extension.fill", Brand.indigo)
            }
            .buttonStyle(.plain)
            Button { tab = .listen } label: {
                action("Audiobooks", "Learn hands-free", "headphones", Brand.cyan)
            }
            .buttonStyle(.plain)
        }
    }

    private func action(_ title: String, _ sub: String, _ icon: String, _ color: Color) -> some View {
        HStack(spacing: 10) {
            Image(systemName: icon).font(.title2).foregroundStyle(color)
            VStack(alignment: .leading, spacing: 2) {
                Text(title).font(.subheadline.weight(.bold))
                Text(sub).font(.caption2).foregroundStyle(.secondary)
            }
            Spacer(minLength: 0)
        }
        .padding(12)
        .frame(maxWidth: .infinity)
        .background(RoundedRectangle(cornerRadius: 14).fill(Color(uiColor: .secondarySystemGroupedBackground)))
    }
}

struct TrackCard: View {
    let track: Track
    @EnvironmentObject private var progress: ProgressStore

    var body: some View {
        let done = track.problems.filter { progress.isSolved($0) }.count
        let color = Color(hex: track.color)
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Image(systemName: track.icon).font(.title2.weight(.bold)).foregroundStyle(.white)
                Spacer()
                Text("\(done)/\(track.problems.count)").font(.caption.weight(.bold)).foregroundStyle(.white.opacity(0.9))
            }
            Spacer(minLength: 0)
            Text(track.title).font(.brand(18, .heavy)).foregroundStyle(.white).lineLimit(2)
            Text(track.summary).font(.caption).foregroundStyle(.white.opacity(0.85)).lineLimit(2)
            ProgressView(value: Double(done), total: Double(max(track.problems.count, 1))).tint(.white)
        }
        .padding(14)
        .frame(width: 210, height: 170)
        .background(
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .fill(LinearGradient(colors: [color, color.opacity(0.6), Brand.indigo.opacity(0.8)], startPoint: .topLeading, endPoint: .bottomTrailing))
        )
    }
}

struct TrackView: View {
    let trackId: String
    @EnvironmentObject private var content: ContentStore

    var body: some View {
        if let t = content.track(trackId) {
            List {
                Section {
                    Label(t.summary, systemImage: t.icon).foregroundStyle(.secondary)
                }
                Section("\(t.problems.count) problems") {
                    ForEach(t.problems, id: \.self) { pid in
                        if let p = content.problem(pid) {
                            NavigationLink(value: Route.problem(p.id)) { ProblemRow(problem: p) }
                        }
                    }
                }
            }
            .navigationTitle(t.title)
        } else {
            ContentUnavailableView("Path not found", systemImage: "map")
        }
    }
}

/// "Which pattern solves this?" — trains recognising techniques from problem statements.
struct PatternQuizView: View {
    @EnvironmentObject private var content: ContentStore
    @State private var problem: Problem?
    @State private var options: [PatternInfo] = []
    @State private var picked: String?
    @State private var score = 0
    @State private var total = 0

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                HStack {
                    Text("Score \(score)/\(total)").font(.headline)
                    Spacer()
                    Button("Skip") { next() }.buttonStyle(.bordered)
                }
                if let p = problem {
                    Text(p.title).font(.brand(22, .heavy))
                    MarkdownBlock(text: p.statement).font(.subheadline)
                        .card()
                    Text("Which pattern gives the cleanest solution?").font(.headline)
                    ForEach(options) { o in
                        Button {
                            guard picked == nil else { return }
                            picked = o.id
                            total += 1
                            if p.patterns.contains(o.id) { score += 1 }
                        } label: {
                            HStack {
                                Image(systemName: o.icon).foregroundStyle(Color(hex: o.color)).frame(width: 26)
                                Text(o.name).fontWeight(.semibold)
                                Spacer()
                                if picked != nil && p.patterns.contains(o.id) {
                                    Image(systemName: "checkmark.circle.fill").foregroundStyle(Brand.mint)
                                } else if picked == o.id {
                                    Image(systemName: "xmark.circle.fill").foregroundStyle(.red)
                                }
                            }
                            .padding(14)
                            .background(RoundedRectangle(cornerRadius: 14).fill(Color(uiColor: .secondarySystemGroupedBackground)))
                        }
                        .buttonStyle(.plain)
                    }
                    if picked != nil {
                        HStack {
                            NavigationLink(value: Route.problem(p.id)) { Text("Open problem") }.buttonStyle(.bordered)
                            Spacer()
                            Button("Next question") { next() }.buttonStyle(.borderedProminent)
                        }
                    }
                }
            }
            .padding(16)
        }
        .background(Color(uiColor: .systemGroupedBackground))
        .navigationTitle("Pattern quiz")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear { if problem == nil { next() } }
        .sensoryFeedback(.selection, trigger: picked)
    }

    private func next() {
        picked = nil
        let pool = content.algorithmProblems
        guard let p = pool.randomElement(), let right = p.patterns.first.flatMap({ content.pattern($0) }) else { return }
        problem = p
        let wrong = content.patterns.filter { !p.patterns.contains($0.id) && !["spring-boot", "angular", "design"].contains($0.id) }.shuffled().prefix(3)
        options = ([right] + wrong).shuffled()
    }
}
