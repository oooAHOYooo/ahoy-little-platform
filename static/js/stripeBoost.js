(() => {
  function getPublishableKey() {
    const meta = document.querySelector('meta[name="stripe-publishable-key"]');
    return (meta && meta.content) || '';
  }

  let stripe;
  let elements;
  let cardElement;
  let mounted = false;

  function ensureStripe() {
    const pk = getPublishableKey();
    if (!pk) {
      console.warn('Stripe publishable key not found in meta tag');
      return null;
    }
    if (!stripe) {
      stripe = window.Stripe(pk);
      elements = stripe.elements();
    }
    return stripe;
  }

  function mountCard() {
    if (mounted) return;
    ensureStripe();
    if (!elements) return;
    cardElement = elements.create('card');
    const target = document.getElementById('card-element');
    if (target) {
      cardElement.mount('#card-element');
      mounted = true;
    }
  }

  async function createPaymentIntent(artistId, boostAmount) {
    const response = await fetch('/api/boost/stripe/create-intent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ artist_id: String(artistId || ''), boost_amount: Number(boostAmount || 0) })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.error || 'Failed to create PaymentIntent');
    }
    const data = await response.json();
    return data.client_secret;
  }

  function setError(message) {
    const el = document.getElementById('stripe-errors');
    if (el) {
      el.textContent = message || '';
      el.style.display = message ? 'block' : 'none';
    }
  }

  function showModal(show) {
    const modal = document.getElementById('stripe-boost-modal');
    if (modal) {
      modal.style.display = show ? 'flex' : 'none';
    }
  }

  async function confirmPayment(clientSecret) {
    const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
      payment_method: {
        card: cardElement,
      },
    });
    if (error) {
      throw new Error(error.message || 'Payment failed');
    }
    if (paymentIntent && paymentIntent.status === 'succeeded') {
      return paymentIntent;
    }
    throw new Error('Payment not completed');
  }

  async function notifyServer(paymentIntentId) {
    try {
      await fetch('/api/boost/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ payment_intent_id: paymentIntentId })
      });
    } catch (_) {
      // Non-fatal
    }
  }

  async function openAndPay({ artistId, amount }) {
    try {
      setError('');
      ensureStripe();
      mountCard();
      showModal(true);
      const clientSecret = await createPaymentIntent(artistId, amount);
      const pi = await confirmPayment(clientSecret);
      await notifyServer(pi.id);
      document.dispatchEvent(new CustomEvent('ahoy:toast', { detail: `Thanks! Your $${Number(amount).toFixed(2)} boost was sent.` }));
      showModal(false);
      return true;
    } catch (e) {
      setError(e && e.message ? e.message : 'Payment error');
      return false;
    }
  }

  // Public API
  window.StripeBoost = {
    open: openAndPay
  };

  // Wire default trigger if present
  document.addEventListener('DOMContentLoaded', () => {
    ensureStripe();
    const btn = document.getElementById('openBoost');
    if (btn) {
      btn.addEventListener('click', async (e) => {
        e.preventDefault();
        // Attempt to read Alpine state if available
        const amountInput = document.querySelector('.tip-jar-amount-input');
        const artistSelect = document.querySelector('.tip-jar-select');
        const amount = amountInput ? parseFloat(amountInput.value || '0') : 0;
        const artistId = artistSelect ? artistSelect.value : '';
        if (!artistId || !amount || amount < 0.5) {
          setError('Select an artist and enter at least $0.50');
          showModal(true);
          return;
        }
        await openAndPay({ artistId, amount });
      });
    }
    // Close button
    const closeBtn = document.getElementById('stripe-boost-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => showModal(false));
    }
  });
})();


