# Font Awesome Icons Reference for Dashboard

## Current Icons in Use

| Section | Current Icon | Class |
|---------|-------------|-------|
| Explore | `fa-compass` | `fas fa-compass` |
| Music | `fa-music` | `fas fa-music` |
| Podcasts | `fa-podcast` | `fas fa-podcast` |
| Live TV | `fa-tv` | `fas fa-tv` |
| Videos | `fa-video` | `fas fa-video` |
| Artists | `fa-users` | `fas fa-users` |
| Radio | `fa-broadcast-tower` | `fas fa-broadcast-tower` |
| Events | `fa-calendar-alt` | `fas fa-calendar-alt` |
| Merch | `fa-shopping-bag` | `fas fa-shopping-bag` |
| Saved/Bookmarks | `fa-bookmark` | `fas fa-bookmark` |
| Profile | `fa-user` | `fas fa-user` |
| Settings | `fa-cog` | `fas fa-cog` |

## Alternative Icon Options

### Explore / Discovery
- `fa-compass` (current) - Navigation compass
- `fa-search` - Search/magnifying glass
- `fa-globe` - Global/worldwide
- `fa-rocket` - Launch/explore
- `fa-star` - Featured/favorites
- `fa-fire` - Trending/hot
- `fa-lightbulb` - Ideas/discover
- `fa-map` - Map/explore locations
- `fa-binoculars` - Discover/view
- `fa-bullseye` - Target/aim

### Music
- `fa-music` (current) - Musical note
- `fa-headphones` - Headphones
- `fa-guitar` - Guitar
- `fa-microphone` - Microphone
- `fa-compact-disc` - CD/Disc
- `fa-waveform-lines` - Sound waves
- `fa-music-note` - Single note
- `fa-radio` - Radio
- `fa-sliders` - Audio controls

### Podcasts
- `fa-podcast` (current) - Podcast icon
- `fa-microphone-alt` - Microphone
- `fa-headphones-alt` - Headphones
- `fa-broadcast-tower` - Broadcasting
- `fa-rss` - RSS feed
- `fa-comments` - Discussion
- `fa-volume-up` - Audio/sound

### Live TV / Television
- `fa-tv` (current) - TV screen
- `fa-desktop` - Desktop monitor
- `fa-satellite-dish` - Satellite
- `fa-signal` - Signal strength
- `fa-satellite` - Satellite
- `fa-video` - Video camera
- `fa-film` - Film reel

### Videos
- `fa-video` (current) - Video camera
- `fa-play-circle` - Play button
- `fa-film` - Film reel
- `fa-clapperboard` - Movie clapperboard
- `fa-video-slash` - Video off
- `fa-camera` - Camera
- `fa-youtube` - YouTube (brand)

### Artists / People
- `fa-users` (current) - Multiple people
- `fa-user` - Single person
- `fa-user-friends` - Friends
- `fa-user-circle` - User profile
- `fa-id-card` - ID card
- `fa-address-card` - Contact card
- `fa-theater-masks` - Performance/art
- `fa-palette` - Artist palette

### Radio
- `fa-broadcast-tower` (current) - Radio tower
- `fa-radio` - Radio device
- `fa-signal` - Signal
- `fa-satellite-dish` - Satellite dish
- `fa-wifi` - Wireless signal
- `fa-waves` - Radio waves
- `fa-volume-up` - Volume/sound

### Events / Calendar
- `fa-calendar-alt` (current) - Calendar
- `fa-calendar` - Calendar
- `fa-calendar-check` - Calendar with check
- `fa-clock` - Clock/time
- `fa-bell` - Notification bell
- `fa-calendar-day` - Day view
- `fa-calendar-week` - Week view
- `fa-birthday-cake` - Celebration
- `fa-ticket-alt` - Event ticket

### Merch / Shopping
- `fa-shopping-bag` (current) - Shopping bag
- `fa-shopping-cart` - Shopping cart
- `fa-store` - Store/shop
- `fa-tshirt` - T-shirt
- `fa-gift` - Gift
- `fa-box` - Package/box
- `fa-tags` - Price tags
- `fa-credit-card` - Payment
- `fa-coins` - Money/currency

### Bookmarks / Saved
- `fa-bookmark` (current) - Bookmark
- `fa-heart` - Heart/favorite
- `fa-star` - Star
- `fa-save` - Save icon
- `fa-folder` - Folder
- `fa-archive` - Archive
- `fa-book` - Book
- `fa-list` - List

### Profile / Account
- `fa-user` (current) - User
- `fa-user-circle` - User circle
- `fa-id-card` - ID card
- `fa-address-card` - Address card
- `fa-user-edit` - Edit profile
- `fa-portrait` - Portrait
- `fa-user-tie` - Professional

### Settings
- `fa-cog` (current) - Gear/settings
- `fa-sliders-h` - Sliders
- `fa-tools` - Tools
- `fa-wrench` - Wrench
- `fa-screwdriver` - Screwdriver
- `fa-cogs` - Multiple gears
- `fa-toggle-on` - Toggle switch

## Icon Styles Available

Font Awesome 6.0.0 (which you're using) has three main styles:

1. **Solid** (`fas`) - Filled icons (most common)
   - Example: `<i class="fas fa-music"></i>`

2. **Regular** (`far`) - Outlined icons
   - Example: `<i class="far fa-bookmark"></i>`

3. **Brands** (`fab`) - Brand logos
   - Example: `<i class="fab fa-youtube"></i>`

## How Icons Are Chosen

Currently, icons are chosen based on semantic meaning:
- **Explore** → Compass (navigation/discovery)
- **Music** → Music note (audio content)
- **Podcasts** → Podcast icon (audio shows)
- **Live TV** → TV (television)
- **Videos** → Video camera (video content)
- **Artists** → Users (people/creators)
- **Radio** → Broadcast tower (radio waves)
- **Events** → Calendar (scheduled events)
- **Merch** → Shopping bag (purchases)
- **Saved** → Bookmark (saved items)
- **Profile** → User (account)
- **Settings** → Cog (configuration)

## Extended Hover Effects

When users hover over sidebar icons for **1.5 seconds or longer**, fun animations trigger:
- **Compass**: Spins continuously
- **Music**: Bounces up and down
- **Podcast**: Pulses with scale
- **TV**: Shakes side to side
- **Video**: Flips 3D rotation
- **Users**: Wiggles rotation
- **Broadcast Tower**: Pulses with golden glow
- **Calendar**: Bounces
- **Shopping Bag**: Shakes
- **Bookmark**: Wiggles
- **User**: Pulses
- **Cog**: Spins continuously

All effects include:
- Color changes to vibrant hues
- Glow effects (drop shadows)
- Sparkle emojis (✨) floating on sides
- No font scaling (as requested)

## How to Change Icons

1. Find the icon you want in the list above
2. Open `templates/base.html`
3. Find the sidebar item (around line 1297-1383)
4. Change the `class` attribute on the `<i>` tag
5. Update the `data-icon` attribute to match (for hover effects)
6. Example:
   ```html
   <!-- Change from fa-music to fa-headphones -->
   <i class="fas fa-headphones" aria-hidden="true"></i>
   ```
   And update:
   ```html
   data-icon="headphones"
   ```

## Popular Icon Categories

### Media & Entertainment
- `fa-play`, `fa-pause`, `fa-stop`, `fa-forward`, `fa-backward`
- `fa-volume-up`, `fa-volume-down`, `fa-volume-mute`
- `fa-expand`, `fa-compress`, `fa-expand-arrows-alt`

### Social & Communication
- `fa-comments`, `fa-comment-dots`, `fa-share`
- `fa-heart`, `fa-thumbs-up`, `fa-thumbs-down`
- `fa-envelope`, `fa-paper-plane`

### Navigation & Actions
- `fa-arrow-left`, `fa-arrow-right`, `fa-arrow-up`, `fa-arrow-down`
- `fa-chevron-left`, `fa-chevron-right`
- `fa-home`, `fa-search`, `fa-filter`

### Status & Feedback
- `fa-check`, `fa-check-circle`, `fa-times`, `fa-exclamation`
- `fa-spinner`, `fa-sync`, `fa-sync-alt`
- `fa-info-circle`, `fa-question-circle`

## Resources

- [Font Awesome Icons Browser](https://fontawesome.com/icons)
- [Font Awesome 6.0.0 Documentation](https://fontawesome.com/docs)
- Current version in use: Font Awesome 6.0.0 (from CDN)
