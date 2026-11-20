import SwiftUI

/// Launch arguments used by CI to open specific screens for screenshots, e.g.
/// `-uiScreen tutorial -uiProblem pair-sum-sorted -uiFrame 8`. Inactive in normal use.
enum DebugLaunch {
    private static let args = ProcessInfo.processInfo.arguments

    static func value(_ key: String) -> String? {
        guard let i = args.firstIndex(of: key), i + 1 < args.count else { return nil }
        return args[i + 1]
    }

    static var screen: String? { value("-uiScreen") }
    static var problem: String? { value("-uiProblem") }
    static var approach: String? { value("-uiApproach") }
    static var frame: Int? { value("-uiFrame").flatMap { Int($0) } }
    static var bite: String? { value("-uiBite") }
    static var book: String? { value("-uiBook") }
    static var isActive: Bool { screen != nil }

    static var tab: AppTab? {
        switch screen {
        case "home": return .home
        case "practice", "problem", "tutorial", "mock": return .practice
        case "learn", "bite", "subject", "path", "review": return .learn
        case "listen", "nowplaying": return .listen
        case "me": return .me
        default: return nil
        }
    }

    static var practicePath: NavigationPath {
        var p = NavigationPath()
        if let id = problem, screen == "problem" || screen == "tutorial" { p.append(Route.problem(id)) }
        if screen == "mock" { p.append(Route.mock("any")) }
        return p
    }

    static var learnPath: NavigationPath {
        var p = NavigationPath()
        if screen == "bite", let id = bite { p.append(Route.bite(id)) }
        if screen == "subject", let id = value("-uiSubject") { p.append(Route.subject(id)) }
        if screen == "path", let id = value("-uiPath") { p.append(Route.path(id)) }
        if screen == "review" { p.append(Route.review) }
        return p
    }
}
