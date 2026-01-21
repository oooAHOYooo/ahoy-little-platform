# Plan: Monthly "What's New" with 6 Consistent Sections

## Overview
Restructure "What's New at Ahoy" as monthly update pages with 6 consistent sections that are updated month to month. Each section can contain either content updates or technical/platform improvements.

---

## URL Structure

**Format**: `/whats-new/<year>/<month>/<section>`

**Examples**:
- `/whats-new/2026/jan` - January 2026 overview (all 6 sections)
- `/whats-new/2026/jan/music` - January 2026 Music section
- `/whats-new/2026/jan/videos` - January 2026 Videos section
- `/whats-new/2026/jan/artists` - January 2026 Artists section
- `/whats-new/2026/jan/platform` - January 2026 Platform/Technical section
- `/whats-new/2026/jan/merch` - January 2026 Merch section
- `/whats-new/2026/jan/events` - January 2026 Events section

**Month Format**: 3-letter abbreviation (jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec)

---

## 6 Consistent Sections

Based on your navigation, here are the 6 sections:

1. **Music** - Music content & music-related features
2. **Videos** - Video content & video-related features
3. **Artists** - Artist content & artist-related features
4. **Platform** - Technical updates, mobile app, general platform improvements
5. **Merch** - Merchandise updates, new products, merch features
6. **Events** - Live events, performances, shows, event announcements

---

## Data Structure

### Monthly Updates JSON

**File**: `static/data/whats_new.json` (restructured)

```json
{
  "updates": {
    "2026": {
      "jan": {
        "music": {
          "title": "Music Updates",
          "items": [
            {
              "type": "content",
              "title": "New Album Release",
              "description": "Artist X released their new album...",
              "link": "/music/album-slug"
            },
            {
              "type": "feature",
              "title": "Playlist Sharing",
              "description": "You can now share playlists with friends...",
              "link": "/music"
            }
          ]
        },
        "videos": {
          "title": "Video Updates",
          "items": [
            {
              "type": "content",
              "title": "New Show Episode",
              "description": "Episode 5 of Show Y is now available...",
              "link": "/shows/show-slug"
            }
          ]
        },
        "artists": {
          "title": "Artist Updates",
          "items": [
            {
              "type": "content",
              "title": "New Artist Spotlight",
              "description": "Check out featured artist...",
              "link": "/artists/artist-slug"
            }
          ]
        },
        "platform": {
          "title": "Platform Updates",
          "items": [
            {
              "type": "technical",
              "title": "Mobile App Improvements",
              "description": "Enhanced mobile experience with better navigation...",
              "features": [
                "Faster loading times",
                "Improved navigation",
                "Better offline support"
              ],
              "link": "/downloads"
            },
            {
              "type": "feature",
              "title": "New Radio Station",
              "description": "We've launched a brand new radio station...",
              "features": [
                "24/7 streaming",
                "Global indie artists",
                "Live DJ sets"
              ],
              "link": "/radio"
            }
          ]
        },
        "merch": {
          "title": "Merch Updates",
          "items": [
            {
              "type": "content",
              "title": "New T-Shirt Collection",
              "description": "Check out our new artist-designed t-shirts...",
              "link": "/merch"
            },
            {
              "type": "feature",
              "title": "Merch Store Improvements",
              "description": "Enhanced shopping experience with better filters...",
              "link": "/merch"
            }
          ]
        },
        "events": {
          "title": "Events Updates",
          "items": [
            {
              "type": "content",
              "title": "Poet and Friends Show #7",
              "description": "Join us for another Poet and Friends show on January 29th...",
              "date": "2026-01-29",
              "link": "/events"
            },
            {
              "type": "content",
              "title": "Live Performance at Koffee",
              "description": "Live music event featuring local artists...",
              "date": "2026-01-20",
              "link": "/performances"
            }
          ]
        }
      },
      "feb": {
        // February updates...
      }
    }
  }
}
```

**Alternative Simpler Structure**:
```json
{
  "updates": [
    {
      "year": "2026",
      "month": "jan",
      "section": "platform",
      "type": "technical",
      "title": "Mobile App Improvements",
      "description": "Enhanced mobile experience...",
      "features": ["Faster loading", "Better navigation"],
      "link": "/downloads",
      "date": "2026-01-15"
    },
    {
      "year": "2026",
      "month": "jan",
      "section": "music",
      "type": "content",
      "title": "New Album Release",
      "description": "Artist X released...",
      "link": "/music/album-slug",
      "date": "2026-01-10"
    }
  ]
}
```

---

## Page Structure

### Monthly Overview Page (`/whats-new/2026/jan`)

**Layout**:
```
┌─────────────────────────────────────┐
│  What's New - January 2026         │
├─────────────────────────────────────┤
│  [Music] [Videos] [Artists] [Platform] [Merch] [Events] │ ← Section tabs/nav
├─────────────────────────────────────┤
│                                     │
│  🎵 Music Updates                   │
│  ────────────────────────────────  │
│  • New Album Release                │
│  • Playlist Sharing Feature         │
│                                     │
│  📹 Video Updates                   │
│  ────────────────────────────────  │
│  • New Show Episode                 │
│                                     │
│  👥 Artist Updates                  │
│  ────────────────────────────────  │
│  • New Artist Spotlight             │
│                                     │
│  ⚙️ Platform Updates                │
│  ────────────────────────────────  │
│  • Mobile App Improvements          │
│  • New Radio Station                │
│                                     │
│  🛍️ Merch Updates                   │
│  ────────────────────────────────  │
│  • New T-Shirt Collection           │
│  • Store Improvements               │
│                                     │
│  📅 Events Updates                  │
│  ────────────────────────────────  │
│  • Poet and Friends Show #7         │
│  • Live Performance at Koffee       │
│                                     │
└─────────────────────────────────────┘
```

### Section Detail Page (`/whats-new/2026/jan/platform`)

**Layout**:
```
┌─────────────────────────────────────┐
│  ← Back to January 2026             │
│                                     │
│  Platform Updates - January 2026   │
├─────────────────────────────────────┤
│                                     │
│  Mobile App Improvements            │
│  ────────────────────────────────  │
│  Enhanced mobile experience with    │
│  better navigation and faster       │
│  loading times.                     │
│                                     │
│  Features:                          │
│  • Faster loading times             │
│  • Improved navigation               │
│  • Better offline support           │
│                                     │
│  [Learn More →]                     │
│                                     │
│  ────────────────────────────────  │
│                                     │
│  New Radio Station                  │
│  ────────────────────────────────  │
│  We've launched a brand new radio  │
│  station featuring indie artists... │
│                                     │
│  Features:                          │
│  • 24/7 streaming                  │
│  • Global indie artists             │
│  • Live DJ sets                     │
│                                     │
│  [Listen Now →]                    │
│                                     │
└─────────────────────────────────────┘
```

---

## Routing

### Routes in `app.py`

```python
@app.route('/whats-new')
def whats_new_index():
    """Redirect to current month or show archive"""
    # Redirect to current month or show list of months
    pass

@app.route('/whats-new/<year>/<month>')
def whats_new_month(year, month):
    """Monthly overview page with all 6 sections"""
    # Load updates for that month
    # Show all 6 sections
    # Render template
    pass

@app.route('/whats-new/<year>/<month>/<section>')
def whats_new_section(year, month, section):
    """Individual section detail page"""
    # Load updates for that month/section
    # Show detailed content
    # Render template
    pass
```

**Section Validation**:
- Valid sections: `music`, `videos`, `artists`, `platform`, `merch`, `events`
- Invalid sections return 404

---

## Home Page Integration

**Current**: Shows 4 recent updates from all sections

**New Approach Options**:

### Option A: Show Current Month Preview
- Show 1-2 items from each of the 6 sections from current month
- "View All January Updates" link → `/whats-new/2026/jan`

### Option B: Show Latest from Each Section
- Show 1 latest item from each of the 6 sections (could be from different months)
- "View All Updates" link → `/whats-new` (archive)

### Option C: Keep Current + Add Monthly Link
- Keep current "What's New" widget (4 recent items)
- Add "View January Updates" link to current month

**Recommendation**: **Option A** - Shows current month's highlights, links to full monthly page

---

## Implementation Steps

1. **Restructure JSON Data**
   - Convert from flat list to monthly/section structure
   - Add section categorization
   - Add month/year organization

2. **Create Monthly Overview Template**
   - `templates/whats_new_month.html`
   - Shows all 6 sections
   - Section navigation/tabs
   - Links to section detail pages

3. **Create Section Detail Template**
   - `templates/whats_new_section.html`
   - Shows detailed content for one section
   - Expandable feature lists
   - CTA buttons

4. **Add Backend Routes**
   - `/whats-new/<year>/<month>` - Monthly overview
   - `/whats-new/<year>/<month>/<section>` - Section detail
   - Handle month abbreviations (jan, feb, etc.)
   - Validate sections

5. **Update Home Page**
   - Show current month preview
   - Link to monthly page
   - Update "What's New" widget

6. **Add Navigation**
   - Month selector (previous/next month)
   - Section tabs on monthly page
   - Breadcrumbs

---

## Section Categories

### Section: `music`
- New tracks/albums (content)
- Music features (feature)
- Playlist updates (feature)
- Music player improvements (technical)

### Section: `videos`
- New shows/episodes (content)
- Video features (feature)
- Video player improvements (technical)
- Live TV updates (feature)

### Section: `artists`
- New artist additions (content)
- Artist spotlight (content)
- Artist features (feature)
- Artist profile improvements (technical)

### Section: `platform`
- Mobile app updates (technical)
- Desktop app updates (technical)
- Radio station launches (feature)
- General platform improvements (technical)
- New features (feature)
- Performance improvements (technical)

### Section: `merch`
- New product releases (content)
- Merch store features (feature)
- Product categories (content)
- Shopping improvements (technical)
- Artist collaborations (content)

### Section: `events`
- Live performance announcements (content)
- Event listings (content)
- Show schedules (content)
- Ticket links (feature)
- Venue information (content)
- Event features (feature)

---

## Benefits of This Structure

✅ **Consistent Organization**: Same 6 sections every month
✅ **Easy Navigation**: Clear URL structure (`/2026/jan/platform`)
✅ **Scalable**: Easy to add new months
✅ **Flexible**: Sections can have content OR technical updates
✅ **SEO-Friendly**: Descriptive URLs
✅ **User-Friendly**: Easy to find what's new in specific areas

---

## Questions to Confirm

1. **Which 6 sections?** ✅ **CONFIRMED**
   - Music, Videos, Artists, Platform, Merch, Events

2. **Home Page Behavior?**
   - Show current month preview?
   - Or keep current "4 recent items" approach?

3. **Archive Page?**
   - List all months?
   - Or just link from home to current month?

4. **Section Names in URLs?**
   - Use `platform` or `mobile-app` or `technical`?
   - Use `videos` or `shows`?

---

## Next Steps

Once you confirm:
1. ✅ The 6 section names (Music, Videos, Artists, Platform, Merch, Events)
2. Home page behavior preference
3. Any adjustments to the structure

I'll implement:
1. Restructured JSON data
2. Monthly overview template
3. Section detail template
4. Backend routes
5. Home page integration
