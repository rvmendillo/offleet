import SwiftUI

struct ProblemsView: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var progress: ProgressStore
    @State private var path = DebugLaunch.practicePath
    @State private var query = ""
    @State private var category = "all"
    @State private var difficulty = "All"
    @State private var pattern: String? = nil
    @State private var bookmarkedOnly = false
    @State private var hideSolved = false

    private var filtered: [Problem] {
        let q = query.trimmingCharacters(in: .whitespaces).lowercased()
        return content.problems.filter { p in
            if category != "all" && p.cat != category { return false }
            if difficulty != "All" && p.diff != difficulty { return false }
            if let pattern, !p.patterns.contains(pattern) { return false }
            if bookmarkedOnly && !progress.isBookmarked(p.id) { return false }
            if hideSolved && progress.isSolved(p.id) { return false }
            if q.isEmpty { return true }
            if p.title.lowercased().contains(q) || String(p.n) == q { return true }
            if p.topics.contains(where: { $0.lowercased().contains(q) }) { return true }
            return p.patterns.contains { pid in (content.pattern(pid)?.name.lowercased() ?? pid).contains(q) }
        }
    }

    var body: some View {
        NavigationStack(path: $path) {
            List {
                Section {
                    filters
                        .listRowInsets(EdgeInsets(top: 4, leading: 0, bottom: 4, trailing: 0))
                        .listRowSeparator(.hidden)
                }
                Section {
                    ForEach(filtered) { p in
                        NavigationLink(value: Route.problem(p.id)) {
                            ProblemRow(problem: p)
                        }
                    }
                } header: {
                    Text("\(filtered.count) problems")
                }
            }
            .listStyle(.plain)
            .overlay {
                if filtered.isEmpty {
                    ContentUnavailableView.search(text: query)
                }
            }
            .searchable(text: $query, prompt: "Search titles, topics, patterns")
            .navigationTitle("Practice")
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    NavigationLink(value: Route.mock(pattern.map { "pattern:" + $0 } ?? (["ai-engineering", "system-design"].contains(category) ? "cat:" + category : "any"))) {
                        Label("Mock interview", systemImage: "timer")
                    }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Menu {
                        Picker("Difficulty", selection: $difficulty) {
                            ForEach(["All", "Easy", "Medium", "Hard"], id: \.self) { Text($0).tag($0) }
                        }
                        Picker("Pattern", selection: $pattern) {
                            Text("Any pattern").tag(String?.none)
                            ForEach(content.patterns) { p in
                                Label(p.name, systemImage: p.icon).tag(String?.some(p.id))
                            }
                        }
                        Toggle("Bookmarked only", isOn: $bookmarkedOnly)
                        Toggle("Hide solved", isOn: $hideSolved)
                        Button("Reset filters", role: .destructive) {
                            difficulty = "All"; pattern = nil; bookmarkedOnly = false; hideSolved = false; category = "all"
                        }
                    } label: {
                        Image(systemName: "line.3.horizontal.decrease.circle")
                    }
                    .accessibilityLabel("Filters")
                }
            }
            .routes()
            .miniPlayerInset()
        }
    }

    private var filters: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(CategoryOption.all) { item in
                    Button { category = item.id } label: {
                        Chip(text: item.title, systemImage: item.icon, selected: category == item.id)
                    }
                    .buttonStyle(.plain)
                }
                Divider().frame(height: 22)
                ForEach(["sliding-window", "two-pointers"], id: \.self) { pid in
                    if let p = content.pattern(pid) {
                        Button { pattern = (pattern == pid ? nil : pid) } label: {
                            Chip(text: p.name, systemImage: p.icon, selected: pattern == pid)
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
            .padding(.horizontal, 16)
        }
    }
}

struct CategoryOption: Identifiable {
    let id: String
    let title: String
    let icon: String

    static let all = [
        CategoryOption(id: "all", title: "All", icon: "square.grid.2x2"),
        CategoryOption(id: "algorithms", title: "Algorithms", icon: "function"),
        CategoryOption(id: "ai-engineering", title: "AI Engineering", icon: "sparkles"),
        CategoryOption(id: "system-design", title: "Senior Design", icon: "building.columns"),
        CategoryOption(id: "spring-boot", title: "Spring Boot", icon: "leaf"),
        CategoryOption(id: "angular", title: "Angular", icon: "a.circle"),
    ]
}

struct ProblemRow: View {
    let problem: Problem
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var progress: ProgressStore

    var body: some View {
        HStack(spacing: 12) {
            ZStack {
                Circle().fill(progress.isSolved(problem.id) ? Brand.mint.opacity(0.2) : Color(uiColor: .tertiarySystemFill))
                if progress.isSolved(problem.id) {
                    Image(systemName: "checkmark").font(.system(size: 13, weight: .heavy)).foregroundStyle(Brand.mint)
                } else {
                    Text("\(problem.n)").font(.system(size: 12, weight: .bold, design: .rounded)).foregroundStyle(.secondary)
                        .minimumScaleFactor(0.6)
                }
            }
            .frame(width: 34, height: 34)
            VStack(alignment: .leading, spacing: 5) {
                HStack(spacing: 6) {
                    Text(problem.title).font(.system(size: 16, weight: .semibold, design: .rounded)).lineLimit(2)
                    if progress.isBookmarked(problem.id) {
                        Image(systemName: "bookmark.fill").font(.caption2).foregroundStyle(Brand.amber)
                    }
                }
                HStack(spacing: 6) {
                    DifficultyPill(difficulty: problem.diff)
                    if !problem.isAlgorithm {
                        Text(Brand.categoryTitle(problem.cat)).font(.caption2.weight(.semibold)).foregroundStyle(.secondary)
                    }
                    ForEach(problem.patterns.prefix(3), id: \.self) { pid in
                        if let p = content.pattern(pid) { PatternBadge(pattern: p, compact: problem.patterns.count > 2) }
                    }
                }
            }
        }
        .padding(.vertical, 4)
    }
}
