
/**
 * API client for Northwind Support Co-pilot backend.
 * All calls go through /api proxy (see vite.config.js)
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

/**
 * Check backend health and LLM mode.
 */
export async function getHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Backend health check failed');
  return res.json();
}

/**
 * Fetch policy passages [P1]-[P8].
 */
export async function getPolicy() {
  const res = await fetch(`${API_BASE}/policy`);
  if (!res.ok) throw new Error('Failed to fetch policy');
  return res.json();
}

/**
 * Fetch all 14 test tickets.
 */
export async function getTickets() {
  const res = await fetch(`${API_BASE}/tickets`);
  if (!res.ok) throw new Error('Failed to fetch test tickets');
  return res.json();
}

/**
 * Send a custom ticket text and run the full pipeline.
 * @param {string} ticketText - Raw ticket text
 * @returns {Promise<object>} Pipeline result with all 4 stages
 */
export async function sendTicket(ticketText) {
  const res = await fetch(`${API_BASE}/ticket`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ticket_text: ticketText }),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Pipeline failed');
  }
  return res.json();
}

/**
 * Run the pipeline on a test-set ticket by ID (1-14).
 * @param {number} ticketId - Test ticket ID
 * @returns {Promise<object>} Pipeline result
 */
export async function runTicketById(ticketId) {
  const res = await fetch(`${API_BASE}/ticket/${ticketId}`, {
    method: 'POST',
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Pipeline failed');
  }
  return res.json();
}