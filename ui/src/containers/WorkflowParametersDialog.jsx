import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Modal } from 'react-bootstrap';
import Form from '@rjsf/core';
import validator from '@rjsf/validator-ajv8';
import {
  showWorkflowParametersDialog,
  submitWorkflowParameters,
} from '../actions/workflow';

import styles from './WorkflowParametersDialog.module.css';

import diagonalNoise from '../img/diagonal-noise.png';

function WorkflowParametersDialog() {
  const dispatch = useDispatch();
  const show = useSelector((state) => state.workflow.showDialog);
  const formData = useSelector((state) => state.workflow.formData);
  const inControl = useSelector((state) => state.login.user.inControl);

  function submitData(values) {
    dispatch(submitWorkflowParameters(values.formData));
    dispatch(showWorkflowParametersDialog(null, false));
  }

  function handleClose() {
    // mxcubecore treats an empty payload as a cancel.
    if (inControl) {
      dispatch(submitWorkflowParameters({}));
    }
    dispatch(showWorkflowParametersDialog(null, false));
  }

  return (
    <Modal show={show} onHide={handleClose} backdrop="static">
      <Modal.Header closeButton>
        <Modal.Title>{formData ? formData.dialogName : ''}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <div className="position-relative" id="form-holder">
          {!inControl && (
            <div
              aria-hidden
              className="position-absolute top-0 start-0 w-100 h-100"
              style={{
                backgroundImage: `url(${diagonalNoise})`,
              }}
            />
          )}
          {/* The Liform generates errors when `schema` is empty or null so
              we only create it when show is true and we have a schema to use. */}
          {show && formData && (
            <div className={styles.rjsfFormContainer}>
              <Form
                validator={validator}
                schema={formData}
                formData={formData.initialValues}
                disabled={!inControl}
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
