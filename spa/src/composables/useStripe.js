import { ref, onMounted } from 'vue'
import { apiFetch } from './useApi'

let stripePromise = null

export function useStripe() {
    const stripe = ref(null)
    const loading = ref(true)
    const error = ref(null)

    async function initStripe() {
        if (stripe.value) return stripe.value
        if (stripePromise) {
            stripe.value = await stripePromise
            loading.value = false
            return stripe.value
        }

        try {
            // 1. Get publishable key from backend
            const { publishable_key } = await apiFetch('/api/config/stripe')
            if (!publishable_key) {
                throw new Error('Stripe publishable key not found')
            }

            // 2. Load Stripe.js if not already loaded
            if (!window.Stripe) {
                await new Promise((resolve, reject) => {
                    const script = document.createElement('script')
                    script.src = 'https://js.stripe.com/v3/'
                    script.onload = resolve
                    script.onerror = reject
                    document.head.appendChild(script)
                })
            }

            // 3. Initialize Stripe
            stripePromise = Promise.resolve(window.Stripe(publishable_key))
            stripe.value = await stripePromise
            return stripe.value
        } catch (e) {
            error.value = e.message
            console.error('Stripe init error:', e)
        } finally {
            loading.value = false
        }
    }

    async function createPaymentIntent(artistId, amount) {
        return apiFetch('/api/boost/stripe/create-intent', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ artist_id: String(artistId), boost_amount: Number(amount) })
        })
    }

    async function confirmBoost(paymentIntentId) {
        return apiFetch('/api/boost/confirm', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ payment_intent_id: paymentIntentId })
        })
    }

    return {
        stripe,
        loading,
        error,
        initStripe,
        createPaymentIntent,
        confirmBoost
    }
}
