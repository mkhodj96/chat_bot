let currentConversation = [];
let loadedConversationId = null;
const chatbox = document.getElementById('chatbox');
const input = document.getElementById('input');
const send = document.getElementById('send');
const verlaufBtn = document.getElementById('sidebar-verlauf');
const historyBox = document.getElementById('sidebar-history-box');
const profileBtn = document.getElementById('sidebar-profile');
const newChatBtn = document.getElementById('sidebar-newchat');
let verlaufOpen = false;
let autoScroll = true;

function isAtBottom() {
    return (window.innerHeight + window.scrollY) >= (document.body.scrollHeight - 40);
}
window.addEventListener('scroll', () => {
    autoScroll = isAtBottom();
});
function scrollToBottom() {
    window.scrollTo({top: document.body.scrollHeight, behavior: 'auto'});
}

function enableAutoScroll() {
    autoScroll = true;
    scrollToBottom();
}

newChatBtn.addEventListener('click', async () => {
    const hasUserMessage = currentConversation.some(msg => msg.role === "user");
    if (hasUserMessage && loadedConversationId === null) {
        await fetch('/save_conversation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(currentConversation)
        });
        await updateChatHistory();
    }
    currentConversation = [];
    resetChatbox();
    enableAutoScroll();
    showPopup('🆕 New chat created');
});

profileBtn.addEventListener('click', () => {
    showPopup('Profile feature coming soon!');
});

verlaufBtn.addEventListener('click', function () {
    verlaufOpen = !verlaufOpen;
    if (verlaufOpen) {
        historyBox.classList.add('open');
    } else {
        historyBox.classList.remove('open');
    }
});

document.getElementById('chat-history').addEventListener('click', function(e) {
    const btn = e.target.closest('.chat-history-btn');
    if (btn) {
        verlaufOpen = false;
        historyBox.classList.remove('open');
    }
});

marked.setOptions({
    highlight: function (code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
    },
    langPrefix: 'hljs language-',
    gfm: true,
    breaks: true
});

function addMessage(text, isUser, isFromHistory = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'} animate-in`;

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';

    if (isUser) {
        messageContent.textContent = text;
    } else {
        messageContent.classList.add('markdown-content');
    }
    messageDiv.appendChild(messageContent);
    chatbox.appendChild(messageDiv);

    if (isUser || isFromHistory) {
        if (!isUser) {
            const processed = preprocessMarkdown(text);
            const html = marked.parse(processed);
            messageContent.innerHTML = html;
            messageContent.querySelectorAll('pre code').forEach(block => hljs.highlightElement(block));
        }
        setTimeout(() => messageDiv.classList.remove('animate-in'), 400);
        currentConversation.push({
            role: isUser ? "user" : "assistant",
            content: text
        });
        enableAutoScroll();
        return;
    }

    const processed = preprocessMarkdown(text);
    const html = marked.parse(processed);
    let i = 0;
    function typeNext() {
        if (i <= processed.length) {
            let partialMarkdown = processed.slice(0, i);
            let partialHtml = marked.parse(partialMarkdown);
            messageContent.innerHTML = partialHtml;
            messageContent.querySelectorAll('pre code').forEach(block => hljs.highlightElement(block));
            if (autoScroll) scrollToBottom();
            i++;
            setTimeout(typeNext, 14);
        } else {
            messageContent.innerHTML = html;
            messageContent.querySelectorAll('pre code').forEach(block => hljs.highlightElement(block));
            if (autoScroll) scrollToBottom();
        }
    }
    typeNext();

    setTimeout(() => messageDiv.classList.remove('animate-in'), 400);
    currentConversation.push({ role: "assistant", content: text });
}

function preprocessMarkdown(text) {
    return text.replace(/^"|"$/g, '')
        .replace(/\\n/g, '\n')
        .replace(/\\t/g, '\t')
        .replace(/\\r/g, '\r');
}

async function sendMessage() {
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, true);
    input.value = '';
    loadedConversationId = null;

    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'message bot-message';
    typingIndicator.innerHTML = `<div class="message-content">
        <img src="./static/loading.gif" alt="Loading..." style="height:32px;"/>
    </div>`;
    chatbox.appendChild(typingIndicator);
    enableAutoScroll();

    try {
        const response = await fetch('/chatbot?message=' + encodeURIComponent(message));
        const reply = await response.text();
        chatbox.removeChild(typingIndicator);
        addMessage(reply, false);
    } catch (error) {
        chatbox.removeChild(typingIndicator);
        addMessage(' The server is not reachable.', false);
        console.error('Error:', error);
    }
    toggleSendBtn();
}

input.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        sendMessage();
    }
});
send.addEventListener('click', sendMessage);

async function updateChatHistory() {
    const response = await fetch('/conversations');
    const data = await response.json();
    const historyEl = document.getElementById('chat-history');
    historyEl.innerHTML = '';

    data.conversations.reverse().forEach(id => {
        const li = document.createElement('li');
        li.className = 'chat-history-entry';

        const btn = document.createElement('button');
        btn.textContent = `Chat ${id.slice(0, 8)}`;
        btn.className = 'chat-history-btn';
        btn.onclick = () => loadConversation(id);

        const delBtn = document.createElement('button');
        delBtn.textContent = "❌";
        delBtn.className = 'delete-btn';
        delBtn.setAttribute('aria-label', 'Delete conversation');
        delBtn.onclick = async () => {
            if (confirm("Delete this conversation?")) {
                await fetch(`/conversations/${id}`, { method: 'DELETE' });
                await updateChatHistory();
                resetChatbox();
                showPopup('🗑️ Conversation deleted');
            }
        };

        li.appendChild(btn);
        li.appendChild(delBtn);
        historyEl.appendChild(li);
    });
}

async function loadConversation(id) {
    const response = await fetch(`/conversations/${id}`);
    const data = await response.json();
    chatbox.innerHTML = '';
    loadedConversationId = id;
    currentConversation = data.messages || [];
    currentConversation.forEach(msg => {
        addMessage(msg.content, msg.role === "user", true);
    });
}

function showPopup(message) {
    const popup = document.getElementById('popup');
    popup.textContent = message;
    popup.style.display = 'block';
    popup.style.opacity = 1;
    setTimeout(() => {
        popup.style.opacity = 0;
        setTimeout(() => {
            popup.style.display = 'none';
        }, 300);
    }, 2000);
}

function resetChatbox() {
    chatbox.innerHTML = '';
    addMessage('Hello! How can i help you today?', false);
    enableAutoScroll();
}

window.addEventListener('DOMContentLoaded', async () => {
    resetChatbox();
    await updateChatHistory();
});

const infoBtn = document.getElementById('sidebar-info');
const infoOverlay = document.getElementById('info-overlay');
const infoClose = document.getElementById('info-close');
const infoText = document.getElementById('info-text');

infoBtn.addEventListener('click', () => {
    infoText.innerHTML = `
        The IDEA BOT is a digital helper<br>
        for customers. It provides quick and easy<br>
        access to information about our products,<br>
        such as paintings, crafts, photography, and sculptures.<br><br>
        You can ask the assistant questions at any time,<br>
        get detailed information, or search for specific products.<br>
        This way, the assistant helps you find the right artwork<br>
        and get support for all your questions about our shop.
    `;
    infoOverlay.classList.add('open');
});

infoClose.addEventListener('click', () => {
    infoOverlay.classList.remove('open');
});

infoOverlay.addEventListener('click', (e) => {
    if (e.target === infoOverlay) infoOverlay.classList.remove('open');
});

const sendBtn = document.getElementById('send');
const inputField = document.getElementById('input');

function toggleSendBtn() {
    if (inputField.value.trim() === "") {
        sendBtn.disabled = true;
    } else {
        sendBtn.disabled = false;
    }
}

toggleSendBtn();
inputField.addEventListener('input', toggleSendBtn);
