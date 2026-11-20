import SwiftUI

struct TutorialLaunch: Identifiable {
    let id = UUID()
    let approachId: String
}

struct ProblemDetailView: View {
    let problemId: String
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var progress: ProgressStore
    @EnvironmentObject private var settings: AppSettings
    @State private var approachIndex = 0
    @State private var lang = "python"
    @State private var launch: TutorialLaunch?
    @State private var revealed: Set<Int> = []
    @State private var showNotes = false
    @StateObject private var reader = ScriptReader(owner: "idea")

    var body: some View {
        if let p = content.problem(problemId) {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    header(p)
                    watchCard(p)
                    statement(p)
                    if !p.examples.isEmpty { examples(p) }
                    if !p.constraints.isEmpty { constraints(p) }
                    if !p.hints.isEmpty { hints(p) }
                    solutions(p)
                }
                .padding(16)
            }
            .background(Color(uiColor: .systemGroupedBackground))
            .navigationTitle("#\(p.n)")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItemGroup(placement: .topBarTrailing) {
                    Button { showNotes = true } label: { Image(systemName: "square.and.pencil") }
                        .accessibilityLabel("My notes")
                    Button { progress.toggleBookmark(p.id) } label: {
                        Image(systemName: progress.isBookmarked(p.id) ? "bookmark.fill" : "bookmark")
                    }
                    .accessibilityLabel("Bookmark")
                    Button { progress.toggleSolved(p.id) } label: {
                        Image(systemName: progress.isSolved(p.id) ? "checkmark.circle.fill" : "checkmark.circle")
                    }
                    .sensoryFeedback(.success, trigger: progress.isSolved(p.id))
                    .accessibilityLabel("Mark solved")
                }
            }
            .fullScreenCover(item: $launch) { l in
                TutorialPlayerView(problem: p, approachId: l.approachId)
            }
            .sheet(isPresented: $showNotes) {
                NotesSheet(problem: p)
            }
            .onAppear {
                if DebugLaunch.screen == "tutorial", DebugLaunch.problem == p.id, launch == nil {
                    launch = TutorialLaunch(approachId: DebugLaunch.approach ?? p.approaches.first?.id ?? "a1")
                }
                progress.opened(problem: p.id)
                let langs = p.approaches.first?.languages ?? []
                lang = langs.contains(settings.language) ? settings.language : (langs.first ?? "python")
            }
            .onDisappear { reader.stop() }
        } else {
            ContentUnavailableView("Problem not found", systemImage: "questionmark.folder")
        }
    }

    // MARK: sections

    private func header(_ p: Problem) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(p.title).font(.brand(28, .heavy)).fixedSize(horizontal: false, vertical: true)
            HStack(spacing: 8) {
                DifficultyPill(difficulty: p.diff)
                Text(Brand.categoryTitle(p.cat)).font(.caption.weight(.semibold)).foregroundStyle(.secondary)
                if progress.isSolved(p.id) {
                    Label("Solved", systemImage: "checkmark.seal.fill").font(.caption.weight(.bold)).foregroundStyle(Brand.mint)
                }
            }
            FlowLayout(spacing: 6) {
                ForEach(p.patterns, id: \.self) { pid in
                    if let pat = content.pattern(pid) { PatternBadge(pattern: pat) }
                }
                ForEach(p.topics.filter { t in !p.patterns.contains { content.pattern($0)?.name == t } }, id: \.self) { t in
                    Text(t).font(.caption2.weight(.medium))
                        .padding(.horizontal, 8).padding(.vertical, 3)
                        .background(Capsule().fill(Color(uiColor: .tertiarySystemFill)))
                }
            }
        }
    }

    private func watchCard(_ p: Problem) -> some View {
        let a = p.approaches.indices.contains(approachIndex) ? p.approaches[approachIndex] : p.approaches.first
        let watched = a.map { progress.data.watched.contains("\(p.id)#\($0.id)") } ?? false
        return Button {
            if let a { launch = TutorialLaunch(approachId: a.id) }
        } label: {
            HStack(spacing: 14) {
                PresenterView(presenter: settings.presenter, size: 64, owner: "none")
                    .overlay(Circle().stroke(Color.white.opacity(0.35), lineWidth: 2))
                VStack(alignment: .leading, spacing: 4) {
                    Text(watched ? "Watch again" : "Watch the animated walkthrough")
                        .font(.system(size: 17, weight: .heavy, design: .rounded))
                        .multilineTextAlignment(.leading)
                    Text("\(settings.presenter.name) explains \(a?.name ?? "the solution") step by step, out loud.")
                        .font(.caption).opacity(0.85)
                        .multilineTextAlignment(.leading)
                }
                Spacer(minLength: 0)
                Image(systemName: "play.circle.fill").font(.system(size: 40))
            }
            .foregroundStyle(.white)
            .padding(14)
            .background(RoundedRectangle(cornerRadius: 20, style: .continuous).fill(Brand.gradient))
            .shadow(color: Brand.violet.opacity(0.3), radius: 10, y: 5)
        }
        .buttonStyle(.plain)
        .accessibilityLabel("Watch the animated walkthrough")
    }

    private func statement(_ p: Problem) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            SectionHeader(title: "Problem")
            MarkdownBlock(text: p.statement)
                .font(.body)
        }
        .card()
    }

    private func examples(_ p: Problem) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            SectionHeader(title: "Examples")
            ForEach(Array(p.examples.enumerated()), id: \.offset) { i, ex in
                VStack(alignment: .leading, spacing: 6) {
                    Text("Example \(i + 1)").font(.caption.weight(.bold)).foregroundStyle(.secondary)
                    exampleLine("Input", ex.input)
                    exampleLine("Output", ex.out)
                    if let why = ex.why {
                        Text(why).font(.footnote).foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true)
                    }
                }
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(RoundedRectangle(cornerRadius: 12).fill(Color(uiColor: .tertiarySystemFill)))
            }
        }
        .card()
    }

    private func exampleLine(_ label: String, _ value: String) -> some View {
        HStack(alignment: .firstTextBaseline, spacing: 8) {
            Text(label).font(.caption.weight(.bold)).foregroundStyle(Brand.indigo).frame(width: 52, alignment: .leading)
            Text(value).font(.system(size: 14, design: .monospaced)).textSelection(.enabled)
                .fixedSize(horizontal: false, vertical: true)
        }
    }

    private func constraints(_ p: Problem) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            SectionHeader(title: "Constraints")
            ForEach(p.constraints, id: \.self) { c in
                HStack(alignment: .firstTextBaseline, spacing: 8) {
                    Circle().fill(Brand.indigo).frame(width: 5, height: 5)
                    MarkdownText(text: c).font(.system(size: 14, design: .monospaced))
                }
            }
        }
        .card()
    }

    private func hints(_ p: Problem) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            SectionHeader(title: "Hints", subtitle: "Tap to reveal one at a time")
            ForEach(Array(p.hints.enumerated()), id: \.offset) { i, h in
                Button {
                    withAnimation(.spring()) { _ = revealed.insert(i) }
                } label: {
                    HStack(alignment: .top, spacing: 10) {
                        Image(systemName: revealed.contains(i) ? "lightbulb.fill" : "lightbulb")
                            .foregroundStyle(Brand.amber)
                        Text(revealed.contains(i) ? h : "Hint \(i + 1)")
                            .font(.subheadline)
                            .foregroundStyle(revealed.contains(i) ? .primary : .secondary)
                            .multilineTextAlignment(.leading)
                            .blur(radius: revealed.contains(i) ? 0 : 0.5)
                        Spacer()
                    }
                    .padding(10)
                    .background(RoundedRectangle(cornerRadius: 10).fill(Color(uiColor: .tertiarySystemFill)))
                }
                .buttonStyle(.plain)
            }
        }
        .card()
    }

    private func solutions(_ p: Problem) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            SectionHeader(title: "Solutions", subtitle: p.approaches.count > 1 ? "\(p.approaches.count) approaches" : nil)
            if p.approaches.count > 1 {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(Array(p.approaches.enumerated()), id: \.offset) { i, a in
                            Button {
                                approachIndex = i
                                reader.stop()
                                if !a.languages.contains(lang) { lang = a.languages.first ?? lang }
                            } label: {
                                Chip(text: a.name, selected: approachIndex == i)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
            }
            if p.approaches.indices.contains(approachIndex) {
                approachView(p, p.approaches[approachIndex])
            }
        }
        .card()
    }

    private func approachView(_ p: Problem, _ a: Approach) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 8) {
                if let pat = content.pattern(a.pattern) { PatternBadge(pattern: pat) }
                Spacer()
                complexity("Time", a.time)
                complexity("Space", a.space)
            }
            MarkdownBlock(text: a.idea).font(.subheadline)
            if let why = a.why {
                Text(why).font(.footnote).foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true)
            }
            HStack {
                Button {
                    if reader.isPlaying { reader.pause() } else {
                        if reader.sentences.isEmpty || reader.sentenceIndex >= reader.sentences.count {
                            reader.load(a.idea + (a.why.map { " " + $0 } ?? ""))
                        }
                        reader.play()
                    }
                } label: {
                    Label(reader.isPlaying ? "Pause" : "Listen to the idea", systemImage: reader.isPlaying ? "pause.fill" : "speaker.wave.2.fill")
                        .font(.footnote.weight(.semibold))
                }
                .buttonStyle(.bordered)
                Spacer()
                Button {
                    launch = TutorialLaunch(approachId: a.id)
                } label: {
                    Label("Watch", systemImage: "play.rectangle.fill").font(.footnote.weight(.semibold))
                }
                .buttonStyle(.borderedProminent)
            }
            if a.languages.count > 1 {
                Picker("Language", selection: $lang) {
                    ForEach(a.languages, id: \.self) { l in Text(Brand.languageTitle(l)).tag(l) }
                }
                .pickerStyle(.segmented)
            }
            if let file = a.code(for: lang) ?? a.code.first {
                CodeView(code: file.src, lang: file.lang, fileName: file.name)
            }
            if a.languages.contains("java") && p.isAlgorithm {
                Text("Java snippets assume `import java.util.*;` and the standard `ListNode` / `TreeNode` classes.")
                    .font(.caption2).foregroundStyle(.secondary)
            }
        }
    }

    private func complexity(_ label: String, _ value: String) -> some View {
        VStack(spacing: 0) {
            Text(label).font(.system(size: 9, weight: .bold)).foregroundStyle(.secondary)
            Text(value).font(.system(size: 13, weight: .heavy, design: .monospaced))
        }
        .padding(.horizontal, 8).padding(.vertical, 4)
        .background(RoundedRectangle(cornerRadius: 8).fill(Color(uiColor: .tertiarySystemFill)))
    }
}

struct NotesSheet: View {
    let problem: Problem
    @EnvironmentObject private var progress: ProgressStore
    @Environment(\.dismiss) private var dismiss
    @State private var text = ""

    var body: some View {
        NavigationStack {
            TextEditor(text: $text)
                .font(.system(size: 14, design: .monospaced))
                .autocorrectionDisabled()
                .textInputAutocapitalization(.never)
                .scrollContentBackground(.hidden)
                .padding(10)
                .background(CodeTheme.background)
                .foregroundStyle(CodeTheme.plain)
                .navigationTitle("My solution & notes")
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .confirmationAction) {
                        Button("Done") {
                            progress.setNote(problem.id, text)
                            dismiss()
                        }
                    }
                }
        }
        .onAppear { text = progress.data.notes[problem.id] ?? "# Write your attempt here — it's saved on this device.\n" }
        .presentationDetents([.medium, .large])
    }
}
