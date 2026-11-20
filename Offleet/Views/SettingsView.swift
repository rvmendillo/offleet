import AVFoundation
import SwiftUI

struct SettingsView: View {
    @EnvironmentObject private var settings: AppSettings
    @EnvironmentObject private var progress: ProgressStore
    @EnvironmentObject private var content: ContentStore
    @State private var confirmReset = false
    @StateObject private var preview = ScriptReader(owner: "preview")

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    HStack(spacing: 14) {
                        LogoTile(size: 56)
                        VStack(alignment: .leading, spacing: 3) {
                            Wordmark(size: 24)
                            Text("\(progress.data.solved.count) solved · \(progress.streak)-day streak · \(progress.data.learned.count) bites")
                                .font(.caption).foregroundStyle(.secondary)
                        }
                    }
                    .padding(.vertical, 4)
                }

                Section("Your tutor") {
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 14) {
                            ForEach(Presenter.all) { p in
                                Button {
                                    settings.presenterId = p.id
                                    settings.voiceId = ""
                                } label: {
                                    VStack(spacing: 6) {
                                        PresenterView(presenter: p, size: 70, owner: "preview")
                                            .overlay(Circle().stroke(settings.presenterId == p.id ? Brand.indigo : Color.clear, lineWidth: 3))
                                        Text(p.name).font(.caption.weight(.bold))
                                        Text(p.tagline).font(.system(size: 9)).foregroundStyle(.secondary).multilineTextAlignment(.center).frame(width: 84)
                                    }
                                }
                                .buttonStyle(.plain)
                            }
                        }
                        .padding(.vertical, 6)
                    }
                    NavigationLink {
                        VoicePicker()
                    } label: {
                        LabeledContent("Voice", value: currentVoiceName)
                    }
                    VStack(alignment: .leading) {
                        Text("Speaking speed: \(settings.speechRate, specifier: "%.2f")×")
                        Slider(value: $settings.speechRate, in: 0.5...2.0, step: 0.05)
                    }
                    Button {
                        preview.load("Hi! I'm \(settings.presenter.name). Let's learn the sliding window pattern together, one step at a time.")
                        preview.play()
                    } label: {
                        Label("Preview voice", systemImage: "speaker.wave.2.fill")
                    }
                    Toggle("Show captions", isOn: $settings.captions)
                }

                Section {
                    Picker("Default code language", selection: $settings.language) {
                        Text("Python").tag("python")
                        Text("Java").tag("java")
                    }
                    Picker("Appearance", selection: $settings.appearance) {
                        Text("System").tag("system")
                        Text("Light").tag("light")
                        Text("Dark").tag("dark")
                    }
                } header: {
                    Text("Preferences")
                }

                Section {
                    Label("Everything works offline: problems, tutorials, audiobooks and reviewers are stored inside the app.", systemImage: "wifi.slash")
                    Label("For the most natural voice, download an Enhanced or Premium English voice in iPhone Settings › Accessibility › Spoken Content › Voices. Offleet picks it up automatically.", systemImage: "arrow.down.circle")
                } header: {
                    Text("Voices & offline use")
                }
                .font(.footnote)

                Section("Library") {
                    LabeledContent("Problems", value: "\(content.problems.count)")
                    LabeledContent("Reviewer bites", value: "\(content.subjects.reduce(0) { $0 + $1.allBites.count })")
                    LabeledContent("Audiobooks", value: "\(content.books.count)")
                }

                Section {
                    Button("Reset all progress", role: .destructive) { confirmReset = true }
                } footer: {
                    Text("Offleet \(Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "1.0"). Original problems, explanations and illustrations. Not affiliated with any coding-interview website.")
                }
            }
            .navigationTitle("Me")
            .confirmationDialog("Reset all progress?", isPresented: $confirmReset, titleVisibility: .visible) {
                Button("Reset", role: .destructive) { progress.resetAll() }
            }
            .onDisappear { preview.stop() }
            .miniPlayerInset()
        }
    }

    private var currentVoiceName: String {
        if !settings.voiceId.isEmpty, let v = AVSpeechSynthesisVoice(identifier: settings.voiceId) { return v.name }
        return "Automatic"
    }
}

struct VoicePicker: View {
    @EnvironmentObject private var settings: AppSettings
    @StateObject private var preview = ScriptReader(owner: "preview")

    var body: some View {
        List {
            Section {
                Button {
                    settings.voiceId = ""
                } label: {
                    HStack {
                        Text("Automatic (best for \(settings.presenter.name))")
                        Spacer()
                        if settings.voiceId.isEmpty { Image(systemName: "checkmark").foregroundStyle(Brand.indigo) }
                    }
                }
            }
            Section("Installed English voices") {
                ForEach(SpeechEngine.englishVoices, id: \.identifier) { v in
                    HStack {
                        Button {
                            settings.voiceId = v.identifier
                            preview.load("This is \(v.name). Two pointers walk toward each other until they meet.")
                            preview.play()
                        } label: {
                            VStack(alignment: .leading, spacing: 2) {
                                Text(v.name).foregroundStyle(.primary)
                                Text("\(v.language) · \(SpeechEngine.qualityLabel(v))").font(.caption).foregroundStyle(.secondary)
                            }
                        }
                        Spacer()
                        if settings.voiceId == v.identifier { Image(systemName: "checkmark").foregroundStyle(Brand.indigo) }
                    }
                }
            }
        }
        .navigationTitle("Voice")
        .onDisappear { preview.stop() }
    }
}
