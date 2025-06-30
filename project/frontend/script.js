// Global Variables
let latestTokens = [];
let intermediateCode = '';
let optimizationSuggestion = '';
let latestParseTree = {};

// Execute SQL Query and Store Data
async function executeQuery() {
    const query = document.getElementById('sqlQuery').value;

    try {
        const response = await fetch('http://127.0.0.1:5000/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });

        const result = await response.json();

        latestTokens = result.tokens || [];
        intermediateCode = result.intermediate || '';
        optimizationSuggestion = result.optimization || '';
        latestParseTree = result.parse_tree || {};

        displayResult(result);
    } catch (error) {
        console.error('Error executing query:', error);
    }
}

// Animate Tokens One by One
function animateTokens() {
    const animatedDiv = document.getElementById('animatedTokens');
    animatedDiv.innerHTML = '';

    let index = 0;

    function showNextToken() {
        if (index < latestTokens.length) {
            let span = document.createElement('span');
            span.textContent = latestTokens[index].value + ' ';

            if (latestTokens[index].type === 'KEYWORD') {
                span.classList.add('keyword');
            } else if (latestTokens[index].type === 'SYMBOL') {
                span.classList.add('symbol');
            } else {
                span.classList.add('identifier');
            }

            animatedDiv.appendChild(span);
            index++;
            setTimeout(showNextToken, 500);
        }
    }

    showNextToken();
}

// Animate Intermediate Code Line by Line
function animateIntermediateCode() {
    const intermediateBlock = document.getElementById('intermediateBlock');
    intermediateBlock.innerHTML = '';

    const lines = intermediateCode.split('\n');
    let index = 0;

    function showNextLine() {
        if (index < lines.length) {
            let line = document.createElement('div');
            line.textContent = lines[index];
            line.classList.add('blue-box');
            line.style.animation = 'popIn 0.4s ease';
            intermediateBlock.appendChild(line);
            index++;
            setTimeout(showNextLine, 500);
        }
    }

    showNextLine();
}

// Animate Optimization Suggestions Line by Line
function animateOptimizationSuggestions() {
    const optimizationBlock = document.getElementById('optimizationBlock');
    optimizationBlock.innerHTML = '';

    const suggestions = optimizationSuggestion.split('\n');
    let index = 0;

    function showNextSuggestion() {
        if (index < suggestions.length) {
            let line = document.createElement('div');
            line.textContent = suggestions[index];
            line.classList.add('blue-box');
            line.style.animation = 'popIn 0.4s ease';
            optimizationBlock.appendChild(line);
            index++;
            setTimeout(showNextSuggestion, 500);
        }
    }

    showNextSuggestion();
}

// Load and Render Parse Tree with Mermaid.js
function loadParseTree() {
    if (!latestParseTree || Object.keys(latestParseTree).length === 0) {
        alert('Please run a query first.');
        return;
    }

    const mermaidString = convertToMermaid(latestParseTree);
    console.log(mermaidString);

    const mermaidContainer = document.getElementById('mermaid');
    mermaidContainer.innerHTML = '';

    const diagramDiv = document.createElement('div');
    diagramDiv.className = 'mermaid';
    diagramDiv.textContent = mermaidString;

    mermaidContainer.appendChild(diagramDiv);
    mermaid.init(undefined, diagramDiv);
}

// Convert Parse Tree to Mermaid Syntax
function convertToMermaid(node) {
    let lines = [];
    let nodeId = { count: 0 };

    function traverse(node, parentId = null) {
        const currentId = 'node' + nodeId.count++;
        const safeName = node.name.replace(/\"/g, '&quot;');

        lines.push(`${currentId}["${safeName}"]`);

        if (parentId !== null) {
            lines.push(`${parentId} --> ${currentId}`);
        }

        if (node.children && node.children.length > 0) {
            node.children.forEach(child => traverse(child, currentId));
        }
    }

    traverse(node);

    return 'graph TD\n' + lines.join('\n');
}

/// Display SQL Query Results
function displayResult(result) {
    const resultDiv = document.getElementById('queryResult');
    resultDiv.innerHTML = '';

    if (result.status === 'success') {
        if (result.data) { // SELECT Query
            if (Array.isArray(result.data) && result.data.length > 0) {
                const table = document.createElement('table');
                table.border = '1';
                table.style.borderCollapse = 'collapse';
                table.style.marginTop = '10px';

                const header = document.createElement('tr');
                Object.keys(result.data[0]).forEach(key => {
                    const th = document.createElement('th');
                    th.textContent = key;
                    th.style.padding = '8px';
                    header.appendChild(th);
                });
                table.appendChild(header);

                result.data.forEach(row => {
                    const tr = document.createElement('tr');
                    Object.values(row).forEach(value => {
                        const td = document.createElement('td');
                        td.textContent = value;
                        td.style.padding = '8px';
                        tr.appendChild(td);
                    });
                    table.appendChild(tr);
                });

                resultDiv.appendChild(table);
            } else {
                resultDiv.innerHTML += '<p>No records found.</p>';
            }
        } else if (result.message) { // INSERT / UPDATE / DELETE Query
            // Show message inside a blue success box
            const messageBox = document.createElement('div');
            messageBox.textContent = result.message;
            messageBox.classList.add('blue-box');
            messageBox.style.fontWeight = 'bold';
            messageBox.style.marginTop = '15px';
            resultDiv.appendChild(messageBox);
        }
    } else if (result.status === 'semantic_error') {
        resultDiv.innerHTML = `<span style="color: red; font-weight: bold;">${result.message}</span>`;
    } else {
        resultDiv.innerHTML = `<span style="color: red;">Error: ${result.message}</span>`;
    }
}

// Show Section Function for Sidebar
function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => { section.style.display = 'none'; });
    document.getElementById(sectionId).style.display = 'block';

    if (sectionId === 'intermediateSection') {
        animateIntermediateCode();
        animateOptimizationSuggestions();
    }
}

// Reset Dashboard
function resetDashboard() {
    document.getElementById('sqlQuery').value = '';
    document.getElementById('queryResult').innerHTML = '';
    document.getElementById('animatedTokens').innerHTML = '';
    document.getElementById('intermediateBlock').innerHTML = '';
    document.getElementById('optimizationBlock').innerHTML = '';
    document.getElementById('mermaid').innerHTML = '';
    latestTokens = [];
    intermediateCode = '';
    optimizationSuggestion = '';
    latestParseTree = {};
}
