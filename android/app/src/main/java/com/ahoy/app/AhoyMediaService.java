package com.ahoy.app;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.support.v4.media.MediaBrowserCompat;
import android.support.v4.media.MediaDescriptionCompat;
import android.support.v4.media.MediaMetadataCompat;
import android.support.v4.media.session.MediaSessionCompat;
import android.support.v4.media.session.PlaybackStateCompat;
import android.media.AudioAttributes;
import android.media.AudioFocusRequest;
import android.media.AudioManager;
import android.media.MediaPlayer;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.core.app.NotificationCompat;
import androidx.media.MediaBrowserServiceCompat;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Android Auto media browser service.
 *
 * Exposes the Ahoy music catalog as a browsable tree:
 *   ROOT
 *   ├── All Music
 *   ├── Artists
 *   │   ├── Artist 1
 *   │   │   └── track ...
 *   │   └── Artist 2
 *   └── Podcasts
 *       ├── Show 1
 *       │   └── episode ...
 *       └── Show 2
 *
 * Handles playback via MediaPlayer with audio focus.
 */
public class AhoyMediaService extends MediaBrowserServiceCompat {

    private static final String TAG = "AhoyMediaService";
    private static final String API_BASE = "https://app.ahoy.ooo";
    private static final String NOTIFICATION_CHANNEL_ID = "ahoy_playback";
    private static final int NOTIFICATION_ID = 1001;

    // Media tree IDs
    private static final String ROOT_ID = "ROOT";
    private static final String MUSIC_ROOT = "MUSIC";
    private static final String ARTISTS_ROOT = "ARTISTS";
    private static final String PODCASTS_ROOT = "PODCASTS";

    private MediaSessionCompat mediaSession;
    private PlaybackStateCompat.Builder stateBuilder;
    private MediaPlayer mediaPlayer;
    private AudioManager audioManager;
    private AudioFocusRequest focusRequest;

    // Cached data
    private List<JSONObject> tracks = new ArrayList<>();
    private List<JSONObject> artists = new ArrayList<>();
    private List<JSONObject> podcastShows = new ArrayList<>();

    // Current playback state
    private List<JSONObject> currentQueue = new ArrayList<>();
    private int currentIndex = -1;

    private final ExecutorService executor = Executors.newSingleThreadExecutor();

    @Override
    public void onCreate() {
        super.onCreate();

        // Create MediaSession
        mediaSession = new MediaSessionCompat(this, TAG);
        mediaSession.setFlags(
            MediaSessionCompat.FLAG_HANDLES_MEDIA_BUTTONS |
            MediaSessionCompat.FLAG_HANDLES_TRANSPORT_CONTROLS
        );

        stateBuilder = new PlaybackStateCompat.Builder()
            .setActions(
                PlaybackStateCompat.ACTION_PLAY |
                PlaybackStateCompat.ACTION_PAUSE |
                PlaybackStateCompat.ACTION_SKIP_TO_NEXT |
                PlaybackStateCompat.ACTION_SKIP_TO_PREVIOUS |
                PlaybackStateCompat.ACTION_STOP |
                PlaybackStateCompat.ACTION_SEEK_TO |
                PlaybackStateCompat.ACTION_PLAY_FROM_MEDIA_ID
            );
        mediaSession.setPlaybackState(stateBuilder.build());
        mediaSession.setCallback(new MediaSessionCallback());
        mediaSession.setActive(true);

        setSessionToken(mediaSession.getSessionToken());

        // Audio manager for focus
        audioManager = (AudioManager) getSystemService(AUDIO_SERVICE);

        createNotificationChannel();

        // Fetch content in background
        executor.execute(this::fetchAllContent);
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                NOTIFICATION_CHANNEL_ID,
                "Ahoy Playback",
                NotificationManager.IMPORTANCE_LOW
            );
            channel.setDescription("Now playing in Ahoy");
            NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            if (nm != null) nm.createNotificationChannel(channel);
        }
    }

    private android.app.Notification buildPlaybackNotification(String title, String artist) {
        Intent openApp = getPackageManager().getLaunchIntentForPackage(getPackageName());
        PendingIntent pending = PendingIntent.getActivity(this, 0,
            openApp != null ? openApp : new Intent(this, MainActivity.class),
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        NotificationCompat.Builder builder = new NotificationCompat.Builder(this, NOTIFICATION_CHANNEL_ID)
            .setContentTitle(title != null && !title.isEmpty() ? title : "Ahoy Indie Media")
            .setContentText(artist != null && !artist.isEmpty() ? artist : "Now playing")
            .setSmallIcon(android.R.drawable.ic_media_play)
            .setContentIntent(pending)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .setOngoing(true);

        androidx.media.app.NotificationCompat.MediaStyle style =
            new androidx.media.app.NotificationCompat.MediaStyle()
                .setMediaSession(mediaSession.getSessionToken());
        builder.setStyle(style);

        return builder.build();
    }

    @Override
    public void onDestroy() {
        if (mediaPlayer != null) {
            mediaPlayer.release();
            mediaPlayer = null;
        }
        if (mediaSession != null) {
            mediaSession.setActive(false);
            mediaSession.release();
        }
        executor.shutdown();
        super.onDestroy();
    }

    // ── Browse tree ─────────────────────────────────────────────────

    @Nullable
    @Override
    public BrowserRoot onGetRoot(@NonNull String clientPackageName, int clientUid, @Nullable Bundle rootHints) {
        // Allow all clients (Android Auto, etc.)
        return new BrowserRoot(ROOT_ID, null);
    }

    @Override
    public void onLoadChildren(@NonNull String parentId, @NonNull Result<List<MediaBrowserCompat.MediaItem>> result) {
        // Defer result so we can load async if needed
        result.detach();
        executor.execute(() -> {
            List<MediaBrowserCompat.MediaItem> items = buildChildren(parentId);
            result.sendResult(items);
        });
    }

    private List<MediaBrowserCompat.MediaItem> buildChildren(String parentId) {
        List<MediaBrowserCompat.MediaItem> items = new ArrayList<>();

        switch (parentId) {
            case ROOT_ID:
                items.add(makeBrowsable(MUSIC_ROOT, "All Music", "Browse all tracks", null));
                items.add(makeBrowsable(ARTISTS_ROOT, "Artists", "Browse by artist", null));
                items.add(makeBrowsable(PODCASTS_ROOT, "Podcasts", "Browse podcasts", null));
                break;

            case MUSIC_ROOT:
                for (JSONObject track : tracks) {
                    items.add(makePlayable(track, "track"));
                }
                break;

            case ARTISTS_ROOT:
                for (JSONObject artist : artists) {
                    String aid = optString(artist, "id");
                    if (aid.isEmpty()) aid = optString(artist, "slug");
                    String id = "ARTIST:" + aid;
                    String name = optString(artist, "name");
                    String image = optString(artist, "image");
                    items.add(makeBrowsable(id, name, optString(artist, "type"), parseUri(image)));
                }
                break;

            case PODCASTS_ROOT:
                for (JSONObject show : podcastShows) {
                    String id = "PODCAST:" + optString(show, "slug");
                    String title = optString(show, "title");
                    String artwork = optString(show, "artwork");
                    int epCount = show.optJSONArray("episodes") != null ? show.optJSONArray("episodes").length() : 0;
                    items.add(makeBrowsable(id, title, epCount + " episodes", parseUri(artwork)));
                }
                break;

            default:
                if (parentId.startsWith("ARTIST:")) {
                    String artistId = parentId.substring(7);
                    String artistName = "";
                    for (JSONObject a : artists) {
                        if (optString(a, "id").equals(artistId) || optString(a, "slug").equals(artistId)) {
                            artistName = optString(a, "name");
                            break;
                        }
                    }
                    for (JSONObject track : tracks) {
                        if (optString(track, "artist").equals(artistName) ||
                            optString(track, "artist_id").equals(artistId) ||
                            optString(track, "artist_slug").equals(artistId)) {
                            items.add(makePlayable(track, "track"));
                        }
                    }
                } else if (parentId.startsWith("PODCAST:")) {
                    String slug = parentId.substring(8);
                    for (JSONObject show : podcastShows) {
                        if (optString(show, "slug").equals(slug)) {
                            JSONArray episodes = show.optJSONArray("episodes");
                            if (episodes != null) {
                                for (int i = 0; i < episodes.length(); i++) {
                                    try {
                                        JSONObject ep = episodes.getJSONObject(i);
                                        items.add(makePlayable(ep, "episode"));
                                    } catch (Exception e) {
                                        Log.w(TAG, "Error parsing episode", e);
                                    }
                                }
                            }
                            break;
                        }
                    }
                }
                break;
        }
        return items;
    }

    private MediaBrowserCompat.MediaItem makeBrowsable(String id, String title, String subtitle, Uri iconUri) {
        MediaDescriptionCompat.Builder desc = new MediaDescriptionCompat.Builder()
            .setMediaId(id)
            .setTitle(title)
            .setSubtitle(subtitle);
        if (iconUri != null) desc.setIconUri(iconUri);
        return new MediaBrowserCompat.MediaItem(desc.build(), MediaBrowserCompat.MediaItem.FLAG_BROWSABLE);
    }

    private MediaBrowserCompat.MediaItem makePlayable(JSONObject item, String type) {
        String id = type + ":" + optString(item, "id");
        String title = optString(item, "title");
        String artist = optString(item, "artist");
        String art = optString(item, "cover_art");
        if (art.isEmpty()) art = optString(item, "artwork");

        MediaDescriptionCompat.Builder desc = new MediaDescriptionCompat.Builder()
            .setMediaId(id)
            .setTitle(title)
            .setSubtitle(artist);
        if (!art.isEmpty()) desc.setIconUri(parseUri(art));

        // Store audio URL in extras (for optional use)
        Bundle extras = new Bundle();
        String audioUrl = optString(item, "audio_url");
        if (audioUrl.isEmpty()) audioUrl = optString(item, "url");
        if (audioUrl.isEmpty()) audioUrl = optString(item, "preview_url");
        extras.putString("audio_url", audioUrl);
        desc.setExtras(extras);

        return new MediaBrowserCompat.MediaItem(desc.build(), MediaBrowserCompat.MediaItem.FLAG_PLAYABLE);
    }

    // ── Playback ────────────────────────────────────────────────────

    private class MediaSessionCallback extends MediaSessionCompat.Callback {

        @Override
        public void onPlayFromMediaId(String mediaId, Bundle extras) {
            // Find the item and play it
            String audioUrl = null;
            String title = "";
            String artist = "";
            String artUrl = "";

            // Search tracks
            for (JSONObject track : tracks) {
                String trackId = "track:" + optString(track, "id");
                if (trackId.equals(mediaId)) {
                    audioUrl = optString(track, "audio_url");
                    if (audioUrl.isEmpty()) audioUrl = optString(track, "url");
                    if (audioUrl.isEmpty()) audioUrl = optString(track, "preview_url");
                    title = optString(track, "title");
                    artist = optString(track, "artist");
                    artUrl = optString(track, "cover_art");
                    // Set queue to all tracks, starting from this one
                    currentQueue = new ArrayList<>(tracks);
                    currentIndex = tracks.indexOf(track);
                    break;
                }
            }

            // Search podcast episodes
            if (audioUrl == null) {
                for (JSONObject show : podcastShows) {
                    JSONArray episodes = show.optJSONArray("episodes");
                    if (episodes != null) {
                        for (int i = 0; i < episodes.length(); i++) {
                            try {
                                JSONObject ep = episodes.getJSONObject(i);
                                String epId = "episode:" + optString(ep, "id");
                                if (epId.equals(mediaId)) {
                                    audioUrl = optString(ep, "audio_url");
                                    if (audioUrl.isEmpty()) audioUrl = optString(ep, "url");
                                    if (audioUrl.isEmpty()) audioUrl = optString(ep, "preview_url");
                                    title = optString(ep, "title");
                                    artist = optString(show, "title");
                                    artUrl = optString(show, "artwork");
                                    // Set queue to this show's episodes so next/prev work in-car
                                    currentQueue = new ArrayList<>();
                                    String showTitle = optString(show, "title");
                                    for (int j = 0; j < episodes.length(); j++) {
                                        JSONObject e = episodes.getJSONObject(j);
                                        try {
                                            JSONObject copy = new JSONObject(e.toString());
                                            copy.put("artist", showTitle);
                                            copy.put("artwork", artUrl.isEmpty() ? optString(e, "artwork") : artUrl);
                                            currentQueue.add(copy);
                                        } catch (Exception e2) {
                                            currentQueue.add(e);
                                        }
                                    }
                                    currentIndex = i;
                                    break;
                                }
                            } catch (Exception e) { /* ignore */ }
                        }
                    }
                }
            }

            if (audioUrl != null && !audioUrl.isEmpty()) {
                playUrl(audioUrl, title, artist, artUrl);
            }
        }

        @Override
        public void onPlay() {
            if (mediaPlayer != null && !mediaPlayer.isPlaying()) {
                requestAudioFocus();
                mediaPlayer.start();
                updatePlaybackState(PlaybackStateCompat.STATE_PLAYING);
            }
        }

        @Override
        public void onPause() {
            if (mediaPlayer != null && mediaPlayer.isPlaying()) {
                mediaPlayer.pause();
                updatePlaybackState(PlaybackStateCompat.STATE_PAUSED);
            }
        }

        @Override
        public void onStop() {
            if (mediaPlayer != null) {
                mediaPlayer.stop();
                mediaPlayer.release();
                mediaPlayer = null;
            }
            stopForeground(true);
            abandonAudioFocus();
            updatePlaybackState(PlaybackStateCompat.STATE_STOPPED);
        }

        @Override
        public void onSkipToNext() {
            if (currentQueue.isEmpty()) return;
            currentIndex = (currentIndex + 1) % currentQueue.size();
            playQueueItem(currentIndex);
        }

        @Override
        public void onSkipToPrevious() {
            if (currentQueue.isEmpty()) return;
            // If past 3 seconds, restart; otherwise go back
            if (mediaPlayer != null && mediaPlayer.getCurrentPosition() > 3000) {
                mediaPlayer.seekTo(0);
                return;
            }
            currentIndex = currentIndex > 0 ? currentIndex - 1 : currentQueue.size() - 1;
            playQueueItem(currentIndex);
        }

        @Override
        public void onSeekTo(long pos) {
            if (mediaPlayer != null) {
                mediaPlayer.seekTo((int) pos);
                updatePlaybackState(mediaPlayer.isPlaying() ?
                    PlaybackStateCompat.STATE_PLAYING : PlaybackStateCompat.STATE_PAUSED);
            }
        }
    }

    private void playQueueItem(int index) {
        if (index < 0 || index >= currentQueue.size()) return;
        JSONObject item = currentQueue.get(index);
        String audioUrl = optString(item, "audio_url");
        if (audioUrl.isEmpty()) audioUrl = optString(item, "url");
        if (audioUrl.isEmpty()) audioUrl = optString(item, "preview_url");
        String title = optString(item, "title");
        String artist = optString(item, "artist");
        String artUrl = optString(item, "cover_art");
        if (artUrl.isEmpty()) artUrl = optString(item, "artwork");
        if (!audioUrl.isEmpty()) {
            playUrl(audioUrl, title, artist, artUrl);
        }
    }

    private void playUrl(String url, String title, String artist, String artUrl) {
        if (url == null || url.isEmpty()) return;
        if (url.startsWith("/")) url = API_BASE + url;
        final String resolvedUrl = url;
        executor.execute(() -> {
            try {
                if (mediaPlayer != null) {
                    mediaPlayer.release();
                }
                mediaPlayer = new MediaPlayer();
                mediaPlayer.setAudioAttributes(
                    new AudioAttributes.Builder()
                        .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                        .setUsage(AudioAttributes.USAGE_MEDIA)
                        .build()
                );
                mediaPlayer.setDataSource(resolvedUrl);
                mediaPlayer.setOnPreparedListener(mp -> {
                    requestAudioFocus();
                    startForeground(NOTIFICATION_ID, buildPlaybackNotification(title, artist));
                    mp.start();
                    updatePlaybackState(PlaybackStateCompat.STATE_PLAYING);
                });
                mediaPlayer.setOnCompletionListener(mp -> {
                    // Auto-advance
                    if (!currentQueue.isEmpty()) {
                        currentIndex = (currentIndex + 1) % currentQueue.size();
                        playQueueItem(currentIndex);
                    } else {
                        stopForeground(true);
                        updatePlaybackState(PlaybackStateCompat.STATE_STOPPED);
                    }
                });
                mediaPlayer.setOnErrorListener((mp, what, extra) -> {
                    Log.e(TAG, "MediaPlayer error: " + what + "/" + extra);
                    updatePlaybackState(PlaybackStateCompat.STATE_ERROR);
                    return true;
                });
                mediaPlayer.prepareAsync();

                // Update metadata
                MediaMetadataCompat.Builder meta = new MediaMetadataCompat.Builder()
                    .putString(MediaMetadataCompat.METADATA_KEY_TITLE, title)
                    .putString(MediaMetadataCompat.METADATA_KEY_ARTIST, artist)
                    .putString(MediaMetadataCompat.METADATA_KEY_ALBUM, "Ahoy Indie Media");
                if (!artUrl.isEmpty()) {
                    meta.putString(MediaMetadataCompat.METADATA_KEY_ALBUM_ART_URI, artUrl);
                }
                mediaSession.setMetadata(meta.build());
                updatePlaybackState(PlaybackStateCompat.STATE_BUFFERING);

            } catch (Exception e) {
                Log.e(TAG, "Error playing URL", e);
                updatePlaybackState(PlaybackStateCompat.STATE_ERROR);
            }
        });
    }

    private void updatePlaybackState(int state) {
        long position = 0;
        if (mediaPlayer != null) {
            try { position = mediaPlayer.getCurrentPosition(); } catch (Exception e) { /* ignore */ }
        }
        stateBuilder.setState(state, position, 1.0f);
        mediaSession.setPlaybackState(stateBuilder.build());
    }

    // ── Audio Focus ─────────────────────────────────────────────────

    private void requestAudioFocus() {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            focusRequest = new AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN)
                .setAudioAttributes(new AudioAttributes.Builder()
                    .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                    .setUsage(AudioAttributes.USAGE_MEDIA)
                    .build())
                .setOnAudioFocusChangeListener(focusChange -> {
                    if (focusChange == AudioManager.AUDIOFOCUS_LOSS) {
                        if (mediaPlayer != null && mediaPlayer.isPlaying()) {
                            mediaPlayer.pause();
                            updatePlaybackState(PlaybackStateCompat.STATE_PAUSED);
                        }
                    }
                })
                .build();
            audioManager.requestAudioFocus(focusRequest);
        }
    }

    private void abandonAudioFocus() {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O && focusRequest != null) {
            audioManager.abandonAudioFocusRequest(focusRequest);
        }
    }

    // ── Network ─────────────────────────────────────────────────────

    private void fetchAllContent() {
        tracks = fetchJsonArray(API_BASE + "/api/music", "tracks");
        artists = fetchJsonArray(API_BASE + "/api/artists", "artists");
        podcastShows = fetchJsonArray(API_BASE + "/api/podcasts", "shows");
        Log.i(TAG, "Loaded " + tracks.size() + " tracks, " + artists.size() + " artists, " + podcastShows.size() + " podcast shows");
    }

    private List<JSONObject> fetchJsonArray(String urlString, String key) {
        List<JSONObject> result = new ArrayList<>();
        try {
            URL url = new URL(urlString);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setRequestProperty("Accept", "application/json");
            conn.setConnectTimeout(10000);
            conn.setReadTimeout(10000);

            if (conn.getResponseCode() == 200) {
                BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                StringBuilder sb = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) sb.append(line);
                reader.close();

                JSONObject json = new JSONObject(sb.toString());
                JSONArray array = json.optJSONArray(key);
                if (array != null) {
                    for (int i = 0; i < array.length(); i++) {
                        result.add(array.getJSONObject(i));
                    }
                }
            }
            conn.disconnect();
        } catch (Exception e) {
            Log.e(TAG, "Error fetching " + urlString, e);
        }
        return result;
    }

    // ── Utilities ───────────────────────────────────────────────────

    private static String optString(JSONObject obj, String key) {
        try { return obj.optString(key, ""); } catch (Exception e) { return ""; }
    }

    private static Uri parseUri(String url) {
        if (url == null || url.isEmpty()) return null;
        return Uri.parse(url);
    }
}
