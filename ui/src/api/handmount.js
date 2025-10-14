import api from '.';

// Create a hand-mounted sample in the database
// params: { project_id: number, sample_name: string }
export function createHandMountedSample(params) {
  return api.post(params, '/lims/hand_mounted_sample').safeJson();
}
