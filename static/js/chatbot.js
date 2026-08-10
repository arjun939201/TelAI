/* =========================================
   ELEMENTS
========================================= */

const form =
    document.getElementById("chatForm");

const input =
    document.getElementById("messageInput");

const chatContainer =
    document.getElementById("chatContainer");

const sendButton =
    document.getElementById("sendButton");

const clearButton =
    document.getElementById("clearButton");

const mobileNewChat =
    document.getElementById("mobileNewChat");


/* =========================================
   CONVERSATION
========================================= */

let conversation = [];


/* =========================================
   ADD MESSAGE
========================================= */

function addMessage(role, content) {

    const welcome =
        document.querySelector(".welcome");

    if (welcome) {
        welcome.remove();
    }


    const message =
        document.createElement("div");

    message.className =
        `message ${role}`;


    const contentElement =
        document.createElement("div");

    contentElement.className =
        "message-content";


    contentElement.textContent =
        content;


    message.appendChild(
        contentElement
    );


    chatContainer.appendChild(
        message
    );


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

    const thinkingMessage =
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


        /* Check response */

        if (!response.ok) {

            let errorMessage =
                `HTTP ${response.status}`;


            try {

                const errorData =
                    await response.json();


                if (errorData.detail) {

                    errorMessage =
                        errorData.detail;

                }

            } catch (_) {
                /* Ignore invalid JSON */
            }


            throw new Error(
                errorMessage
            );
        }


        /* Read response */

        const data =
            await response.json();


        if (!data.reply) {

            throw new Error(
                "AI నుంచి సమాధానం రాలేదు."
            );
        }


        /* Replace thinking message */

        thinkingMessage.textContent =
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
            "Chat error:",
            error
        );


        thinkingMessage.textContent =
            `క్షమించండి. సమాధానం ఇవ్వడంలో సమస్య వచ్చింది.

${error.message}`;


    } finally {

        sendButton.disabled = false;

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
                మేలిమి తెలుగు పదాలు, పదనిర్మాణం,
                వ్యాకరణం లేదా ఏదైనా విషయాన్ని అడుగు.
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
                    data-message="హత్తరం అనే పదానికి అర్థం ఏమిటి?"
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
   NEW CHAT BUTTONS
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
   SUGGESTION BUTTONS
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
