(function () {
    // ---------- Create Floating Button ----------
    const btn = document.createElement("div");
    btn.id = "gh-chat-button";
    btn.innerHTML = "💬";
    Object.assign(btn.style, {
        position: "fixed",
        bottom: "25px",
        right: "25px",
        width: "60px",
        height: "60px",
        borderRadius: "50%",
        background: "#667eea",
        color: "white",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        cursor: "pointer",
        fontSize: "30px",
        boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
        zIndex: 999999,
        userSelect: "none",
    });
    document.body.appendChild(btn);

    // ---------- Create Chat Window ----------
    const win = document.createElement("div");
    win.id = "gh-chat-window";
    Object.assign(win.style, {
        position: "fixed",
        bottom: "100px",
        right: "50px",
        width: "420px",
        height: "550px",
        background: "white",
        borderRadius: "14px",
        boxShadow: "0 6px 20px rgba(0,0,0,.15)",
        zIndex: 999998,
        overflow: "hidden",
        display: "none",
        resize: "both",
    });

    win.innerHTML = `
        <iframe src="/chatbot.html"
            style="width:100%;height:100%;border:none;">
        </iframe>
    `;
    document.body.appendChild(win);

    // ---------- Show / Hide ----------
    btn.addEventListener("click", () => {
        win.style.display = win.style.display === "none" ? "block" : "none";
    });

    // ---------- Make Draggable ----------
    let isDragging = false;
    let offsetX = 0, offsetY = 0;

    win.addEventListener("mousedown", (e) => {
        isDragging = true;
        offsetX = e.clientX - win.offsetLeft;
        offsetY = e.clientY - win.offsetTop;
    });

    document.addEventListener("mouseup", () => (isDragging = false));

    document.addEventListener("mousemove", (e) => {
        if (isDragging) {
            win.style.left = e.clientX - offsetX + "px";
            win.style.top = e.clientY - offsetY + "px";
            win.style.right = "auto";
            win.style.bottom = "auto";
        }
    });
})();
