import Foundation

// MARK: - Problems

struct PatternInfo: Codable, Identifiable, Hashable {
    let id: String
    let name: String
    let summary: String
    let icon: String
    let color: String
}

struct ProblemsFile: Codable {
    let patterns: [PatternInfo]
    let problems: [Problem]
}

struct Problem: Codable, Identifiable, Hashable {
    let id: String
    let n: Int
    let title: String
    let diff: String
    let cat: String
    let topics: [String]
    let patterns: [String]
    let statement: String
    let examples: [Example]
    let constraints: [String]
    let hints: [String]
    let approaches: [Approach]
    let eli5: String?

    static func == (lhs: Problem, rhs: Problem) -> Bool { lhs.id == rhs.id }
    func hash(into hasher: inout Hasher) { hasher.combine(id) }

    var hasSlidingWindow: Bool { patterns.contains("sliding-window") }
    var hasTwoPointers: Bool { patterns.contains("two-pointers") || patterns.contains("fast-slow") }
    var isAlgorithm: Bool { ["algorithms", "ai-engineering", "system-design"].contains(cat) }
}

struct Example: Codable, Hashable {
    let input: String
    let out: String
    let why: String?

    enum CodingKeys: String, CodingKey {
        case input = "in"
        case out, why
    }
}

struct Approach: Codable, Identifiable, Hashable {
    let id: String
    let name: String
    let pattern: String
    let time: String
    let space: String
    let idea: String
    let why: String?
    let code: [CodeFile]

    func code(for lang: String) -> CodeFile? { code.first { $0.lang == lang } }
    var languages: [String] { code.map(\.lang) }
}

struct CodeFile: Codable, Hashable {
    let lang: String
    let name: String
    let src: String
}

// MARK: - Tutorials

struct Frame: Codable, Hashable {
    let k: String
    let cap: String
    let say: String?
    let ln: [String: Int]?
    let st: VizState?
    let card: Card?
    let file: Int?

    var speech: String { say ?? cap }
    var isStep: Bool { ["step", "trace", "skip", "done"].contains(k) }
}

struct Card: Codable, Hashable {
    let title: String?
    let sub: String?
    let pattern: String?
    let name: String?
    let lines: [String]?
    let time: String?
    let space: String?
}

struct VizState: Codable, Hashable {
    let arrays: [ArrayViz]?
    let vars: [KV]?
    let maps: [MapViz]?
    let stacks: [StackViz]?
    let grid: GridViz?
    let table: GridViz?
    let linked: LinkedViz?
    let tree: TreeViz?
    let graph: GraphViz?
    let intervals: [IntervalRow]?
    let bits: [BitsRow]?
    let out: OutViz?
}

struct ArrayViz: Codable, Hashable {
    let n: String
    let v: [String]
    let p: [IdxPtr]?
    let w: [Int]?
    let m: [Int]?
}

struct IdxPtr: Codable, Hashable { let l: String; let i: Int }
struct KV: Codable, Hashable { let k: String; let v: String }
struct MapViz: Codable, Hashable { let n: String; let e: [KV] }
struct StackViz: Codable, Hashable { let n: String; let v: [String]; let t: String }

struct GridViz: Codable, Hashable {
    let n: String
    let v: [[String]]
    let p: [CellPtr]?
    let m: [[Int]]?
}

struct CellPtr: Codable, Hashable { let l: String; let r: Int; let c: Int }

struct LinkedViz: Codable, Hashable {
    let nodes: [LNode]
    let p: [NodePtr]?
}

struct LNode: Codable, Hashable, Identifiable {
    let id: Int
    let v: String
    let nx: Int
    let row: Int
    let col: Int
    let dim: Bool
}

struct NodePtr: Codable, Hashable { let l: String; let id: Int }

struct TreeViz: Codable, Hashable {
    let nodes: [TNode]
    let p: [NodePtr]?
    let m: [Int]?
}

struct TNode: Codable, Hashable, Identifiable {
    let id: Int
    let v: String
    let x: Int
    let y: Int
    let l: Int
    let r: Int
}

struct GraphViz: Codable, Hashable {
    let nodes: [String]
    let edges: [Edge]
    let dir: Bool
    let p: [KeyPtr]?
    let vis: [String]?
}

struct Edge: Codable, Hashable { let a: String; let b: String }
struct KeyPtr: Codable, Hashable { let l: String; let k: String }
struct IntervalRow: Codable, Hashable { let n: String; let v: [[Double]] }
struct BitsRow: Codable, Hashable { let k: String; let v: String; let b: String }
struct OutViz: Codable, Hashable { let n: String; let v: [String] }

// MARK: - Reviewer

struct ReviewerFile: Codable { let subjects: [Subject] }

struct Subject: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let icon: String
    let color: String
    let blurb: String
    let units: [ReviewUnit]

    var allBites: [Bite] { units.flatMap(\.bites) }
}

struct ReviewUnit: Codable, Hashable {
    let title: String
    let blurb: String
    let bites: [Bite]
}

struct Bite: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let tldr: String
    let points: [String]
    let formula: String?
    let example: String?
    let tip: String?
    let quiz: Quiz?
    let say: String
    let flow: [String]?
}

struct Quiz: Codable, Hashable {
    let q: String
    let opts: [String]
    let a: Int
    let why: String
}

// MARK: - Audiobooks

struct BooksFile: Codable { let books: [Book] }

struct Book: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let author: String
    let blurb: String
    let icon: String
    let color: String
    let chapters: [Chapter]
}

struct Chapter: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let paras: [Para]
}

struct Para: Codable, Hashable {
    let t: String
    let s: String?
    var speech: String { s ?? t }
}

// MARK: - Tracks

struct TracksFile: Codable { let tracks: [Track] }

struct Track: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let summary: String
    let icon: String
    let color: String
    let problems: [String]
}

// MARK: - Career paths

struct PathsFile: Codable { let paths: [CareerPath] }

struct CareerPath: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let subtitle: String
    let icon: String
    let color: String
    let blurb: String
    let stages: [PathStage]
}

struct PathStage: Codable, Hashable {
    let title: String
    let blurb: String
    let items: [PathItem]
}

struct PathItem: Codable, Hashable {
    let kind: String
    let id: String
    let title: String?
}

// MARK: - Loading

struct LoadedContent {
    var patterns: [PatternInfo]
    var problems: [Problem]
    var subjects: [Subject]
    var books: [Book]
    var tracks: [Track]
    var paths: [CareerPath]
}

enum ContentLoader {
    static func folder(in bundle: Bundle = .main) -> URL? {
        bundle.url(forResource: "Content", withExtension: nil)
    }

    static func decode<T: Decodable>(_ type: T.Type, _ url: URL) throws -> T {
        let data = try Data(contentsOf: url)
        return try JSONDecoder().decode(T.self, from: data)
    }

    static func loadAll(from root: URL) throws -> LoadedContent {
        let p = try decode(ProblemsFile.self, root.appendingPathComponent("problems.json"))
        let r = try decode(ReviewerFile.self, root.appendingPathComponent("reviewer.json"))
        let b = try decode(BooksFile.self, root.appendingPathComponent("books.json"))
        let t = try decode(TracksFile.self, root.appendingPathComponent("tracks.json"))
        let paths = try decode(PathsFile.self, root.appendingPathComponent("paths.json"))
        return LoadedContent(patterns: p.patterns, problems: p.problems, subjects: r.subjects, books: b.books,
                             tracks: t.tracks, paths: paths.paths)
    }

    static func tutorial(problemId: String, root: URL) -> [String: [Frame]] {
        let url = root.appendingPathComponent("tutorials").appendingPathComponent(problemId + ".json")
        return (try? decode([String: [Frame]].self, url)) ?? [:]
    }
}
