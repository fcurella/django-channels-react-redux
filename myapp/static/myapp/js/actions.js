import { createAction } from 'redux-actions';

import ActionTypes from './constants';
import { WebsocketBridge } from './utils/WebsocketBridge';


export const incrementCounter = createAction(ActionTypes.INCREMENT_COUNTER, (incrementBy) => {
  WebsocketBridge.send({
    type: ActionTypes.INCREMENT_COUNTER,
    incrementBy
  });
});
