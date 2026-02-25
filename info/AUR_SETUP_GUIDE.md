# AUR Setup Guide: Making Ahoy Installable via `yay -S ahoy`

This guide explains how to set up an AUR (Arch User Repository) package so Garuda/Arch users can install with:

```bash
yay -S ahoy-indie-media
```

---

## What is AUR?

AUR is Arch's community-maintained package repository. Users can install packages using `yay` or `pacman`.

---

## Setup Steps

### 1. Create AUR Git Repository

You'll need a **separate git repository** for AUR (it's a different repo than the main project):

```bash
# Create new repo at https://aur.archlinux.org (requires AUR account)
# Or use a temporary setup at: https://github.com/yourusername/ahoy-indie-media-aur
```

### 2. Clone the PKGBUILD

The `PKGBUILD` file in `packaging/PKGBUILD` is ready to use:

```bash
# In the AUR repo, copy/commit the PKGBUILD file
cp packaging/PKGBUILD .
git add PKGBUILD
git commit -m "initial: add ahoy-indie-media PKGBUILD"
git push
```

### 3. Submit to Official AUR (Long-term)

For the official AUR repository:

1. **Create AUR account** at https://aur.archlinux.org/register/
2. **Configure SSH keys** for AUR
3. **Submit package** following [AUR submission guide](https://wiki.archlinux.org/title/AUR_submission_guidelines)

Steps:
```bash
# Clone empty AUR repo
git clone ssh+git://aur@aur.archlinux.org/ahoy-indie-media.git

# Add your PKGBUILD and .SRCINFO
cd ahoy-indie-media
cp /path/to/packaging/PKGBUILD .

# Generate .SRCINFO (required for AUR)
makepkg --printsrcinfo > .SRCINFO

# Commit and push
git add PKGBUILD .SRCINFO
git commit -m "initial: add ahoy-indie-media package"
git push
```

### 4. Temporary AUR (Quick Testing)

For testing before official AUR submission:

```bash
# Create repo on GitHub
gh repo create ahoy-indie-media-aur --public

# Push PKGBUILD
git clone https://github.com/yourusername/ahoy-indie-media-aur.git
cd ahoy-indie-media-aur
cp packaging/PKGBUILD .
makepkg --printsrcinfo > .SRCINFO
git add .
git commit -m "Add PKGBUILD"
git push
```

Then users can install with:
```bash
yay -S ahoy-indie-media-aur
# or
git clone https://github.com/yourusername/ahoy-indie-media-aur
cd ahoy-indie-media-aur
makepkg -si
```

---

## How PKGBUILD Works

The `PKGBUILD` file tells Arch's build system:

1. **Where to get the code** — GitHub repository
2. **How to build it** — Run npm and electron-builder
3. **What to install** — AppImage to `/opt/ahoy-indie-media`
4. **Create shortcuts** — Symlink in `/usr/bin` and desktop entry

When user runs `yay -S ahoy-indie-media`:
1. AUR downloads the PKGBUILD
2. Clones the GitHub repo at the specified tag (v0.2.1)
3. Runs `makepkg` to build locally
4. Installs the built package

---

## Maintenance

When you release a new version:

1. **Tag the release** in GitHub:
   ```bash
   git tag v0.2.2
   git push --tags
   ```

2. **Update PKGBUILD** version:
   ```bash
   # In packaging/PKGBUILD
   pkgver=0.2.2
   ```

3. **Update .SRCINFO** (AUR only):
   ```bash
   makepkg --printsrcinfo > .SRCINFO
   ```

4. **Commit and push** to AUR repo

---

## Test Before Submitting

Test the PKGBUILD locally:

```bash
# Build locally
cd /tmp
git clone https://github.com/yourusername/ahoy-indie-media-aur.git
cd ahoy-indie-media-aur
makepkg -si

# Test the installed app
ahoy-indie-media
```

---

## After Official AUR Submission

Once approved by AUR maintainers:
- Users can install with: `yay -S ahoy-indie-media`
- Automatically updated when new versions are tagged
- Available in all AUR clients (yay, paru, etc.)

---

## Current Status

✅ PKGBUILD ready in `packaging/PKGBUILD`
⏳ Needs AUR account setup
⏳ Needs official AUR submission

---

## Further Reading

- [AUR official documentation](https://wiki.archlinux.org/title/Arch_User_Repository)
- [PKGBUILD reference](https://wiki.archlinux.org/title/PKGBUILD)
- [AUR submission guidelines](https://wiki.archlinux.org/title/AUR_submission_guidelines)
- [makepkg documentation](https://man.archlinux.org/man/makepkg.8)
