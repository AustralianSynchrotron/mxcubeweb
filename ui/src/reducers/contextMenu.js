const INITIAL_STATE = {
  show: false,
  shape: { type: 'NONE' },
  pageX: 0,
  pageY: 0,
  sampleViewX: 0,
  sampleViewY: 0,
  genericContextMenu: {
    id: '',
    show: false,
    x: 0,
    y: 0,
  },
};

function contextMenuReducer(state = INITIAL_STATE, action = {}) {
  switch (action.type) {
    case 'SHOW_CONTEXT_MENU': {
      return {
        ...state,
        show: action.show,
        shape: action.shape,
        pageX: action.pageX,
        pageY: action.pageY,
        sampleViewX: action.sampleViewX,
        sampleViewY: action.sampleViewY,
      };
    }
    case 'SHOW_GENERIC_CONTEXT_MENU': {
      const genericContextMenu = { ...state.genericContextMenu };

      genericContextMenu.id = action.id;
      genericContextMenu.show = action.show;
      genericContextMenu.x = action.x;
      genericContextMenu.y = action.y;

      return { ...state, genericContextMenu };
    }
    default: {
      return state;
    }
  }
}

export default contextMenuReducer;
