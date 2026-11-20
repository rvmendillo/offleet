import SwiftUI

struct LibraryView: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var audiobook: AudiobookPlayer
    @EnvironmentObject private var progress: ProgressStore

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    if let id = progress.data.lastBook, let b = content.book(id) {
                        Button {
                            audiobook.open(b)
                            audiobook.showFullPlayer = true
                        } label: {
                            HStack(spacing: 14) {
                                BookCover(book: b, size: 70)
                                VStack(alignment: .leading, spacing: 4) {
                                    Text("Continue listening").font(.caption.weight(.bold)).foregroundStyle(.white.opacity(0.8))
                                    Text(b.title).font(.headline).foregroundStyle(.white)
                                    if let pos = progress.position(book: b.id), b.chapters.indices.contains(pos.chapter) {
                                        Text(b.chapters[pos.chapter].title).font(.caption).foregroundStyle(.white.opacity(0.8)).lineLimit(1)
                                    }
                                }
                                Spacer()
                                Image(systemName: "play.circle.fill").font(.system(size: 38)).foregroundStyle(.white)
                            }
                            .padding(14)
                            .background(RoundedRectangle(cornerRadius: 20, style: .continuous).fill(Brand.gradient))
                        }
                        .buttonStyle(.plain)
                    }
                    SectionHeader(title: "Audiobooks", subtitle: "Narrated offline by your tutor. Keeps playing with the screen locked.")
                    ForEach(content.books) { b in
                        NavigationLink(value: Route.book(b.id)) {
                            HStack(spacing: 14) {
                                BookCover(book: b, size: 64)
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(b.title).font(.system(size: 17, weight: .bold, design: .rounded))
                                    Text(b.blurb).font(.caption).foregroundStyle(.secondary).lineLimit(2)
                                    Text("\(b.chapters.count) chapters").font(.caption2.weight(.semibold)).foregroundStyle(.secondary)
                                }
                                Spacer()
                                ProgressRing(value: audiobook.bookProgress(b), color: Color(hex: b.color), lineWidth: 4).frame(width: 26, height: 26)
                            }
                            .card(padding: 12)
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(16)
            }
            .background(Color(uiColor: .systemGroupedBackground))
            .navigationTitle("Listen")
            .routes()
            .miniPlayerInset()
        }
    }
}

struct BookCover: View {
    let book: Book
    var size: CGFloat = 64
    var body: some View {
        RoundedRectangle(cornerRadius: size * 0.2, style: .continuous)
            .fill(LinearGradient(colors: [Color(hex: book.color), Color(hex: book.color).opacity(0.55)], startPoint: .topLeading, endPoint: .bottomTrailing))
            .frame(width: size, height: size)
            .overlay(Image(systemName: book.icon).font(.system(size: size * 0.38, weight: .bold)).foregroundStyle(.white))
            .overlay(alignment: .bottomTrailing) {
                LogoMark(size: size * 0.26).padding(size * 0.06)
            }
    }
}

struct BookView: View {
    let bookId: String
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var audiobook: AudiobookPlayer
    @EnvironmentObject private var progress: ProgressStore
    @State private var query = ""

    var body: some View {
        if let b = content.book(bookId) {
            List {
                Section {
                    HStack(spacing: 16) {
                        BookCover(book: b, size: 90)
                        VStack(alignment: .leading, spacing: 6) {
                            Text(b.title).font(.brand(22, .heavy))
                            Text(b.blurb).font(.subheadline).foregroundStyle(.secondary)
                            Button {
                                audiobook.open(b)
                                audiobook.showFullPlayer = true
                            } label: {
                                Label(progress.position(book: b.id) == nil ? "Play" : "Resume", systemImage: "play.fill")
                            }
                            .buttonStyle(.borderedProminent)
                        }
                    }
                }
                Section("Chapters") {
                    ForEach(filtered(b), id: \.element.id) { item in
                        Button {
                            audiobook.open(b, chapter: item.offset)
                            audiobook.showFullPlayer = true
                        } label: {
                            HStack {
                                let current = audiobook.book?.id == b.id && audiobook.chapterIndex == item.offset
                                Image(systemName: current && audiobook.isPlaying ? "speaker.wave.2.fill" : "play.circle")
                                    .foregroundStyle(Color(hex: b.color))
                                    .symbolEffect(.variableColor.iterative, isActive: current && audiobook.isPlaying)
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(item.element.title).font(.subheadline.weight(.semibold)).foregroundStyle(.primary)
                                    Text("\(item.element.paras.count) parts").font(.caption2).foregroundStyle(.secondary)
                                }
                                Spacer()
                                if let pos = progress.position(book: b.id), pos.chapter > item.offset {
                                    Image(systemName: "checkmark").font(.caption).foregroundStyle(Brand.mint)
                                }
                            }
                        }
                    }
                }
            }
            .searchable(text: $query, prompt: "Find a chapter")
            .navigationTitle(b.title)
            .navigationBarTitleDisplayMode(.inline)
        } else {
            ContentUnavailableView("Book not found", systemImage: "book")
        }
    }

    private struct Item {
        let offset: Int
        let element: Chapter
    }

    private func filtered(_ b: Book) -> [Item] {
        let all = b.chapters.enumerated().map { Item(offset: $0.offset, element: $0.element) }
        let q = query.lowercased().trimmingCharacters(in: .whitespaces)
        return q.isEmpty ? all : all.filter { $0.element.title.lowercased().contains(q) }
    }
}

struct NowPlayingView: View {
    @EnvironmentObject private var audiobook: AudiobookPlayer
    @EnvironmentObject private var settings: AppSettings
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ZStack {
            LinearGradient(colors: [Color(hex: audiobook.book?.color ?? "#4F46E5").opacity(0.55), Brand.ink], startPoint: .top, endPoint: .bottom)
                .ignoresSafeArea()
            VStack(spacing: 18) {
                Capsule().fill(Color.white.opacity(0.3)).frame(width: 40, height: 5).padding(.top, 8)
                HStack {
                    Button { dismiss() } label: { Image(systemName: "chevron.down").font(.title3.weight(.bold)) }
                        .accessibilityLabel("Close player")
                    Spacer()
                    sleepMenu
                }
                .foregroundStyle(.white)
                PresenterView(presenter: settings.presenter, size: 150, owner: AudiobookPlayer.owner)
                    .overlay(Circle().stroke(Color.white.opacity(0.3), lineWidth: 3))
                    .shadow(color: .black.opacity(0.3), radius: 16, y: 8)
                VStack(spacing: 4) {
                    Text(audiobook.chapter?.title ?? "").font(.brand(20, .heavy)).multilineTextAlignment(.center).lineLimit(2)
                    Text(audiobook.book?.title ?? "").font(.subheadline).opacity(0.7)
                }
                .foregroundStyle(.white)
                ScrollView {
                    Text(audiobook.para?.t ?? "")
                        .font(.system(size: 19, weight: .medium, design: .rounded))
                        .foregroundStyle(.white.opacity(0.95))
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .id("\(audiobook.chapterIndex)-\(audiobook.paraIndex)")
                        .transition(.opacity)
                }
                .frame(maxHeight: .infinity)
                .padding(16)
                .background(RoundedRectangle(cornerRadius: 20, style: .continuous).fill(Color.white.opacity(0.08)))
                .animation(.easeInOut, value: audiobook.paraIndex)
                ProgressView(value: audiobook.chapterProgress).tint(.white)
                controls
                Menu {
                    ForEach([0.75, 1.0, 1.25, 1.5, 1.75, 2.0], id: \.self) { s in
                        Button("\(s, specifier: "%g")×") { audiobook.speed = s }
                    }
                } label: {
                    Label("Speed \(audiobook.speed, specifier: "%g")×", systemImage: "gauge.with.dots.needle.67percent")
                        .font(.footnote.weight(.semibold))
                        .padding(.horizontal, 12).padding(.vertical, 8)
                        .background(Capsule().fill(Color.white.opacity(0.12)))
                }
                .foregroundStyle(.white)
            }
            .padding(.horizontal, 20)
            .padding(.bottom, 12)
        }
        .preferredColorScheme(.dark)
    }

    private var controls: some View {
        HStack(spacing: 26) {
            Button { audiobook.prevChapter() } label: { Image(systemName: "backward.end.fill").font(.title3) }
                .accessibilityLabel("Previous chapter")
            Button { audiobook.prevPara() } label: { Image(systemName: "gobackward.15").font(.title2) }
                .accessibilityLabel("Back")
            Button { audiobook.toggle() } label: {
                Image(systemName: audiobook.isPlaying ? "pause.fill" : "play.fill")
                    .font(.system(size: 30))
                    .frame(width: 72, height: 72)
                    .background(Circle().fill(.white))
                    .foregroundStyle(Brand.ink)
                    .contentTransition(.symbolEffect(.replace))
            }
            .accessibilityLabel(audiobook.isPlaying ? "Pause" : "Play")
            Button { audiobook.nextPara() } label: { Image(systemName: "goforward.15").font(.title2) }
                .accessibilityLabel("Forward")
            Button { audiobook.nextChapter() } label: { Image(systemName: "forward.end.fill").font(.title3) }
                .accessibilityLabel("Next chapter")
        }
        .foregroundStyle(.white)
    }

    private var sleepMenu: some View {
        Menu {
            Button("Off") { audiobook.setSleep(minutes: nil) }
            ForEach([5, 15, 30, 45, 60], id: \.self) { m in
                Button("\(m) minutes") { audiobook.setSleep(minutes: m) }
            }
            Button("End of chapter") { audiobook.setSleepAtChapterEnd() }
        } label: {
            Image(systemName: (audiobook.sleepDeadline != nil || audiobook.sleepAtChapterEnd) ? "moon.zzz.fill" : "moon.zzz")
                .font(.title3)
        }
        .accessibilityLabel("Sleep timer")
    }
}

struct MiniPlayerBar: View {
    @EnvironmentObject private var audiobook: AudiobookPlayer

    var body: some View {
        if let book = audiobook.book {
            HStack(spacing: 12) {
                BookCover(book: book, size: 40)
                VStack(alignment: .leading, spacing: 2) {
                    Text(audiobook.chapter?.title ?? book.title).font(.subheadline.weight(.semibold)).lineLimit(1)
                    Text(book.title).font(.caption2).foregroundStyle(.secondary).lineLimit(1)
                }
                Spacer()
                Button { audiobook.toggle() } label: {
                    Image(systemName: audiobook.isPlaying ? "pause.fill" : "play.fill").font(.title3)
                }
                .accessibilityLabel(audiobook.isPlaying ? "Pause" : "Play")
                Button { audiobook.nextPara() } label: { Image(systemName: "goforward.15") }
                    .accessibilityLabel("Forward")
                Button { audiobook.stop() } label: { Image(systemName: "xmark").font(.caption.weight(.bold)) }
                    .accessibilityLabel("Close player")
            }
            .foregroundStyle(.primary)
            .padding(.horizontal, 12).padding(.vertical, 8)
            .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
            .overlay(alignment: .bottom) {
                GeometryReader { g in
                    Capsule().fill(Color(hex: book.color)).frame(width: g.size.width * audiobook.chapterProgress, height: 2)
                }
                .frame(height: 2)
                .padding(.horizontal, 14)
            }
            .padding(.horizontal, 10)
            .padding(.bottom, 4)
            .contentShape(Rectangle())
            .onTapGesture { audiobook.showFullPlayer = true }
        }
    }
}

extension View {
    func miniPlayerInset() -> some View {
        safeAreaInset(edge: .bottom) { MiniPlayerBar() }
    }
}
