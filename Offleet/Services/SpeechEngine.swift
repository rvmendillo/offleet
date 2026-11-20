import AVFoundation
import Combine
import Foundation
import SwiftUI

/// The on-screen tutors. Each has a look and a preferred voice gender; all speech is offline (on-device TTS).
struct Presenter: Identifiable, Hashable {
    enum Hair: Hashable { case bob, short, curly, bun }

    let id: String
    let name: String
    let tagline: String
    let skin: Color
    let hair: Color
    let shirt: Color
    let style: Hair
    let glasses: Bool
    let pitch: Float
    let prefersFemaleVoice: Bool

    static let all: [Presenter] = [
        Presenter(id: "mira", name: "Mira", tagline: "Calm, clear and patient", skin: Color(hex: "#F2C6A0"),
                  hair: Color(hex: "#3B2416"), shirt: Brand.indigo, style: .bob, glasses: false, pitch: 1.05, prefersFemaleVoice: true),
        Presenter(id: "theo", name: "Theo", tagline: "Upbeat and to the point", skin: Color(hex: "#C68B5E"),
                  hair: Color(hex: "#1B1B1F"), shirt: Brand.cyan, style: .short, glasses: true, pitch: 0.95, prefersFemaleVoice: false),
        Presenter(id: "ada", name: "Ada", tagline: "Loves math and proofs", skin: Color(hex: "#8D5A3B"),
                  hair: Color(hex: "#111014"), shirt: Brand.violet, style: .curly, glasses: true, pitch: 1.0, prefersFemaleVoice: true),
        Presenter(id: "kai", name: "Kai", tagline: "Explains it like a friend", skin: Color(hex: "#E9B98F"),
                  hair: Color(hex: "#5A3A22"), shirt: Color(hex: "#0F766E"), style: .bun, glasses: false, pitch: 1.0, prefersFemaleVoice: false),
    ]

    static func find(_ id: String) -> Presenter { all.first { $0.id == id } ?? all[0] }
}

/// Wraps AVSpeechSynthesizer: one utterance at a time, word callbacks for lip sync, owner tracking so the
/// audiobook and tutorials don't talk over each other.
final class SpeechEngine: NSObject, ObservableObject, AVSpeechSynthesizerDelegate {
    static let shared = SpeechEngine()

    @Published private(set) var isSpeaking = false
    @Published private(set) var isPaused = false
    @Published private(set) var owner: String?
    @Published private(set) var lastWordAt = Date.distantPast
    @Published private(set) var spokenRange: NSRange?
    @Published private(set) var currentText = ""

    private let synth = AVSpeechSynthesizer()
    private var current: AVSpeechUtterance?
    private var completion: (() -> Void)?

    override init() {
        super.init()
        synth.delegate = self
    }

    // MARK: voices

    static var englishVoices: [AVSpeechSynthesisVoice] {
        AVSpeechSynthesisVoice.speechVoices()
            .filter { $0.language.hasPrefix("en") }
            .sorted { a, b in
                if a.quality.rawValue != b.quality.rawValue { return a.quality.rawValue > b.quality.rawValue }
                return a.name < b.name
            }
    }

    static func qualityLabel(_ v: AVSpeechSynthesisVoice) -> String {
        switch v.quality {
        case .premium: return "Premium"
        case .enhanced: return "Enhanced"
        default: return "Standard"
        }
    }

    func voice(for presenter: Presenter) -> AVSpeechSynthesisVoice? {
        let chosen = UserDefaults.standard.string(forKey: AppSettings.Keys.voice) ?? ""
        if !chosen.isEmpty, let v = AVSpeechSynthesisVoice(identifier: chosen) { return v }
        let voices = Self.englishVoices
        let wanted: AVSpeechSynthesisVoiceGender = presenter.prefersFemaleVoice ? .female : .male
        let us = voices.filter { $0.language == "en-US" }
        if let v = us.first(where: { $0.gender == wanted }) { return v }
        if let v = voices.first(where: { $0.gender == wanted }) { return v }
        return us.first ?? voices.first ?? AVSpeechSynthesisVoice(language: "en-US")
    }

    // MARK: playback

    private func activateSession() {
        let s = AVAudioSession.sharedInstance()
        try? s.setCategory(.playback, mode: .spokenAudio, options: [])
        try? s.setActive(true)
    }

    /// Speak `text`. `rateScale` multiplies the user's speed setting. `completion` runs when it finishes naturally.
    func speak(_ text: String, owner: String, rateScale: Double = 1, completion: (() -> Void)? = nil) {
        stop()
        activateSession()
        let presenter = Presenter.find(UserDefaults.standard.string(forKey: AppSettings.Keys.presenter) ?? "")
        let userRate = UserDefaults.standard.object(forKey: AppSettings.Keys.rate) as? Double ?? 1.0
        let u = AVSpeechUtterance(string: text)
        u.voice = voice(for: presenter)
        let base = Double(AVSpeechUtteranceDefaultSpeechRate)
        let rate = base * (0.55 + 0.45 * userRate * rateScale)
        u.rate = Float(min(max(rate, Double(AVSpeechUtteranceMinimumSpeechRate)), Double(AVSpeechUtteranceMaximumSpeechRate)))
        u.pitchMultiplier = presenter.pitch
        u.postUtteranceDelay = 0.12
        current = u
        self.completion = completion
        self.owner = owner
        currentText = text
        spokenRange = nil
        synth.speak(u)
    }

    func pause() {
        if synth.isSpeaking { synth.pauseSpeaking(at: .word) }
    }

    func resume() {
        if synth.isPaused { synth.continueSpeaking() }
    }

    func stop() {
        completion = nil
        current = nil
        if synth.isSpeaking || synth.isPaused { synth.stopSpeaking(at: .immediate) }
        isSpeaking = false
        isPaused = false
    }

    /// Stop only if `owner` currently controls the engine.
    func stop(owner: String) {
        if self.owner == owner { stop() }
    }

    func isActive(owner: String) -> Bool { self.owner == owner && (isSpeaking || isPaused) }

    // MARK: delegate

    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didStart utterance: AVSpeechUtterance) {
        DispatchQueue.main.async {
            guard utterance === self.current else { return }
            self.isSpeaking = true
            self.isPaused = false
        }
    }

    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {
        DispatchQueue.main.async {
            guard utterance === self.current else { return }
            self.isSpeaking = false
            self.isPaused = false
            self.current = nil
            let done = self.completion
            self.completion = nil
            done?()
        }
    }

    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didCancel utterance: AVSpeechUtterance) {
        DispatchQueue.main.async {
            if utterance === self.current || self.current == nil {
                self.isSpeaking = false
                self.isPaused = false
            }
        }
    }

    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didPause utterance: AVSpeechUtterance) {
        DispatchQueue.main.async { self.isPaused = true }
    }

    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didContinue utterance: AVSpeechUtterance) {
        DispatchQueue.main.async { self.isPaused = false }
    }

    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, willSpeakRangeOfSpeechString characterRange: NSRange, utterance: AVSpeechUtterance) {
        DispatchQueue.main.async {
            guard utterance === self.current else { return }
            self.lastWordAt = Date()
            self.spokenRange = characterRange
        }
    }
}
