import api from '.';

// Fetch list of projects from LIMS scope. Expected response: array of { id, name } or strings.
export function fetchProjects() {
  return api.get('/lims/projects').safeJson();
}
