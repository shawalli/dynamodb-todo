import axios from "axios";

axios.defaults.baseURL = 'https://2utbomhdmi.execute-api.us-east-1.amazonaws.com/dev';

export function getTodos(user) {
  return axios.get(`/user/${user}/todos`)
  .then((response) => {
      const tasks = response.data.result.map(todo => (
        {
          id: todo.todoId,
          name: todo.body,
          completed: 'completed' in todo ? todo.completed : false
        }
      ));

      return tasks;
  })
}

export function createTodo(user, body, category) {
  if (category === undefined) {
    category = "default"
  }
  return axios.post(`/user/${user}/todos`, {
    body: body,
    category: category
  })
  .then((response) => {
    return response.data.todoId;
  });
}

export function editTodo(user, todoId, body, category, completed) {
  return axios.put(`/user/${user}/todos/${todoId}`, {
    body: body,
    category: category,
    completed: completed
  })
  .then((response) => {});
}

export function deleteTodo(user, todoId) {
    return axios.delete(`/user/${user}/todos/${todoId}`)
    .then(function(response) {});
}