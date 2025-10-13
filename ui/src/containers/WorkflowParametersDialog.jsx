import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Modal } from 'react-bootstrap';
import Form from '@rjsf/core';
import validator from '@rjsf/validator-ajv8';
import {
  showWorkflowParametersDialog,
  submitWorkflowParameters,
} from '../actions/workflow';
import { setSampleAttribute } from '../actions/queue';

import styles from './WorkflowParametersDialog.module.css';

function WorkflowParametersDialog() {
  const dispatch = useDispatch();
  const show = useSelector((state) => state.workflow.showDialog);
  const formData = useSelector((state) => state.workflow.formData);
  const currentSampleID = useSelector((state) => state.queue.currentSampleID);
  const currentSample = useSelector((state) =>
    state.sampleGrid.sampleList[state.queue.currentSampleID],
  );

  function submitData(values) {
    const submitted = values.formData || {};
    const newSampleName = submitted.sample_name;

    // If the user provided a sample name, update the current sample in the UI
    if (newSampleName && currentSampleID) {
      dispatch(setSampleAttribute([currentSampleID], 'sampleName', newSampleName));

      // Always show only the sample name for prefix
      dispatch(
        setSampleAttribute(
          [currentSampleID],
          'defaultPrefix',
          `${newSampleName}`,
        ),
      );
    }

    dispatch(submitWorkflowParameters(values.formData));
    dispatch(showWorkflowParametersDialog(null, false));
  }

  function handleClose() {
    dispatch(submitWorkflowParameters({}));
    dispatch(showWorkflowParametersDialog(null, false));
  }
  console.log("formData", formData);


  return (
    <Modal show={show} onHide={handleClose} backdrop="static">
      <Modal.Header closeButton>
        <Modal.Title>{formData ? formData.dialogName : ''}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <div id="form-holder">
          {/* The Liform generates errors when `schema` is empty or null so
              we only create it when show is true and we have a schema to use. */}
          {show && formData && (
            <div className={styles.rjsfFormContainer}>
              <Form
                validator={validator}
                schema={formData}
                formData={formData.initialValues}
                onSubmit={submitData}
                onError={console.log('error')} // eslint-disable-line no-console
              />
            </div>
          )}
        </div>
      </Modal.Body>
      <Modal.Footer />
    </Modal>
  );
}

export default WorkflowParametersDialog;
