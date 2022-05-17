import React, { useEffect, useRef, useState } from "react";

import { createTodo, deleteTodo, editTodo, getTodos } from "./api";
import { createUser, getUser } from "./api";
import Authenticated from "./components/Authenticated";
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

function getUserIdFromIdToken(idToken) {
  const tokenPayload = idToken.split('.')[1];
  const userDetails = JSON.parse(atob(tokenPayload));
  console.log(userDetails);

  return userDetails.email;
}

const FILTER_MAP = {
  All: () => true,
  Active: task => !task.completed,
  Completed: task => task.completed
};
const FILTER_NAMES = Object.keys(FILTER_MAP);


export default function App(props) {
  const [idToken, setIdToken] = useState()
  const [userId, setUserId] = useState()
  const [tasks, setTasks] = useState([])
  const [filter, setFilter] = useState('All')

  // load todo data
  useEffect(() => {
    if (idToken === undefined) {
      return;
    }

    const user = getUserIdFromIdToken(idToken);
    setUserId(user);
    console.log(`Getting user details for ${user}`)

    getUser(user)
      .then((userDetails) => {
        if (userDetails === undefined) {
          console.log(`user ${user} does not exist; creating...`)
          return createUser(user).then(() => {
            console.log(`user ${user} created`)
          });
        }
      }).then(() => {
        getTodos(user).then((newTasks) => {
          setTasks([...tasks, ...newTasks]);
        });
      })
  }, [idToken]);

  function addTask(body, category) {
    createTodo(userId, body, category).then((response) => {

      const newTask = { id: response.todoId, body: body, completed: false };

      setTasks([...tasks, newTask]);
    })
  }

  function toggleTaskCompleted(id) {
    let updatedTask

    const updatedTasks = tasks.map(task => {
      if (id === task.id) {
        updatedTask = { ...task, completed: !task.completed };

        return updatedTask;
      }

      return task;
    });

    if (updatedTask !== undefined) {
      editTodo(userId, updatedTask.id, updatedTask.body, "default", updatedTask.completed).then((response) => {
        setTasks(updatedTasks);
      });
    }
  }

  function editTask(id, newBody) {
    let updatedTask

    const updatedTasks = tasks.map(task => {
      if (id === task.id) {
        updatedTask = { ...task, body: newBody };

        return updatedTask;
      }

      return task;
    });

    if (updatedTask !== undefined) {
      editTodo(userId, updatedTask.id, newBody, "default", updatedTask.completed).then((response) => {
        setTasks(updatedTasks);
      });
    }


  }

  function deleteTask(id) {
    deleteTodo(userId, id).then(() => {
      const remainingTasks = tasks.filter(task => (id !== task.id));
      setTasks(remainingTasks);
    })
  }

  const taskList = tasks
    .filter(FILTER_MAP[filter])
    .map(task => (
      <Todo
        id={task.id}
        body={task.body}
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
      <Authenticated idToken={idToken} setIdToken={setIdToken}>
        {/* <Logout idToken={idToken} setIdToken={setIdToken} /> */}
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
      </Authenticated>
    </div>
  );
}