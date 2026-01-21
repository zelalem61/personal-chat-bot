const chatEl = document.getElementById("chat");
const formEl = document.getElementById("form");
const inputEl = document.getElementById("message");
const sendBtn = document.getElementById("send");
const statusEl = document.getElementById("status");
const newThreadBtn = document.getElementById("newThread");

const THREAD_KEY = "portfolio_bot_thread_id";

function getThreadId() {
  return localStorage.getItem(THREAD_KEY) || "default";
}

function setThreadId(id) {
  localStorage.setItem(THREAD_KEY, id);
}

function scrollToBottom() {
  chatEl.scrollTop = chatEl.scrollHeight;
}

function formatTime(d = new Date()) {
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function addMessage(role, text, opts = {}) {
  const row = document.createElement("div");
  row.className = `row ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  if (opts.isHtml) {
    bubble.innerHTML = text;
  } else {
    bubble.textContent = text;
  }

  if (opts.meta) {
    const meta = document.createElement("div");
    meta.className = "metaLine";
    meta.textContent = opts.meta;
    bubble.appendChild(meta);
  }

  row.appendChild(bubble);
  chatEl.appendChild(row);
  scrollToBottom();
  return { row, bubble };
}

function setStatus(text) {
  statusEl.textContent = text || "";
}

function setBusy(isBusy) {
  sendBtn.disabled = isBusy;
  inputEl.disabled = isBusy;
}

function addTyping() {
  const html = `
    <span class="typing" aria-label="Bot is typing">
      <span class="dot"></span><span class="dot"></span><span class="dot"></span>
    </span>
  `;
  const { row } = addMessage("bot", html, { isHtml: true });
  return row;
}

async function sendMessage(message) {
  const payload = {
    message,
    thread_id: getThreadId(),
  };

  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}${detail ? `: ${detail}` : ""}`);
  }

  return await res.json();
}

function bootstrap() {
  // Initial hint
  addMessage(
    "bot",
    "Hi! Ask me anything about the portfolio. For example: “What are your skills?”",
    { meta: `Thread: ${getThreadId()}` }
  );

  inputEl.focus();
}

newThreadBtn.addEventListener("click", () => {
  const id = `thread-${Date.now().toString(36)}`;
  setThreadId(id);
  chatEl.innerHTML = "";
  addMessage("bot", "Started a new conversation.", { meta: `Thread: ${getThreadId()}` });
  inputEl.focus();
});

formEl.addEventListener("submit", async (e) => {
  e.preventDefault();

  const message = (inputEl.value || "").trim();
  if (!message) return;

  setStatus("");
  addMessage("user", message, { meta: formatTime() });
  inputEl.value = "";

  setBusy(true);
  const typingRow = addTyping();

  try {
    const data = await sendMessage(message);

    if (data && typeof data.thread_id === "string" && data.thread_id.length > 0) {
      setThreadId(data.thread_id);
    }

    typingRow.remove();
    addMessage("bot", data?.response ?? "(No response)", { meta: `Thread: ${getThreadId()}` });
  } catch (err) {
    typingRow.remove();
    addMessage("bot", "Sorry — I couldn’t reach the backend. Check the server logs and try again.", {
      meta: String(err?.message || err),
    });
  } finally {
    setBusy(false);
    setStatus("");
    inputEl.focus();
  }
});

bootstrap();

