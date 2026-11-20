import SwiftUI

/// Horizontal cards for the career roadmaps (Software Engineer → AI Engineer, → Senior Engineer).
struct CareerPathCards: View {
    @EnvironmentObject private var content: ContentStore

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(content.paths) { path in
                    NavigationLink(value: Route.path(path.id)) { CareerPathCard(path: path) }
                        .buttonStyle(.plain)
                }
            }
        }
    }
}

struct CareerPathCard: View {
    let path: CareerPath
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var progress: ProgressStore

    var body: some View {
        let color = Color(hex: path.color)
        let fraction = PathProgress.fraction(path, content: content, progress: progress)
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: path.icon).font(.title2.weight(.bold))
                Spacer()
                Text("\(Int(fraction * 100))%").font(.caption.weight(.heavy))
            }
            .foregroundStyle(.white)
            Spacer(minLength: 0)
            Text(path.title).font(.brand(19, .heavy)).foregroundStyle(.white).lineLimit(2).minimumScaleFactor(0.8)
            Text(path.subtitle).font(.caption).foregroundStyle(.white.opacity(0.85)).lineLimit(2)
            ProgressView(value: fraction).tint(.white)
        }
        .padding(14)
        .frame(width: 260, height: 170)
        .background(
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .fill(LinearGradient(colors: [color, Brand.indigo, Brand.ink.opacity(0.9)], startPoint: .topLeading, endPoint: .bottomTrailing))
        )
        .overlay(alignment: .bottomTrailing) {
            LogoMark(size: 34).opacity(0.25).padding(10)
        }
    }
}

enum PathProgress {
    @MainActor
    static func done(_ item: PathItem, content: ContentStore, progress: ProgressStore) -> Double? {
        switch item.kind {
        case "problem": return progress.isSolved(item.id) ? 1 : 0
        case "bite": return progress.isLearned(item.id) ? 1 : 0
        case "subject":
            guard let s = content.subject(item.id), !s.allBites.isEmpty else { return 0 }
            return Double(s.allBites.filter { progress.isLearned($0.id) }.count) / Double(s.allBites.count)
        case "track":
            guard let t = content.track(item.id), !t.problems.isEmpty else { return 0 }
            return Double(t.problems.filter { progress.isSolved($0) }.count) / Double(t.problems.count)
        case "book":
            guard let b = content.book(item.id), !b.chapters.isEmpty else { return 0 }
            return min(1, Double(progress.position(book: b.id)?.chapter ?? 0) / Double(b.chapters.count))
        case "mock":
            return progress.data.mocks.isEmpty ? 0 : 1
        default:
            return nil
        }
    }

    @MainActor
    static func fraction(_ stage: PathStage, content: ContentStore, progress: ProgressStore) -> Double {
        let values = stage.items.compactMap { done($0, content: content, progress: progress) }
        return values.isEmpty ? 0 : values.reduce(0, +) / Double(values.count)
    }

    @MainActor
    static func fraction(_ path: CareerPath, content: ContentStore, progress: ProgressStore) -> Double {
        let values = path.stages.map { fraction($0, content: content, progress: progress) }
        return values.isEmpty ? 0 : values.reduce(0, +) / Double(values.count)
    }
}

struct CareerPathView: View {
    let pathId: String
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var progress: ProgressStore
    @EnvironmentObject private var settings: AppSettings
    @EnvironmentObject private var audiobook: AudiobookPlayer

    var body: some View {
        if let path = content.careerPath(pathId) {
            let color = Color(hex: path.color)
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    HStack(alignment: .top, spacing: 14) {
                        PresenterView(presenter: settings.presenter, size: 70, owner: "none")
                        VStack(alignment: .leading, spacing: 6) {
                            Text(path.title).font(.brand(24, .heavy))
                            Text(path.blurb).font(.subheadline).foregroundStyle(.secondary)
                        }
                    }
                    ProgressView(value: PathProgress.fraction(path, content: content, progress: progress)).tint(color)
                    ForEach(Array(path.stages.enumerated()), id: \.offset) { i, stage in
                        stageCard(i, stage, color)
                    }
                }
                .padding(16)
            }
            .background(Color(uiColor: .systemGroupedBackground))
            .navigationTitle("Career path")
            .navigationBarTitleDisplayMode(.inline)
        } else {
            ContentUnavailableView("Path not found", systemImage: "map")
        }
    }

    private func stageCard(_ i: Int, _ stage: PathStage, _ color: Color) -> some View {
        let fraction = PathProgress.fraction(stage, content: content, progress: progress)
        return VStack(alignment: .leading, spacing: 10) {
            HStack(spacing: 12) {
                ZStack {
                    Circle().fill(fraction >= 1 ? Brand.mint : color.opacity(0.18))
                    if fraction >= 1 {
                        Image(systemName: "checkmark").font(.system(size: 14, weight: .heavy)).foregroundStyle(.white)
                    } else {
                        Text("\(i + 1)").font(.system(size: 15, weight: .heavy, design: .rounded)).foregroundStyle(color)
                    }
                }
                .frame(width: 34, height: 34)
                VStack(alignment: .leading, spacing: 2) {
                    Text(stage.title).font(.headline)
                    Text(stage.blurb).font(.caption).foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true)
                }
                Spacer(minLength: 0)
                ProgressRing(value: fraction, color: color, lineWidth: 4).frame(width: 24, height: 24)
            }
            VStack(spacing: 6) {
                ForEach(Array(stage.items.enumerated()), id: \.offset) { _, item in
                    itemRow(item, color)
                }
            }
        }
        .card()
    }

    @ViewBuilder
    private func itemRow(_ item: PathItem, _ color: Color) -> some View {
        let done = PathProgress.done(item, content: content, progress: progress)
        switch item.kind {
        case "problem":
            if let p = content.problem(item.id) {
                NavigationLink(value: Route.problem(p.id)) {
                    row(icon: "chevron.left.forwardslash.chevron.right", title: p.title, sub: "\(p.diff) · \(Brand.categoryTitle(p.cat))", done: done, color: color)
                }
                .buttonStyle(.plain)
            }
        case "bite":
            if let pair = content.bite(item.id) {
                NavigationLink(value: Route.bite(item.id)) {
                    row(icon: "text.book.closed.fill", title: pair.1.title, sub: pair.0.title, done: done, color: color)
                }
                .buttonStyle(.plain)
            }
        case "subject":
            if let s = content.subject(item.id) {
                NavigationLink(value: Route.subject(s.id)) {
                    row(icon: s.icon, title: "\(s.title) reviewer", sub: "\(s.allBites.count) bites", done: done, color: color)
                }
                .buttonStyle(.plain)
            }
        case "track":
            if let t = content.track(item.id) {
                NavigationLink(value: Route.track(t.id)) {
                    row(icon: t.icon, title: t.title, sub: "\(t.problems.count) problems", done: done, color: color)
                }
                .buttonStyle(.plain)
            }
        case "book":
            if let b = content.book(item.id) {
                Button {
                    audiobook.open(b)
                    audiobook.showFullPlayer = true
                } label: {
                    row(icon: "headphones", title: b.title, sub: "Audiobook · \(b.chapters.count) chapters", done: done, color: color)
                }
                .buttonStyle(.plain)
            }
        case "mock":
            NavigationLink(value: Route.mock(item.id)) {
                row(icon: "timer", title: item.title ?? "Mock interview", sub: "Timed practice", done: done, color: color)
            }
            .buttonStyle(.plain)
        default:
            HStack(alignment: .top, spacing: 10) {
                Image(systemName: "lightbulb.fill").foregroundStyle(Brand.amber)
                Text(item.title ?? "").font(.subheadline).fixedSize(horizontal: false, vertical: true)
                Spacer(minLength: 0)
            }
            .padding(10)
            .background(RoundedRectangle(cornerRadius: 12).fill(Brand.amber.opacity(0.1)))
        }
    }

    private func row(icon: String, title: String, sub: String, done: Double?, color: Color) -> some View {
        HStack(spacing: 10) {
            Image(systemName: icon).font(.system(size: 14, weight: .semibold)).foregroundStyle(color).frame(width: 24)
            VStack(alignment: .leading, spacing: 1) {
                Text(title).font(.subheadline.weight(.semibold)).foregroundStyle(.primary).lineLimit(2)
                Text(sub).font(.caption2).foregroundStyle(.secondary)
            }
            Spacer(minLength: 0)
            if let done {
                if done >= 1 {
                    Image(systemName: "checkmark.circle.fill").foregroundStyle(Brand.mint)
                } else if done > 0 {
                    ProgressRing(value: done, color: color, lineWidth: 3).frame(width: 18, height: 18)
                } else {
                    Image(systemName: "circle").foregroundStyle(.tertiary)
                }
            }
        }
        .padding(10)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color(uiColor: .tertiarySystemFill)))
    }
}
