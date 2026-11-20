import SwiftUI

enum AppTab: Hashable {
    case home, practice, learn, listen, me
}

struct RootView: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var settings: AppSettings
    @EnvironmentObject private var progress: ProgressStore
    @EnvironmentObject private var audiobook: AudiobookPlayer
    @State private var tab: AppTab = .home

    var body: some View {
        ZStack {
            if !content.isLoaded {
                SplashView(error: content.loadError)
                    .transition(.opacity)
            } else if !settings.hasOnboarded {
                OnboardingView()
                    .transition(.opacity)
            } else {
                TabView(selection: $tab) {
                    HomeView(tab: $tab)
                        .tabItem { Label("Home", systemImage: "house.fill") }
                        .tag(AppTab.home)
                    ProblemsView()
                        .tabItem { Label("Practice", systemImage: "chevron.left.forwardslash.chevron.right") }
                        .tag(AppTab.practice)
                    ReviewerHomeView()
                        .tabItem { Label("Learn", systemImage: "graduationcap.fill") }
                        .tag(AppTab.learn)
                    LibraryView()
                        .tabItem { Label("Listen", systemImage: "headphones") }
                        .tag(AppTab.listen)
                    SettingsView()
                        .tabItem { Label("Me", systemImage: "person.crop.circle") }
                        .tag(AppTab.me)
                }
                .transition(.opacity)
            }
        }
        .animation(.easeInOut(duration: 0.35), value: content.isLoaded)
        .animation(.easeInOut(duration: 0.35), value: settings.hasOnboarded)
        .sheet(isPresented: $audiobook.showFullPlayer) {
            NowPlayingView()
        }
        .task {
            audiobook.attach(progress: progress)
            await content.load()
        }
    }
}

struct SplashView: View {
    let error: String?
    @State private var pulse = false

    var body: some View {
        ZStack {
            Brand.ink.ignoresSafeArea()
            VStack(spacing: 18) {
                LogoMark(size: 110)
                    .scaleEffect(pulse ? 1.04 : 0.96)
                    .animation(.easeInOut(duration: 0.9).repeatForever(autoreverses: true), value: pulse)
                HStack(spacing: 0) {
                    Text("off").foregroundStyle(.white)
                    Text("leet").foregroundStyle(Brand.gradient)
                }
                .font(.system(size: 40, weight: .heavy, design: .rounded))
                if let error {
                    Text(error).font(.footnote).foregroundStyle(.red).multilineTextAlignment(.center).padding()
                } else {
                    ProgressView().tint(.white)
                }
            }
        }
        .onAppear { pulse = true }
    }
}

struct OnboardingView: View {
    @EnvironmentObject private var settings: AppSettings
    @State private var page = 0
    @StateObject private var reader = ScriptReader(owner: "onboarding")

    var body: some View {
        ZStack {
            LinearGradient(colors: [Brand.ink, Brand.stage, Brand.indigo.opacity(0.6)], startPoint: .top, endPoint: .bottom)
                .ignoresSafeArea()
            VStack(spacing: 0) {
                TabView(selection: $page) {
                    welcome.tag(0)
                    features.tag(1)
                    choose.tag(2)
                }
                .tabViewStyle(.page(indexDisplayMode: .always))
                Button {
                    if page < 2 {
                        withAnimation { page += 1 }
                    } else {
                        reader.stop()
                        settings.hasOnboarded = true
                    }
                } label: {
                    Text(page < 2 ? "Continue" : "Start learning")
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 16)
                        .background(RoundedRectangle(cornerRadius: 16, style: .continuous).fill(Brand.gradient))
                        .foregroundStyle(.white)
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 24)
            }
        }
        .preferredColorScheme(.dark)
    }

    private var welcome: some View {
        VStack(spacing: 22) {
            Spacer()
            LogoTile(size: 110)
            HStack(spacing: 0) {
                Text("off").foregroundStyle(.white)
                Text("leet").foregroundStyle(Brand.gradient)
            }
            .font(.system(size: 46, weight: .heavy, design: .rounded))
            Text("Coding interview prep that works anywhere: on a plane, on the subway, with zero bars.")
                .font(.title3).multilineTextAlignment(.center).foregroundStyle(.white.opacity(0.85))
                .padding(.horizontal, 28)
            Spacer()
        }
    }

    private var features: some View {
        VStack(alignment: .leading, spacing: 20) {
            Spacer()
            feature("play.rectangle.fill", "Animated walkthroughs", "Every problem comes with a narrated, step-by-step animation of the real solution.", Brand.amber)
            feature("arrow.left.and.right", "Sliding Window & Two Pointers first", "Short, optimal Java and Python solutions, O(n) wherever possible.", Brand.aqua)
            feature("headphones", "Audiobook mode", "Listen to patterns, problems and reviewers with the screen locked.", Brand.mint)
            feature("graduationcap.fill", "Bite-sized reviewers", "Computer science, AI, advanced math and calculus in condensed, spoken bites.", Color(hex: "#F472B6"))
            Spacer()
        }
        .padding(.horizontal, 28)
    }

    private func feature(_ icon: String, _ title: String, _ text: String, _ color: Color) -> some View {
        HStack(alignment: .top, spacing: 14) {
            Image(systemName: icon).font(.title2).foregroundStyle(color).frame(width: 34)
            VStack(alignment: .leading, spacing: 3) {
                Text(title).font(.headline).foregroundStyle(.white)
                Text(text).font(.subheadline).foregroundStyle(.white.opacity(0.75))
            }
        }
    }

    private var choose: some View {
        VStack(spacing: 18) {
            Spacer()
            Text("Pick your tutor").font(.brand(28, .heavy)).foregroundStyle(.white)
            PresenterView(presenter: settings.presenter, size: 150, owner: "onboarding")
                .overlay(Circle().stroke(Color.white.opacity(0.3), lineWidth: 3))
            HStack(spacing: 12) {
                ForEach(Presenter.all) { p in
                    Button {
                        settings.presenterId = p.id
                        settings.voiceId = ""
                        reader.load("Hi, I'm \(p.name)! I'll explain every solution out loud, step by step.")
                        reader.play()
                    } label: {
                        Text(p.name)
                            .font(.subheadline.weight(.bold))
                            .padding(.horizontal, 14).padding(.vertical, 8)
                            .background(Capsule().fill(settings.presenterId == p.id ? AnyShapeStyle(Brand.gradient) : AnyShapeStyle(Color.white.opacity(0.12))))
                            .foregroundStyle(.white)
                    }
                }
            }
            Picker("Language", selection: $settings.language) {
                Text("Python").tag("python")
                Text("Java").tag("java")
            }
            .pickerStyle(.segmented)
            .padding(.horizontal, 40)
            Text("You can change both anytime in Me.").font(.footnote).foregroundStyle(.white.opacity(0.6))
            Spacer()
        }
    }
}
