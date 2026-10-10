const list = document.getElementById("list");
const form = document.getElementById("form");
const titleInput = document.getElementById("title");
const statusEl = document.getElementById("status");
const emptyEl = document.getElementById("empty");

async function api(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.status === 204 ? null : res.json();
}

function render(tasks) {
  list.innerHTML = "";
  emptyEl.hidden = tasks.length > 0;

  for (const task of tasks) {
    const li = document.createElement("li");
    li.className = task.done ? "done" : "";

    const text = document.createElement("span");
    text.className = "text";
    text.textContent = task.title;
    text.onclick = () => toggle(task.id);

    const del = document.createElement("button");
    del.className = "del";
    del.textContent = "x";
    del.title = "Удалить";
    del.onclick = () => remove(task.id);

    li.append(text, del);
    list.append(li);
  }
}

async function load() {
  try {
    render(await api("/tasks"));
    const health = await api("/health");
    statusEl.textContent = `ok v${health.version}`;
  } catch (err) {
    statusEl.textContent = "ошибка связи";
    console.error(err);
  }
}

async function toggle(id) {
  await api(`/tasks/${id}/toggle`, { method: "POST" });
  render(await api("/tasks"));
}

async function remove(id) {
  await api(`/tasks/${id}`, { method: "DELETE" });
  render(await api("/tasks"));
}

form.onsubmit = async (event) => {
  event.preventDefault();
  const title = titleInput.value.trim();
  if (!title) return;
  await api("/tasks", { method: "POST", body: JSON.stringify({ title }) });
  titleInput.value = "";
  render(await api("/tasks"));
};

load();
