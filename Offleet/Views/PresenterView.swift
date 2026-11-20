import SwiftUI

/// An original illustrated tutor that blinks, sways and lip-syncs to the speech engine's word callbacks.
struct PresenterView: View {
    let presenter: Presenter
    var size: CGFloat = 120
    /// Only animate the mouth when this owner is the one speaking (nil = any owner).
    var owner: String? = nil
    @ObservedObject private var engine = SpeechEngine.shared

    var body: some View {
        TimelineView(.animation(minimumInterval: 1.0 / 30.0)) { tl in
            let t = tl.date.timeIntervalSinceReferenceDate
            let mine = owner == nil || engine.owner == owner
            let talking = mine && engine.isSpeaking && !engine.isPaused
            let dt = tl.date.timeIntervalSince(engine.lastWordAt)
            let open: CGFloat = (talking && dt < 0.5) ? CGFloat((1 - dt / 0.5) * (0.55 + 0.45 * abs(sin(t * 21)))) : 0
            let blink = t.truncatingRemainder(dividingBy: 4.3) < 0.13
            AvatarDrawing(p: presenter, u: size / 100, mouth: open, blink: blink, talking: talking, t: t)
        }
        .frame(width: size, height: size)
        .accessibilityLabel("\(presenter.name), your tutor")
    }
}

private struct AvatarDrawing: View {
    let p: Presenter
    let u: CGFloat
    let mouth: CGFloat
    let blink: Bool
    let talking: Bool
    let t: Double

    var body: some View {
        let bob = CGFloat(sin(t * 1.7)) * 0.9 * u
        let tilt = Angle.degrees(sin(t * (talking ? 1.3 : 0.6)) * (talking ? 3 : 1.4))
        ZStack {
            Circle().fill(LinearGradient(colors: [p.shirt.opacity(0.45), p.shirt.opacity(0.12)], startPoint: .top, endPoint: .bottom))
            Ellipse().fill(p.shirt).frame(width: 82 * u, height: 46 * u).position(x: 50 * u, y: 99 * u)
            Ellipse().fill(Color.white.opacity(0.12)).frame(width: 30 * u, height: 10 * u).position(x: 50 * u, y: 79 * u)
            LogoMark(size: 11 * u).position(x: 50 * u, y: 90 * u)
            Rectangle().fill(p.skin).frame(width: 15 * u, height: 16 * u).position(x: 50 * u, y: 72 * u)
            Rectangle().fill(Color.black.opacity(0.08)).frame(width: 15 * u, height: 5 * u).position(x: 50 * u, y: 68 * u)
            head
                .rotationEffect(tilt, anchor: UnitPoint(x: 0.5, y: 0.74))
                .offset(y: bob)
        }
        .frame(width: 100 * u, height: 100 * u)
        .clipShape(Circle())
    }

    private var head: some View {
        ZStack {
            hairBack
            Circle().fill(p.skin).frame(width: 10 * u, height: 10 * u).position(x: 25.5 * u, y: 48 * u)
            Circle().fill(p.skin).frame(width: 10 * u, height: 10 * u).position(x: 74.5 * u, y: 48 * u)
            Ellipse().fill(p.skin).frame(width: 50 * u, height: 56 * u).position(x: 50 * u, y: 46 * u)
            hairFront
            cheeks
            brows
            eyes
            if p.glasses { glasses }
            Capsule().fill(Color.black.opacity(0.10)).frame(width: 3.2 * u, height: 6 * u).position(x: 50 * u, y: 53 * u)
            mouthView
        }
        .frame(width: 100 * u, height: 100 * u)
    }

    @ViewBuilder private var hairBack: some View {
        switch p.style {
        case .bob:
            RoundedRectangle(cornerRadius: 26 * u, style: .continuous).fill(p.hair)
                .frame(width: 64 * u, height: 62 * u).position(x: 50 * u, y: 50 * u)
        case .curly:
            ZStack {
                ForEach(Array(Self.curls.enumerated()), id: \.offset) { _, c in
                    Circle().fill(p.hair).frame(width: c.2 * u, height: c.2 * u).position(x: c.0 * u, y: c.1 * u)
                }
            }
        case .bun:
            Circle().fill(p.hair).frame(width: 20 * u, height: 20 * u).position(x: 50 * u, y: 13 * u)
        case .short:
            EmptyView()
        }
    }

    private static let curls: [(CGFloat, CGFloat, CGFloat)] = [
        (30, 30, 20), (38, 20, 20), (50, 16, 22), (62, 20, 20), (70, 30, 20), (27, 43, 16), (73, 43, 16), (26, 55, 12), (74, 55, 12),
    ]

    @ViewBuilder private var hairFront: some View {
        switch p.style {
        case .bob:
            HairCap(part: 0.08).fill(p.hair).frame(width: 56 * u, height: 34 * u).position(x: 50 * u, y: 31 * u)
        case .short:
            HairCap(part: -0.04).fill(p.hair).frame(width: 54 * u, height: 26 * u).position(x: 50 * u, y: 28 * u)
        case .curly:
            HairCap(part: 0).fill(p.hair).frame(width: 52 * u, height: 24 * u).position(x: 50 * u, y: 27 * u)
        case .bun:
            HairCap(part: 0.02).fill(p.hair).frame(width: 54 * u, height: 26 * u).position(x: 50 * u, y: 28 * u)
        }
    }

    private var cheeks: some View {
        ZStack {
            Circle().fill(Color(hex: "#FF7A93").opacity(0.25)).frame(width: 9 * u, height: 9 * u).position(x: 33 * u, y: 57 * u)
            Circle().fill(Color(hex: "#FF7A93").opacity(0.25)).frame(width: 9 * u, height: 9 * u).position(x: 67 * u, y: 57 * u)
        }
    }

    private var brows: some View {
        let lift = talking ? CGFloat(abs(sin(t * 2.3))) * 1.4 * u : 0
        return ZStack {
            Capsule().fill(p.hair).frame(width: 10 * u, height: 2.4 * u).rotationEffect(.degrees(-7)).position(x: 39.5 * u, y: 37.5 * u - lift)
            Capsule().fill(p.hair).frame(width: 10 * u, height: 2.4 * u).rotationEffect(.degrees(7)).position(x: 60.5 * u, y: 37.5 * u - lift)
        }
    }

    private var eyes: some View {
        ZStack {
            eye.position(x: 40 * u, y: 46 * u)
            eye.position(x: 60 * u, y: 46 * u)
        }
    }

    private var eye: some View {
        ZStack {
            Ellipse().fill(Color(hex: "#1E1B2E")).frame(width: 5.6 * u, height: 7 * u)
            Circle().fill(Color.white).frame(width: 1.9 * u, height: 1.9 * u).offset(x: 1 * u, y: -1.4 * u)
        }
        .scaleEffect(x: 1, y: blink ? 0.12 : 1)
    }

    private var glasses: some View {
        let frameColor = Color(hex: "#1F2937")
        return ZStack {
            RoundedRectangle(cornerRadius: 4 * u).stroke(frameColor, lineWidth: 1.6 * u).frame(width: 15 * u, height: 12 * u).position(x: 40 * u, y: 46 * u)
            RoundedRectangle(cornerRadius: 4 * u).stroke(frameColor, lineWidth: 1.6 * u).frame(width: 15 * u, height: 12 * u).position(x: 60 * u, y: 46 * u)
            Rectangle().fill(frameColor).frame(width: 5 * u, height: 1.5 * u).position(x: 50 * u, y: 45 * u)
        }
    }

    @ViewBuilder private var mouthView: some View {
        if mouth > 0.05 {
            ZStack(alignment: .bottom) {
                RoundedRectangle(cornerRadius: 5 * u, style: .continuous).fill(Color(hex: "#5B1A2B"))
                Ellipse().fill(Color(hex: "#F28B9B")).frame(width: 8 * u, height: (1.2 + 3.2 * mouth) * u).offset(y: -0.6 * u)
            }
            .frame(width: (11 + 3 * mouth) * u, height: (2.5 + 9 * mouth) * u)
            .position(x: 50 * u, y: (62 + 2 * mouth) * u)
        } else {
            SmileArc().stroke(Color(hex: "#7A2E3B"), style: StrokeStyle(lineWidth: 2 * u, lineCap: .round))
                .frame(width: 13 * u, height: 4 * u)
                .position(x: 50 * u, y: 62 * u)
        }
    }
}

private struct HairCap: Shape {
    var part: CGFloat

    func path(in r: CGRect) -> Path {
        var p = Path()
        let w = r.width, h = r.height
        p.move(to: CGPoint(x: r.minX, y: r.minY + h * 0.8))
        p.addCurve(to: CGPoint(x: r.midX, y: r.minY),
                   control1: CGPoint(x: r.minX, y: r.minY + h * 0.15), control2: CGPoint(x: r.minX + w * 0.22, y: r.minY))
        p.addCurve(to: CGPoint(x: r.maxX, y: r.minY + h * 0.8),
                   control1: CGPoint(x: r.minX + w * 0.78, y: r.minY), control2: CGPoint(x: r.maxX, y: r.minY + h * 0.15))
        p.addCurve(to: CGPoint(x: r.minX + w * (0.45 + part), y: r.minY + h * 0.46),
                   control1: CGPoint(x: r.maxX - w * 0.06, y: r.minY + h * 0.5), control2: CGPoint(x: r.minX + w * 0.72, y: r.minY + h * 0.66))
        p.addCurve(to: CGPoint(x: r.minX, y: r.minY + h * 0.8),
                   control1: CGPoint(x: r.minX + w * 0.24, y: r.minY + h * 0.64), control2: CGPoint(x: r.minX + w * 0.06, y: r.minY + h * 0.52))
        p.closeSubpath()
        return p
    }
}

private struct SmileArc: Shape {
    func path(in r: CGRect) -> Path {
        var p = Path()
        p.move(to: CGPoint(x: r.minX, y: r.minY))
        p.addQuadCurve(to: CGPoint(x: r.maxX, y: r.minY), control: CGPoint(x: r.midX, y: r.maxY * 2))
        return p
    }
}

/// Presenter with a name tag, used across the app.
struct PresenterBadge: View {
    let presenter: Presenter
    var size: CGFloat = 64
    var owner: String? = nil

    var body: some View {
        VStack(spacing: 4) {
            PresenterView(presenter: presenter, size: size, owner: owner)
                .overlay(Circle().stroke(Color.white.opacity(0.25), lineWidth: 2))
                .shadow(color: .black.opacity(0.25), radius: 6, y: 3)
            Text(presenter.name)
                .font(.caption2.weight(.bold))
                .padding(.horizontal, 8).padding(.vertical, 2)
                .background(Capsule().fill(presenter.shirt))
                .foregroundStyle(.white)
        }
    }
}
