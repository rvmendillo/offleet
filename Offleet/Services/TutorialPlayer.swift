import Foundation
import SwiftUI

/// Drives an animated tutorial: shows a frame, speaks its narration, then advances automatically.
@MainActor
final class TutorialPlayer: ObservableObject {
    @Published private(set) var frames: [Frame] = []
    @Published var index = 0
    @Published private(set) var isPlaying = false
    @Published private(set) var finished = false
    @Published var speed: Double = 1.0

    static let owner = "tutorial"
    private let engine = SpeechEngine.shared
    private var token = 0
    var presenterName = "Mira"
    var greeting = true

    var frame: Frame? { frames.indices.contains(index) ? frames[index] : nil }
    var progress: Double { frames.count > 1 ? Double(index) / Double(frames.count - 1) : 0 }

    func load(_ frames: [Frame]) {
        stop()
        self.frames = frames
        index = 0
        finished = false
    }

    func play() {
        guard !frames.isEmpty else { return }
        if finished {
            finished = false
            index = 0
        }
        isPlaying = true
        if engine.owner == Self.owner && engine.isPaused {
            engine.resume()
        } else {
            speakCurrent()
        }
    }

    func pause() {
        isPlaying = false
        token += 1
        if engine.owner == Self.owner { engine.pause() }
    }

    func toggle() { isPlaying ? pause() : play() }

    func stop() {
        isPlaying = false
        token += 1
        engine.stop(owner: Self.owner)
    }

    func next() { go(to: index + 1) }
    func previous() { go(to: index - 1) }

    func go(to i: Int) {
        guard frames.indices.contains(i) else { return }
        token += 1
        withAnimation(.spring(response: 0.5, dampingFraction: 0.85)) { index = i }
        finished = false
        if isPlaying {
            speakCurrent()
        } else {
            engine.stop(owner: Self.owner)
        }
    }

    private func speakCurrent() {
        guard let f = frame else { return }
        token += 1
        let my = token
        var text = f.speech
        if index == 0 && greeting {
            text = "Hi, I'm \(presenterName)! " + text
        }
        engine.speak(text, owner: Self.owner, rateScale: speed) { [weak self] in
            guard let self else { return }
            Task { @MainActor in
                try? await Task.sleep(nanoseconds: 350_000_000)
                guard self.isPlaying, self.token == my else { return }
                if self.index + 1 < self.frames.count {
                    withAnimation(.spring(response: 0.55, dampingFraction: 0.85)) { self.index += 1 }
                    self.speakCurrent()
                } else {
                    self.isPlaying = false
                    self.finished = true
                }
            }
        }
    }
}

/// Speaks a single script (reviewer bites, approach ideas) with the presenter.
@MainActor
final class ScriptReader: ObservableObject {
    @Published private(set) var isPlaying = false
    @Published private(set) var sentenceIndex = 0
    @Published private(set) var sentences: [String] = []
    let owner: String
    private let engine = SpeechEngine.shared
    private var token = 0

    init(owner: String = "script") { self.owner = owner }

    func load(_ text: String) {
        stop()
        sentences = Self.split(text)
        sentenceIndex = 0
    }

    static func split(_ text: String) -> [String] {
        var out: [String] = []
        var cur = ""
        let chars = Array(text)
        for (i, ch) in chars.enumerated() {
            cur.append(ch)
            if ".!?".contains(ch) {
                let next = i + 1 < chars.count ? chars[i + 1] : " "
                if next == " " || next == "\n" {
                    let t = cur.trimmingCharacters(in: .whitespacesAndNewlines)
                    if !t.isEmpty { out.append(t) }
                    cur = ""
                }
            }
        }
        let t = cur.trimmingCharacters(in: .whitespacesAndNewlines)
        if !t.isEmpty { out.append(t) }
        // merge very short fragments into the previous sentence
        var merged: [String] = []
        for s in out {
            if let last = merged.last, s.count < 18 {
                merged[merged.count - 1] = last + " " + s
            } else {
                merged.append(s)
            }
        }
        return merged
    }

    func toggle() { isPlaying ? pause() : play() }

    func play() {
        guard !sentences.isEmpty else { return }
        if sentenceIndex >= sentences.count { sentenceIndex = 0 }
        isPlaying = true
        if engine.owner == owner && engine.isPaused { engine.resume() } else { speakCurrent() }
    }

    func pause() {
        isPlaying = false
        token += 1
        if engine.owner == owner { engine.pause() }
    }

    func stop() {
        isPlaying = false
        token += 1
        engine.stop(owner: owner)
    }

    private func speakCurrent() {
        guard sentences.indices.contains(sentenceIndex) else { isPlaying = false; return }
        token += 1
        let my = token
        engine.speak(sentences[sentenceIndex], owner: owner) { [weak self] in
            guard let self else { return }
            Task { @MainActor in
                guard self.isPlaying, self.token == my else { return }
                if self.sentenceIndex + 1 < self.sentences.count {
                    self.sentenceIndex += 1
                    self.speakCurrent()
                } else {
                    self.sentenceIndex = self.sentences.count
                    self.isPlaying = false
                }
            }
        }
    }
}
