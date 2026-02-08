/**
 * Client-side search across music, artists, shows, podcasts.
 * Call runSearch(tracks, artists, shows, query) with catalog data and query string.
 */
export function useSearch() {
  function runSearch(tracks, artists, shows, podcasts, query) {
    const q = (query || '').trim().toLowerCase()
    if (!q) {
      return { tracks: [], artists: [], shows: [], podcasts: [] }
    }

    const tracksFiltered = (tracks || []).filter(
      (t) =>
        (t.title || '').toLowerCase().includes(q) ||
        (t.artist || '').toLowerCase().includes(q)
    )
    const artistsFiltered = (artists || []).filter(
      (a) => (a.name || '').toLowerCase().includes(q)
    )
    const showsFiltered = (shows || []).filter(
      (s) =>
        (s.title || '').toLowerCase().includes(q) ||
        (s.host || '').toLowerCase().includes(q)
    )
    const podcastsFiltered = (podcasts || []).filter(
      (p) =>
        (p.title || '').toLowerCase().includes(q) ||
        (p.host || '').toLowerCase().includes(q)
    )

    return {
      tracks: tracksFiltered.slice(0, 20),
      artists: artistsFiltered.slice(0, 15),
      shows: showsFiltered.slice(0, 15),
      podcasts: podcastsFiltered.slice(0, 15),
    }
  }

  return { runSearch }
}
