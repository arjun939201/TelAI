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


/* LANGUAGE FILE ELEMENTS */

const languageFiles =
    document.getElementById("languageFiles");

const uploadLanguageFile =
    document.getElementById(
        "uploadLanguageFile"
    );

const languageFileInput =
    document.getElementById(
        "languageFileInput"
    );


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


    /* USER MESSAGE */

    addMessage(
        "user",
        message
    );


    input.value = "";

    autoResizeTextarea();


    sendButton.disabled = true;


    /* THINKING */

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
                /* Ignore JSON parsing failure */
            }


            throw new Error(
                errorMessage
            );
        }


        const data =
            await response.json();


        if (!data.reply) {

            throw new Error(
                "AI నుంచి సమాధానం రాలేదు."
            );
        }


        /* SHOW AI RESPONSE */

        thinkingMessage.textContent =
            data.reply;


        /* SAVE HISTORY */

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
            `క్షమించండి. సమాధానం ఇవ్వడంలో సమస్య వచ్చింది.\n\n${error.message}`;


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

form.addEventListener(
    "submit",
    function (event) {

        event.preventDefault();

        sendMessage();

    }
);


/* =========================================
   ENTER TO SEND
========================================= */

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


/* =========================================
   AUTO RESIZE TEXTAREA
========================================= */

function autoResizeTextarea() {

    input.style.height = "auto";

    input.style.height =
        Math.min(
            input.scrollHeight,
            180
        ) + "px";
}


input.addEventListener(
    "input",
    autoResizeTextarea
);


/* =========================================
   NEW CHAT
========================================= */

function startNewChat() {

    conversation = [];


    chatContainer.innerHTML = `

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


    attachSuggestionEvents();


    input.value = "";

    autoResizeTextarea();

    input.focus();
}


/* =========================================
   NEW CHAT BUTTONS
========================================= */

clearButton.addEventListener(
    "click",
    startNewChat
);


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


attachSuggestionEvents();


/* =========================================
   LANGUAGE FILES
========================================= */

async function loadLanguageFiles() {

    if (!languageFiles) {
        return;
    }


    languageFiles.innerHTML = `

        <div class="language-loading">
            దస్తాలు తెస్తోంది...
        </div>

    `;


    try {

        const response =
            await fetch(
                "/api/language/files"
            );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );

        }


        const data =
            await response.json();


        languageFiles.innerHTML = "";


        if (
            !data.files ||
            data.files.length === 0
        ) {

            languageFiles.innerHTML = `

                <div class="language-empty">
                    దస్తాలు లేవు
                </div>

            `;

            return;
        }


        data.files.forEach(
            filename => {

                const row =
                    document.createElement(
                        "button"
                    );


                row.type = "button";


                row.className =
                    "language-file";


                row.innerHTML = `

                    <span class="file-icon">
                        📄
                    </span>

                    <span class="file-name">
                        ${escapeHtml(filename)}
                    </span>

                `;


                row.addEventListener(
                    "click",
                    () =>
                        openLanguageFile(
                            filename
                        )
                );


                languageFiles.appendChild(
                    row
                );

            }
        );


    } catch (error) {

        console.error(
            "Language files error:",
            error
        );


        languageFiles.innerHTML = `

            <div class="language-error">
                దస్తాలు తెచ్చుటలో సమస్య
            </div>

        `;

    }
}


/* =========================================
   OPEN LANGUAGE FILE
========================================= */

async function openLanguageFile(
    filename
) {

    try {

        const response =
            await fetch(
                `/api/language/content/${encodeURIComponent(filename)}`
            );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );

        }


        const content =
            await response.text();


        addMessage(
            "assistant",
            `📄 ${filename}\n\n${content}`
        );


    } catch (error) {

        console.error(
            "File open error:",
            error
        );


        addMessage(
            "assistant",
            `దస్తాను తెరవలేకపోయాను: ${error.message}`
        );

    }
}


/* =========================================
   UPLOAD LANGUAGE FILE
========================================= */

if (uploadLanguageFile) {

    uploadLanguageFile.addEventListener(
        "click",
        function () {

            languageFileInput.click();

        }
    );

}


if (languageFileInput) {

    languageFileInput.addEventListener(
        "change",
        uploadLanguageFileToServer
    );

}


async function uploadLanguageFileToServer() {

    const file =
        languageFileInput.files[0];


    if (!file) {
        return;
    }


    const allowedTypes = [
        ".txt",
        ".md",
        ".json",
        ".csv"
    ];


    const filename =
        file.name.toLowerCase();


    const valid =
        allowedTypes.some(
            extension =>
                filename.endsWith(extension)
        );


    if (!valid) {

        addMessage(
            "assistant",
            "ఈ దస్తా రకం అనుమతించబడలేదు. .txt, .md, .json లేదా .csv దస్తాను ఎక్కించు."
        );


        languageFileInput.value = "";

        return;
    }


    const formData =
        new FormData();


    formData.append(
        "file",
        file
    );


    if (uploadLanguageFile) {

        uploadLanguageFile.disabled =
            true;

    }


    try {

        const response =
            await fetch(
                "/api/language/upload",
                {
                    method: "POST",
                    body: formData
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                `HTTP ${response.status}`
            );

        }


        await loadLanguageFiles();


        addMessage(
            "assistant",
            `✓ ${file.name} భాషా దస్తాలలోకి ఎక్కించబడింది.`
        );


    } catch (error) {

        console.error(
            "Upload error:",
            error
        );


        addMessage(
            "assistant",
            `దస్తాను ఎక్కించలేకపోయాను: ${error.message}`
        );


    } finally {

        if (uploadLanguageFile) {

            uploadLanguageFile.disabled =
                false;

        }


        languageFileInput.value = "";

    }
}


/* =========================================
   HTML ESCAPE
========================================= */

function escapeHtml(value) {

    const div =
        document.createElement("div");


    div.textContent = value;


    return div.innerHTML;
}


/* =========================================
   INITIALIZE
========================================= */

loadLanguageFiles();

input.focus();

autoResizeTextarea();
