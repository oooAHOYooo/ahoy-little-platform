/**
 * Color Extractor - Extracts dominant colors from album artwork
 * Uses canvas-based color sampling with k-means clustering
 */

class ColorExtractor {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.initializeCanvas();
    }

    initializeCanvas() {
        this.canvas = document.createElement('canvas');
        this.canvas.width = 200;
        this.canvas.height = 200;
        this.ctx = this.canvas.getContext('2d', { willReadFrequently: true });
    }

    /**
     * Extract dominant colors from an image URL
     * @param {string} imageUrl - URL of the image
     * @returns {Promise<{dominant: string, secondary: string, accent: string}>}
     */
    async extractColors(imageUrl) {
        return new Promise((resolve, reject) => {
            if (!imageUrl) {
                resolve(this.getFallbackColors());
                return;
            }

            const img = new Image();
            img.crossOrigin = 'anonymous';

            img.onload = () => {
                try {
                    // Draw image to canvas
                    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                    this.ctx.drawImage(img, 0, 0, this.canvas.width, this.canvas.height);

                    // Get image data
                    const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
                    const pixels = imageData.data;

                    // Sample colors (every 10th pixel for performance)
                    const colorSamples = [];
                    for (let i = 0; i < pixels.length; i += 40) { // RGBA = 4 values
                        const r = pixels[i];
                        const g = pixels[i + 1];
                        const b = pixels[i + 2];
                        const a = pixels[i + 3];

                        // Skip transparent pixels
                        if (a < 128) continue;

                        // Skip very dark or very light pixels (likely noise)
                        const brightness = (r + g + b) / 3;
                        if (brightness < 20 || brightness > 235) continue;

                        colorSamples.push({ r, g, b });
                    }

                    if (colorSamples.length === 0) {
                        resolve(this.getFallbackColors());
                        return;
                    }

                    // Extract dominant colors using k-means clustering
                    const colors = this.kMeansClustering(colorSamples, 3);
                    
                    // Sort by frequency/brightness
                    colors.sort((a, b) => {
                        const brightnessA = (a.r + a.g + a.b) / 3;
                        const brightnessB = (b.r + b.g + b.b) / 3;
                        return brightnessB - brightnessA;
                    });

                    const dominant = this.rgbToHex(colors[0]);
                    const secondary = colors[1] ? this.rgbToHex(colors[1]) : dominant;
                    const accent = colors[2] ? this.rgbToHex(colors[2]) : secondary;

                    resolve({ dominant, secondary, accent });
                } catch (error) {
                    console.error('Error extracting colors:', error);
                    resolve(this.getFallbackColors());
                }
            };

            img.onerror = () => {
                console.warn('Failed to load image for color extraction:', imageUrl);
                resolve(this.getFallbackColors());
            };

            img.src = imageUrl;
        });
    }

    /**
     * Simple k-means clustering to find dominant colors
     * @param {Array} samples - Array of {r, g, b} objects
     * @param {number} k - Number of clusters
     * @returns {Array} Array of {r, g, b} cluster centers
     */
    kMeansClustering(samples, k = 3) {
        if (samples.length === 0) return [];

        // Initialize centroids randomly
        const centroids = [];
        for (let i = 0; i < k; i++) {
            const randomSample = samples[Math.floor(Math.random() * samples.length)];
            centroids.push({ r: randomSample.r, g: randomSample.g, b: randomSample.b });
        }

        // Iterate (simplified - just a few iterations for performance)
        for (let iter = 0; iter < 5; iter++) {
            const clusters = Array(k).fill(null).map(() => []);
            
            // Assign samples to nearest centroid
            samples.forEach(sample => {
                let minDist = Infinity;
                let nearestCluster = 0;
                
                centroids.forEach((centroid, idx) => {
                    const dist = this.colorDistance(sample, centroid);
                    if (dist < minDist) {
                        minDist = dist;
                        nearestCluster = idx;
                    }
                });
                
                clusters[nearestCluster].push(sample);
            });

            // Update centroids
            centroids.forEach((centroid, idx) => {
                const cluster = clusters[idx];
                if (cluster.length > 0) {
                    const avgR = Math.round(cluster.reduce((sum, s) => sum + s.r, 0) / cluster.length);
                    const avgG = Math.round(cluster.reduce((sum, s) => sum + s.g, 0) / cluster.length);
                    const avgB = Math.round(cluster.reduce((sum, s) => sum + s.b, 0) / cluster.length);
                    centroids[idx] = { r: avgR, g: avgG, b: avgB };
                }
            });
        }

        return centroids;
    }

    /**
     * Calculate color distance (Euclidean distance in RGB space)
     */
    colorDistance(c1, c2) {
        const dr = c1.r - c2.r;
        const dg = c1.g - c2.g;
        const db = c1.b - c2.b;
        return Math.sqrt(dr * dr + dg * dg + db * db);
    }

    /**
     * Convert RGB to hex
     */
    rgbToHex({ r, g, b }) {
        return `#${[r, g, b].map(x => {
            const hex = x.toString(16);
            return hex.length === 1 ? '0' + hex : hex;
        }).join('')}`;
    }

    /**
     * Get fallback colors (Ahoy brand colors)
     */
    getFallbackColors() {
        return {
            dominant: '#6366f1', // Indigo
            secondary: '#8b5cf6', // Purple
            accent: '#ec4899' // Pink
        };
    }

    /**
     * Convert hex to RGB
     */
    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }

    /**
     * Interpolate between two colors
     */
    interpolateColor(color1, color2, factor) {
        const rgb1 = this.hexToRgb(color1);
        const rgb2 = this.hexToRgb(color2);
        
        if (!rgb1 || !rgb2) return color1;
        
        const r = Math.round(rgb1.r + (rgb2.r - rgb1.r) * factor);
        const g = Math.round(rgb1.g + (rgb2.g - rgb1.g) * factor);
        const b = Math.round(rgb1.b + (rgb2.b - rgb1.b) * factor);
        
        return this.rgbToHex({ r, g, b });
    }
}

// Export singleton instance
window.colorExtractor = new ColorExtractor();

