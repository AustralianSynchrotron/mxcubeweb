import api from '.';

// Fetch list of labs from LIMS scope. Expected response: array of { id, name } or strings.
export function fetchLabs() {
  return api.get('/lims/labs').safeJson();
}
