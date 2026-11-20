import SwiftUI
import UIKit

// MARK: - Navigation

enum Route: Hashable {
    case problem(String)
    case track(String)
    case subject(String)
    case bite(String)
    case book(String)
    case quiz(String)
    case patternQuiz
    case flashcards(String)
    case path(String)
    case mock(String)
    case review
}

struct RouteView: View {
    let route: Route
    var body: some View {
        switch route {
        case .problem(let id): ProblemDetailView(problemId: id)
        case .track(let id): TrackView(trackId: id)
        case .subject(let id): SubjectView(subjectId: id)
        case .bite(let id): BiteDetailView(biteId: id)
        case .book(let id): BookView(bookId: id)
        case .quiz(let id): QuizView(subjectId: id)
        case .patternQuiz: PatternQuizView()
        case .flashcards(let id): FlashcardsView(subjectId: id)
        case .path(let id): CareerPathView(pathId: id)
        case .mock(let focus): MockInterviewView(focus: focus)
        case .review: ReviewQueueView()
        }
    }
}

extension View {
    func routes() -> some View {
        navigationDestination(for: Route.self) { RouteView(route: $0) }
    }

    func card(padding: CGFloat = 16, radius: CGFloat = 18) -> some View {
        self.padding(padding)
            .background(RoundedRectangle(cornerRadius: radius, style: .continuous).fill(Color(uiColor: .secondarySystemGroupedBackground)))
    }
}

// MARK: - Small components

struct DifficultyPill: View {
    let difficulty: String
    var body: some View {
        Text(difficulty)
            .font(.caption2.weight(.bold))
            .padding(.horizontal, 8).padding(.vertical, 3)
            .background(Capsule().fill(Brand.difficultyColor(difficulty).opacity(0.16)))
            .foregroundStyle(Brand.difficultyColor(difficulty))
    }
}

struct PatternBadge: View {
    let pattern: PatternInfo
    var compact = false
    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: pattern.icon).font(.system(size: compact ? 9 : 11, weight: .bold))
            if !compact { Text(pattern.name).font(.caption2.weight(.semibold)) }
        }
        .padding(.horizontal, compact ? 5 : 8).padding(.vertical, 3)
        .background(Capsule().fill(Color(hex: pattern.color).opacity(0.18)))
        .foregroundStyle(Color(hex: pattern.color).opacity(0.95))
        .accessibilityLabel(pattern.name)
    }
}

struct Chip: View {
    let text: String
    var systemImage: String? = nil
    var selected = false
    var body: some View {
        HStack(spacing: 5) {
            if let systemImage { Image(systemName: systemImage) }
            Text(text)
        }
        .font(.footnote.weight(.semibold))
        .padding(.horizontal, 12).padding(.vertical, 7)
        .background(Capsule().fill(selected ? AnyShapeStyle(Brand.gradient) : AnyShapeStyle(Color(uiColor: .tertiarySystemFill))))
        .foregroundStyle(selected ? Color.white : Color.primary)
    }
}

struct ProgressRing: View {
    let value: Double
    var color: Color = Brand.indigo
    var lineWidth: CGFloat = 6
    var body: some View {
        ZStack {
            Circle().stroke(color.opacity(0.18), lineWidth: lineWidth)
            Circle().trim(from: 0, to: max(0.001, min(1, value)))
                .stroke(color, style: StrokeStyle(lineWidth: lineWidth, lineCap: .round))
                .rotationEffect(.degrees(-90))
        }
        .animation(.easeOut(duration: 0.6), value: value)
    }
}

struct SectionHeader: View {
    let title: String
    var subtitle: String? = nil
    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(title).font(.brand(20, .heavy))
            if let subtitle { Text(subtitle).font(.subheadline).foregroundStyle(.secondary) }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

/// Inline markdown (code, bold, italics) with graceful fallback.
struct MarkdownText: View {
    let text: String
    var body: some View {
        Text(Self.attributed(text))
    }

    static func attributed(_ s: String) -> AttributedString {
        let opts = AttributedString.MarkdownParsingOptions(interpretedSyntax: .inlineOnlyPreservingWhitespace)
        return (try? AttributedString(markdown: s, options: opts)) ?? AttributedString(s)
    }
}

/// Paragraph-aware markdown block.
struct MarkdownBlock: View {
    let text: String
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            ForEach(Array(paragraphs.enumerated()), id: \.offset) { _, p in
                MarkdownText(text: p).fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    private var paragraphs: [String] {
        text.components(separatedBy: "\n\n").map {
            $0.replacingOccurrences(of: "\n", with: " ").trimmingCharacters(in: .whitespaces)
        }.filter { !$0.isEmpty }
    }
}

// MARK: - Code

struct CodeView: View {
    let code: String
    let lang: String
    var highlight: Int? = nil
    var fontSize: CGFloat = 13
    var showHeader = true
    var fileName: String? = nil
    @State private var copied = false

    var body: some View {
        let lines = SyntaxHighlighter.lines(code, lang: lang)
        VStack(alignment: .leading, spacing: 0) {
            if showHeader {
                HStack {
                    Circle().fill(Color(hex: "#FF5F57")).frame(width: 8, height: 8)
                    Circle().fill(Color(hex: "#FEBC2E")).frame(width: 8, height: 8)
                    Circle().fill(Color(hex: "#28C840")).frame(width: 8, height: 8)
                    Text(fileName ?? Brand.languageTitle(lang))
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(CodeTheme.gutter)
                        .padding(.leading, 6)
                    Spacer()
                    Button {
                        UIPasteboard.general.string = code
                        copied = true
                        DispatchQueue.main.asyncAfter(deadline: .now() + 1.4) { copied = false }
                    } label: {
                        Label(copied ? "Copied" : "Copy", systemImage: copied ? "checkmark" : "doc.on.doc")
                            .font(.caption.weight(.semibold))
                    }
                    .foregroundStyle(copied ? Brand.mint : CodeTheme.plain.opacity(0.8))
                }
                .padding(.horizontal, 12).padding(.top, 10).padding(.bottom, 6)
            }
            ScrollView(.horizontal, showsIndicators: false) {
                VStack(alignment: .leading, spacing: 0) {
                    ForEach(Array(lines.enumerated()), id: \.offset) { i, line in
                        CodeLine(number: i + 1, text: line, fontSize: fontSize, active: highlight == i + 1)
                            .id(i + 1)
                    }
                }
                .padding(.horizontal, 8).padding(.bottom, 12).padding(.top, showHeader ? 0 : 10)
            }
        }
        .background(RoundedRectangle(cornerRadius: 14, style: .continuous).fill(CodeTheme.background))
    }
}

struct CodeLine: View {
    let number: Int
    let text: AttributedString
    let fontSize: CGFloat
    let active: Bool

    var body: some View {
        HStack(alignment: .firstTextBaseline, spacing: 8) {
            Text("\(number)")
                .foregroundStyle(active ? CodeTheme.highlight : CodeTheme.gutter)
                .frame(width: 22, alignment: .trailing)
            Text(text)
                .fixedSize(horizontal: true, vertical: false)
                .padding(.trailing, 16)
        }
        .font(.system(size: fontSize, design: .monospaced))
        .padding(.vertical, 2)
        .padding(.leading, 2)
        .background(
            RoundedRectangle(cornerRadius: 5, style: .continuous)
                .fill(active ? CodeTheme.highlight.opacity(0.16) : Color.clear)
        )
        .overlay(alignment: .leading) {
            if active {
                RoundedRectangle(cornerRadius: 1.5).fill(CodeTheme.highlight).frame(width: 3)
            }
        }
        .animation(.easeInOut(duration: 0.25), value: active)
    }
}
