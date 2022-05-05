import axios from "axios";
import { nanoid } from "nanoid";
import React, { useEffect, useRef, useState } from "react";

import FilterButton from "./components/FilterButton";
import Form from "./components/Form";
import Todo from "./components/Todo";

function usePrevious(value) {
  const ref = useRef();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}

const FILTER_MAP = {
  All: () => true,
  Active: task => !task.completed,
  Completed: task => task.completed
};
const FILTER_NAMES = Object.keys(FILTER_MAP);

axios.defaults.baseURL = 'https://2utbomhdmi.execute-api.us-east-1.amazonaws.com/dev';

export default function App(props) {
  const [tasks, setTasks] = useState([])
  const [filter, setFilter] = useState('All')

  useEffect(() => {
    axios.get('/user/shawn/todos')
    .then(function (response) {
      console.log("GOT RESULTS");
      console.log(response);
      console.log(response.data);
      console.log(response.data.result)

      const newTasks = response.data.result.map(todo => (
        {
          id: todo.todoId,
          name: todo.body,
          completed: 'completed' in todo ? todo.completed : false
        }
      ));

      setTasks([...tasks, ...newTasks]);

    })
    .catch(function (error) {
      console.log("GOT ERROR");
      console.log(error);
    });
  }, [])

  function addTask(name) {
    const newTask = { id: "todo-" + nanoid(), name: name, completed: false };

    setTasks([...tasks, newTask]);
  }

  function toggleTaskCompleted(id) {
    const updatedTasks = tasks.map(task => {
      if (id === task.id) {
        return {...task, completed: !task.completed}
      }

      return task;
    });
    setTasks(updatedTasks);
  }

  function editTask(id, newName) {
    const updatedTasks = tasks.map(task => {
      if (id === task.id) {
        return {...task, name: newName}
      }

      return task;
    });
    setTasks(updatedTasks);
  }

  function deleteTask(id) {
    const remainingTasks = tasks.filter(task => (id !== task.id));
    setTasks(remainingTasks);
  }

  const taskList = tasks
  .filter(FILTER_MAP[filter])
  .map(task => (
    <Todo
        id={task.id}
        name={task.name}
        completed={task.completed}
        key={task.id}
        toggleTaskCompleted={toggleTaskCompleted}
        editTask={editTask}
        deleteTask={deleteTask}
      />
    )
  );

  const filterList = FILTER_NAMES.map(name => (
    <FilterButton
      key={name}
      name={name}
      isPressed={name === filter}
      setFilter={setFilter}  
    />
  ));

  const headingText = `${taskList.length} ${taskList.length !== 1 ? 'tasks' : 'task'} remaining`;

  const listHeadingRef = useRef(null);

  const prevTaskLength = usePrevious(tasks.length);

  useEffect(() => {
    if (tasks.length - prevTaskLength === -1) {
      listHeadingRef.current.focus();
    }
  }, [tasks.length, prevTaskLength]);

  return (
    <div className="todoapp stack-large">
      <h1>TodoMatic</h1>
      <Form addTask={addTask} />
      <div className="filters btn-group stack-exception">
        {filterList}
      </div>
      <h2 id="list-heading" tabIndex="-1" ref={listHeadingRef}>
        {headingText}
      </h2>
      <ul
        className="todo-list stack-large stack-exception"
        aria-labelledby="list-heading"
      >
        {taskList}
      </ul>
    </div>
  );
}