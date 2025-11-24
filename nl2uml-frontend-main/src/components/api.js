/**
 * General-purpose API call helper for secured endpoints.
 * @param {string} endpoint - The API endpoint URL.
 * @param {string} [method='GET'] - HTTP method (GET, POST, DELETE, etc.).
 * @param {Object|null} [body=null] - JSON payload for POST/PUT requests.
 * @returns {Promise<any>} - Parsed JSON response.
 */
export async function callApi({ endpoint, method = 'GET', body = null, sessionId }) {
  const headers = {};
  if (sessionId) {
    headers['X-User-Email'] = sessionId;
  }
  // Only set JSON content type when we are actually sending a body to avoid extra preflight
  if (body) {
    headers['Content-Type'] = 'application/json';
  }

  // Setup fetch options
  const options = {
    method,
    headers,
  };
  if (body) {
    const payload = (typeof body === 'object' && body !== null) ? { ...body } : body;
    if (payload && typeof payload === 'object' && sessionId && !payload.userEmail) {
      payload.userEmail = sessionId;
    }
    options.body = JSON.stringify(payload);
  }

  // Make the API call
  const response = await fetch(endpoint, options);

  // Read the body once so we can safely attempt JSON parse or fall back to text.
  const raw = await response.text();

  // Optional: throw for error status codes
  if (!response.ok) {
    const message = raw || response.statusText || 'Request failed';
    throw new Error(`API error ${response.status}: ${message}`);
  }

  // Handle empty responses (204 No Content)
  if (response.status === 204 || raw.trim() === '') {
    return {}; // Return an empty object for 204 No Content responses
  }

  // Parse JSON if possible, otherwise return plain text
  try {
    return JSON.parse(raw);
  } catch (err) {
    return raw;
  }
}
