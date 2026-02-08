import CarPlay
import MediaPlayer
import AVFoundation

/**
 * CarPlay scene delegate for Ahoy Indie Media.
 *
 * Displays a tab bar with:
 *   - Music (list of all tracks)
 *   - Artists (list of artists → their tracks)
 *   - Podcasts (list of shows → episodes)
 *   - Now Playing (transport controls)
 *
 * NOTE: CarPlay requires an Apple-approved entitlement.
 * Apply at: https://developer.apple.com/contact/carplay/
 * Select "Audio" app type → you'll receive a CarPlay entitlement provisioning profile.
 *
 * Until the entitlement is approved, this code compiles but CarPlay won't launch the app.
 */
@available(iOS 14.0, *)
class AhoyCarPlaySceneDelegate: UIResponder, CPTemplateApplicationSceneDelegate {

    var interfaceController: CPInterfaceController?
    private let apiBase = "https://app.ahoy.ooo"

    // Cached data
    private var tracks: [[String: Any]] = []
    private var artists: [[String: Any]] = []
    private var podcastShows: [[String: Any]] = []

    // ── Scene lifecycle ─────────────────────────────────────────────

    func templateApplicationScene(
        _ templateApplicationScene: CPTemplateApplicationScene,
        didConnect interfaceController: CPInterfaceController
    ) {
        self.interfaceController = interfaceController

        // Fetch content then show UI
        fetchAllContent { [weak self] in
            guard let self = self else { return }
            let tabBar = self.buildTabBar()
            interfaceController.setRootTemplate(tabBar, animated: true, completion: nil)
        }
    }

    func templateApplicationScene(
        _ templateApplicationScene: CPTemplateApplicationScene,
        didDisconnectInterfaceController interfaceController: CPInterfaceController
    ) {
        self.interfaceController = nil
    }

    // ── Tab bar ─────────────────────────────────────────────────────

    private func buildTabBar() -> CPTabBarTemplate {
        let musicTab = buildMusicTab()
        let artistsTab = buildArtistsTab()
        let podcastsTab = buildPodcastsTab()

        let tabBar = CPTabBarTemplate(templates: [musicTab, artistsTab, podcastsTab])
        return tabBar
    }

    // ── Music tab ───────────────────────────────────────────────────

    private func buildMusicTab() -> CPListTemplate {
        let items = tracks.prefix(100).map { track -> CPListItem in
            let title = track["title"] as? String ?? "Unknown"
            let artist = track["artist"] as? String ?? ""
            let item = CPListItem(text: title, detailText: artist)
            item.handler = { [weak self] _, completion in
                self?.playTrack(track)
                completion()
            }
            return item
        }

        let section = CPListSection(items: items)
        let template = CPListTemplate(title: "Music", sections: [section])
        template.tabSystemItem = .mostViewed
        return template
    }

    // ── Artists tab ─────────────────────────────────────────────────

    private func buildArtistsTab() -> CPListTemplate {
        let items = artists.map { artist -> CPListItem in
            let name = artist["name"] as? String ?? "Unknown"
            let type = artist["type"] as? String ?? "Artist"
            let item = CPListItem(text: name, detailText: type)
            item.handler = { [weak self] _, completion in
                self?.showArtistTracks(artist)
                completion()
            }
            return item
        }

        let section = CPListSection(items: items)
        let template = CPListTemplate(title: "Artists", sections: [section])
        template.tabSystemItem = .contacts
        return template
    }

    private func showArtistTracks(_ artist: [String: Any]) {
        let artistName = artist["name"] as? String ?? ""
        let artistId = "\(artist["id"] ?? "")"

        let artistTracks = tracks.filter { track in
            let trackArtist = track["artist"] as? String ?? ""
            let trackArtistId = "\(track["artist_id"] ?? "")"
            return trackArtist == artistName || trackArtistId == artistId
        }

        let items = artistTracks.map { track -> CPListItem in
            let title = track["title"] as? String ?? "Unknown"
            let item = CPListItem(text: title, detailText: artistName)
            item.handler = { [weak self] _, completion in
                self?.playTrack(track)
                completion()
            }
            return item
        }

        let section = CPListSection(items: items)
        let template = CPListTemplate(title: artistName, sections: [section])
        interfaceController?.pushTemplate(template, animated: true, completion: nil)
    }

    // ── Podcasts tab ────────────────────────────────────────────────

    private func buildPodcastsTab() -> CPListTemplate {
        let items = podcastShows.map { show -> CPListItem in
            let title = show["title"] as? String ?? "Unknown"
            let episodes = show["episodes"] as? [[String: Any]] ?? []
            let item = CPListItem(text: title, detailText: "\(episodes.count) episodes")
            item.handler = { [weak self] _, completion in
                self?.showPodcastEpisodes(show)
                completion()
            }
            return item
        }

        let section = CPListSection(items: items)
        let template = CPListTemplate(title: "Podcasts", sections: [section])
        template.tabSystemItem = .downloads
        return template
    }

    private func showPodcastEpisodes(_ show: [String: Any]) {
        let showTitle = show["title"] as? String ?? "Podcast"
        let episodes = show["episodes"] as? [[String: Any]] ?? []

        let items = episodes.map { ep -> CPListItem in
            let title = ep["title"] as? String ?? "Episode"
            let date = ep["date"] as? String ?? ""
            let item = CPListItem(text: title, detailText: date)
            item.handler = { [weak self] _, completion in
                self?.playEpisode(ep, showTitle: showTitle, artwork: show["artwork"] as? String)
                completion()
            }
            return item
        }

        let section = CPListSection(items: items)
        let template = CPListTemplate(title: showTitle, sections: [section])
        interfaceController?.pushTemplate(template, animated: true, completion: nil)
    }

    // ── Playback ────────────────────────────────────────────────────

    private func playTrack(_ track: [String: Any]) {
        let audioUrl = track["audio_url"] as? String ?? track["url"] as? String ?? ""
        let title = track["title"] as? String ?? "Unknown"
        let artist = track["artist"] as? String ?? ""
        let artUrl = track["cover_art"] as? String ?? ""

        playAudio(url: audioUrl, title: title, artist: artist, artworkUrl: artUrl)
    }

    private func playEpisode(_ episode: [String: Any], showTitle: String, artwork: String?) {
        let audioUrl = episode["audio_url"] as? String ?? episode["url"] as? String ?? ""
        let title = episode["title"] as? String ?? "Episode"

        playAudio(url: audioUrl, title: title, artist: showTitle, artworkUrl: artwork ?? "")
    }

    private func playAudio(url: String, title: String, artist: String, artworkUrl: String) {
        guard let audioURL = URL(string: url) else { return }

        // Use AVPlayer for background-capable playback
        let playerItem = AVPlayerItem(url: audioURL)
        let player = AVPlayer(playerItem: playerItem)
        AhoyAudioPlayer.shared.player = player
        player.play()

        // Update Now Playing info
        var nowPlayingInfo: [String: Any] = [
            MPMediaItemPropertyTitle: title,
            MPMediaItemPropertyArtist: artist,
            MPNowPlayingInfoPropertyPlaybackRate: 1.0,
        ]

        // Load artwork async
        if !artworkUrl.isEmpty, let artURL = URL(string: artworkUrl) {
            URLSession.shared.dataTask(with: artURL) { data, _, _ in
                if let data = data, let image = UIImage(data: data) {
                    let artwork = MPMediaItemArtwork(boundsSize: image.size) { _ in image }
                    nowPlayingInfo[MPMediaItemPropertyArtwork] = artwork
                    MPNowPlayingInfoCenter.default().nowPlayingInfo = nowPlayingInfo
                }
            }.resume()
        }

        MPNowPlayingInfoCenter.default().nowPlayingInfo = nowPlayingInfo

        // Set up remote command center
        let commandCenter = MPRemoteCommandCenter.shared()
        commandCenter.playCommand.isEnabled = true
        commandCenter.playCommand.addTarget { _ in
            player.play()
            return .success
        }
        commandCenter.pauseCommand.isEnabled = true
        commandCenter.pauseCommand.addTarget { _ in
            player.pause()
            return .success
        }

        // Show Now Playing template on CarPlay
        if let controller = interfaceController {
            let nowPlaying = CPNowPlayingTemplate.shared
            controller.pushTemplate(nowPlaying, animated: true, completion: nil)
        }
    }

    // ── Network ─────────────────────────────────────────────────────

    private func fetchAllContent(completion: @escaping () -> Void) {
        let group = DispatchGroup()

        group.enter()
        fetchJSON(path: "/api/music", key: "tracks") { [weak self] items in
            self?.tracks = items
            group.leave()
        }

        group.enter()
        fetchJSON(path: "/api/artists", key: "artists") { [weak self] items in
            self?.artists = items
            group.leave()
        }

        group.enter()
        fetchJSON(path: "/api/podcasts", key: "shows") { [weak self] items in
            self?.podcastShows = items
            group.leave()
        }

        group.notify(queue: .main) {
            completion()
        }
    }

    private func fetchJSON(path: String, key: String, completion: @escaping ([[String: Any]]) -> Void) {
        guard let url = URL(string: apiBase + path) else {
            completion([])
            return
        }
        var request = URLRequest(url: url)
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        request.timeoutInterval = 15

        URLSession.shared.dataTask(with: request) { data, _, error in
            guard let data = data, error == nil,
                  let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let items = json[key] as? [[String: Any]] else {
                DispatchQueue.main.async { completion([]) }
                return
            }
            DispatchQueue.main.async { completion(items) }
        }.resume()
    }
}

// Shared audio player singleton so playback persists across templates
class AhoyAudioPlayer {
    static let shared = AhoyAudioPlayer()
    var player: AVPlayer?
    private init() {}
}
