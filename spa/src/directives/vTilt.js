/**
 * v-tilt directive
 * Applies a 3D tilt effect to the element based on mouse position.
 */
export default {
    mounted(el, binding) {
        const options = {
            max: 15, // max tilt rotation (degrees)
            perspective: 1000, // transform perspective (px)
            scale: 1.05, // scale on hover
            speed: 1000, // transition speed (ms)
            ...binding.value
        }

        el.style.transformStyle = 'preserve-3d'
        el.style.transform = `perspective(${options.perspective}px)`

        const handleMouseMove = (e) => {
            const rect = el.getBoundingClientRect()
            const x = e.clientX - rect.left // x position within the element
            const y = e.clientY - rect.top  // y position within the element

            const centerX = rect.width / 2
            const centerY = rect.height / 2

            const rotateX = ((y - centerY) / centerY) * -options.max
            const rotateY = ((x - centerX) / centerX) * options.max

            el.style.transition = 'none' // remove transition for instant follow
            el.style.transform = `
        perspective(${options.perspective}px)
        rotateX(${rotateX}deg)
        rotateY(${rotateY}deg)
        scale3d(${options.scale}, ${options.scale}, ${options.scale})
      `
        }

        const handleMouseLeave = () => {
            el.style.transition = `transform ${options.speed}ms cubic-bezier(.03,.98,.52,.99)`
            el.style.transform = `
        perspective(${options.perspective}px)
        rotateX(0deg)
        rotateY(0deg)
        scale3d(1, 1, 1)
      `
        }

        el.addEventListener('mousemove', handleMouseMove)
        el.addEventListener('mouseleave', handleMouseLeave)

        // Cleanup function stored on element
        el._tiltCleanup = () => {
            el.removeEventListener('mousemove', handleMouseMove)
            el.removeEventListener('mouseleave', handleMouseLeave)
        }
    },
    unmounted(el) {
        if (el._tiltCleanup) el._tiltCleanup()
    }
}
