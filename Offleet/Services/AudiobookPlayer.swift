import Combine
import Foundation
import MediaPlayer
import SwiftUI
import UIKit

/// Plays books paragraph by paragraph through the speech engine, with lock-screen controls,
/// background audio, a sleep timer and remembered positions.
@MainActor
final class AudiobookPlayer: ObservableObject {
    @Published private(set) var book: Book?
    @Published private(set) var chapterIndex = 0
    @Published private(set) var paraIndex = 0
    @Published private(set) var isPlaying = false
    @Published var speed: Double = 1.0
    @Published private(set) var sleepDeadline: Date?
    @Published var sleepAtChapterEnd = false
    @Published var showFullPlayer = false

    static let owner = "audiobook"
    private let engine = SpeechEngine.shared
    private var progress: ProgressStore?
    private var bag = Set<AnyCancellable>()
    private var remoteReady = false

    init() {
        engine.$owner
            .receive(on: RunLoop.main)
            .sink { [weak self] owner in
                guard let self else { return }
                if owner != Self.owner && self.isPlaying {
                    self.isPlaying = false
                    self.updateNowPlaying()
                }
            }
            .store(in: &bag)
    }

    func attach(progress: ProgressStore) { self.progress = progress }

    var chapter: Chapter? {
        guard let book, book.chapters.indices.contains(chapterIndex) else { return nil }
        return book.chapters[chapterIndex]
    }

    var para: Para? {
        guard let chapter, chapter.paras.indices.contains(paraIndex) else { return nil }
        return chapter.paras[paraIndex]
    }

    /// 0...1 progress through the current chapter.
    var chapterProgress: Double {
        guard let chapter, !chapter.paras.isEmpty else { return 0 }
        return Double(paraIndex) / Double(chapter.paras.count)
    }

    func bookProgress(_ b: Book) -> Double {
        guard let pos = progress?.position(book: b.id), !b.chapters.isEmpty else { return 0 }
        return min(1, Double(pos.chapter) / Double(b.chapters.count))
    }

    // MARK: control

    func open(_ b: Book, chapter: Int? = nil, autoplay: Bool = true) {
        if book?.id != b.id || chapter != nil {
            book = b
            if let chapter {
                chapterIndex = max(0, min(chapter, b.chapters.count - 1))
                paraIndex = 0
            } else if let pos = progress?.position(book: b.id), b.chapters.indices.contains(pos.chapter) {
                chapterIndex = pos.chapter
                paraIndex = min(pos.para, max(0, b.chapters[pos.chapter].paras.count - 1))
            } else {
                chapterIndex = 0
                paraIndex = 0
            }
        }
        setupRemoteCommands()
        if autoplay { play() } else { updateNowPlaying() }
    }

    func play() {
        guard book != nil else { return }
        isPlaying = true
        if engine.owner == Self.owner && engine.isPaused {
            engine.resume()
        } else {
            speakCurrent()
        }
        updateNowPlaying()
    }

    func pause() {
        isPlaying = false
        engine.pause()
        savePosition()
        updateNowPlaying()
    }

    func toggle() { isPlaying ? pause() : play() }

    func stop() {
        isPlaying = false
        engine.stop(owner: Self.owner)
        savePosition()
        book = nil
        MPNowPlayingInfoCenter.default().nowPlayingInfo = nil
    }

    func nextPara() { move(by: 1) }
    func prevPara() { move(by: -1) }

    func nextChapter() {
        guard let book, chapterIndex + 1 < book.chapters.count else { return }
        jump(chapter: chapterIndex + 1)
    }

    func prevChapter() {
        if paraIndex > 1 { jump(chapter: chapterIndex) } else { jump(chapter: max(0, chapterIndex - 1)) }
    }

    func jump(chapter: Int, para: Int = 0) {
        guard let book, book.chapters.indices.contains(chapter) else { return }
        chapterIndex = chapter
        paraIndex = max(0, min(para, book.chapters[chapter].paras.count - 1))
        savePosition()
        if isPlaying { speakCurrent() } else { engine.stop(owner: Self.owner) }
        updateNowPlaying()
    }

    func setSleep(minutes: Int?) {
        sleepAtChapterEnd = false
        sleepDeadline = minutes.map { Date().addingTimeInterval(TimeInterval($0 * 60)) }
    }

    func setSleepAtChapterEnd() {
        sleepDeadline = nil
        sleepAtChapterEnd = true
    }

    private func move(by delta: Int) {
        guard let book else { return }
        var c = chapterIndex, p = paraIndex + delta
        if p < 0 {
            if c > 0 { c -= 1; p = max(0, book.chapters[c].paras.count - 1) } else { p = 0 }
        } else if p >= book.chapters[c].paras.count {
            if c + 1 < book.chapters.count { c += 1; p = 0 } else { p = book.chapters[c].paras.count - 1 }
        }
        jump(chapter: c, para: p)
    }

    private func speakCurrent() {
        guard let para else { isPlaying = false; return }
        var text = para.speech
        if paraIndex == 0, let chapter {
            text = chapter.title + ". " + text
        }
        engine.speak(text, owner: Self.owner, rateScale: speed) { [weak self] in
            self?.advance()
        }
    }

    private func advance() {
        guard isPlaying, let book else { return }
        if let d = sleepDeadline, Date() >= d {
            sleepDeadline = nil
            pause()
            return
        }
        if paraIndex + 1 < book.chapters[chapterIndex].paras.count {
            paraIndex += 1
        } else if chapterIndex + 1 < book.chapters.count {
            if sleepAtChapterEnd {
                sleepAtChapterEnd = false
                chapterIndex += 1
                paraIndex = 0
                pause()
                return
            }
            chapterIndex += 1
            paraIndex = 0
        } else {
            isPlaying = false
            savePosition()
            updateNowPlaying()
            return
        }
        savePosition()
        speakCurrent()
        updateNowPlaying()
    }

    private func savePosition() {
        guard let book else { return }
        progress?.savePosition(book: book.id, BookPosition(chapter: chapterIndex, para: paraIndex))
    }

    // MARK: lock screen

    private func setupRemoteCommands() {
        guard !remoteReady else { return }
        remoteReady = true
        let c = MPRemoteCommandCenter.shared()
        c.playCommand.addTarget { [weak self] _ in
            Task { @MainActor in self?.play() }
            return .success
        }
        c.pauseCommand.addTarget { [weak self] _ in
            Task { @MainActor in self?.pause() }
            return .success
        }
        c.togglePlayPauseCommand.addTarget { [weak self] _ in
            Task { @MainActor in self?.toggle() }
            return .success
        }
        c.nextTrackCommand.addTarget { [weak self] _ in
            Task { @MainActor in self?.nextChapter() }
            return .success
        }
        c.previousTrackCommand.addTarget { [weak self] _ in
            Task { @MainActor in self?.prevChapter() }
            return .success
        }
        c.skipForwardCommand.preferredIntervals = [15]
        c.skipForwardCommand.addTarget { [weak self] _ in
            Task { @MainActor in self?.nextPara() }
            return .success
        }
        c.skipBackwardCommand.preferredIntervals = [15]
        c.skipBackwardCommand.addTarget { [weak self] _ in
            Task { @MainActor in self?.prevPara() }
            return .success
        }
    }

    private func updateNowPlaying() {
        guard let book, let chapter else { return }
        var info: [String: Any] = [
            MPMediaItemPropertyTitle: chapter.title,
            MPMediaItemPropertyArtist: "Offleet · \(Presenter.find(UserDefaults.standard.string(forKey: AppSettings.Keys.presenter) ?? "").name)",
            MPMediaItemPropertyAlbumTitle: book.title,
            MPNowPlayingInfoPropertyPlaybackRate: isPlaying ? 1.0 : 0.0,
            MPMediaItemPropertyPlaybackDuration: Double(max(chapter.paras.count, 1)) * 20,
            MPNowPlayingInfoPropertyElapsedPlaybackTime: Double(paraIndex) * 20,
        ]
        if let img = UIImage(named: "Artwork") {
            info[MPMediaItemPropertyArtwork] = Self.artwork(img)
        }
        MPNowPlayingInfoCenter.default().nowPlayingInfo = info
    }

    nonisolated private static func artwork(_ img: UIImage) -> MPMediaItemArtwork {
        MPMediaItemArtwork(boundsSize: img.size) { _ in img }
    }
}
