const INITIAL_STATE = {
  // the null value is used to distinguish between signed out (null) or logged in (true/false)
  sid: null,
  observers: [],
  allowRemote: false,
  timeoutGivesControl: false,
  messages: [],
};

export default function remoteAccessReducer(
  state = INITIAL_STATE,
  action = {},
) {
  switch (action.type) {
    case 'SET_RA_STATE': {
      return {
        ...state,
        observers: action.data.observers,
        allowRemote: action.data.allowRemote,
        timeoutGivesControl: action.data.timeoutGivesControl,
        operator: action.data.operator,
      };
    }
    case 'SET_MASTER': {
      return { ...state, sid: action.sid };
    }
    case 'SET_ALLOW_REMOTE': {
      return { ...state, allowRemote: action.allow };
    }
    case 'SET_TIMEOUT_GIVES_CONTROL': {
      return { ...state, timeoutGivesControl: action.timeoutGivesControl };
    }
    case 'SET_CHAT_MESSAGES': {
      return {
        ...state,
        messages: action.messages,
      };
    }
    case 'ADD_CHAT_MESSAGE': {
      return {
        ...state,
        messages: [...state.messages, action.message],
      };
    }
    case 'SET_INITIAL_STATE': {
      return {
        ...state,
        observers: action.data.remoteAccess.observers,
        sid: action.data.remoteAccess.sid,
        allowRemote: action.data.remoteAccess.allowRemote,
        timeoutGivesControl: action.data.remoteAccess.timeoutGivesControl,
        operator: action.data.remoteAccess.operator,
      };
    }
    default: {
      return state;
    }
  }
}
