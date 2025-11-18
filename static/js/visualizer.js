/**
 * Three.js Visualizer - Creates animated visualizer that responds to audio
 * Uses frequency data and album art colors for reactive visuals
 */

class Visualizer {
    constructor(container, options = {}) {
        this.container = container;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.bars = [];
        this.particles = null;
        this.animationId = null;
        this.isActive = false;
        this.colors = {
            dominant: '#6366f1',
            secondary: '#8b5cf6',
            accent: '#ec4899'
        };
        
        // Options
        this.type = options.type || 'bars'; // 'bars', 'particles', 'waveform'
        this.maxFPS = options.maxFPS || 45;
        this.frameTime = 1000 / this.maxFPS;
        this.lastFrameTime = 0;
        this.isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        // Performance mode for mobile
        if (this.isMobile) {
            this.maxFPS = 30;
            this.frameTime = 1000 / 30;
        }
    }

    /**
     * Initialize Three.js scene
     */
    init() {
        if (!window.THREE) {
            console.error('Three.js not loaded');
            return false;
        }

        try {
            // Scene
            this.scene = new THREE.Scene();
            this.scene.background = null; // Transparent

            // Camera
            const width = this.container.clientWidth;
            const height = this.container.clientHeight;
            this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
            this.camera.position.z = 5;

            // Renderer
            this.renderer = new THREE.WebGLRenderer({
                antialias: !this.isMobile,
                alpha: true,
                powerPreference: 'high-performance'
            });
            this.renderer.setSize(width, height);
            this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // Cap pixel ratio for performance
            this.renderer.setClearColor(0x000000, 0); // Transparent
            this.container.appendChild(this.renderer.domElement);

            // Create visualizer based on type
            if (this.type === 'bars') {
                this.createBars();
            } else if (this.type === 'particles') {
                this.createParticles();
            } else {
                this.createBars(); // Default
            }

            // Handle resize
            window.addEventListener('resize', () => this.handleResize());

            return true;
        } catch (error) {
            console.error('Error initializing visualizer:', error);
            return false;
        }
    }

    /**
     * Create bar visualizer
     */
    createBars() {
        this.bars = [];
        const barCount = this.isMobile ? 32 : 64;
        const barWidth = 0.1;
        const barSpacing = 0.15;
        const totalWidth = (barCount - 1) * (barWidth + barSpacing);

        for (let i = 0; i < barCount; i++) {
            const geometry = new THREE.BoxGeometry(barWidth, 0.1, 0.1);
            const material = new THREE.MeshBasicMaterial({
                color: this.colors.dominant,
                transparent: true,
                opacity: 0.8
            });

            const bar = new THREE.Mesh(geometry, material);
            bar.position.x = (i - barCount / 2) * (barWidth + barSpacing);
            bar.position.y = -2;
            bar.userData.originalY = -2;
            bar.userData.index = i;

            this.scene.add(bar);
            this.bars.push(bar);
        }
    }

    /**
     * Create particle visualizer
     */
    createParticles() {
        const particleCount = this.isMobile ? 200 : 500;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);

        const color1 = new THREE.Color(this.colors.dominant);
        const color2 = new THREE.Color(this.colors.secondary);

        for (let i = 0; i < particleCount; i++) {
            const i3 = i * 3;
            positions[i3] = (Math.random() - 0.5) * 10;
            positions[i3 + 1] = (Math.random() - 0.5) * 10;
            positions[i3 + 2] = (Math.random() - 0.5) * 10;

            const color = Math.random() > 0.5 ? color1 : color2;
            colors[i3] = color.r;
            colors[i3 + 1] = color.g;
            colors[i3 + 2] = color.b;
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

        const material = new THREE.PointsMaterial({
            size: 0.05,
            vertexColors: true,
            transparent: true,
            opacity: 0.8
        });

        this.particles = new THREE.Points(geometry, material);
        this.scene.add(this.particles);
    }

    /**
     * Update visualizer with frequency data
     * @param {Uint8Array} frequencyData - Frequency data from analyser
     */
    update(frequencyData) {
        if (!frequencyData || !this.isActive) return;

        const now = performance.now();
        if (now - this.lastFrameTime < this.frameTime) {
            return; // Throttle to max FPS
        }
        this.lastFrameTime = now;

        if (this.type === 'bars' && this.bars.length > 0) {
            this.updateBars(frequencyData);
        } else if (this.type === 'particles' && this.particles) {
            this.updateParticles(frequencyData);
        }
    }

    /**
     * Update bars based on frequency data
     */
    updateBars(frequencyData) {
        const barCount = this.bars.length;
        const dataStep = Math.floor(frequencyData.length / barCount);

        this.bars.forEach((bar, i) => {
            const dataIndex = Math.min(i * dataStep, frequencyData.length - 1);
            const value = frequencyData[dataIndex] / 255; // Normalize to 0-1

            // Animate bar height
            const targetHeight = 0.1 + value * 3;
            bar.scale.y = THREE.MathUtils.lerp(bar.scale.y, targetHeight, 0.3);

            // Update color based on frequency
            const color = this.getColorForFrequency(value);
            bar.material.color.set(color);

            // Slight rotation for visual interest
            bar.rotation.z = Math.sin(Date.now() * 0.001 + i) * 0.1;
        });
    }

    /**
     * Update particles based on frequency data
     */
    updateParticles(frequencyData) {
        if (!this.particles) return;

        const positions = this.particles.geometry.attributes.position.array;
        const energy = this.getAverageEnergy(frequencyData);

        for (let i = 0; i < positions.length; i += 3) {
            const index = i / 3;
            const freqIndex = Math.floor((index / positions.length) * frequencyData.length);
            const value = frequencyData[freqIndex] / 255;

            // Move particles based on frequency
            positions[i + 1] += value * 0.1;
            if (positions[i + 1] > 5) {
                positions[i + 1] = -5;
            }
        }

        this.particles.geometry.attributes.position.needsUpdate = true;
    }

    /**
     * Get color for frequency value (interpolate between colors)
     */
    getColorForFrequency(value) {
        if (value < 0.33) {
            return new THREE.Color(this.colors.dominant);
        } else if (value < 0.66) {
            return new THREE.Color(this.colors.secondary);
        } else {
            return new THREE.Color(this.colors.accent);
        }
    }

    /**
     * Get average energy from frequency data
     */
    getAverageEnergy(frequencyData) {
        let sum = 0;
        for (let i = 0; i < frequencyData.length; i++) {
            sum += frequencyData[i];
        }
        return sum / (frequencyData.length * 255);
    }

    /**
     * Update colors from album art
     * @param {Object} colors - {dominant, secondary, accent}
     */
    updateColors(colors) {
        this.colors = { ...this.colors, ...colors };

        // Update existing bars
        if (this.bars.length > 0) {
            this.bars.forEach(bar => {
                bar.material.color.set(this.colors.dominant);
            });
        }

        // Update particles
        if (this.particles) {
            const color1 = new THREE.Color(this.colors.dominant);
            const color2 = new THREE.Color(this.colors.secondary);
            const colors = this.particles.geometry.attributes.color.array;

            for (let i = 0; i < colors.length; i += 3) {
                const color = Math.random() > 0.5 ? color1 : color2;
                colors[i] = color.r;
                colors[i + 1] = color.g;
                colors[i + 2] = color.b;
            }

            this.particles.geometry.attributes.color.needsUpdate = true;
        }
    }

    /**
     * Start animation loop
     */
    start() {
        if (this.isActive) return;
        this.isActive = true;
        this.animate();
    }

    /**
     * Stop animation loop
     */
    stop() {
        this.isActive = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    /**
     * Animation loop
     */
    animate() {
        if (!this.isActive) return;

        this.animationId = requestAnimationFrame(() => this.animate());

        // Render scene
        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
    }

    /**
     * Handle window resize
     */
    handleResize() {
        if (!this.camera || !this.renderer) return;

        const width = this.container.clientWidth;
        const height = this.container.clientHeight;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }

    /**
     * Cleanup and destroy
     */
    destroy() {
        this.stop();

        // Remove event listeners
        window.removeEventListener('resize', () => this.handleResize());

        // Dispose of Three.js resources
        if (this.bars) {
            this.bars.forEach(bar => {
                bar.geometry.dispose();
                bar.material.dispose();
                this.scene.remove(bar);
            });
            this.bars = [];
        }

        if (this.particles) {
            this.particles.geometry.dispose();
            this.particles.material.dispose();
            this.scene.remove(this.particles);
            this.particles = null;
        }

        if (this.renderer) {
            this.renderer.dispose();
            if (this.renderer.domElement && this.renderer.domElement.parentNode) {
                this.renderer.domElement.parentNode.removeChild(this.renderer.domElement);
            }
        }

        this.scene = null;
        this.camera = null;
        this.renderer = null;
    }
}

// Export class
window.Visualizer = Visualizer;

