import SwiftUI

/// Offleet brand system: palette, gradients, type and the logo mark.
enum Brand {
    static let violet = Color(hex: "#6D28D9")
    static let indigo = Color(hex: "#4F46E5")
    static let cyan = Color(hex: "#0891B2")
    static let aqua = Color(hex: "#67E8F9")
    static let amber = Color(hex: "#FBBF24")
    static let mint = Color(hex: "#34D399")
    static let rose = Color(hex: "#FB7185")
    static let ink = Color(hex: "#0B1026")
    static let inkSoft = Color(hex: "#141B3A")
    static let stage = Color(hex: "#0E1430")

    static let gradient = LinearGradient(colors: [violet, indigo, cyan], startPoint: .topLeading, endPoint: .bottomTrailing)
    static let softGradient = LinearGradient(colors: [violet.opacity(0.18), cyan.opacity(0.14)], startPoint: .topLeading, endPoint: .bottomTrailing)
    static let warm = LinearGradient(colors: [amber, Color(hex: "#F97316")], startPoint: .topLeading, endPoint: .bottomTrailing)

    static func difficultyColor(_ d: String) -> Color {
        switch d {
        case "Easy": return Color(hex: "#22C55E")
        case "Medium": return Color(hex: "#F59E0B")
        default: return Color(hex: "#EF4444")
        }
    }

    static func categoryTitle(_ c: String) -> String {
        switch c {
        case "spring-boot": return "Spring Boot"
        case "angular": return "Angular"
        default: return "Algorithms"
        }
    }

    static func languageTitle(_ lang: String) -> String {
        switch lang {
        case "python": return "Python"
        case "java": return "Java"
        case "typescript": return "TypeScript"
        case "html": return "HTML"
        case "yaml": return "YAML"
        case "properties": return "Properties"
        case "json": return "JSON"
        default: return lang.capitalized
        }
    }
}

extension Color {
    init(hex: String) {
        var s = hex.trimmingCharacters(in: .whitespacesAndNewlines)
        if s.hasPrefix("#") { s.removeFirst() }
        var v: UInt64 = 0
        Scanner(string: s).scanHexInt64(&v)
        let r, g, b: Double
        if s.count == 6 {
            r = Double((v >> 16) & 0xFF) / 255
            g = Double((v >> 8) & 0xFF) / 255
            b = Double(v & 0xFF) / 255
        } else {
            r = 0.5; g = 0.5; b = 0.5
        }
        self.init(.sRGB, red: r, green: g, blue: b, opacity: 1)
    }
}

extension Font {
    static func brand(_ size: CGFloat, _ weight: Font.Weight = .bold) -> Font {
        .system(size: size, weight: weight, design: .rounded)
    }
}

/// The Offleet mark: two pointer arcs around the amber "window" pill.
struct LogoMark: View {
    var size: CGFloat = 64
    var left: Color = .white
    var right: Color = Brand.aqua
    var pill: Color = Brand.amber

    var body: some View {
        let w = size * 0.17
        ZStack {
            Circle()
                .trim(from: 0, to: 124.0 / 360.0)
                .stroke(left, style: StrokeStyle(lineWidth: w, lineCap: .round))
                .rotationEffect(.degrees(118))
            Circle()
                .trim(from: 0, to: 124.0 / 360.0)
                .stroke(right, style: StrokeStyle(lineWidth: w, lineCap: .round))
                .rotationEffect(.degrees(-62))
            Capsule()
                .fill(pill)
                .frame(width: size * 0.46, height: size * 0.16)
        }
        .padding(w / 2)
        .frame(width: size, height: size)
    }
}

/// App-icon style tile with the gradient background.
struct LogoTile: View {
    var size: CGFloat = 72
    var body: some View {
        RoundedRectangle(cornerRadius: size * 0.24, style: .continuous)
            .fill(Brand.gradient)
            .frame(width: size, height: size)
            .overlay(LogoMark(size: size * 0.6))
            .shadow(color: Brand.violet.opacity(0.35), radius: size * 0.12, y: size * 0.06)
    }
}

/// "offleet" wordmark with the gradient on "leet".
struct Wordmark: View {
    var size: CGFloat = 34
    var body: some View {
        HStack(spacing: 0) {
            Text("off").foregroundStyle(.primary)
            Text("leet").foregroundStyle(Brand.gradient)
        }
        .font(.system(size: size, weight: .heavy, design: .rounded))
        .accessibilityLabel("Offleet")
    }
}
