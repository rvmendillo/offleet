import SwiftUI

struct ReviewerHomeView: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var progress: ProgressStore
    @EnvironmentObject private var settings: AppSettings

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    HStack(spacing: 14) {
                        PresenterView(presenter: settings.presenter, size: 74, owner: "none")
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Bite-sized reviewers").font(.brand(22, .heavy))
                            Text("Condensed lessons that \(settings.presenter.name) explains out loud. Learn one bite at a time.")
                                .font(.subheadline).foregroundStyle(.secondary)
                        }
                    }
                    .card()
                    LazyVGrid(columns: [GridItem(.adaptive(minimum: 160), spacing: 12)], spacing: 12) {
                        ForEach(content.subjects) { s in
                            NavigationLink(value: Route.subject(s.id)) { SubjectCard(subject: s) }
                                .buttonStyle(.plain)
                        }
                    }
                    if let pair = content.biteOfTheDay {
                        let s = pair.0
                        let b = pair.1
                        NavigationLink(value: Route.bite(b.id)) {
                            HStack(spacing: 12) {
                                Image(systemName: "sparkles").font(.title2).foregroundStyle(Brand.amber)
                                VStack(alignment: .leading, spacing: 3) {
                                    Text("Bite of the day · \(s.title)").font(.caption.weight(.bold)).foregroundStyle(.secondary)
                                    Text(b.title).font(.headline)
                                    Text(b.tldr).font(.subheadline).foregroundStyle(.secondary).lineLimit(2)
                                }
                                Spacer()
                            }
                            .card()
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(16)
            }
            .background(Color(uiColor: .systemGroupedBackground))
            .navigationTitle("Learn")
            .routes()
            .miniPlayerInset()
        }
    }
}

struct SubjectCard: View {
    let subject: Subject
    @EnvironmentObject private var progress: ProgressStore

    var body: some View {
        let bites = subject.allBites
        let learned = bites.filter { progress.isLearned($0.id) }.count
        let color = Color(hex: subject.color)
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Image(systemName: subject.icon).font(.title2.weight(.bold)).foregroundStyle(color)
                Spacer()
                ProgressRing(value: bites.isEmpty ? 0 : Double(learned) / Double(bites.count), color: color, lineWidth: 5)
                    .frame(width: 30, height: 30)
            }
            Text(subject.title).font(.brand(18, .heavy)).lineLimit(2).minimumScaleFactor(0.8)
            Text("\(learned)/\(bites.count) bites").font(.caption.weight(.semibold)).foregroundStyle(.secondary)
        }
        .padding(14)
        .frame(maxWidth: .infinity, minHeight: 130, alignment: .topLeading)
        .background(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .fill(Color(uiColor: .secondarySystemGroupedBackground))
                .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).fill(color.opacity(0.08)))
        )
    }
}

struct SubjectView: View {
    let subjectId: String
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var progress: ProgressStore
    @EnvironmentObject private var audiobook: AudiobookPlayer

    var body: some View {
        if let s = content.subject(subjectId) {
            List {
                Section {
                    Text(s.blurb).font(.subheadline).foregroundStyle(.secondary)
                    HStack(spacing: 10) {
                        NavigationLink(value: Route.flashcards(s.id)) {
                            Label("Flashcards", systemImage: "rectangle.stack.fill")
                        }
                        .buttonStyle(.bordered)
                        NavigationLink(value: Route.quiz(s.id)) {
                            Label("Quiz", systemImage: "checkmark.circle.badge.questionmark")
                        }
                        .buttonStyle(.bordered)
                        if let book = content.book("rev-\(s.id)") {
                            Button {
                                audiobook.open(book)
                                audiobook.showFullPlayer = true
                            } label: {
                                Label("Listen", systemImage: "headphones")
                            }
                            .buttonStyle(.borderedProminent)
                        }
                    }
                    .font(.footnote.weight(.semibold))
                }
                ForEach(Array(s.units.enumerated()), id: \.offset) { _, u in
                    Section {
                        ForEach(u.bites) { b in
                            NavigationLink(value: Route.bite(b.id)) {
                                HStack(spacing: 10) {
                                    Image(systemName: progress.isLearned(b.id) ? "checkmark.circle.fill" : "circle")
                                        .foregroundStyle(progress.isLearned(b.id) ? Brand.mint : Color.secondary)
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(b.title).font(.system(size: 16, weight: .semibold, design: .rounded))
                                        Text(b.tldr).font(.caption).foregroundStyle(.secondary).lineLimit(2)
                                    }
                                }
                            }
                        }
                    } header: {
                        Text(u.title)
                    } footer: {
                        if !u.blurb.isEmpty { Text(u.blurb) }
                    }
                }
            }
            .navigationTitle(s.title)
        } else {
            ContentUnavailableView("Subject not found", systemImage: "books.vertical")
        }
    }
}

struct BiteDetailView: View {
    let biteId: String
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var progress: ProgressStore
    @EnvironmentObject private var settings: AppSettings
    @EnvironmentObject private var audiobook: AudiobookPlayer
    @StateObject private var reader = ScriptReader(owner: "bite")
    @State private var picked: Int?
    @State private var currentId: String = ""

    var body: some View {
        let id = currentId.isEmpty ? biteId : currentId
        if let pair = content.bite(id) {
            let s = pair.0
            let b = pair.1
            let color = Color(hex: s.color)
            let all = s.allBites
            let idx = all.firstIndex { $0.id == b.id } ?? 0
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    presenterPanel(b, color: color)
                    VStack(alignment: .leading, spacing: 10) {
                        Text(b.title).font(.brand(26, .heavy))
                        Text(b.tldr).font(.title3.weight(.medium)).foregroundStyle(color)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    VStack(alignment: .leading, spacing: 10) {
                        ForEach(Array(b.points.enumerated()), id: \.offset) { _, pt in
                            HStack(alignment: .firstTextBaseline, spacing: 10) {
                                Circle().fill(color).frame(width: 7, height: 7)
                                MarkdownText(text: pt).fixedSize(horizontal: false, vertical: true)
                            }
                        }
                    }
                    .card()
                    if let f = b.formula {
                        VStack(alignment: .leading, spacing: 6) {
                            Label("Formula", systemImage: "function").font(.caption.weight(.bold)).foregroundStyle(.secondary)
                            Text(f).font(.system(size: 18, weight: .semibold, design: .serif))
                                .textSelection(.enabled)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(16)
                        .background(RoundedRectangle(cornerRadius: 16).fill(color.opacity(0.12)))
                    }
                    if let ex = b.example {
                        VStack(alignment: .leading, spacing: 6) {
                            Label("Example", systemImage: "lightbulb.fill").font(.caption.weight(.bold)).foregroundStyle(Brand.amber)
                            MarkdownText(text: ex).fixedSize(horizontal: false, vertical: true)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .card()
                    }
                    if let tip = b.tip {
                        Label { Text(tip).fixedSize(horizontal: false, vertical: true) } icon: {
                            Image(systemName: "brain.head.profile").foregroundStyle(Brand.violet)
                        }
                        .font(.subheadline)
                        .card()
                    }
                    if let q = b.quiz { quiz(q, biteId: b.id) }
                    HStack {
                        Button {
                            progress.setLearned(b.id, !progress.isLearned(b.id))
                        } label: {
                            Label(progress.isLearned(b.id) ? "Learned" : "Mark as learned",
                                  systemImage: progress.isLearned(b.id) ? "checkmark.seal.fill" : "seal")
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(progress.isLearned(b.id) ? Brand.mint : Brand.indigo)
                        Spacer()
                        Button { go(all, idx - 1) } label: { Image(systemName: "chevron.left") }
                            .buttonStyle(.bordered).disabled(idx == 0)
                        Button { go(all, idx + 1) } label: { Label("Next", systemImage: "chevron.right") }
                            .buttonStyle(.bordered).disabled(idx + 1 >= all.count)
                    }
                    Text("\(idx + 1) of \(all.count) in \(s.title)").font(.caption).foregroundStyle(.secondary)
                }
                .padding(16)
            }
            .background(Color(uiColor: .systemGroupedBackground))
            .navigationTitle(s.title)
            .navigationBarTitleDisplayMode(.inline)
            .onDisappear { reader.stop() }
        } else {
            ContentUnavailableView("Bite not found", systemImage: "questionmark")
        }
    }

    private func go(_ all: [Bite], _ i: Int) {
        guard all.indices.contains(i) else { return }
        reader.stop()
        picked = nil
        withAnimation { currentId = all[i].id }
    }

    private func presenterPanel(_ b: Bite, color: Color) -> some View {
        HStack(spacing: 14) {
            PresenterView(presenter: settings.presenter, size: 86, owner: "bite")
                .overlay(Circle().stroke(color.opacity(0.6), lineWidth: 3))
            VStack(alignment: .leading, spacing: 8) {
                if reader.isPlaying, reader.sentences.indices.contains(reader.sentenceIndex) {
                    Text(reader.sentences[reader.sentenceIndex])
                        .font(.subheadline.weight(.medium))
                        .lineLimit(4)
                        .transition(.opacity)
                        .id(reader.sentenceIndex)
                } else {
                    Text("Let \(settings.presenter.name) explain this bite in under a minute.")
                        .font(.subheadline).foregroundStyle(.secondary)
                }
                Button {
                    if audiobook.isPlaying { audiobook.pause() }
                    if reader.isPlaying {
                        reader.pause()
                    } else {
                        if reader.sentences.isEmpty || reader.sentenceIndex >= reader.sentences.count { reader.load(b.say) }
                        reader.play()
                    }
                } label: {
                    Label(reader.isPlaying ? "Pause" : "Explain it to me", systemImage: reader.isPlaying ? "pause.fill" : "play.fill")
                        .font(.footnote.weight(.bold))
                }
                .buttonStyle(.borderedProminent)
                .tint(color)
            }
            Spacer(minLength: 0)
        }
        .animation(.easeInOut, value: reader.sentenceIndex)
        .card()
        .onChange(of: b.id) { _, _ in reader.stop(); reader.load(b.say) }
        .onAppear { reader.load(b.say) }
    }

    private func quiz(_ q: Quiz, biteId: String) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Label("Quick check", systemImage: "checkmark.circle.badge.questionmark").font(.caption.weight(.bold)).foregroundStyle(.secondary)
            Text(q.q).font(.headline).fixedSize(horizontal: false, vertical: true)
            ForEach(Array(q.opts.enumerated()), id: \.offset) { i, opt in
                Button {
                    guard picked == nil else { return }
                    picked = i
                    progress.recordQuiz(biteId, correct: i == q.a)
                } label: {
                    HStack {
                        Text(opt).multilineTextAlignment(.leading)
                        Spacer()
                        if picked != nil, i == q.a { Image(systemName: "checkmark.circle.fill").foregroundStyle(Brand.mint) }
                        if picked == i, i != q.a { Image(systemName: "xmark.circle.fill").foregroundStyle(.red) }
                    }
                    .padding(12)
                    .background(RoundedRectangle(cornerRadius: 12).fill(optionFill(i, q)))
                }
                .buttonStyle(.plain)
            }
            if picked != nil {
                Text(q.why).font(.footnote).foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true)
            }
        }
        .card()
        .sensoryFeedback(.selection, trigger: picked)
    }

    private func optionFill(_ i: Int, _ q: Quiz) -> Color {
        guard let picked else { return Color(uiColor: .tertiarySystemFill) }
        if i == q.a { return Brand.mint.opacity(0.22) }
        if i == picked { return Color.red.opacity(0.18) }
        return Color(uiColor: .tertiarySystemFill)
    }
}

struct FlashcardsView: View {
    let subjectId: String
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var progress: ProgressStore
    @State private var flipped: Set<String> = []
    @State private var shuffled: [Bite] = []

    var body: some View {
        let s = content.subject(subjectId)
        let color = Color(hex: s?.color ?? "#4F46E5")
        TabView {
            ForEach(shuffled) { b in
                VStack(spacing: 16) {
                    Spacer(minLength: 0)
                    VStack(spacing: 14) {
                        Text(flipped.contains(b.id) ? "Answer" : "Do you remember…").font(.caption.weight(.bold)).foregroundStyle(.secondary)
                        Text(b.title).font(.brand(26, .heavy)).multilineTextAlignment(.center)
                        if flipped.contains(b.id) {
                            Text(b.tldr).font(.title3).multilineTextAlignment(.center).foregroundStyle(color)
                            VStack(alignment: .leading, spacing: 6) {
                                ForEach(Array(b.points.prefix(3).enumerated()), id: \.offset) { _, p in
                                    Text("• " + p).font(.subheadline).fixedSize(horizontal: false, vertical: true)
                                }
                            }
                            if let f = b.formula { Text(f).font(.system(.body, design: .serif).weight(.semibold)) }
                        } else {
                            Text("Tap to flip").font(.footnote).foregroundStyle(.secondary)
                        }
                    }
                    .padding(24)
                    .frame(maxWidth: .infinity, minHeight: 360)
                    .background(RoundedRectangle(cornerRadius: 26, style: .continuous).fill(Color(uiColor: .secondarySystemGroupedBackground)))
                    .overlay(RoundedRectangle(cornerRadius: 26, style: .continuous).stroke(color.opacity(0.4), lineWidth: 2))
                    .rotation3DEffect(.degrees(flipped.contains(b.id) ? 360 : 0), axis: (x: 0, y: 1, z: 0))
                    .onTapGesture {
                        withAnimation(.spring(response: 0.5, dampingFraction: 0.8)) { flipped.formSymmetricDifference([b.id]) }
                    }
                    Button {
                        progress.setLearned(b.id, true)
                    } label: {
                        Label(progress.isLearned(b.id) ? "Learned" : "I know this", systemImage: "checkmark")
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(progress.isLearned(b.id) ? Brand.mint : color)
                    Spacer(minLength: 30)
                }
                .padding(20)
            }
        }
        .tabViewStyle(.page(indexDisplayMode: .never))
        .background(Color(uiColor: .systemGroupedBackground))
        .navigationTitle("Flashcards")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear { if shuffled.isEmpty { shuffled = (s?.allBites ?? []).shuffled() } }
    }
}

struct QuizView: View {
    let subjectId: String
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var progress: ProgressStore
    @State private var questions: [Bite] = []
    @State private var index = 0
    @State private var picked: Int?
    @State private var score = 0

    var body: some View {
        VStack(spacing: 16) {
            if questions.isEmpty {
                ContentUnavailableView("No questions", systemImage: "questionmark.circle")
            } else if index >= questions.count {
                Spacer()
                Image(systemName: score * 2 >= questions.count ? "trophy.fill" : "arrow.clockwise.circle.fill")
                    .font(.system(size: 60)).foregroundStyle(Brand.warm)
                Text("\(score) / \(questions.count)").font(.brand(44, .heavy))
                Text(score * 2 >= questions.count ? "Great work!" : "Review the bites and try again.").foregroundStyle(.secondary)
                Button("Try another round") { start() }.buttonStyle(.borderedProminent)
                Spacer()
            } else {
                let b = questions[index]
                if let q = b.quiz {
                    ProgressView(value: Double(index), total: Double(questions.count)).tint(Brand.indigo)
                    Text(b.title).font(.caption.weight(.bold)).foregroundStyle(.secondary)
                    Text(q.q).font(.title3.weight(.semibold)).multilineTextAlignment(.center).fixedSize(horizontal: false, vertical: true)
                    ForEach(Array(q.opts.enumerated()), id: \.offset) { i, opt in
                        Button {
                            guard picked == nil else { return }
                            picked = i
                            if i == q.a { score += 1 }
                            progress.recordQuiz(b.id, correct: i == q.a)
                        } label: {
                            Text(opt).frame(maxWidth: .infinity, alignment: .leading).padding(14)
                                .background(RoundedRectangle(cornerRadius: 14).fill(fill(i, q)))
                        }
                        .buttonStyle(.plain)
                    }
                    if picked != nil {
                        Text(q.why).font(.footnote).foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true)
                        Button(index + 1 < questions.count ? "Next" : "See score") {
                            picked = nil
                            index += 1
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    Spacer()
                }
            }
        }
        .padding(20)
        .navigationTitle("Quiz")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear { if questions.isEmpty { start() } }
        .sensoryFeedback(.selection, trigger: picked)
    }

    private func start() {
        let pool = (content.subject(subjectId)?.allBites ?? []).filter { $0.quiz != nil }
        questions = Array(pool.shuffled().prefix(10))
        index = 0
        score = 0
        picked = nil
    }

    private func fill(_ i: Int, _ q: Quiz) -> Color {
        guard let picked else { return Color(uiColor: .secondarySystemGroupedBackground) }
        if i == q.a { return Brand.mint.opacity(0.25) }
        if i == picked { return Color.red.opacity(0.2) }
        return Color(uiColor: .secondarySystemGroupedBackground)
    }
}
