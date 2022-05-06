import axios from "axios";

axios.defaults.baseURL = 'https://2utbomhdmi.execute-api.us-east-1.amazonaws.com/dev';

export function getTodos(user) {
  return axios.get(`/user/${user}/todos`)
  .then(function (response) {
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

export function deleteTodo(user, todoId) {
    return axios.delete(`/user/${user}/${todoId}`)
    .then(function(response) {});
}