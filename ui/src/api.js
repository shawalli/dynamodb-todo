import axios from "axios";

import { retrieveTokenFromStorage } from './token';

axios.defaults.baseURL = 'https://2utbomhdmi.execute-api.us-east-1.amazonaws.com/dev';

axios.interceptors.request.use(function (config) {
  const token = retrieveTokenFromStorage();

  // inject authorization for each request
  config.headers['Authorization'] = `Bearer ${token}`;

  // inject content-type if necessary and not provided
  if ((config.data !== undefined) && !('Content-Type' in config.headers)) {
    // assume that all payloads are JSON
    config.headers['Content-Type'] = 'application/json';
  }

  return config;
});

export function getUser(userId) {
  return axios({
    method: 'get',
    url: `/user/${userId}`
  })
    .then((response) => {
      return Object.keys(response.data.result).length !== 0 ? response.data.result : undefined;
    });
}

export function createUser(userId) {
  const token = retrieveTokenFromStorage()

  return axios({
    method: 'post',
    url: '/user',
    data: {
      userId: userId
    }
  })
    .then(() => {
      return;
    });
}


export function getTodos(userId) {
  const token = retrieveTokenFromStorage()

  return axios({
    method: 'get',
    url: `/user/${userId}/todos`
  })
    .then((response) => {
      const tasks = response.data.result.map(todo => (
        {
          id: todo.todoId,
          body: todo.body,
          completed: 'completed' in todo ? todo.completed : false
        }
      ));

      return tasks;
    })
}

export function createTodo(userId, body, category) {
  const token = retrieveTokenFromStorage()

  if (category === undefined) {
    category = "default"
  }
  return axios({
    method: 'post',
    url: `/user/${userId}/todos`,
    data: {
      body: body,
      category: category
    }
  })
    .then((response) => {
      return response.data.todoId;
    });
}

export function editTodo(userId, todoId, body, category, completed) {
  const token = retrieveTokenFromStorage()

  return axios({
    method: 'put',
    url: `/user/${userId}/todos/${todoId}`,
    data: {
      body: body,
      category: category,
      completed: completed
    }
  })
    .then((response) => { });
}

export function deleteTodo(userId, todoId) {
  const token = retrieveTokenFromStorage()

  return axios({
    method: 'delete',
    url: `/user/${userId}/todos/${todoId}`
  })
    .then(function (response) { });
}