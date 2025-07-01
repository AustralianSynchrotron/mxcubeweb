import { omit } from 'lodash/object';

const INITIAL_STATE = {
  shapes: {},
};

function shapesReducer(state = INITIAL_STATE, action = {}) {
  switch (action.type) {
    case 'SET_SHAPES': {
      // when grid shapes are updated, do not update screenCoord
      // as the screenCoord gets weirdly updated by other motors
      // (e.g., Omega, Y, and so on), but not the X motor.
      const updatedShapes = { ...action.shapes };
      Object.keys(updatedShapes).forEach((key) => {
        // assume we can use label = 'Grid' or t = 'G' according to the payload
        if (updatedShapes[key].label === 'Grid') {
          const previousScreenCoord = state.shapes[key].screenCoord;
          updatedShapes[key].screenCoord = previousScreenCoord;
        }
      });

      return { ...state, shapes: updatedShapes };
    }
    case 'ADD_SHAPE': {
      return {
        ...state,
        shapes: { ...state.shapes, [action.shape.id]: action.shape },
      };
    }
    case 'UPDATE_SHAPES': {
      const shapes = { ...state.shapes };

      action.shapes.forEach((shape) => {
        shapes[shape.id] = shape;
      });

      return { ...state, shapes };
    }
    case 'DELETE_SHAPE': {
      return { ...state, shapes: omit(state.shapes, action.id) };
    }
    case 'SET_OVERLAY': {
      return { ...state, overlayLevel: action.level };
    }
    case 'SET_CURRENT_SAMPLE': {
      return INITIAL_STATE;
    }
    case 'CLEAR_ALL': {
      return INITIAL_STATE;
    }
    case 'SET_INITIAL_STATE': {
      return {
        ...state,
        shapes: action.data.shapes,
      };
    }
    default: {
      return state;
    }
  }
}

export default shapesReducer;
