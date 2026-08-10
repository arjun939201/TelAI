const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const chatContainer = document.getElementById("chatContainer");
const sendButton = document.getElementById("sendButton");
const clearButton = document.getElementById("clearButton");
const mobileNewChat = document.getElementById("mobileNewChat");

let conversation = [];


/* =========================================
   ADD MESSAGE
========================================= */

function addMessage(role, content) {

    const welcome = document.querySelector(".welcome");

    if (welcome) {
        welcome.remove();
    }

    const message = document.createElement("div");

    message.className = `message ${role}`;

    const contentElement =
        document.createElement("div");

    contentElement.className =
        "message-content";

    contentElement.textContent = content;

    message.appendChild(contentElement);

    chatContainer.appendChild(message);

    chatContainer.scrollTop =
        chatContainer.scrollHeight;

    return contentElement;
}


/* =========================================
   SEND MESSAGE
========================================= */

async function sendMessage() {

    const message =
        input.value.trim();

    if (
        !message ||
        sendButton.disabled
    ) {
        return;
    }

    /* Show user message */

    addMessage(
        "user",
        message
    );

    input.value = "";

    autoResizeTextarea();

    sendButton.disabled = true;


    /* Show thinking */

    const thinking =
        addMessage(
            "assistant",
            "ఆలోచిస్తున్నాను..."
        );


    try {

        const response =
            await fetch(
                "/api/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message: message,
                        history: conversation
                    })
                }
            );


        /* Read response */

        let data = {};

        try {

            data =
                await response.json();

        } catch (_) {

            data = {};

        }


        /* Backend error */

        if (!response.ok) {

            throw new Error(
                data.detail ||
                `HTTP ${response.status}`
            );
        }


        /* Missing reply */

        if (!data.reply) {

            throw new Error(
                "AI నుంచి సమాధానం రాలేదు."
            );
        }


        /* Show AI response */

        thinking.textContent =
            data.reply;


        /* Save conversation */

        conversation.push({
            role: "user",
            content: message
        });

        conversation.push({
            role: "assistant",
            content: data.reply
        });


    } catch (error) {

        console.error(
            "TelAI error:",
            error
        );


        /*
         * IMPORTANT:
         * Show the real backend error.
         * Do not hide it behind a generic message.
         */

        thinking.textContent =
            `లోపం: ${error.message}`;


    } finally {

        sendButton.disabled =
            false;

        input.focus();

        chatContainer.scrollTop =
            chatContainer.scrollHeight;
    }
}


/* =========================================
   FORM SUBMIT
========================================= */

if (form) {

    form.addEventListener(
        "submit",
        function (event) {

            event.preventDefault();

            sendMessage();

        }
    );
}


/* =========================================
   ENTER TO SEND
========================================= */

if (input) {

    input.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendMessage();

            }

        }
    );
}


/* =========================================
   AUTO RESIZE TEXTAREA
========================================= */

function autoResizeTextarea() {

    if (!input) {
        return;
    }

    input.style.height =
        "auto";

    input.style.height =
        Math.min(
            input.scrollHeight,
            180
        ) + "px";
}


if (input) {

    input.addEventListener(
        "input",
        autoResizeTextarea
    );
}


/* =========================================
   WELCOME SCREEN
========================================= */

function getWelcomeHTML() {

    return `

        <div class="welcome">

            <div class="welcome-icon">
                T
            </div>

            <h1>
                ఏమి తెలుసుకొనగోరుతున్నావు?
            </h1>

            <p>
                తెలుగులో ఏదైనా అడుగు.
                మేలిమి తెలుగు పదాలు,
                వ్యాకరణం, పదనిర్మాణం
                లేదా ఏదైనా విషయాన్ని అడవచ్చు.
            </p>

            <div class="suggestions">

                <button
                    class="suggestion"
                    data-message="మేలిమి తెలుగు అంటే ఏమిటి?"
                    type="button"
                >

                    <span>
                        ◈
                    </span>

                    మేలిమి తెలుగు అంటే ఏమిటి?

                </button>


                <button
                    class="suggestion"
                    data-message="హత్తరం అంటే ఏమిటి?"
                    type="button"
                >

                    <span>
                        ◇
                    </span>

                    పదం అర్థం అడుగు

                </button>


                <button
                    class="suggestion"
                    data-message="ఒక కొత్త మేలిమి తెలుగు పదాన్ని సూచించు."
                    type="button"
                >

                    <span>
                        ✦
                    </span>

                    కొత్త పదం సూచించు

                </button>


                <button
                    class="suggestion"
                    data-message="మేలిమి తెలుగు పదనిర్మాణ నియమాలను వివరించు."
                    type="button"
                >

                    <span>
                        ⌘
                    </span>

                    పదనిర్మాణం నేర్చుకో

                </button>

            </div>

        </div>

    `;
}


/* =========================================
   NEW CHAT
========================================= */

function startNewChat() {

    conversation = [];

    chatContainer.innerHTML =
        getWelcomeHTML();

    attachSuggestionEvents();

    input.value = "";

    autoResizeTextarea();

    input.focus();
}


/* =========================================
   NEW CHAT BUTTON
========================================= */

if (clearButton) {

    clearButton.addEventListener(
        "click",
        startNewChat
    );
}


if (mobileNewChat) {

    mobileNewChat.addEventListener(
        "click",
        startNewChat
    );
}


/* =========================================
   SUGGESTIONS
========================================= */

function attachSuggestionEvents() {

    document
        .querySelectorAll(".suggestion")
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    function () {

                        input.value =
                            this.dataset.message;

                        autoResizeTextarea();

                        input.focus();

                    }
                );

            }
        );
}


/* =========================================
   INITIALIZE
========================================= */

attachSuggestionEvents();

autoResizeTextarea();
