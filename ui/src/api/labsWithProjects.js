import api from '.';

// Fetch labs with associated projects from LIMS.
// Expected shape: [{ id, name, projects: [{ id, name }, ...] }, ...]
export function fetchLabsWithProjects() {
  return api.get('/lims/labs_with_projects').safeJson();
}
