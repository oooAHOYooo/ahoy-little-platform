# Plan: "What's New at Ahoy" Detail Pages

## Overview
Transform the "What's New at Ahoy" section from a simple list into an interactive system where each update item is clickable and opens a dedicated detail page with expanded content, features, and more information.

---

## Current State Analysis

### Current Implementation
- **Data Source**: `static/data/whats_new.json` - Simple JSON with basic fields (id, title, description, date, type)
- **Display**: Home page (`templates/home.html`) shows a list of 4 updates
- **API**: `/api/whats-new` endpoint serves the JSON data
- **Frontend**: Alpine.js component `whatsNew()` loads and displays updates
- **Styling**: Items have hover effects but are not clickable

### Current Data Structure
```json
{
  "id": "update-2",
  "title": "New Radio Station Launch",
  "description": "We've launched a brand new radio station...",
  "date": "2026-01-15",
  "type": "feature"
}
```

---

## Proposed Solution

### 1. Data Structure Enhancement

**Expand `whats_new.json` to include detail page content:**

```json
{
  "updates": [
    {
      "id": "update-2",
      "title": "New Radio Station Launch",
      "description": "We've launched a brand new radio station featuring indie artists from around the world. Tune in 24/7!",
      "date": "2026-01-15",
      "type": "feature",
      "slug": "new-radio-station-launch",
      "full_content": {
        "hero_image": "/static/img/whats-new/radio-station-hero.jpg",
        "intro": "We're thrilled to announce the launch of our brand new 24/7 radio station, bringing you the best in independent music from artists around the globe.",
        "sections": [
          {
            "heading": "24/7 Streaming",
            "content": "Our radio station streams continuously, featuring curated playlists and live DJ sets.",
            "features": [
              "Continuous streaming without interruption",
              "Curated playlists updated daily",
              "Live DJ sets on weekends"
            ]
          },
          {
            "heading": "Global Indie Artists",
            "content": "Discover music from independent artists worldwide, handpicked by our team.",
            "features": [
              "Artists from 50+ countries",
              "New music added weekly",
              "Genre diversity across all styles"
            ]
          }
        ],
        "cta": {
          "text": "Listen Now",
          "link": "/radio"
        }
      }
    }
  ]
}
```

**Alternative Simpler Structure (if full_content is too complex):**
```json
{
  "id": "update-2",
  "title": "New Radio Station Launch",
  "description": "Short description...",
  "date": "2026-01-15",
  "type": "feature",
  "slug": "new-radio-station-launch",
  "detail_content": "Full expanded content with HTML support...",
  "features": [
    "24/7 streaming",
    "Global indie artists",
    "Live DJ sets"
  ],
  "hero_image": "/static/img/whats-new/radio-hero.jpg",
  "cta_link": "/radio"
}
```

---

### 2. URL Structure & Routing

**Route Patterns**:
- `/whats-new` - Archive page (all updates, with filters/pagination)
- `/whats-new/<slug>` - Individual update detail page

**Detail Page Examples** (using simplest slug format):
- `/whats-new/new-radio-station-launch`
- `/whats-new/live-tv-channels-expanded`
- `/whats-new/mobile-app-improvements`
- `/whats-new/poet-and-friends-show-7`

**Implementation**:
- Add route in `app.py`: 
  - `@app.route('/whats-new')` - Archive/list page
  - `@app.route('/whats-new/<slug>')` - Detail page
- Detail route will:
  1. Load `whats_new.json`
  2. Find update by slug
  3. Return 404 if not found
  4. Render `templates/whats_new_detail.html` with update data
- Archive route will:
  1. Load all updates from `whats_new.json`
  2. Support pagination (optional)
  3. Support filtering by type (optional)
  4. Render `templates/whats_new_archive.html` (or reuse home template)

---

### 3. Template Structure

**New Template**: `templates/whats_new_detail.html`

**Layout Structure**:
```
- Hero Section (with optional hero image)
  - Title
  - Date & Type badge
  - Short intro/description
  
- Main Content Area
  - Expanded content sections
  - Feature lists (if applicable)
  - Images/media (if applicable)
  
- Call-to-Action (if applicable)
  - Link to related page/feature
  
- Navigation
  - Back to home link
  - "View All Updates" link
```

**Design Considerations**:
- Match existing Ahoy design language (dark theme, glassmorphism)
- Responsive mobile-first design
- Consistent with `artist_detail.html` style patterns
- Use Alpine.js for interactivity

---

### 4. Home Page Updates

**Make items clickable**:
- Wrap each `.whats-new-item` in a link or add click handler
- Link to `/whats-new/<slug>`
- Add visual indicator (cursor pointer, maybe arrow icon)
- Update hover state to indicate clickability

**Implementation Options**:
1. **Option A**: Wrap in `<a>` tag
   ```html
   <a :href="`/whats-new/${update.slug}`" class="whats-new-item">
   ```

2. **Option B**: Use Alpine.js click handler
   ```html
   <div @click="window.location.href = `/whats-new/${update.slug}`" 
        class="whats-new-item clickable">
   ```

**Recommendation**: Option A (semantic HTML, better for SEO and accessibility)

---

### 5. API Updates

**Current**: `/api/whats-new` - Returns all updates (limited to 4 on frontend)

**New Endpoint**: `/api/whats-new/<slug>`
- Returns single update by slug
- Used for detail page data loading
- Returns 404 if not found

**Keep existing endpoint** for home page list view.

---

### 6. Slug Generation - Human-Readable URLs

**Goal**: Create very human-readable URLs that are self-explanatory and SEO-friendly.

**Slug Options** (with examples):

#### Option A: Title-Only (Simplest) ⭐ **SIMPLEST**
- **Format**: `new-radio-station-launch`
- **Example URLs**:
  - `/whats-new/new-radio-station-launch`
  - `/whats-new/live-tv-channels-expanded`
  - `/whats-new/mobile-app-improvements`
  - `/whats-new/poet-and-friends-show-7`
- **Pros**: 
  - ✅ Shortest and easiest to type
  - ✅ Clean, natural reading
  - ✅ Easy to remember and share
  - ✅ No date clutter
- **Cons**: Potential collisions if similar titles exist (but can handle with numbers: `new-radio-station-launch-2`)
- **Best for**: Most use cases - simple and clean
- **Collision Handling**: If duplicate, append `-2`, `-3`, etc.

#### Option B: Date + Title (Most Descriptive)
- **Format**: `january-2026-new-radio-station-launch`
- **Example URLs**:
  - `/whats-new/january-2026-new-radio-station-launch`
  - `/whats-new/january-2026-live-tv-channels-expanded`
- **Pros**: Very clear when it happened, prevents collisions
- **Cons**: Longer URLs
- **Best for**: When date context is important

#### Option C: Title + Date (Feature First) ⭐ **RECOMMENDED**
- **Format**: `new-radio-station-launch-january-2026`
- **Example URLs**:
  - `/whats-new/new-radio-station-launch-january-2026`
  - `/whats-new/poet-and-friends-show-7-january-2026`
- **Pros**: Feature name first (better for scanning), date provides context, collision-proof
- **Cons**: Slightly longer than title-only
- **Best for**: When you want feature name prominent but date visible

#### Option D: Year-Month + Title (Technical but Clear)
- **Format**: `2026-01-new-radio-station-launch`
- **Example URLs**:
  - `/whats-new/2026-01-new-radio-station-launch`
  - `/whats-new/2026-01-live-tv-channels-expanded`
- **Pros**: Sortable, very clear date, prevents collisions
- **Cons**: Less natural reading (numbers first)
- **Best for**: When chronological organization matters

**Recommended Approach**: **Option A** (`title-only` format) - **SIMPLEST**
- ✅ Shortest possible: "new-radio-station-launch"
- ✅ Easiest to type and remember
- ✅ Clean and natural
- ✅ SEO-friendly (feature name is clear)
- ✅ Collisions handled automatically (add `-2` if needed)

**Alternative if you want date context**: **Option C** (`title-date` format)
- Human-readable: "new-radio-station-launch-january-2026" 
- Collision-proof: Date prevents duplicates
- Better for chronological context

**Slug Generation Function** (Simplest - Title Only):
```python
def generate_whats_new_slug(title, existing_slugs=None):
    """Generate simple slug from title only"""
    import re
    
    # Convert title to slug
    title_slug = title.lower().strip()
    title_slug = re.sub(r'[^\w\s-]', '', title_slug)  # Remove special chars
    title_slug = re.sub(r'[-\s]+', '-', title_slug)   # Replace spaces with hyphens
    title_slug = title_slug.strip('-')                 # Remove leading/trailing hyphens
    
    # Handle collisions if existing_slugs provided
    if existing_slugs:
        base_slug = title_slug
        counter = 1
        while title_slug in existing_slugs:
            title_slug = f"{base_slug}-{counter}"
            counter += 1
    
    return title_slug
```

**Example Generated Slugs** (Simplest):
- "New Radio Station Launch" → `new-radio-station-launch`
- "Poet and Friends Show #7" → `poet-and-friends-show-7`
- "Live TV Channels Expanded" → `live-tv-channels-expanded`
- "Mobile App Improvements" → `mobile-app-improvements`

**Alternative with Date** (if you want date context):
```python
def generate_whats_new_slug(title, date):
    """Generate slug with date for context"""
    from datetime import datetime
    import re
    
    title_slug = title.lower().strip()
    title_slug = re.sub(r'[^\w\s-]', '', title_slug)
    title_slug = re.sub(r'[-\s]+', '-', title_slug)
    title_slug = title_slug.strip('-')
    
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        date_slug = date_obj.strftime('%B-%Y').lower()  # "january-2026"
        return f"{title_slug}-{date_slug}"
    except:
        return title_slug
```

**Implementation**: Store `slug` field explicitly in JSON for full control, but auto-generate if missing.

---

### 7. Content Organization Strategy

**For each update type, organize content differently:**

#### Feature Updates (e.g., "New Radio Station Launch")
- Hero image
- Introduction paragraph
- Feature sections with:
  - Heading
  - Description
  - Bullet list of features
- Call-to-action button/link

#### Event Updates (e.g., "Poet and Friends Show #7")
- Event image
- Date/time details
- Location information
- Description
- Ticket/RSVP link (if applicable)

#### Improvement Updates (e.g., "Mobile App Improvements")
- Before/after comparison (optional)
- List of improvements
- Benefits to users
- How to access new features

#### Content Updates (e.g., "New Artist Spotlight")
- Featured content preview
- Link to full content
- Description

---

### 8. Implementation Steps

1. **Update JSON Structure**
   - Add `slug` field to all existing updates
   - Add `full_content` or `detail_content` fields
   - Add optional `hero_image`, `features`, `cta_link` fields

2. **Create Detail Template**
   - Create `templates/whats_new_detail.html`
   - Design hero section
   - Design content sections
   - Add navigation/back links
   - Style to match Ahoy design

3. **Add Backend Route**
   - Add `/whats-new/<slug>` route in `app.py`
   - Implement slug lookup logic
   - Handle 404 cases
   - Pass data to template

4. **Add API Endpoint** (optional, for client-side loading)
   - Add `/api/whats-new/<slug>` endpoint
   - Return single update JSON

5. **Update Home Page**
   - Make items clickable (wrap in links)
   - Add slug to data structure
   - Update styling for clickable state
   - Test navigation

6. **Content Creation**
   - Write expanded content for each update
   - Add feature lists where applicable
   - Create/add hero images if needed
   - Add CTA links where relevant

7. **Testing**
   - Test all slug variations
   - Test 404 handling
   - Test mobile responsiveness
   - Test navigation flow

---

### 9. File Organization

**New Files**:
- `templates/whats_new_detail.html` - Detail page template
- `templates/whats_new_archive.html` - Archive/list page template (optional, can reuse home template)

**Modified Files**:
- `static/data/whats_new.json` - Enhanced with detail content and slugs
- `templates/home.html` - Make items clickable, add "View All Updates" link
- `app.py` - Add routes (`/whats-new` and `/whats-new/<slug>`) and API endpoints
- `static/js/app.js` (optional) - Add detail page Alpine.js component

**Optional New Files**:
- `static/img/whats-new/` - Directory for update hero images

---

### 10. SEO Considerations

- Add proper meta tags to detail pages
- Use semantic HTML structure
- Include structured data (JSON-LD) for articles/announcements
- Ensure slugs are descriptive and URL-friendly
- Add canonical URLs

---

### 11. Archive Strategy for Old Updates

**Problem**: As new updates are added, older ones need a home. The home page shows only 4 recent updates.

**Solution Options**:

#### Option A: Archive Page (Recommended)
- **Route**: `/whats-new` (list view) or `/whats-new/archive`
- **Functionality**:
  - Shows ALL updates (not just 4)
  - Sorted by date (newest first)
  - Paginated (e.g., 20 per page)
  - Filterable by type (feature, event, improvement, content)
  - Searchable
- **Home Page**: Shows 4 most recent with "View All Updates" link
- **Detail Pages**: Still accessible via `/whats-new/<slug>` regardless of age

#### Option B: Chronological Sections
- **Home Page Structure**:
  - "Latest Updates" (4 most recent)
  - "This Month" (all from current month)
  - "Previous Updates" (collapsible/expandable section)
- **Pros**: Everything visible on one page
- **Cons**: Can get long, less organized

#### Option C: "View All" Modal/Page
- **Home Page**: Shows 4 recent, "View All" button
- **Clicking "View All"**: Opens full-page archive with all updates
- **Archive Page**: Similar to Option A but triggered from home

**Recommended: Option A - Dedicated Archive Page**

**Archive Page Structure**:
```
/whats-new (or /whats-new/archive)
├── Header: "What's New at Ahoy - Archive"
├── Filters: [All] [Features] [Events] [Improvements] [Content]
├── Search: [Search updates...]
└── Update List:
    ├── Update cards (same style as home, but all visible)
    ├── Pagination (20 per page)
    └── Each card links to detail page
```

**Implementation**:
1. Home page shows 4 most recent (current behavior)
2. Add "View All Updates" link → `/whats-new`
3. `/whats-new` route shows all updates with filters/pagination
4. Detail pages (`/whats-new/<slug>`) work for any update, old or new
5. Archive page has breadcrumb: "Home > What's New > [Update Title]"

**Old Updates Behavior**:
- ✅ Still accessible via direct URL (`/whats-new/<slug>`)
- ✅ Appear in archive page
- ✅ Can be searched/filtered
- ✅ Never "deleted" - just moved out of home page spotlight
- ✅ Shareable links remain valid forever

---

### 12. Future Enhancements (Out of Scope for Now)

- Filter by update type on archive page
- Search within updates
- Share buttons for updates
- Related updates section on detail pages
- Comments/discussion (if applicable)
- RSS feed for updates
- Email notifications for new updates

---

## Recommended Approach

**Phase 1: Minimal Viable Implementation**
1. Add `slug` field to existing JSON entries
2. Create simple detail template with basic layout
3. Add route and make home page items clickable
4. Use existing description as detail content initially

**Phase 2: Content Enhancement**
1. Expand JSON with full content sections
2. Add feature lists and structured content
3. Add hero images
4. Enhance template with sections

**Phase 3: Polish**
1. Add CTA buttons
2. Improve styling and animations
3. Add related updates
4. SEO optimization

---

## Questions to Consider

1. **Content Management**: Will updates be edited manually in JSON, or do you want an admin interface later?
2. **Images**: Do you have hero images for updates, or should we use placeholders?
3. **Content Format**: Prefer HTML in JSON, Markdown, or plain text with auto-formatting?
4. **Backward Compatibility**: Should old updates without detail content still work?
5. **Archive**: ✅ **SOLVED** - Archive page at `/whats-new` shows all updates, home shows 4 recent
6. **Slug Format**: ✅ **SOLVED** - Using simplest `title-only` format (e.g., `new-radio-station-launch`) - easy to type and remember!

---

## Next Steps

Once you approve this plan, I'll implement:
1. Enhanced JSON structure with slugs
2. Detail page template
3. Backend routing
4. Clickable home page items
5. Basic content for existing updates

Let me know if you'd like any adjustments to this plan!
