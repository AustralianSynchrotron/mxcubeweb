import React, { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';
import { Modal, ButtonToolbar, Button, Form, Row, Col } from 'react-bootstrap';
import { addSamplesToList } from '../../actions/sampleGrid';
import { addSampleAndMount, addSamplesToQueue } from '../../actions/queue';
import { showList } from '../../actions/queueGUI';
import { useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { hideTaskParametersForm } from '../../actions/taskForm';
import { showErrorPanel } from '../../actions/general';
import { fetchLabsWithProjects } from '../../api/labsWithProjects';
import { createHandMountedSample } from '../../api/handmount';

const REQUIRED_MSG = 'This field is required';
const PATTERN = /^[\w+:-]*$/u;
const PATTERN_MSG = 'Characters allowed: A-Z a-z 0-9 _+:-';

function getSampleData(params) {
  return {
    ...params,
    type: 'Sample',
    // Use project name (if provided) as prefix; fallback to sample name
    defaultPrefix: params.projectName
      ? `${params.projectName}-${params.sampleName}`
      : params.sampleName,
    location: 'Manual',
    loadable: true,
    tasks: [],
  };
}

function AddSample() {
  const { register, formState, handleSubmit, setFocus, watch, setValue } = useForm();
  const { isSubmitted, errors } = formState;
  const [labs, setLabs] = useState([]);
  const [projectsByLab, setProjectsByLab] = useState({});
  const [loading, setLoading] = useState(false);

  const dispatch = useDispatch();
  const { pathname } = useLocation();

  useEffect(() => {
    // Timeout required when creating new sample from "Samples" page
    setTimeout(() => setFocus('sampleName'), 0);
  }, [setFocus]);

  useEffect(() => {
    let mounted = true;
    async function loadLists() {
      try {
        setLoading(true);
        const resp = await fetchLabsWithProjects().catch(() => []);
        if (!mounted) return;

        // Normalize labs and nested projects into consistent shape
        const labsNorm = [];
        const projMap = {};
        const toPair = (it) =>
          typeof it === 'string'
            ? { id: it, name: it }
            : { id: it.id ?? it.value ?? it.name, name: it.name ?? it.label ?? it.id };

        const dataArr = Array.isArray(resp) ? resp : [];
        dataArr.forEach((lab) => {
          const labPair = toPair(lab);
          labsNorm.push(labPair);
          const projects = Array.isArray(lab.projects) ? lab.projects : [];
          projMap[labPair.name] = projects.map(toPair);
        });

        setLabs(labsNorm);
        setProjectsByLab(projMap);
      } finally {
        mounted && setLoading(false);
      }
    }
    loadLists();
    return () => {
      mounted = false;
    };
  }, []);

  const selectedLab = watch('labName');

  // When lab changes, clear project selection if it no longer matches
  useEffect(() => {
    setValue('projectName', '');
  }, [selectedLab, setValue]);

  async function addAndMount(params) {
    // First, create the hand-mounted sample in LIMS
    try {
      // Map selected names to IDs for LIMS call
      const project = (projectsByLab[params.labName] || []).find(
        (p) => p.name === params.projectName,
      );
      const projectId = project?.id;
      if (!projectId) {
        throw new Error('No project selected or project not found for selected lab');
      }

      const limsSample = await createHandMountedSample({
        project_id: projectId,
        sample_name: params.sampleName,
      });
      // Optionally attach created LIMS sample id to sample data
      const sampleData = getSampleData({
        ...params,
        projectId,
        limsID: limsSample?.id,
      });

      dispatch(addSamplesToList([sampleData]));
      dispatch(hideTaskParametersForm());

      await dispatch(addSampleAndMount(sampleData));

      if (pathname === '/' || pathname === '/datacollection') {
        // Switch to mounted sample tab
        dispatch(showList('current'));
      }
    } catch (error) {
      const message =
        error?.response?.headers?.get?.('message') ||
        error?.message ||
        'Failed to create sample in LIMS';
      dispatch(showErrorPanel(true, message));
      return;
    }
  }

  function addAndQueue(params) {
    const sampleData = getSampleData(params);
    dispatch(addSamplesToList([sampleData]));
    dispatch(addSamplesToQueue([sampleData]));
    dispatch(hideTaskParametersForm());
  }

  return (
    <Modal
      show
      onHide={() => dispatch(hideTaskParametersForm())}
      data-default-styles
    >
      <Form noValidate onSubmit={handleSubmit(addAndMount)}>
        <Modal.Header closeButton>
          <Modal.Title>New Sample</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form.Group as={Row} className="mb-3" controlId="sampleName">
            <Col sm={4}>
              <Form.Label column>Sample name</Form.Label>
            </Col>
            <Col sm={8}>
              <Form.Control
                type="text"
                {...register('sampleName', {
                  required: REQUIRED_MSG,
                  pattern: { value: PATTERN, message: PATTERN_MSG },
                })}
                isValid={isSubmitted && !errors.sampleName}
                isInvalid={isSubmitted && !!errors.sampleName}
              />
              <Form.Control.Feedback type="invalid">
                {errors.sampleName?.message}
              </Form.Control.Feedback>
            </Col>
          </Form.Group>
          <Form.Group as={Row} className="mb-3" controlId="labName">
            <Col sm={4}>
              <Form.Label column>Lab name</Form.Label>
            </Col>
            <Col sm={8}>
              <Form.Select
                {...register('labName', { required: REQUIRED_MSG })}
                isValid={isSubmitted && !errors.labName}
                isInvalid={isSubmitted && !!errors.labName}
                defaultValue=""
              >
                <option value="" disabled>
                  {loading ? 'Loading labs…' : 'Select a lab'}
                </option>
                {labs.map((l) => (
                  <option key={l.id} value={l.name}>
                    {l.name}
                  </option>
                ))}
              </Form.Select>
              <Form.Control.Feedback type="invalid">
                {errors.labName?.message}
              </Form.Control.Feedback>
            </Col>
          </Form.Group>

          <Form.Group as={Row} className="mb-3" controlId="projectName">
            <Col sm={4}>
              <Form.Label column>Project name</Form.Label>
            </Col>
            <Col sm={8}>
              <Form.Select
                {...register('projectName', { required: REQUIRED_MSG })}
                isValid={isSubmitted && !errors.projectName}
                isInvalid={isSubmitted && !!errors.projectName}
                defaultValue=""
                disabled={!selectedLab}
              >
                <option value="" disabled>
                  {!selectedLab
                    ? 'Select a lab first'
                    : loading
                      ? 'Loading projects…'
                      : 'Select a project'}
                </option>
                {(projectsByLab[selectedLab] || []).map((p) => (
                  <option key={p.id} value={p.name}>
                    {p.name}
                  </option>
                ))}
              </Form.Select>
              <Form.Control.Feedback type="invalid">
                {errors.projectName?.message}
              </Form.Control.Feedback>
            </Col>
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <ButtonToolbar>
            <Button className="me-3" type="submit">
              Mount
            </Button>
            <Button
              variant="outline-secondary"
              onClick={handleSubmit(addAndQueue)}
            >
              Queue
            </Button>
          </ButtonToolbar>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}

export default AddSample;
