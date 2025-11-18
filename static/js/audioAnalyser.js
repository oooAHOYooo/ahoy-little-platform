/**
 * Audio Analyser - Web Audio API integration for frequency analysis
 * Connects to audio element and provides real-time frequency data
 */

class AudioAnalyser {
    constructor() {
        this.audioContext = null;
        this.analyser = null;
        this.source = null;
        this.dataArray = null;
        this.bufferLength = 0;
        this.isInitialized = false;
        this.audioElement = null;
    }

    /**
     * Initialize Web Audio API context
     * Must be called after user interaction (browser security)
     */
    async initialize() {
        if (this.isInitialized) return Promise.resolve(true);

        try {
            // Create AudioContext (with fallback for older browsers)
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            if (!AudioContextClass) {
                console.warn('Web Audio API not supported');
                return Promise.resolve(false);
            }

            this.audioContext = new AudioContextClass();
            this.analyser = this.audioContext.createAnalyser();
            
            // Configure analyser
            this.analyser.fftSize = 256; // 128 frequency bins
            this.analyser.smoothingTimeConstant = 0.8;
            
            this.bufferLength = this.analyser.frequencyBinCount;
            this.dataArray = new Uint8Array(this.bufferLength);

            this.isInitialized = true;
            return Promise.resolve(true);
        } catch (error) {
            console.error('Error initializing AudioAnalyser:', error);
            return Promise.resolve(false);
        }
    }

    /**
     * Connect audio element to analyser
     * @param {HTMLAudioElement} audioElement - The audio element to analyze
     */
    connect(audioElement) {
        if (!this.isInitialized) {
            console.warn('AudioAnalyser not initialized. Call initialize() first.');
            return false;
        }

        if (!audioElement) {
            console.warn('No audio element provided');
            return false;
        }

        // If already connected to this element, skip
        if (this.audioElement === audioElement && this.source) {
            return true;
        }

        try {
            // Disconnect previous source if exists
            if (this.source) {
                try {
                    this.source.disconnect();
                } catch (e) {
                    // Source might already be disconnected
                }
            }

            // Check if audio element already has a source node (can only have one)
            // We need to check if the element is already connected to avoid errors
            try {
                // Create media source from audio element
                // This can only be called once per audio element
                this.source = this.audioContext.createMediaElementSource(audioElement);
                
                // Connect: source -> analyser -> destination
                // The analyser acts as a pass-through, so audio still plays
                this.source.connect(this.analyser);
                this.analyser.connect(this.audioContext.destination);

                this.audioElement = audioElement;
                return true;
            } catch (error) {
                // If createMediaElementSource fails (element already has a source),
                // we can't analyze it, but don't break playback
                // This is expected if the element was already connected elsewhere
                if (error.name === 'InvalidStateError' || error.message.includes('already connected')) {
                    console.warn('Audio element already has a MediaElementSource. Visualizer may not work, but audio will play normally.');
                } else {
                    console.warn('Cannot create MediaElementSource. Audio will play but visualizer may not work:', error);
                }
                this.audioElement = audioElement;
                return false; // Return false but don't throw - audio will still play
            }
        } catch (error) {
            console.error('Error connecting audio element:', error);
            // Don't break playback if analyser fails
            return false;
        }
    }

    /**
     * Get current frequency data
     * @returns {Uint8Array} Frequency data array (0-255 values)
     */
    getFrequencyData() {
        if (!this.analyser || !this.dataArray) {
            return null;
        }

        this.analyser.getByteFrequencyData(this.dataArray);
        return this.dataArray;
    }

    /**
     * Get current time domain data (waveform)
     * @returns {Uint8Array} Time domain data array
     */
    getTimeDomainData() {
        if (!this.analyser || !this.dataArray) {
            return null;
        }

        const timeData = new Uint8Array(this.bufferLength);
        this.analyser.getByteTimeDomainData(timeData);
        return timeData;
    }

    /**
     * Get average frequency in a range
     * @param {number} startBin - Start bin index
     * @param {number} endBin - End bin index
     * @returns {number} Average frequency value
     */
    getAverageFrequency(startBin = 0, endBin = null) {
        const data = this.getFrequencyData();
        if (!data) return 0;

        const end = endBin !== null ? Math.min(endBin, data.length) : data.length;
        let sum = 0;
        let count = 0;

        for (let i = startBin; i < end; i++) {
            sum += data[i];
            count++;
        }

        return count > 0 ? sum / count : 0;
    }

    /**
     * Get bass frequency (low frequencies)
     */
    getBass() {
        return this.getAverageFrequency(0, 8);
    }

    /**
     * Get mid frequency
     */
    getMid() {
        return this.getAverageFrequency(8, 32);
    }

    /**
     * Get treble frequency (high frequencies)
     */
    getTreble() {
        return this.getAverageFrequency(32, 64);
    }

    /**
     * Get overall energy level (0-1)
     */
    getEnergy() {
        const data = this.getFrequencyData();
        if (!data) return 0;

        let sum = 0;
        for (let i = 0; i < data.length; i++) {
            sum += data[i];
        }

        return (sum / (data.length * 255));
    }

    /**
     * Disconnect and cleanup
     */
    disconnect() {
        if (this.source) {
            this.source.disconnect();
            this.source = null;
        }
        this.audioElement = null;
    }

    /**
     * Resume audio context (required after user interaction)
     */
    async resume() {
        if (this.audioContext && this.audioContext.state === 'suspended') {
            await this.audioContext.resume();
        }
    }

    /**
     * Check if audio context is running
     */
    isRunning() {
        return this.audioContext && this.audioContext.state === 'running';
    }
}

// Export singleton instance
window.audioAnalyser = new AudioAnalyser();

