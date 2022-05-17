import axios from "axios";

axios.defaults.baseURL = 'https://2utbomhdmi.execute-api.us-east-1.amazonaws.com/dev';

export function getUser(userId) {
  return axios.get(`/user/${userId}`)
    .then((response) => {
      return Object.keys(response.data.result).length !== 0 ? response.data.result : undefined;
    });
}

export function createUser(userId) {
  return axios({
    method: 'post',
    url: '/user',
    headers: {
      'Content-Type': 'application/json'
    },
    data: {
      userId: userId
    }
  })
    .then(() => {
      return;
    });
}


export function getTodos(userId) {
  return axios.get(`/user/${userId}/todos`)
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
  if (category === undefined) {
    category = "default"
  }
  return axios({
    method: 'post',
    url: `/user/${userId}/todos`,
    headers: {
      'Content-Type': 'application/json'
    },
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
  return axios.put(`/user/${userId}/todos/${todoId}`, {
    body: body,
    category: category,
    completed: completed
  })
    .then((response) => { });
}

export function deleteTodo(userId, todoId) {
  return axios.delete(`/user/${userId}/todos/${todoId}`)
    .then(function (response) { });
}