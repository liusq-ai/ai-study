const form = document.querySelector("#chat-form");
const input = document.querySelector("#message-input");
const messages = document.querySelector("#messages");
const statusText = document.querySelector("#status");
const sendButton = document.querySelector("#send-button");
const clearButton = document.querySelector("#clear-button");

function addMessage(role, text, meta = "") {
  const article = document.createElement("article");
  article.className = `message ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  if (meta) {
    const metaNode = document.createElement("div");
    metaNode.className = "meta";
    metaNode.textContent = meta;
    bubble.appendChild(metaNode);
  }

  article.appendChild(bubble);
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
}

function setBusy(isBusy) {
  sendButton.disabled = isBusy;
  statusText.textContent = isBusy ? "模型回复中" : "准备就绪";
}

async function sendMessage(message) {
  addMessage("user", message);
  setBusy(true);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await response.json();

    if (!response.ok) {
      addMessage("assistant", data.error || "请求失败");
      return;
    }

    const intent = data.intent || {};
    const meta = `意图：${intent.type || "-"}，需要订单：${intent.need_order_info ? "是" : "否"}`;
    addMessage("assistant", data.reply, meta);
  } catch (error) {
    addMessage("assistant", `请求失败：${error}`);
  } finally {
    setBusy(false);
    input.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = input.value.trim();

  if (!message) {
    return;
  }

  input.value = "";
  sendMessage(message);
});

document.querySelectorAll("[data-message]").forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.dataset.message || "";
    input.focus();
  });
});

clearButton.addEventListener("click", () => {
  messages.innerHTML = "";
  addMessage("assistant", "您好，我是 AI 客服小白。请输入物流、退款、商品咨询或故障问题。");
});

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

