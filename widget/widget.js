/**
 * Embeddable website chat widget.
 * Usage: <script src="widget.js" data-api-url="https://your-api-url"></script>
 */
(function () {
  "use strict";

  /** Return the script element loading this widget. */
  function getCurrentScript() {
    return document.currentScript || document.querySelector('script[src*="widget.js"]');
  }

  /** Inject widget stylesheet based on widget.js source path. */
  function injectStylesheet(scriptEl) {
    if (!scriptEl || !scriptEl.src) return;
    var cssHref = scriptEl.src.replace(/widget\.js(\?.*)?$/, "widget.css");
    var link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = cssHref;
    document.head.appendChild(link);
  }

  /** Create and return a DOM element with optional class and text. */
  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (typeof text === "string") node.textContent = text;
    return node;
  }

  var scriptEl = getCurrentScript();
  var apiUrl = scriptEl ? scriptEl.getAttribute("data-api-url") : "";
  if (!apiUrl) {
    console.error("Widget error: missing data-api-url on script tag.");
    return;
  }

  injectStylesheet(scriptEl);

  var conversation = [];
  var userId = "web_" + Math.random().toString(36).slice(2) + Date.now().toString(36);
  var isOpen = false;

  var button = el("button", "wa-widget-button", "Chat");
  var panel = el("div", "wa-widget-panel");
  var header = el("div", "wa-widget-header", "Customer Support");
  var body = el("div", "wa-widget-body");
  var inputWrap = el("div", "wa-widget-input-wrap");
  var input = el("input", "wa-widget-input");
  var send = el("button", "wa-widget-send", "Send");

  input.type = "text";
  input.placeholder = "Type your message...";

  panel.appendChild(header);
  panel.appendChild(body);
  inputWrap.appendChild(input);
  inputWrap.appendChild(send);
  panel.appendChild(inputWrap);

  document.body.appendChild(button);
  document.body.appendChild(panel);

  /** Scroll chat body to the latest message. */
  function scrollToBottom() {
    body.scrollTop = body.scrollHeight;
  }

  /** Render one chat bubble into the panel body. */
  function addMessage(role, text) {
    var wrap = el("div", "wa-widget-msg-wrap " + (role === "user" ? "user" : "bot"));
    var bubble = el("div", "wa-widget-msg", text);
    wrap.appendChild(bubble);
    body.appendChild(wrap);
    scrollToBottom();
  }

  /** Show typing indicator and return its node. */
  function showTyping() {
    var wrap = el("div", "wa-widget-msg-wrap bot");
    var bubble = el("div", "wa-widget-msg wa-widget-typing");
    bubble.innerHTML = '<span></span><span></span><span></span>';
    wrap.appendChild(bubble);
    body.appendChild(wrap);
    scrollToBottom();
    return wrap;
  }

  /** Toggle panel visibility. */
  function togglePanel() {
    isOpen = !isOpen;
    panel.style.display = isOpen ? "flex" : "none";
  }

  /** Send user text to backend and render response. */
  async function sendMessage() {
    var text = input.value.trim();
    if (!text) return;

    conversation.push({ role: "user", text: text });
    addMessage("user", text);
    input.value = "";

    var typingNode = showTyping();
    try {
      var response = await fetch(apiUrl.replace(/\/$/, "") + "/chat/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, message: text }),
      });
      var data = await response.json();
      var reply = data.reply || "Sorry, I could not process that right now.";
      conversation.push({ role: "bot", text: reply });
      typingNode.remove();
      addMessage("bot", reply);
    } catch (error) {
      typingNode.remove();
      addMessage("bot", "Network error. Please try again.");
    }
  }

  button.addEventListener("click", togglePanel);
  send.addEventListener("click", sendMessage);
  input.addEventListener("keydown", function (event) {
    if (event.key === "Enter") sendMessage();
  });
})();
