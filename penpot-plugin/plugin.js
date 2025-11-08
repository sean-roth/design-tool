"use strict";
/// <reference types="@penpot/plugin-types" />
/**
 * AI Design Bridge Plugin for PenPot
 *
 * This plugin enables Claude AI agents to create and modify designs
 * in PenPot through natural conversation via the MCP server.
 */
console.log("AI Design Bridge Plugin initializing...");
// ============================================================================
// SHAPE CREATION OPERATIONS
// ============================================================================
function createRectangle(properties) {
    try {
        const shape = penpot.createRectangle();
        // Set properties
        if (properties.name) {
            shape.name = properties.name;
        }
        if (properties.width && properties.height) {
            shape.resize(properties.width, properties.height);
        }
        if (properties.fills) {
            shape.fills = properties.fills;
        }
        if (properties.strokes) {
            shape.strokes = properties.strokes;
        }
        if (properties.borderRadius !== undefined) {
            shape.borderRadius = properties.borderRadius;
        }
        console.log(`Created rectangle: ${shape.name} (${shape.id})`);
        return {
            success: true,
            data: {
                id: shape.id,
                name: shape.name,
                type: 'rectangle'
            }
        };
    }
    catch (error) {
        console.error("Failed to create rectangle:", error);
        return {
            success: false,
            error: error.message
        };
    }
}
function createEllipse(properties) {
    try {
        const shape = penpot.createEllipse();
        if (properties.name) {
            shape.name = properties.name;
        }
        if (properties.width && properties.height) {
            shape.resize(properties.width, properties.height);
        }
        if (properties.fills) {
            shape.fills = properties.fills;
        }
        if (properties.strokes) {
            shape.strokes = properties.strokes;
        }
        console.log(`Created ellipse: ${shape.name} (${shape.id})`);
        return {
            success: true,
            data: {
                id: shape.id,
                name: shape.name,
                type: 'ellipse'
            }
        };
    }
    catch (error) {
        console.error("Failed to create ellipse:", error);
        return {
            success: false,
            error: error.message
        };
    }
}
function createText(properties) {
    try {
        const shape = penpot.createText("Text");
        if (!shape) {
            throw new Error("Failed to create text shape");
        }
        if (properties.name) {
            shape.name = properties.name;
        }
        if (properties.text) {
            shape.characters = properties.text;
        }
        if (properties.fontFamily) {
            console.log(`Font ${properties.fontFamily} requested (using default for now)`);
        }
        if (properties.fontSize) {
            shape.fontSize = properties.fontSize;
        }
        if (properties.fills) {
            shape.fills = properties.fills;
        }
        console.log(`Created text: ${shape.name} (${shape.id})`);
        return {
            success: true,
            data: {
                id: shape.id,
                name: shape.name,
                type: 'text',
                text: shape.characters
            }
        };
    }
    catch (error) {
        console.error("Failed to create text:", error);
        return {
            success: false,
            error: error.message
        };
    }
}
function createBoard(properties) {
    try {
        const board = penpot.createBoard();
        if (properties.name) {
            board.name = properties.name;
        }
        if (properties.width && properties.height) {
            board.resize(properties.width, properties.height);
        }
        if (properties.fills) {
            board.fills = properties.fills;
        }
        console.log(`Created board: ${board.name} (${board.id})`);
        return {
            success: true,
            data: {
                id: board.id,
                name: board.name,
                type: 'board'
            }
        };
    }
    catch (error) {
        console.error("Failed to create board:", error);
        return {
            success: false,
            error: error.message
        };
    }
}
// ============================================================================
// SHAPE MODIFICATION OPERATIONS
// ============================================================================
function modifyElement(elementId, properties) {
    try {
        const element = findElementById(elementId);
        if (!element) {
            return {
                success: false,
                error: `Element not found: ${elementId}`
            };
        }
        // Apply properties
        if (properties.name) {
            element.name = properties.name;
        }
        if (properties.width && properties.height) {
            element.resize(properties.width, properties.height);
        }
        if (properties.fills) {
            element.fills = properties.fills;
        }
        if (properties.strokes) {
            element.strokes = properties.strokes;
        }
        if (properties.borderRadius !== undefined && 'borderRadius' in element) {
            element.borderRadius = properties.borderRadius;
        }
        console.log(`Modified element: ${element.name} (${element.id})`);
        return {
            success: true,
            data: {
                id: element.id,
                name: element.name
            }
        };
    }
    catch (error) {
        console.error("Failed to modify element:", error);
        return {
            success: false,
            error: error.message
        };
    }
}
function findElementById(id) {
    if (!penpot.currentPage) {
        return null;
    }
    function traverse(node) {
        if (node.id === id) {
            return node;
        }
        if ('children' in node && node.children) {
            for (const child of node.children) {
                const found = traverse(child);
                if (found)
                    return found;
            }
        }
        return null;
    }
    return traverse(penpot.currentPage);
}
// ============================================================================
// STATE QUERY OPERATIONS
// ============================================================================
function getState(query = {}) {
    try {
        if (!penpot.currentPage) {
            return {
                success: false,
                error: "No active page"
            };
        }
        const elements = [];
        function collectElements(node) {
            elements.push({
                id: node.id,
                name: node.name,
                type: node.type,
                x: node.x,
                y: node.y,
                width: node.width,
                height: node.height
            });
            if ('children' in node && node.children) {
                for (const child of node.children) {
                    collectElements(child);
                }
            }
        }
        // Get all shapes from the current page
        const shapes = penpot.currentPage.findShapes();
        for (const shape of shapes) {
            collectElements(shape);
        }
        console.log(`Retrieved state: ${elements.length} elements`);
        return {
            success: true,
            data: {
                elements,
                page: {
                    id: penpot.currentPage.id,
                    name: penpot.currentPage.name
                }
            }
        };
    }
    catch (error) {
        console.error("Failed to get state:", error);
        return {
            success: false,
            error: error.message
        };
    }
}
// ============================================================================
// COMMAND DISPATCHER
// ============================================================================
function executeCommand(command) {
    console.log("Executing command:", command.operation);
    switch (command.operation) {
        case 'createRectangle':
            return createRectangle(command.properties || {});
        case 'createEllipse':
            return createEllipse(command.properties || {});
        case 'createText':
            return createText(command.properties || {});
        case 'createBoard':
            return createBoard(command.properties || {});
        case 'modifyElement':
            if (!command.element_id) {
                return {
                    success: false,
                    error: "element_id required for modifyElement"
                };
            }
            return modifyElement(command.element_id, command.properties || {});
        case 'getState':
            return getState(command.query || {});
        default:
            return {
                success: false,
                error: `Unknown operation: ${command.operation}`
            };
    }
}
// ============================================================================
// MESSAGE HANDLING (MCP SERVER INTEGRATION)
// ============================================================================
// Handle messages from UI
penpot.ui.onMessage((message) => {
    console.log("Received command via UI:", message);
    const result = executeCommand(message);
    // Send result back to UI
    penpot.ui.sendMessage({
        type: 'commandResult',
        result
    });
});
// ============================================================================
// PLUGIN INITIALIZATION
// ============================================================================
console.log("AI Design Bridge Plugin loaded successfully");
console.log("Current page:", penpot.currentPage?.name);
console.log("Current file:", penpot.currentFile?.name);
// Open UI for testing and MCP communication
penpot.ui.open('AI Design Bridge', 'http://localhost:4400/index.html', {
    width: 400,
    height: 600
});
console.log("Plugin ready for commands");
