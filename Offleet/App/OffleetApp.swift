import SwiftUI

@main
struct OffleetApp: App {
    @StateObject private var content = ContentStore()
    @StateObject private var progress = ProgressStore()
    @StateObject private var settings = AppSettings()
    @StateObject private var audiobook = AudiobookPlayer()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(content)
                .environmentObject(progress)
                .environmentObject(settings)
                .environmentObject(audiobook)
                .preferredColorScheme(settings.colorScheme)
                .tint(Brand.indigo)
        }
    }
}
