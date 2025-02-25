/* eslint-disable react/jsx-handler-names */
import React, { useCallback } from 'react';
import { connect } from 'react-redux';
import { reduxForm, formValueSelector } from 'redux-form';
import validate from './validate';

function Workflow(props) {
  const isGphlWorkflow = props.wfpath === 'Gphl';

  const addToQueue = useCallback((runNow, params) => {
    const parameters = {
      ...params,
      type: isGphlWorkflow ? 'GphlWorkflow' : 'Workflow',
      label: params.wfname,
      shape: props.pointID,
      suffix: props.suffix,
    };

    // Form gives us all parameter values in strings so we need to transform numbers back
    const stringFields = [
      'centringMethod',
      'prefix',
      'subdir',
      'type',
      'shape',
      'label',
      'wfname',
      'wfpath',
      'suffix',
    ];

    if (isGphlWorkflow) {
      parameters.strategy_name = props.strategy_name;
      stringFields.push('strategy_name');
    }

    props.addTask(parameters, stringFields, runNow);
    props.hide();
  }, [isGphlWorkflow, props]);

  // Automatically call the function that the "Run Now" button triggers
  React.useEffect(() => {
    if (!props.invalid) {
      addToQueue(true, props.initialValues);
    }
  }, [props.invalid, props.initialValues, addToQueue]);

  return null; // Do not render anything
}

const WorkflowForm = reduxForm({
  form: 'workflow',
  validate,
})(Workflow);

const selector = formValueSelector('workflow');

const WorkflowFormConnect = connect((state) => {
  const subdir = selector(state, 'subdir');
  const fileSuffix = state.taskForm.fileSuffix === 'h5' ? '_master.h5' : 'cbf';
  const strategy_name = selector(state, 'strategy_name');
  let position = state.taskForm.pointID === '' ? 'PX' : state.taskForm.pointID;
  if (typeof position === 'object') {
    const vals = Object.values(position).sort();
    position = `[${vals}]`;
  }

  let fname = '';

  if (state.taskForm.taskData.sampleID) {
    fname = state.taskForm.taskData.parameters.fileName;
  } else {
    const prefix = selector(state, 'prefix');
    fname = `${prefix}_[RUN#]_[IMG#]`;
  }

  const limits = {};

  return {
    path: `${state.login.rootPath}/${subdir}`,
    origin: state.taskForm.origin,
    filename: fname,
    wfname: state.taskForm.taskData.parameters.wfname,
    wfpath: state.taskForm.taskData.parameters.wfpath,
    acqParametersLimits: limits,
    beamline: state.beamline,
    suffix: fileSuffix,
    strategy_name,
    initialValues: {
      ...state.taskForm.taskData.parameters,
      beam_size: state.sampleview.currentAperture,
    },
  };
})(WorkflowForm);

export default WorkflowFormConnect;
