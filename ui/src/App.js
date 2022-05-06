import React, { useEffect, useRef, useState } from "react";

import { createTodo, deleteTodo, editTodo, getTodos } from "./api";
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


export default function App(props) {
  const [tasks, setTasks] = useState([])
  const [filter, setFilter] = useState('All')

  // load todo data
  useEffect(() => {
    getTodos('shawn').then((newTasks) => {
      setTasks([...tasks, ...newTasks]);
    });
  }, []);

  function addTask(body, category) {
    createTodo('shawn', body, category).then((response) => {

      const newTask = { id: response.todoId, name: body, completed: false };

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
      editTodo("shawn", updatedTask.id, updatedTask.name, "default", updatedTask.completed).then((response) => {
        setTasks(updatedTasks);
      });
    }
  }

  function editTask(id, newBody) {
    let updatedTask

    const updatedTasks = tasks.map(task => {
      if (id === task.id) {
        updatedTask = { ...task, name: newBody };

        return updatedTask;
      }

      return task;
    });

    editTodo("shawn", updatedTask.id, newBody, "default", updatedTask.completed).then((response) => {
      setTasks(updatedTasks);
    });


  }

  function deleteTask(id) {
    deleteTodo('shawn', id).then(() => {
      const remainingTasks = tasks.filter(task => (id !== task.id));
      setTasks(remainingTasks);
    })
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