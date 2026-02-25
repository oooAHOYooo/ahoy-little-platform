#!/bin/bash
# Post-installation script for Ahoy Indie Media DEB package

# Update application menu
which update-desktop-database > /dev/null 2>&1 && update-desktop-database /usr/share/applications

# Update icon cache if available
if [ -d /usr/share/icons/hicolor ]; then
    which gtk-update-icon-cache > /dev/null 2>&1 && gtk-update-icon-cache -f -t /usr/share/icons/hicolor
fi

echo "✓ Ahoy Indie Media installed successfully!"
echo ""
echo "Launch the app from your application menu or run: ahoy-indie-media"
