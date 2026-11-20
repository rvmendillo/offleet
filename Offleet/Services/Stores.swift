import Foundation
import SwiftUI

// MARK: - Content

@MainActor
final class ContentStore: ObservableObject {
    @Published private(set) var patterns: [PatternInfo] = []
    @Published private(set) var problems: [Problem] = []
    @Published private(set) var subjects: [Subject] = []
    @Published private(set) var books: [Book] = []
    @Published private(set) var tracks: [Track] = []
    @Published private(set) var paths: [CareerPath] = []
    @Published private(set) var isLoaded = false
    @Published private(set) var loadError: String?

    private var problemIndex: [String: Problem] = [:]
    private var patternIndex: [String: PatternInfo] = [:]
    private var biteIndex: [String: (Subject, Bite)] = [:]
    private var tutorialCache: [String: [String: [Frame]]] = [:]
    private var root: URL?

    func load() async {
        guard !isLoaded else { return }
        guard let root = ContentLoader.folder() else {
            loadError = "Content folder missing from the app bundle."
            return
        }
        self.root = root
        let result: Result<LoadedContent, Error> = await Task.detached(priority: .userInitiated) {
            do { return .success(try ContentLoader.loadAll(from: root)) } catch { return .failure(error) }
        }.value
        switch result {
        case .success(let c):
            patterns = c.patterns
            problems = c.problems
            subjects = c.subjects
            books = c.books
            tracks = c.tracks
            paths = c.paths
            problemIndex = Dictionary(uniqueKeysWithValues: c.problems.map { ($0.id, $0) })
            patternIndex = Dictionary(uniqueKeysWithValues: c.patterns.map { ($0.id, $0) })
            var bi: [String: (Subject, Bite)] = [:]
            for s in c.subjects { for b in s.allBites { bi[b.id] = (s, b) } }
            biteIndex = bi
            isLoaded = true
        case .failure(let e):
            loadError = String(describing: e)
        }
    }

    func problem(_ id: String) -> Problem? { problemIndex[id] }
    func pattern(_ id: String) -> PatternInfo? { patternIndex[id] }
    func bite(_ id: String) -> (Subject, Bite)? { biteIndex[id] }
    func subject(_ id: String) -> Subject? { subjects.first { $0.id == id } }
    func book(_ id: String) -> Book? { books.first { $0.id == id } }
    func track(_ id: String) -> Track? { tracks.first { $0.id == id } }
    func careerPath(_ id: String) -> CareerPath? { paths.first { $0.id == id } }

    /// Problems matching a mock-interview focus such as "any", "pattern:sliding-window" or "cat:ai-engineering".
    func problems(focus: String, difficulty: String) -> [Problem] {
        problems.filter { p in
            guard p.isAlgorithm else { return false }
            if difficulty != "Any" && p.diff != difficulty { return false }
            if focus.hasPrefix("pattern:") { return p.patterns.contains(String(focus.dropFirst(8))) }
            if focus.hasPrefix("cat:") { return p.cat == String(focus.dropFirst(4)) }
            return true
        }
    }

    func tutorial(for problemId: String) -> [String: [Frame]] {
        if let t = tutorialCache[problemId] { return t }
        guard let root else { return [:] }
        let t = ContentLoader.tutorial(problemId: problemId, root: root)
        tutorialCache[problemId] = t
        return t
    }

    var algorithmProblems: [Problem] { problems.filter(\.isAlgorithm) }

    /// A deterministic "bite of the day".
    var biteOfTheDay: (Subject, Bite)? {
        let all = subjects.flatMap { s in s.allBites.map { (s, $0) } }
        guard !all.isEmpty else { return nil }
        let day = Calendar.current.ordinality(of: .day, in: .era, for: Date()) ?? 0
        return all[day % all.count]
    }
}

// MARK: - Progress

struct BookPosition: Codable, Hashable {
    var chapter: Int
    var para: Int
}

struct SRSItem: Codable, Hashable {
    var interval: Int
    var ease: Double
    var due: String
    var reps: Int
}

struct MockAttempt: Codable, Hashable, Identifiable {
    var id: String
    var problemId: String
    var date: String
    var seconds: Int
    var rating: Int
    var hints: Int
}

struct ProgressData: Codable {
    var solved: Set<String> = []
    var bookmarked: Set<String> = []
    var watched: Set<String> = []
    var learned: Set<String> = []
    var quiz: [String: Bool] = [:]
    var notes: [String: String] = [:]
    var lastProblem: String?
    var lastBook: String?
    var books: [String: BookPosition] = [:]
    var activeDays: [String] = []
    var activity: [String: Int] = [:]
    var srs: [String: SRSItem] = [:]
    var mocks: [MockAttempt] = []

    init() {}

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        solved = (try? c.decodeIfPresent(Set<String>.self, forKey: .solved)) ?? []
        bookmarked = (try? c.decodeIfPresent(Set<String>.self, forKey: .bookmarked)) ?? []
        watched = (try? c.decodeIfPresent(Set<String>.self, forKey: .watched)) ?? []
        learned = (try? c.decodeIfPresent(Set<String>.self, forKey: .learned)) ?? []
        quiz = (try? c.decodeIfPresent([String: Bool].self, forKey: .quiz)) ?? [:]
        notes = (try? c.decodeIfPresent([String: String].self, forKey: .notes)) ?? [:]
        lastProblem = try? c.decodeIfPresent(String.self, forKey: .lastProblem)
        lastBook = try? c.decodeIfPresent(String.self, forKey: .lastBook)
        books = (try? c.decodeIfPresent([String: BookPosition].self, forKey: .books)) ?? [:]
        activeDays = (try? c.decodeIfPresent([String].self, forKey: .activeDays)) ?? []
        activity = (try? c.decodeIfPresent([String: Int].self, forKey: .activity)) ?? [:]
        srs = (try? c.decodeIfPresent([String: SRSItem].self, forKey: .srs)) ?? [:]
        mocks = (try? c.decodeIfPresent([MockAttempt].self, forKey: .mocks)) ?? []
    }
}

@MainActor
final class ProgressStore: ObservableObject {
    @Published private(set) var data = ProgressData()
    private let url: URL
    private var saveTask: Task<Void, Never>?

    init() {
        let dir = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        url = dir.appendingPathComponent("offleet-progress.json")
        if let d = try? Data(contentsOf: url), let p = try? JSONDecoder().decode(ProgressData.self, from: d) {
            data = p
        }
    }

    private func mutate(_ change: (inout ProgressData) -> Void) {
        change(&data)
        let today = Self.dayString(Date())
        if data.activeDays.last != today { data.activeDays.append(today) }
        data.activity[today, default: 0] += 1
        scheduleSave()
    }

    static func day(offset: Int) -> String {
        dayString(Calendar.current.date(byAdding: .day, value: offset, to: Date()) ?? Date())
    }

    private func scheduleSave() {
        saveTask?.cancel()
        let snapshot = data
        let url = url
        saveTask = Task.detached(priority: .utility) {
            try? await Task.sleep(nanoseconds: 400_000_000)
            if Task.isCancelled { return }
            if let d = try? JSONEncoder().encode(snapshot) { try? d.write(to: url, options: .atomic) }
        }
    }

    static func dayString(_ d: Date) -> String {
        let f = DateFormatter()
        f.calendar = Calendar(identifier: .gregorian)
        f.dateFormat = "yyyy-MM-dd"
        return f.string(from: d)
    }

    func isSolved(_ id: String) -> Bool { data.solved.contains(id) }
    func isBookmarked(_ id: String) -> Bool { data.bookmarked.contains(id) }
    func isLearned(_ id: String) -> Bool { data.learned.contains(id) }

    func toggleSolved(_ id: String) {
        mutate {
            $0.solved.formSymmetricDifference([id])
            if $0.solved.contains(id) && $0.srs["p:" + id] == nil {
                $0.srs["p:" + id] = SRSItem(interval: 1, ease: 2.3, due: Self.day(offset: 1), reps: 0)
            }
        }
    }
    func toggleBookmark(_ id: String) { mutate { $0.bookmarked.formSymmetricDifference([id]) } }
    func markWatched(_ key: String) { mutate { $0.watched.insert(key) } }
    func setLearned(_ id: String, _ on: Bool) {
        mutate {
            if on {
                $0.learned.insert(id)
                if $0.srs["b:" + id] == nil { $0.srs["b:" + id] = SRSItem(interval: 1, ease: 2.3, due: Self.day(offset: 1), reps: 0) }
            } else {
                $0.learned.remove(id)
            }
        }
    }

    // MARK: spaced repetition

    /// Keys ("p:<problem>" or "b:<bite>") that are due today or overdue.
    var dueKeys: [String] {
        let today = Self.dayString(Date())
        return data.srs.filter { $0.value.due <= today }.sorted { $0.value.due < $1.value.due }.map(\.key)
    }

    /// grade: 0 again, 1 hard, 2 good, 3 easy.
    func review(_ key: String, grade: Int) {
        mutate {
            var it = $0.srs[key] ?? SRSItem(interval: 1, ease: 2.3, due: Self.day(offset: 0), reps: 0)
            switch grade {
            case 0:
                it.interval = 1
                it.ease = max(1.3, it.ease - 0.2)
            case 1:
                it.interval = max(1, Int((Double(it.interval) * 1.2).rounded()))
                it.ease = max(1.3, it.ease - 0.15)
            case 2:
                it.interval = max(2, Int((Double(it.interval) * it.ease).rounded()))
            default:
                it.interval = max(3, Int((Double(it.interval) * it.ease * 1.3).rounded()))
                it.ease += 0.15
            }
            it.reps += 1
            it.due = Self.day(offset: it.interval)
            $0.srs[key] = it
        }
    }

    // MARK: mock interviews

    func recordMock(problemId: String, seconds: Int, rating: Int, hints: Int) {
        let attempt = MockAttempt(id: UUID().uuidString, problemId: problemId, date: Self.dayString(Date()),
                                  seconds: seconds, rating: rating, hints: hints)
        mutate { $0.mocks.insert(attempt, at: 0) }
        review("p:" + problemId, grade: rating)
    }
    func recordQuiz(_ id: String, correct: Bool) { mutate { $0.quiz[id] = correct } }
    func setNote(_ id: String, _ text: String) { mutate { $0.notes[id] = text } }
    func opened(problem id: String) { mutate { $0.lastProblem = id } }
    func savePosition(book: String, _ pos: BookPosition) { mutate { $0.books[book] = pos; $0.lastBook = book } }
    func position(book: String) -> BookPosition? { data.books[book] }

    func resetAll() {
        data = ProgressData()
        scheduleSave()
    }

    /// Consecutive active days ending today (or yesterday).
    var streak: Int {
        let days = Set(data.activeDays)
        var count = 0
        var d = Date()
        if !days.contains(Self.dayString(d)) { d = Calendar.current.date(byAdding: .day, value: -1, to: d) ?? d }
        while days.contains(Self.dayString(d)) {
            count += 1
            d = Calendar.current.date(byAdding: .day, value: -1, to: d) ?? d
        }
        return count
    }
}

// MARK: - Settings

final class AppSettings: ObservableObject {
    enum Keys {
        static let presenter = "presenter"
        static let voice = "voiceId"
        static let rate = "speechRate"
        static let language = "codeLanguage"
        static let captions = "captions"
        static let appearance = "appearance"
        static let onboarded = "onboarded"
    }

    private let d = UserDefaults.standard

    @Published var presenterId: String { didSet { d.set(presenterId, forKey: Keys.presenter) } }
    @Published var voiceId: String { didSet { d.set(voiceId, forKey: Keys.voice) } }
    @Published var speechRate: Double { didSet { d.set(speechRate, forKey: Keys.rate) } }
    @Published var language: String { didSet { d.set(language, forKey: Keys.language) } }
    @Published var captions: Bool { didSet { d.set(captions, forKey: Keys.captions) } }
    @Published var appearance: String { didSet { d.set(appearance, forKey: Keys.appearance) } }
    @Published var hasOnboarded: Bool { didSet { d.set(hasOnboarded, forKey: Keys.onboarded) } }

    init() {
        presenterId = d.string(forKey: Keys.presenter) ?? Presenter.all[0].id
        voiceId = d.string(forKey: Keys.voice) ?? ""
        speechRate = d.object(forKey: Keys.rate) as? Double ?? 1.0
        language = d.string(forKey: Keys.language) ?? "python"
        captions = d.object(forKey: Keys.captions) as? Bool ?? true
        appearance = d.string(forKey: Keys.appearance) ?? "system"
        hasOnboarded = d.bool(forKey: Keys.onboarded)
    }

    var presenter: Presenter { Presenter.find(presenterId) }

    var colorScheme: ColorScheme? {
        switch appearance {
        case "light": return .light
        case "dark": return .dark
        default: return nil
        }
    }
}
