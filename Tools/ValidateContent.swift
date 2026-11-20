import Foundation

/// CI check: decode every bundled content file with the app's own models.
@main
struct ValidateContent {
    static func main() throws {
        let path = CommandLine.arguments.dropFirst().first ?? "Offleet/Resources/Content"
        let root = URL(fileURLWithPath: path)
        let c = try ContentLoader.loadAll(from: root)
        var frames = 0
        var problems = 0
        for p in c.problems {
            let tut = ContentLoader.tutorial(problemId: p.id, root: root)
            for a in p.approaches {
                guard let fs = tut[a.id] else { continue }
                frames += fs.count
                for f in fs {
                    if let ln = f.ln {
                        for (lang, line) in ln {
                            let key = lang == "line" ? nil : lang
                            if let key, let code = a.code(for: key) {
                                let count = code.src.components(separatedBy: "\n").count
                                precondition(line >= 1 && line <= count, "\(p.id)/\(a.id): line \(line) out of range for \(lang)")
                            }
                        }
                    }
                }
            }
            problems += 1
        }
        let bites = c.subjects.reduce(0) { $0 + $1.allBites.count }
        let chapters = c.books.reduce(0) { $0 + $1.chapters.count }
        print("OK problems=\(problems) frames=\(frames) subjects=\(c.subjects.count) bites=\(bites) books=\(c.books.count) chapters=\(chapters) tracks=\(c.tracks.count)")
    }
}
