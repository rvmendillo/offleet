import SwiftUI

/// Full-screen animated walkthrough: visual stage + presenter + synced code + captions + transport controls.
struct TutorialPlayerView: View {
    let problem: Problem
    let approachId: String

    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var settings: AppSettings
    @EnvironmentObject private var progress: ProgressStore
    @EnvironmentObject private var audiobook: AudiobookPlayer
    @Environment(\.dismiss) private var dismiss
    @StateObject private var player = TutorialPlayer()
    @State private var lang = "python"
    @State private var scrub: Double = 0
    @State private var scrubbing = false

    private var approach: Approach? { problem.approaches.first { $0.id == approachId } ?? problem.approaches.first }

    var body: some View {
        GeometryReader { geo in
            let wide = geo.size.width > geo.size.height * 1.1
            ZStack {
                LinearGradient(colors: [Brand.ink, Brand.stage], startPoint: .top, endPoint: .bottom).ignoresSafeArea()
                VStack(spacing: 10) {
                    topBar
                    if wide {
                        HStack(alignment: .top, spacing: 12) {
                            stage.frame(maxWidth: .infinity, maxHeight: .infinity)
                            codePanel.frame(width: geo.size.width * 0.42)
                        }
                    } else {
                        stage.frame(maxHeight: .infinity)
                        codePanel.frame(height: min(geo.size.height * 0.27, 240))
                    }
                    controls
                }
                .padding(.horizontal, 14)
                .padding(.bottom, 6)
            }
        }
        .preferredColorScheme(.dark)
        .onAppear(perform: setup)
        .onDisappear { player.stop() }
        .onChange(of: player.finished) { _, done in
            if done, let a = approach { progress.markWatched("\(problem.id)#\(a.id)") }
        }
        .onChange(of: player.index) { _, i in
            if !scrubbing { scrub = Double(i) }
        }
    }

    private func setup() {
        if audiobook.isPlaying { audiobook.pause() }
        let tut = content.tutorial(for: problem.id)
        player.presenterName = settings.presenter.name
        player.load(tut[approach?.id ?? ""] ?? [])
        if let a = approach {
            lang = a.languages.contains(settings.language) ? settings.language : (a.languages.first ?? "python")
        }
        if let f = DebugLaunch.frame {
            player.go(to: min(f, max(player.frames.count - 1, 0)))
            scrub = Double(player.index)
            return
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) { player.play() }
    }

    // MARK: top bar

    private var topBar: some View {
        HStack(spacing: 12) {
            Button {
                player.stop()
                dismiss()
            } label: {
                Image(systemName: "xmark").font(.system(size: 15, weight: .bold))
                    .frame(width: 34, height: 34)
                    .background(Circle().fill(Color.white.opacity(0.1)))
            }
            .accessibilityLabel("Close tutorial")
            VStack(alignment: .leading, spacing: 1) {
                Text(problem.title).font(.brand(16, .heavy)).lineLimit(1)
                Text(approach?.name ?? "").font(.caption).foregroundStyle(.white.opacity(0.6)).lineLimit(1)
            }
            Spacer()
            if let a = approach, problem.isAlgorithm, a.languages.count > 1 {
                Menu {
                    ForEach(a.languages, id: \.self) { l in
                        Button(Brand.languageTitle(l)) { lang = l }
                    }
                } label: {
                    Label(Brand.languageTitle(lang), systemImage: "chevron.left.forwardslash.chevron.right")
                        .font(.caption.weight(.bold))
                        .padding(.horizontal, 10).padding(.vertical, 7)
                        .background(Capsule().fill(Color.white.opacity(0.1)))
                }
            }
            Button {
                settings.captions.toggle()
            } label: {
                Image(systemName: settings.captions ? "captions.bubble.fill" : "captions.bubble")
                    .frame(width: 34, height: 34)
                    .background(Circle().fill(Color.white.opacity(0.1)))
            }
            .accessibilityLabel("Toggle captions")
        }
        .foregroundStyle(.white)
        .padding(.top, 6)
    }

    // MARK: stage

    private var stage: some View {
        ZStack(alignment: .bottomLeading) {
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .fill(Color.white.opacity(0.04))
                .overlay(RoundedRectangle(cornerRadius: 22, style: .continuous).stroke(Color.white.opacity(0.08)))
            VStack(spacing: 0) {
                if let f = player.frame {
                    StageContent(frame: f, problem: problem, approach: approach, patterns: content.patterns)
                        .id(f.isStep ? "viz" : "card-\(player.index)")
                        .transition(.asymmetric(insertion: .opacity.combined(with: .scale(scale: 0.97)), removal: .opacity))
                        .padding(14)
                        .padding(.bottom, 70)
                } else {
                    ContentUnavailableView("No tutorial yet", systemImage: "film", description: Text("This problem doesn't have an animated walkthrough."))
                }
            }
            HStack(alignment: .bottom, spacing: 10) {
                PresenterBadge(presenter: settings.presenter, size: 66, owner: TutorialPlayer.owner)
                if settings.captions, let f = player.frame, f.isStep || ["complexity", "outro", "example"].contains(f.k) {
                    Text(f.cap)
                        .font(.system(size: 15, weight: .medium, design: .rounded))
                        .foregroundStyle(.white)
                        .lineLimit(5)
                        .minimumScaleFactor(0.75)
                        .padding(.horizontal, 12).padding(.vertical, 9)
                        .background(
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .fill(Color.black.opacity(0.55))
                                .overlay(RoundedRectangle(cornerRadius: 14, style: .continuous).stroke(Color.white.opacity(0.1)))
                        )
                        .id(player.index)
                        .transition(.opacity)
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
            }
            .padding(10)
        }
        .environment(\.vizNames, VizNames(map: lang == "java" ? (approach?.jn ?? [:]) : [:]))
        .animation(.easeInOut(duration: 0.3), value: player.index)
    }

    // MARK: code

    private var codePanel: some View {
        let f = player.frame
        let a = approach
        let fileIndex = f?.file
        let file: CodeFile? = {
            guard let a else { return nil }
            if let fileIndex, a.code.indices.contains(fileIndex) { return a.code[fileIndex] }
            return a.code(for: lang) ?? a.code.first
        }()
        let line: Int? = {
            guard let ln = f?.ln else { return nil }
            if let l = ln["line"] { return l }
            return ln[file?.lang ?? lang]
        }()
        return ScrollViewReader { proxy in
            ScrollView(.vertical, showsIndicators: false) {
                if let file {
                    CodeView(code: file.src, lang: file.lang, highlight: line, fontSize: 12, fileName: file.name)
                }
            }
            .onChange(of: line) { _, l in
                guard let l else { return }
                // leading x keeps the gutter and the start of long lines in view; only the vertical position is centred
                withAnimation(.easeInOut(duration: 0.3)) { proxy.scrollTo(l, anchor: UnitPoint(x: 0, y: 0.5)) }
            }
        }
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
    }

    // MARK: controls

    private var controls: some View {
        VStack(spacing: 6) {
            if player.frames.count > 1 {
                Slider(value: $scrub, in: 0...Double(max(player.frames.count - 1, 1)), step: 1) { editing in
                    scrubbing = editing
                    if !editing { player.go(to: Int(scrub)) }
                }
                .tint(Brand.amber)
            }
            HStack {
                Text("\(player.index + 1)/\(max(player.frames.count, 1))")
                    .font(.caption.monospacedDigit())
                    .foregroundStyle(.white.opacity(0.6))
                    .frame(width: 56, alignment: .leading)
                Spacer()
                Button { player.previous() } label: {
                    Image(systemName: "backward.fill").font(.title3)
                }
                .accessibilityLabel("Previous step")
                Button { player.toggle() } label: {
                    Image(systemName: player.finished ? "arrow.counterclockwise" : (player.isPlaying ? "pause.fill" : "play.fill"))
                        .font(.title)
                        .frame(width: 64, height: 64)
                        .background(Circle().fill(Brand.gradient))
                        .contentTransition(.symbolEffect(.replace))
                }
                .padding(.horizontal, 22)
                .accessibilityLabel(player.isPlaying ? "Pause" : "Play")
                Button { player.next() } label: {
                    Image(systemName: "forward.fill").font(.title3)
                }
                .accessibilityLabel("Next step")
                Spacer()
                Menu {
                    ForEach([0.75, 1.0, 1.25, 1.5], id: \.self) { s in
                        Button("\(s, specifier: "%g")×") {
                            player.speed = s
                        }
                    }
                } label: {
                    Text("\(player.speed, specifier: "%g")×")
                        .font(.caption.weight(.bold))
                        .frame(width: 56, height: 30)
                        .background(Capsule().fill(Color.white.opacity(0.1)))
                }
            }
            .foregroundStyle(.white)
        }
    }
}

/// What the big stage shows for each kind of frame.
private struct StageContent: View {
    let frame: Frame
    let problem: Problem
    let approach: Approach?
    let patterns: [PatternInfo]

    private func patternLookup(_ id: String) -> PatternInfo? { patterns.first { $0.id == id } }

    var body: some View {
        switch frame.k {
        case "step", "trace", "skip", "done":
            VStack(alignment: .leading, spacing: 8) {
                if frame.k == "skip" {
                    Label("Fast-forward", systemImage: "forward.end.alt.fill")
                        .font(.caption.weight(.bold)).foregroundStyle(Brand.amber)
                }
                if frame.k == "done" {
                    Label("Answer", systemImage: "checkmark.seal.fill")
                        .font(.caption.weight(.bold)).foregroundStyle(Brand.mint)
                }
                if let st = frame.st { VizStage(state: st) } else { Spacer() }
            }
        case "title":
            VStack(spacing: 16) {
                Spacer()
                LogoTile(size: 64)
                Text(frame.card?.title ?? problem.title)
                    .font(.brand(28, .heavy)).multilineTextAlignment(.center)
                    .foregroundStyle(.white)
                if let p = frame.card?.pattern.flatMap(patternLookup) {
                    PatternBadge(pattern: p)
                }
                Text(frame.card?.sub ?? "").font(.subheadline).foregroundStyle(.white.opacity(0.6))
                Spacer()
            }
            .frame(maxWidth: .infinity)
        case "problem", "example":
            VStack(alignment: .leading, spacing: 12) {
                Label(frame.k == "problem" ? "The problem" : "Example", systemImage: frame.k == "problem" ? "questionmark.bubble.fill" : "text.magnifyingglass")
                    .font(.headline).foregroundStyle(Brand.aqua)
                ForEach(Array((frame.card?.lines ?? [frame.cap]).enumerated()), id: \.offset) { i, line in
                    Text(line)
                        .font(frame.k == "example" ? .system(size: 16, weight: i < 2 ? .semibold : .regular, design: .monospaced) : .system(size: 18, weight: .medium, design: .rounded))
                        .foregroundStyle(.white.opacity(i < 2 ? 0.95 : 0.75))
                        .fixedSize(horizontal: false, vertical: true)
                }
                Spacer()
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        case "idea":
            let p = frame.card?.pattern.flatMap(patternLookup)
            VStack(alignment: .leading, spacing: 14) {
                HStack(spacing: 10) {
                    Image(systemName: p?.icon ?? "lightbulb.fill")
                        .font(.system(size: 26, weight: .bold))
                        .foregroundStyle(Color(hex: p?.color ?? "#FBBF24"))
                        .frame(width: 52, height: 52)
                        .background(RoundedRectangle(cornerRadius: 14).fill(Color(hex: p?.color ?? "#FBBF24").opacity(0.18)))
                    VStack(alignment: .leading) {
                        Text("Key idea").font(.caption.weight(.bold)).foregroundStyle(.white.opacity(0.6))
                        Text(p?.name ?? approach?.name ?? "").font(.brand(20, .heavy)).foregroundStyle(.white)
                    }
                }
                Text(frame.cap)
                    .font(.system(size: 19, weight: .medium, design: .rounded))
                    .foregroundStyle(.white.opacity(0.92))
                    .fixedSize(horizontal: false, vertical: true)
                Spacer()
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        case "complexity":
            VStack(spacing: 18) {
                Spacer()
                Text("Complexity").font(.headline).foregroundStyle(.white.opacity(0.7))
                HStack(spacing: 14) {
                    badge("Time", frame.card?.time ?? approach?.time ?? "", Brand.aqua)
                    badge("Space", frame.card?.space ?? approach?.space ?? "", Brand.amber)
                }
                Spacer()
            }
            .frame(maxWidth: .infinity)
        case "code":
            VStack(alignment: .leading, spacing: 10) {
                if let a = approach, let fi = frame.file, a.code.indices.contains(fi) {
                    Label(a.code[fi].name, systemImage: "doc.text.fill").font(.headline).foregroundStyle(Brand.aqua)
                }
                Text(frame.cap)
                    .font(.system(size: 19, weight: .medium, design: .rounded))
                    .foregroundStyle(.white.opacity(0.92))
                    .fixedSize(horizontal: false, vertical: true)
                Spacer()
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        default:
            VStack(spacing: 16) {
                Spacer()
                Image(systemName: "party.popper.fill").font(.system(size: 46)).foregroundStyle(Brand.warm)
                Text("Your turn!").font(.brand(28, .heavy)).foregroundStyle(.white)
                Text("Open the code below, then try it yourself without peeking.")
                    .multilineTextAlignment(.center).foregroundStyle(.white.opacity(0.7))
                Spacer()
            }
            .frame(maxWidth: .infinity)
        }
    }

    private func badge(_ title: String, _ value: String, _ color: Color) -> some View {
        VStack(spacing: 6) {
            Text(title).font(.caption.weight(.bold)).foregroundStyle(.white.opacity(0.6))
            Text(value).font(.system(size: 28, weight: .heavy, design: .monospaced)).foregroundStyle(color)
                .minimumScaleFactor(0.5).lineLimit(1)
        }
        .frame(maxWidth: 150)
        .padding(.vertical, 18)
        .background(RoundedRectangle(cornerRadius: 18).fill(color.opacity(0.12)))
    }
}
