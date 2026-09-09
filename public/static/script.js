const messagesEl = document.getElementById("messages");
const chatForm = document.getElementById("chat-form");
const questionInput = document.getElementById("question");
const sendBtn = document.getElementById("send-btn");

const ingestBtn = document.getElementById("ingest-btn");
const clearBtn = document.getElementById("clear-btn");

const topKInput = document.getElementById("top-k");
const topKValue = document.getElementById("top-k-value");

const indexStatus = document.getElementById("index-status");
const ingestMessage = document.getElementById("ingest-message");

const hero = document.getElementById("hero");

let isBusy = false;


/* =========================================================
   TOP-K SLIDER
========================================================= */

topKInput.addEventListener("input", () => {
    topKValue.textContent = topKInput.value;
});


/* =========================================================
   SAMPLE QUESTIONS
========================================================= */

document.querySelectorAll(".sample-question").forEach(button => {

    button.addEventListener("click", () => {

        const question = button.textContent.trim();

        questionInput.value = question;

        questionInput.focus();

        chatForm.dispatchEvent(
            new Event("submit", {
                bubbles: true,
                cancelable: true
            })
        );
    });

});


/* =========================================================
   ADD MESSAGE
========================================================= */

function addMessage(
    role,
    content,
    {
        sources = [],
        relevant = true,
        typing = false,
        error = false
    } = {}
) {

    // Remove hero once conversation starts
    if (hero) {
        hero.style.display = "none";
    }

    const wrapper = document.createElement("div");

    wrapper.className =
        `message ${role}`;

    if (typing) {
        wrapper.classList.add("typing");
    }


    /* Avatar */

    const avatar = document.createElement("div");

    avatar.className = "avatar";

    avatar.textContent =
        role === "user"
            ? "👤"
            : "🤖";


    /* Column */

    const column = document.createElement("div");

    column.className = "message-column";


    /* Bubble */

    const bubble = document.createElement("div");

    bubble.className = "bubble";


    if (
        role === "assistant" &&
        (!relevant || error)
    ) {
        bubble.classList.add(
            error
                ? "error"
                : "off-topic"
        );
    }

    bubble.textContent = content;


    column.appendChild(bubble);


    /* Sources */

    if (
        role === "assistant" &&
        !typing &&
        sources &&
        sources.length > 0
    ) {

        column.appendChild(
            buildSources(sources)
        );
    }


    wrapper.appendChild(avatar);

    wrapper.appendChild(column);

    messagesEl.appendChild(wrapper);

    scrollToBottom();


    return {
        wrapper,
        column,
        bubble
    };
}


/* =========================================================
   BUILD SOURCES
========================================================= */

function buildSources(sources) {

    const details =
        document.createElement("details");

    details.className = "sources";


    const summary =
        document.createElement("summary");

    summary.textContent =
        "📄 View sources";

    details.appendChild(summary);


    const list =
        document.createElement("div");

    list.className = "sources-list";


    sources.forEach((source, index) => {

        const row =
            document.createElement("div");

        row.className = "source-row";


        const idx =
            document.createElement("span");

        idx.className = "source-idx";

        idx.textContent = index + 1;


        const name =
            document.createElement("span");

        name.className = "source-name";

        const code =
            document.createElement("code");

        code.textContent =
            source.source ||
            source.id ||
            "unknown";

        name.textContent = "📎 ";

        name.appendChild(code);


        const score =
            document.createElement("span");

        score.className = "source-score";

        const numericScore =
            Number(source.score);

        score.textContent =
            Number.isFinite(numericScore)
                ? numericScore.toFixed(3)
                : "—";


        row.appendChild(idx);

        row.appendChild(name);

        row.appendChild(score);

        list.appendChild(row);

    });


    details.appendChild(list);

    return details;
}


/* =========================================================
   ELAPSED TIME
========================================================= */

function addElapsedCaption(column, seconds) {

    const elapsed =
        document.createElement("div");

    elapsed.className = "elapsed";

    elapsed.textContent =
        `⏱️ answered in ${seconds.toFixed(1)}s`;

    column.appendChild(elapsed);

    scrollToBottom();
}


/* =========================================================
   SCROLL
========================================================= */

function scrollToBottom() {

    requestAnimationFrame(() => {

        messagesEl.scrollTop =
            messagesEl.scrollHeight;

    });
}


/* =========================================================
   BUSY STATE
========================================================= */

function setBusy(busy) {

    isBusy = busy;

    sendBtn.disabled = busy;

    ingestBtn.disabled = busy;

    questionInput.disabled = busy;

    document
        .querySelectorAll(".sample-question")
        .forEach(button => {
            button.disabled = busy;
        });
}


/* =========================================================
   CHAT
========================================================= */

chatForm.addEventListener(
    "submit",
    async event => {

        event.preventDefault();

        if (isBusy) {
            return;
        }


        const question =
            questionInput.value.trim();


        if (!question) {
            return;
        }


        questionInput.value = "";


        /* User message */

        addMessage(
            "user",
            question
        );


        /* Typing indicator */

        const typing =
            addMessage(
                "assistant",
                "🔍 Retrieving context and generating answer…",
                {
                    typing: true
                }
            );


        const startedAt =
            Date.now();


        setBusy(true);


        try {

            const url =
                `/query?q=${encodeURIComponent(question)}&top_k=${topKInput.value}`;


            const response =
                await fetch(url);


            if (!response.ok) {

                const error =
                    await response
                        .json()
                        .catch(() => ({}));


                throw new Error(
                    error.detail ||
                    `Request failed (${response.status})`
                );
            }


            const result =
                await response.json();


            const seconds =
                (Date.now() - startedAt) / 1000;


            /* Remove typing */

            typing.wrapper.remove();


            /* Assistant answer */

            const assistant =
                addMessage(
                    "assistant",
                    result.answer || "No answer was returned.",
                    {
                        sources: result.sources || [],
                        relevant:
                            result.relevant !== false
                    }
                );


            addElapsedCaption(
                assistant.column,
                seconds
            );

        }

        catch (error) {

            typing.wrapper.remove();


            addMessage(
                "assistant",
                `⚠️ Query failed — ${error.message}`,
                {
                    relevant: false,
                    error: true
                }
            );
        }

        finally {

            setBusy(false);

            questionInput.focus();
        }

    }
);


/* =========================================================
   INGEST / REBUILD INDEX
========================================================= */

ingestBtn.addEventListener(
    "click",
    async () => {

        if (isBusy) {
            return;
        }


        ingestBtn.disabled = true;

        ingestMessage.className =
            "ingest-message";

        ingestMessage.textContent =
            "Extract → chunk → embed → upsert…";

        ingestMessage.classList.remove(
            "hidden"
        );


        try {

            const response =
                await fetch(
                    "/ingest",
                    {
                        method: "POST"
                    }
                );


            if (!response.ok) {

                const error =
                    await response
                        .json()
                        .catch(() => ({}));


                throw new Error(
                    error.detail ||
                    `Request failed (${response.status})`
                );
            }


            const result =
                await response.json();


            const uploaded =
                Number(result.uploaded || 0);


            const characters =
                Number(result.characters || 0);


            /* Update status */

            indexStatus.className =
                "pill pill-ok";


            indexStatus.textContent =
                `🟢 Index ready · ${uploaded} chunks`;


            ingestMessage.className =
                "ingest-message success";


            ingestMessage.textContent =
                `Uploaded ${uploaded.toLocaleString()} chunks from ${characters.toLocaleString()} characters.`;


        }

        catch (error) {

            ingestMessage.className =
                "ingest-message error";


            ingestMessage.textContent =
                `🚨 Ingestion failed: ${error.message}`;
        }

        finally {

            ingestBtn.disabled = false;
        }

    }
);


/* =========================================================
   CLEAR CONVERSATION
========================================================= */

clearBtn.addEventListener(
    "click",
    () => {

        messagesEl.innerHTML = "";

        if (hero) {
            hero.style.display = "";
        }

        ingestMessage.className =
            "ingest-message hidden";

        questionInput.value = "";

        questionInput.focus();
    }
);


/* =========================================================
   ENTER KEY
========================================================= */

questionInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            chatForm.dispatchEvent(
                new Event("submit", {
                    bubbles: true,
                    cancelable: true
                })
            );
        }
    }
);