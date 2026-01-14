/**
 * Advanced Loading Progress Tracker
 * Tracks actual resource loading and provides smooth 0-100% progress
 */

(function() {
    'use strict';
    
    const loader = document.getElementById('app-loader');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const progressPercent = document.getElementById('progress-percent');
    
    // Create status details element if it doesn't exist
    let statusDetails = document.getElementById('status-details');
    if (!statusDetails) {
        statusDetails = document.createElement('div');
        statusDetails.id = 'status-details';
        statusDetails.className = 'status-details';
        progressText.parentElement.appendChild(statusDetails);
    }
    
    if (!loader) return;
    
    let progress = 0;
    let targetProgress = 0;
    let animationFrame = null;
    
    // Progress milestones
    const milestones = {
        DOM_READY: 10,
        CSS_LOADED: 20,
        JS_LOADED: 40,
        API_CALLS: 60,
        IMAGES_LOADED: 80,
        COMPLETE: 100
    };
    
    // Track loaded resources
    const resourceTracker = {
        cssFiles: 0,
        jsFiles: 0,
        apiCalls: 0,
        images: 0,
        totalCss: 0,
        totalJs: 0,
        totalApi: 0,
        totalImages: 0
    };
    
    // Smooth progress animation
    function animateProgress() {
        if (progress < targetProgress) {
            progress += Math.max(0.5, (targetProgress - progress) * 0.1);
            updateProgress(progress);
            animationFrame = requestAnimationFrame(animateProgress);
        } else {
            progress = targetProgress;
            updateProgress(progress);
        }
    }
    
    function setProgress(value, text, details, icon) {
        targetProgress = Math.min(100, Math.max(0, value));
        if (text) {
            // Update text with icon
            if (icon) {
                progressText.innerHTML = `<span class="status-icon">${icon}</span><span>${text}</span>`;
            } else {
                progressText.innerHTML = `<span class="status-icon">⏳</span><span>${text}</span>`;
            }
        }
        if (details && statusDetails) {
            statusDetails.textContent = details;
        }
        if (!animationFrame) {
            animationFrame = requestAnimationFrame(animateProgress);
        }
    }
    
    function updateProgress(value) {
        const rounded = Math.round(value);
        progressBar.style.width = rounded + '%';
        progressPercent.textContent = rounded + '%';
    }
    
    // Track CSS loading
    function trackCSS() {
        const stylesheets = document.querySelectorAll('link[rel="stylesheet"]');
        resourceTracker.totalCss = stylesheets.length;
        
        stylesheets.forEach((link, index) => {
            if (link.sheet) {
                resourceTracker.cssFiles++;
            } else {
                link.addEventListener('load', () => {
                    resourceTracker.cssFiles++;
                    updateResourceProgress();
                });
                link.addEventListener('error', () => {
                    resourceTracker.cssFiles++;
                    updateResourceProgress();
                });
            }
        });
        
        // Fallback: assume CSS loaded after short delay
        setTimeout(() => {
            if (resourceTracker.cssFiles < resourceTracker.totalCss) {
                resourceTracker.cssFiles = resourceTracker.totalCss;
                updateResourceProgress();
            }
        }, 500);
    }
    
    // Track JavaScript loading
    function trackJS() {
        const scripts = document.querySelectorAll('script[src]');
        resourceTracker.totalJs = scripts.length;
        
        scripts.forEach((script) => {
            if (script.readyState === 'complete' || script.readyState === 'loaded') {
                resourceTracker.jsFiles++;
            } else {
                script.addEventListener('load', () => {
                    resourceTracker.jsFiles++;
                    updateResourceProgress();
                });
                script.addEventListener('error', () => {
                    resourceTracker.jsFiles++;
                    updateResourceProgress();
                });
            }
        });
        
        // Fallback: assume JS loaded after delay
        setTimeout(() => {
            if (resourceTracker.jsFiles < resourceTracker.totalJs) {
                resourceTracker.jsFiles = resourceTracker.totalJs;
                updateResourceProgress();
            }
        }, 1000);
    }
    
    // Track API calls (intercept fetch)
    const originalFetch = window.fetch;
    let apiCallCount = 0;
    const trackedApiCalls = new Set();
    
    window.fetch = function(...args) {
        const url = args[0];
        if (typeof url === 'string' && url.startsWith('/api/')) {
            if (!trackedApiCalls.has(url)) {
                trackedApiCalls.add(url);
                apiCallCount++;
                resourceTracker.totalApi = Math.max(resourceTracker.totalApi, apiCallCount);
                
                const promise = originalFetch.apply(this, args);
                promise.finally(() => {
                    resourceTracker.apiCalls++;
                    updateResourceProgress();
                });
                return promise;
            }
        }
        return originalFetch.apply(this, args);
    };
    
    // Track images
    function trackImages() {
        const images = document.querySelectorAll('img');
        resourceTracker.totalImages = images.length;
        
        if (resourceTracker.totalImages === 0) {
            resourceTracker.images = 0;
            updateResourceProgress();
            return;
        }
        
        images.forEach((img) => {
            if (img.complete && img.naturalHeight !== 0) {
                resourceTracker.images++;
            } else {
                img.addEventListener('load', () => {
                    resourceTracker.images++;
                    updateResourceProgress();
                });
                img.addEventListener('error', () => {
                    resourceTracker.images++;
                    updateResourceProgress();
                });
            }
        });
        
        // Fallback: don't wait forever for images
        setTimeout(() => {
            updateResourceProgress();
        }, 2000);
    }
    
    // Update progress based on resource loading
    function updateResourceProgress() {
        const cssProgress = resourceTracker.totalCss > 0 
            ? (resourceTracker.cssFiles / resourceTracker.totalCss) * 10 
            : 10;
        
        const jsProgress = resourceTracker.totalJs > 0 
            ? (resourceTracker.jsFiles / resourceTracker.totalJs) * 20 
            : 20;
        
        const apiProgress = resourceTracker.totalApi > 0 
            ? (resourceTracker.apiCalls / resourceTracker.totalApi) * 20 
            : 20;
        
        const imageProgress = resourceTracker.totalImages > 0 
            ? (resourceTracker.images / resourceTracker.totalImages) * 20 
            : 20;
        
        const total = milestones.DOM_READY + cssProgress + jsProgress + apiProgress + imageProgress;
        const status = getProgressText();
        setProgress(total, status.text, status.details, status.icon);
    }
    
    function getProgressText() {
        if (progress < milestones.DOM_READY) {
            return {
                text: 'Initializing...',
                icon: '⚙️',
                details: 'Setting up application...'
            };
        }
        if (progress < milestones.CSS_LOADED) {
            const cssProgress = resourceTracker.totalCss > 0 
                ? Math.round((resourceTracker.cssFiles / resourceTracker.totalCss) * 100)
                : 0;
            return {
                text: 'Loading styles...',
                icon: '🎨',
                details: `${resourceTracker.cssFiles}/${resourceTracker.totalCss} stylesheets loaded`
            };
        }
        if (progress < milestones.JS_LOADED) {
            const jsProgress = resourceTracker.totalJs > 0 
                ? Math.round((resourceTracker.jsFiles / resourceTracker.totalJs) * 100)
                : 0;
            return {
                text: 'Loading scripts...',
                icon: '📜',
                details: `${resourceTracker.jsFiles}/${resourceTracker.totalJs} scripts loaded`
            };
        }
        if (progress < milestones.API_CALLS) {
            return {
                text: 'Fetching data...',
                icon: '📡',
                details: `${resourceTracker.apiCalls} API call${resourceTracker.apiCalls !== 1 ? 's' : ''} completed`
            };
        }
        if (progress < milestones.IMAGES_LOADED) {
            const imgProgress = resourceTracker.totalImages > 0 
                ? Math.round((resourceTracker.images / resourceTracker.totalImages) * 100)
                : 0;
            return {
                text: 'Loading images...',
                icon: '🖼️',
                details: `${resourceTracker.images}/${resourceTracker.totalImages} images loaded`
            };
        }
        return {
            text: 'Almost ready...',
            icon: '✨',
            details: 'Finalizing...'
        };
    }
    
    // Start tracking
    function init() {
        setProgress(0, 'Initializing...', 'Preparing your experience...', '⚙️');
        
        // DOM ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                setProgress(milestones.DOM_READY, 'DOM ready...', 'Document structure loaded', '✅');
                trackCSS();
                trackJS();
            });
        } else {
            setProgress(milestones.DOM_READY, 'DOM ready...', 'Document structure loaded', '✅');
            trackCSS();
            trackJS();
        }
        
        // Track images after a short delay
        setTimeout(trackImages, 100);
        
        // Window load
        window.addEventListener('load', () => {
            setProgress(95, 'Finalizing...', 'Almost there!', '✨');
            setTimeout(() => {
                setProgress(100, 'Ready!', 'Welcome to Ahoy!', '🎉');
                setTimeout(hideLoader, 300);
            }, 200);
        });
        
        // Safety net: hide loader after max time
        setTimeout(() => {
            if (progress < 100) {
                setProgress(100, 'Ready!', 'Welcome to Ahoy!', '🎉');
                setTimeout(hideLoader, 300);
            }
        }, 8000); // Max 8 seconds
    }
    
    function hideLoader() {
        if (loader) {
            loader.classList.add('hidden');
            setTimeout(() => {
                loader.style.display = 'none';
                // Dispatch event for other scripts
                document.dispatchEvent(new CustomEvent('loader:hidden'));
            }, 500);
        }
    }
    
    // Initialize when script loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Expose API for manual progress updates
    window.loaderProgress = {
        set: setProgress,
        hide: hideLoader
    };
})();
