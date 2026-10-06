// ==========================================
// RoboLang Frontend
// ==========================================

// ==========================================
// BACKEND CONFIGURATION
// ==========================================

const API_URL = "http://127.0.0.1:8000";

// ==========================================
// DOM ELEMENTS
// ==========================================

const codeEditor =
    document.getElementById("codeEditor");

const lineNumbers =
    document.getElementById("lineNumbers");

const consoleOutput =
    document.getElementById("console");

const robotElement =
    document.getElementById("robot");

const robotX =
    document.getElementById("robotX");

const robotY =
    document.getElementById("robotY");

const robotDirection =
    document.getElementById("robotDirection");

const robotAngle =
    document.getElementById("robotAngle");

const simulationCanvas =
    document.getElementById("simulationCanvas");

const world =
    document.querySelector(".world");

// ==========================================
// LINE NUMBERS
// ==========================================

function updateLineNumbers() {

    if (!codeEditor || !lineNumbers) {
        return;
    }

    const lines =
        codeEditor.value.split("\n");

    lineNumbers.innerHTML = "";

    lines.forEach((_, index) => {

        const line =
            document.createElement("div");

        line.textContent =
            index + 1;

        lineNumbers.appendChild(line);

    });

}

// ==========================================
// EDITOR EVENTS
// ==========================================

if (codeEditor) {

    codeEditor.addEventListener(
        "input",
        updateLineNumbers
    );

    codeEditor.addEventListener(
        "scroll",
        () => {

            if (lineNumbers) {

                lineNumbers.scrollTop =
                    codeEditor.scrollTop;

            }

        }
    );

    // Ctrl + Enter → Run
    codeEditor.addEventListener(
        "keydown",
        function (event) {

            if (
                event.ctrlKey &&
                event.key === "Enter"
            ) {

                event.preventDefault();

                runProgram();

            }

        }
    );

}

// ==========================================
// INITIALIZE
// ==========================================

updateLineNumbers();

// ==========================================
// BACKEND CONNECTION
// ==========================================

async function checkBackend() {

    try {

        const response =
            await fetch(
                `${API_URL}/compiler/status`
            );

        if (!response.ok) {

            throw new Error(
                "Backend unavailable"
            );

        }

        setConnectionStatus(true);

    } catch (error) {

        console.error(
            "Backend connection error:",
            error
        );

        setConnectionStatus(false);

    }

}

// ==========================================
// CONNECTION STATUS
// ==========================================

function setConnectionStatus(connected) {

    const status =
        document.querySelector(
            ".connection"
        );

    if (!status) {
        return;
    }

    if (connected) {

        status.textContent =
            "● Backend Connected";

        status.classList.remove(
            "offline"
        );

    } else {

        status.textContent =
            "● Backend Offline";

        status.classList.add(
            "offline"
        );

    }

}

// ==========================================
// RUN PROGRAM
// ==========================================

async function runProgram() {

    if (!codeEditor) {
        return;
    }

    const source =
        codeEditor.value;

    // ======================================
    // EMPTY PROGRAM
    // ======================================

    if (!source.trim()) {

        showError({

            stage: "compiler",

            errors: [
                {
                    line: 1,
                    message:
                        "Program cannot be empty.",
                    type: "compiler"
                }
            ]

        });

        return;

    }

    // ======================================
    // CLEAR OLD OUTPUT
    // ======================================

    clearCompilerOutput();

    setConsole(
        "Compiling RoboLang program..."
    );

    let response;
    let data;

    // ======================================
    // SEND TO BACKEND
    // ======================================

    try {

        response =
            await fetch(
                `${API_URL}/execute`,
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        source: source
                    })

                }
            );

    } catch (error) {

        console.error(
            "Backend connection error:",
            error
        );

        showError({

            stage: "connection",

            errors: [
                {
                    line: 1,
                    message:
                        "Unable to connect to RoboLang backend.",
                    type: "connection"
                }
            ]

        });

        return;

    }

    // ======================================
    // READ RESPONSE
    // ======================================

    try {

        data =
            await response.json();

    } catch (error) {

        console.error(
            "Invalid backend response:",
            error
        );

        showError({

            stage: "backend",

            errors: [
                {
                    line: 1,
                    message:
                        "Backend returned an invalid response.",
                    type: "backend"
                }
            ]

        });

        return;

    }

    // ======================================
    // COMPILATION FAILED
    // ======================================

    if (!data.success) {

        showError(data);

        return;

    }

    // ======================================
    // COMPILATION SUCCESSFUL
    // ======================================

    try {

        showSuccess(data);

        if (data.robot) {

            // Update final state immediately
            updateRobotInfo(
                data.robot
            );

            // Animate robot along path
            if (
                data.robot.path &&
                data.robot.path.length > 0
            ) {

                await animateRobotPath(
                    data.robot.path,
                    data.robot.direction
                );

            }

        }

    } catch (error) {

        console.error(
            "Simulator error:",
            error
        );

        setConsole(

            "✓ Compilation successful\n\n" +

            "However, the simulator could not " +
            "display the robot.\n\n" +

            `Simulator Error: ${error.message}`

        );

    }

}

// ==========================================
// SHOW ERROR
// ==========================================

function showError(data) {

    const stage =
        formatStageName(
            data.stage || "compiler"
        );

    let output = "";

    output +=
        "❌ COMPILATION FAILED\n";

    output +=
        "==============================\n\n";

    output +=
        `Stage: ${stage}\n\n`;

    // ======================================
    // Errors
    // ======================================

    if (
        data.errors &&
        data.errors.length > 0
    ) {

        data.errors.forEach(
            error => {

                output +=
                    `❌ Line ${error.line}: ` +
                    `${error.message}\n\n`;

            }
        );

    } else {

        output +=
            `❌ ${data.error || "Unknown error"}\n`;

    }

    output +=
        "🛑 Program execution stopped.";

    setConsole(output);

    // ======================================
    // Highlight Error Line
    // ======================================

    if (
        data.errors &&
        data.errors.length > 0
    ) {

        highlightErrorLine(
            data.errors[0].line
        );

    }

    // ======================================
    // Pipeline
    // ======================================

    updatePipeline(
        data.stage,
        false
    );

    // ======================================
    // IMPORTANT
    //
    // DO NOT RESET ROBOT HERE
    //
    // A compilation error should not
    // move the robot back to the center.
    // ======================================

}

// ==========================================
// SHOW SUCCESS
// ==========================================

function showSuccess(data) {

    let output = "";

    output +=
        "✓ COMPILATION SUCCESSFUL\n";

    output +=
        "==============================\n\n";

    output +=
        "Lexer       ✓\n";

    output +=
        "Parser      ✓\n";

    output +=
        "AST         ✓\n";

    output +=
        "Semantic    ✓\n";

    output +=
        "IR          ✓\n";

    output +=
        "CodeGen     ✓\n";

    output +=
        "VM          ✓\n\n";

    // ======================================
    // IR
    // ======================================

    output +=
        "Generated Intermediate Representation:\n";

    output +=
        "----------------------------------------\n";

    output +=
        data.ir || "(empty)";

    output += "\n\n";

    // ======================================
    // BYTECODE
    // ======================================

    output +=
        "Generated Bytecode:\n";

    output +=
        "----------------------------------------\n";

    output +=
        (data.bytecode || []).join(" ");

    output += "\n\n";

    // ======================================
    // ROBOT STATE
    // ======================================

    if (data.robot) {

        output +=
            "Final Robot State:\n";

        output +=
            "----------------------------------------\n";

        output +=
            `Position: (${data.robot.x}, ${data.robot.y})\n`;

        output +=
            `Direction: ${data.robot.direction}\n`;

        output +=
            `Angle: ${directionToAngle(data.robot.direction)}°\n`;

    }

    setConsole(output);

    // ======================================
    // Pipeline
    // ======================================

    updatePipeline(
        "vm",
        true
    );

}

// ==========================================
// FORMAT STAGE NAME
// ==========================================

function formatStageName(stage) {

    const names = {

        lexer:
            "Lexical Analysis",

        parser:
            "Syntax Analysis",

        ast:
            "Abstract Syntax Tree",

        semantic:
            "Semantic Analysis",

        ir:
            "Intermediate Representation",

        codegen:
            "Code Generation",

        vm:
            "Virtual Machine",

        connection:
            "Backend Connection",

        backend:
            "Backend",

        compiler:
            "Compiler"

    };

    return (
        names[stage] ||
        stage
    );

}

// ==========================================
// HIGHLIGHT ERROR LINE
// ==========================================

function highlightErrorLine(lineNumber) {

    if (!codeEditor) {
        return;
    }

    const lines =
        codeEditor.value.split("\n");

    if (
        lineNumber < 1 ||
        lineNumber > lines.length
    ) {

        return;

    }

    let start = 0;

    for (
        let i = 0;
        i < lineNumber - 1;
        i++
    ) {

        start +=
            lines[i].length + 1;

    }

    const end =
        start +
        lines[lineNumber - 1].length;

    codeEditor.focus();

    codeEditor.setSelectionRange(
        start,
        end
    );

    const lineHeight = 24;

    codeEditor.scrollTop =
        (lineNumber - 1) *
        lineHeight;

    if (lineNumbers) {

        lineNumbers.scrollTop =
            codeEditor.scrollTop;

    }

}

// ==========================================
// CONSOLE
// ==========================================

function setConsole(message) {

    if (!consoleOutput) {
        return;
    }

    consoleOutput.textContent =
        message;

}

function clearCompilerOutput() {

    if (!consoleOutput) {
        return;
    }

    consoleOutput.textContent =
        "Compiling...";

}

// ==========================================
// COMPILER PIPELINE
// ==========================================

function updatePipeline(
    failedStage,
    success
) {

    // IMPORTANT:
    // HTML uses .pipeline-stage
    const stages =
        document.querySelectorAll(
            ".pipeline-stage"
        );

    stages.forEach(
        stage => {

            stage.classList.remove(
                "active",
                "success",
                "error"
            );

        }
    );

    const stageMap = {

        lexer: 0,

        parser: 1,

        ast: 2,

        semantic: 3,

        ir: 4,

        codegen: 5,

        vm: 6

    };

    if (
        failedStage &&
        stageMap[failedStage] !== undefined
    ) {

        const index =
            stageMap[failedStage];

        // Previous stages succeeded
        for (
            let i = 0;
            i < index;
            i++
        ) {

            if (stages[i]) {

                stages[i].classList.add(
                    "success"
                );

            }

        }

        // Current stage
        if (stages[index]) {

            stages[index].classList.add(
                success
                    ? "success"
                    : "error"
            );

        }

    }

    // Complete success
    if (success) {

        stages.forEach(
            stage => {

                stage.classList.remove(
                    "error"
                );

                stage.classList.add(
                    "success"
                );

            }
        );

    }

}

// ==========================================
// UPDATE ROBOT INFORMATION
// ==========================================

function updateRobotInfo(state) {

    if (!state) {
        return;
    }

    const x =
        Number(state.x);

    const y =
        Number(state.y);

    const direction =
        normalizeDirection(
            state.direction
        );

    updateRobotDisplay(
        x,
        y,
        direction
    );

}

// ==========================================
// NORMALIZE DIRECTION
// ==========================================

function normalizeDirection(direction) {

    if (!direction) {
        return "NORTH";
    }

    const value =
        String(direction)
            .trim()
            .toUpperCase();

    if (value === "N") {
        return "NORTH";
    }

    if (value === "E") {
        return "EAST";
    }

    if (value === "S") {
        return "SOUTH";
    }

    if (value === "W") {
        return "WEST";
    }

    if (
        value === "NORTH" ||
        value === "EAST" ||
        value === "SOUTH" ||
        value === "WEST"
    ) {

        return value;

    }

    return "NORTH";

}

// ==========================================
// UPDATE ROBOT DISPLAY
// ==========================================

function updateRobotDisplay(
    x,
    y,
    direction = null
) {

    if (robotX) {

        robotX.textContent =
            Number(x).toFixed(0);

    }

    if (robotY) {

        robotY.textContent =
            Number(y).toFixed(0);

    }

    if (direction) {

        const normalized =
            normalizeDirection(
                direction
            );

        if (robotDirection) {

            robotDirection.textContent =
                normalized;

        }

        if (robotAngle) {

            robotAngle.textContent =
                `${directionToAngle(normalized)}°`;

        }

    }

}

// ==========================================
// DIRECTION → ANGLE
// ==========================================
//
// Coordinate convention:
//
//              NORTH
//               270°
//                 ↑
//
// WEST  180° ←─────┼─────→ 0° EAST
//
//                 ↓
//               SOUTH
//                90°
//
// ==========================================

function directionToAngle(direction) {

    switch (
        normalizeDirection(direction)
    ) {

        case "EAST":
            return 0;

        case "SOUTH":
            return 90;

        case "WEST":
            return 180;

        case "NORTH":
            return 270;

        default:
            return 270;

    }

}

// ==========================================
// CALCULATE DIRECTION FROM MOVEMENT
// ==========================================

function getDirectionFromMovement(
    previous,
    current,
    previousDirection = null
) {

    if (!previous || !current) {

        return previousDirection ||
            "NORTH";

    }

    const dx =
        Number(current.x) -
        Number(previous.x);

    const dy =
        Number(current.y) -
        Number(previous.y);

    // No position change.
    // This usually means a TURN instruction
    // may have happened, but path data alone
    // cannot reveal that turn.
    if (
        dx === 0 &&
        dy === 0
    ) {

        return null;

    }

    // Horizontal movement
    if (
        Math.abs(dx) >
        Math.abs(dy)
    ) {

        if (dx > 0) {
            return "EAST";
        }

        return "WEST";

    }

    // Vertical movement
    if (dy > 0) {

        return "NORTH";

    }

    return "SOUTH";

}

// ==========================================
// GET WORLD COORDINATES
// ==========================================

function getWorldPoint(
    point,
    minX,
    maxX,
    minY,
    maxY
) {

    if (!world) {

        return {
            x: 0,
            y: 0
        };

    }

    const width =
        world.clientWidth;

    const height =
        world.clientHeight;

    // Simulator center = logical (0, 0)
    const centerX =
        width / 2;

    const centerY =
        height / 2;

    // Calculate logical range
    const maxAbsX =
        Math.max(
            Math.abs(Number(minX)),
            Math.abs(Number(maxX)),
            100
        );

    const maxAbsY =
        Math.max(
            Math.abs(Number(minY)),
            Math.abs(Number(maxY)),
            100
        );

    // Scale
    const scaleX =
        (width - 100) /
        (maxAbsX * 2);

    const scaleY =
        (height - 100) /
        (maxAbsY * 2);

    const scale =
        Math.min(
            scaleX,
            scaleY
        );

    // Logical → Screen
    //
    // +X = right
    // -X = left
    // +Y = up
    // -Y = down

    const screenX =
        centerX +
        Number(point.x) * scale;

    const screenY =
        centerY -
        Number(point.y) * scale;

    return {
        x: screenX,
        y: screenY
    };

}

// ==========================================
// MOVE ROBOT ICON
// ==========================================

function moveRobotIcon(
    screenX,
    screenY,
    animate = true
) {

    if (!robotElement) {
        return;
    }

    // Make sure robot is positioned
    robotElement.style.position =
        "absolute";

    // DO NOT ROTATE ROBOT
    robotElement.style.transform =
        "translate(-50%, -50%)";

    if (animate) {

        robotElement.style.transition =
            "left 0.8s ease, top 0.8s ease";

    } else {

        robotElement.style.transition =
            "none";

    }

    robotElement.style.left =
        `${screenX}px`;

    robotElement.style.top =
        `${screenY}px`;

}

// ==========================================
// ANIMATE ROBOT PATH
// ==========================================

async function animateRobotPath(
    path,
    finalDirection = "NORTH"
) {

    if (
        !world ||
        !robotElement ||
        !path ||
        path.length === 0
    ) {

        return;

    }

    // ======================================
    // Draw path
    // ======================================

    drawRobotPath(path);

    // ======================================
    // IMPORTANT:
    //
    // DO NOT MOVE ROBOT BACK TO CENTER
    // ======================================
    //
    // The old code did this:
    //
    // moveRobotIcon(centerX, centerY, false);
    //
    // updateRobotDisplay(0, 0, "NORTH");
    //
    // That caused the robot to visually reset
    // every time the program was executed.
    //
    // We intentionally removed it.
    // ======================================

    await sleep(500);

    // ======================================
    // Calculate path boundaries
    // ======================================

    const xs =
        path.map(
            point =>
                Number(point.x)
        );

    const ys =
        path.map(
            point =>
                Number(point.y)
        );

    const minX =
        Math.min(...xs);

    const maxX =
        Math.max(...xs);

    const minY =
        Math.min(...ys);

    const maxY =
        Math.max(...ys);

    // ======================================
    // Current direction
    // ======================================

    let currentDirection =
        normalizeDirection(finalDirection);

    // ======================================
    // Move through path
    // ======================================

    for (
        let i = 1;
        i < path.length;
        i++
    ) {

        const previous =
            path[i - 1];

        const current =
            path[i];

        // ==================================
        // Calculate direction
        // ==================================

        const movementDirection =
            getDirectionFromMovement(
                previous,
                current,
                currentDirection
            );

        if (movementDirection) {

            currentDirection =
                movementDirection;

        }

        // ==================================
        // Screen position
        // ==================================

        const screenPoint =
            getWorldPoint(
                current,
                minX,
                maxX,
                minY,
                maxY
            );

        moveRobotIcon(
            screenPoint.x,
            screenPoint.y,
            true
        );

        // ==================================
        // Update X/Y
        // ==================================

        updateRobotDisplay(
            current.x,
            current.y,
            currentDirection
        );

        await sleep(850);

    }

    // ======================================
    // FINAL VM STATE
    // ======================================

    const finalPoint =
        path[path.length - 1];

    const normalizedFinalDirection =
        normalizeDirection(
            finalDirection
        );

    updateRobotDisplay(
        finalPoint.x,
        finalPoint.y,
        normalizedFinalDirection
    );

}

// ==========================================
// DRAW ROBOT PATH
// ==========================================

function drawRobotPath(
    path,
    minX = null,
    maxX = null,
    minY = null,
    maxY = null
) {

    if (
        !simulationCanvas ||
        !world ||
        !path ||
        path.length === 0
    ) {

        return;

    }

    const canvas =
        simulationCanvas;

    const ctx =
        canvas.getContext("2d");

    // Canvas size
    canvas.width =
        world.clientWidth;

    canvas.height =
        world.clientHeight;

    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    // Calculate boundaries
    if (
        minX === null ||
        maxX === null ||
        minY === null ||
        maxY === null
    ) {

        const xs =
            path.map(
                point =>
                    Number(point.x)
            );

        const ys =
            path.map(
                point =>
                    Number(point.y)
            );

        minX =
            Math.min(...xs);

        maxX =
            Math.max(...xs);

        minY =
            Math.min(...ys);

        maxY =
            Math.max(...ys);

    }

    // Draw path
    ctx.beginPath();

    path.forEach(
        (point, index) => {

            const screenPoint =
                getWorldPoint(
                    point,
                    minX,
                    maxX,
                    minY,
                    maxY
                );

            if (index === 0) {

                ctx.moveTo(
                    screenPoint.x,
                    screenPoint.y
                );

            } else {

                ctx.lineTo(
                    screenPoint.x,
                    screenPoint.y
                );

            }

        }
    );

    ctx.lineWidth = 3;

    ctx.stroke();

    // Draw path points
    path.forEach(
        point => {

            const screenPoint =
                getWorldPoint(
                    point,
                    minX,
                    maxX,
                    minY,
                    maxY
                );

            ctx.beginPath();

            ctx.arc(
                screenPoint.x,
                screenPoint.y,
                4,
                0,
                Math.PI * 2
            );

            ctx.fill();

        }
    );

    // Origin Marker
    const origin =
        getWorldPoint(
            {
                x: 0,
                y: 0
            },
            minX,
            maxX,
            minY,
            maxY
        );

    ctx.beginPath();

    ctx.arc(
        origin.x,
        origin.y,
        6,
        0,
        Math.PI * 2
    );

    ctx.fill();

}

// ==========================================
// RESET ROBOT POSITION
// ==========================================

function resetRobotPosition() {

    if (!world || !robotElement) {
        return;
    }

    const centerX =
        world.clientWidth / 2;

    const centerY =
        world.clientHeight / 2;

    moveRobotIcon(
        centerX,
        centerY,
        false
    );

    updateRobotDisplay(
        0,
        0,
        "NORTH"
    );

}

// ==========================================
// CLEAR PATH
// ==========================================

function clearRobotPath() {

    if (!simulationCanvas) {
        return;
    }

    const ctx =
        simulationCanvas.getContext(
            "2d"
        );

    ctx.clearRect(
        0,
        0,
        simulationCanvas.width,
        simulationCanvas.height
    );

}

// ==========================================
// RESET EVERYTHING
// ==========================================

async function resetRobot() {

    clearRobotPath();

    resetRobotPosition();

    setConsole(
        "RoboLang compiler ready..."
    );

    // Clear pipeline status
    const stages =
        document.querySelectorAll(
            ".pipeline-stage"
        );

    stages.forEach(
        stage => {

            stage.classList.remove(
                "active",
                "success",
                "error"
            );

        }
    );

    updateLineNumbers();

}

// ==========================================
// SLEEP
// ==========================================

function sleep(milliseconds) {

    return new Promise(
        resolve =>
            setTimeout(
                resolve,
                milliseconds
            )
    );

}

// ==========================================
// INITIAL ROBOT POSITION
// ==========================================

window.addEventListener(
    "load",
    () => {

        setTimeout(
            () => {

                resetRobotPosition();

            },
            100
        );

    }
);

// ==========================================
// WINDOW RESIZE
// ==========================================

window.addEventListener(
    "resize",
    () => {

        updateLineNumbers();

        // Keep robot centered when no program
        // has been executed yet.
        if (
            robotX &&
            robotY &&
            robotX.textContent === "0" &&
            robotY.textContent === "0"
        ) {

            resetRobotPosition();

        }

    }
);

// ==========================================
// START
// ==========================================

checkBackend();