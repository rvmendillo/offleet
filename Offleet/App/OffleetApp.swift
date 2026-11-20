import SwiftUI

@main
struct OffleetApp: App {
    var body: some Scene {
        WindowGroup {
            VStack(spacing: 16) {
                Image("LaunchLogo")
                Text("offleet").font(.system(size: 44, weight: .heavy, design: .rounded))
                Text("Interview prep that works offline.").foregroundStyle(.secondary)
            }
            .padding()
        }
    }
}
