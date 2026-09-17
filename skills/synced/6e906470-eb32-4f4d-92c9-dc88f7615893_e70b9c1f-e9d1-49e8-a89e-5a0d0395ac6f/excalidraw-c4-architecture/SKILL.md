---
name: excalidraw-c4-architecture
description: >
  Generate Excalidraw `.excalidraw` JSON files for C4 model architecture diagrams at all four levels:
  Context, Container, Component, and Code. Use this skill whenever the user asks for a C4 diagram,
  C4 model, context diagram, container diagram, component diagram, system context, software architecture
  using C4, or wants to visualize software architecture at different levels of abstraction. Also trigger
  when the user says "draw a C4", "show the system context", "container view of the system", "component
  breakdown", "C4 level 1/2/3/4", or references the C4 model by Simon Brown. Produces static .excalidraw
  JSON files that open directly in excalidraw.com or VS Code - no server needed.
---

# Excalidraw C4 Architecture Generator

Generate `.excalidraw` JSON files for C4 model diagrams. The output opens directly in excalidraw.com or the VS Code Excalidraw extension.

## What is C4?

The C4 model (by Simon Brown) describes software architecture at four levels of zoom:

1. **Level 1 - System Context**: Shows your system as a box in the center, surrounded by the users and other systems it interacts with. Answers: "What is the big picture?"
2. **Level 2 - Container**: Zooms into your system and shows the high-level technology choices - web apps, APIs, databases, message queues. Answers: "What are the main building blocks?"
3. **Level 3 - Component**: Zooms into a single container and shows its internal components (modules, services, controllers). Answers: "What are the major structural pieces inside this container?"
4. **Level 4 - Code**: Zooms into a component and shows classes/functions. Usually auto-generated from code, rarely drawn manually. Only create if explicitly requested.

Each level strips away detail from the levels below it. The key discipline is: **each diagram shows ONE level of abstraction**. Don't mix containers and components in the same diagram.

---

## C4 Visual Language

The C4 model has a specific visual vocabulary. Follow it so diagrams are recognizable as C4.

### Shape Types by C4 Element

| C4 Element | Shape | Size | Description Placement |
|---|---|---|---|
| Person | Ellipse (top) + Rectangle (body) | 120x120 total | Name above, role below |
| Software System | Rectangle with rounded corners | 240x140 | Name + description inside |
| Container | Rectangle with rounded corners | 220x120 | Name + technology + description |
| Component | Rectangle with rounded corners | 200x100 | Name + technology |
| External System | Rectangle with rounded corners (dashed stroke) | 240x140 | Name + description inside |
| System Boundary | Large dashed rectangle | Wraps all containers | Label at top-left |
| Container Boundary | Large dashed rectangle | Wraps all components | Label at top-left |

### Person Element

C4 persons are represented as a small ellipse (head) stacked on top of a rectangle (body), grouped together. This is a recognizable C4 convention.

```
Head: ellipse, 60x40, centered above body
Body: rectangle, 120x60, below head
Label: name text below the body
```

### Labeling Convention

Every element in C4 should show:
1. **Name** (bold/larger text, 18px)
2. **Type/Technology** in brackets (smaller text, 14px, gray)
3. **Description** (smallest text, 14px, below)

Format the label as multi-line text:
```
System Name
[Container: Technology]
Description of what it does
```

### Relationship Arrows

Every arrow in C4 must have a label describing what the relationship is. The format is:
```
[Verb] [what] [how/protocol]
```

Examples:
- "Reads/writes data" 
- "Sends emails using SMTP"
- "Makes API calls to [JSON/HTTPS]"
- "Publishes events to"

---

## Design Process

### Step 1: Determine the Level
Ask or infer which C4 level the user wants:
- **Context (L1)**: User mentions "big picture", "system context", "who uses the system", or it's the first diagram
- **Container (L2)**: User mentions "containers", "tech stack", "what runs where", "deployment units"
- **Component (L3)**: User mentions "inside the API", "component breakdown", "internal structure"
- **Code (L4)**: User explicitly asks for class/function level detail

If unclear, default to Level 1 (Context) and offer to drill down.

### Step 2: Identify Elements

#### For Level 1 (Context):
- The system being described (center, blue)
- People who use it (top or left)
- External systems it depends on (right or bottom, gray)

#### For Level 2 (Container):
- The system boundary (large dashed rectangle)
- All containers inside the boundary (web app, API, database, etc.)
- People and external systems outside the boundary (same as L1)

#### For Level 3 (Component):
- The container boundary (large dashed rectangle, labeled)
- All components inside the container
- Other containers or systems this container talks to (outside the boundary)

### Step 3: Map Relationships
Every connection needs a label. No unlabeled arrows in C4.

### Step 4: Plan Layout
C4 diagrams typically use a center-out layout:
- **L1**: System in center, people above, external systems around the edges
- **L2**: System boundary fills most of the canvas, containers inside in a grid, people and externals outside
- **L3**: Container boundary fills the canvas, components in a grid, connected containers outside

### Step 5: Build Section by Section
1. Create the file with title and any boundary rectangles
2. Add the primary system/container elements
3. Add people and external systems
4. Add all relationship arrows with labels
5. Review bindings

Use descriptive IDs: `"person_customer"`, `"system_banking"`, `"container_api"`, `"component_auth_controller"`.
Namespace seeds: people = 100xxx, systems = 200xxx, containers = 300xxx, components = 400xxx, arrows = 900xxx.

### Step 6: Save the File
Save as `<system-name>-c4-<level>.excalidraw` (e.g., `banking-c4-context.excalidraw`).

---

## Color Palette

C4 has a conventional color scheme. Follow it so diagrams are immediately recognizable.

### Core C4 Colors

| Element | Fill | Stroke | Notes |
|---|---|---|---|
| Person | `#083d77` | `#05294f` | Dark blue, person is always prominent |
| Software System (yours) | `#1168bd` | `#0b4884` | Medium blue - the focus system |
| Software System (external) | `#999999` | `#6b6b6b` | Gray - things you don't control |
| Container | `#438dd5` | `#2e6fa0` | Lighter blue - inside your system |
| Component | `#85bbf0` | `#5a9bd5` | Lightest blue - inside a container |
| Database Container | `#438dd5` | `#2e6fa0` | Same as container (label indicates DB) |
| System Boundary | transparent | `#444444` | Dashed, no fill |
| Container Boundary | transparent | `#444444` | Dashed, no fill |

### Text Colors

| Context | Color |
|---|---|
| Name on dark fills (Person, System) | `#ffffff` |
| Technology label | `#cccccc` (on dark) or `#888888` (on light) |
| Description on dark fills | `#e0e0e0` |
| Name on light fills (Component) | `#1e1e1e` |
| Description on light fills | `#555555` |
| Boundary label | `#444444` |
| Arrow label | `#555555` |
| Diagram title | `#1e1e1e` |

### Background
Canvas background: `#ffffff`

---

## JSON Structure

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [],
  "appState": {
    "viewBackgroundColor": "#ffffff",
    "gridSize": 20
  },
  "files": {}
}
```

---

## Element Templates

### Person (Head + Body + Label)
A person is three grouped elements:

**Head (ellipse):**
```json
{
  "type": "ellipse",
  "id": "person_head",
  "x": 130, "y": 30,
  "width": 60, "height": 50,
  "strokeColor": "#05294f",
  "backgroundColor": "#083d77",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 100001,
  "version": 1,
  "versionNonce": 100002,
  "isDeleted": false,
  "groupIds": ["person_group_1"],
  "boundElements": [],
  "link": null,
  "locked": false
}
```

**Body (rectangle):**
```json
{
  "type": "rectangle",
  "id": "person_body",
  "x": 110, "y": 80,
  "width": 100, "height": 60,
  "strokeColor": "#05294f",
  "backgroundColor": "#083d77",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 100003,
  "version": 1,
  "versionNonce": 100004,
  "isDeleted": false,
  "groupIds": ["person_group_1"],
  "boundElements": [{"id": "person_name_text", "type": "text"}],
  "link": null,
  "locked": false,
  "roundness": {"type": 3}
}
```

**Name label (inside body):**
```json
{
  "type": "text",
  "id": "person_name_text",
  "x": 120, "y": 90,
  "width": 80, "height": 40,
  "text": "Customer\n[Person]",
  "originalText": "Customer\n[Person]",
  "fontSize": 14,
  "fontFamily": 3,
  "textAlign": "center",
  "verticalAlign": "middle",
  "strokeColor": "#ffffff",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 100005,
  "version": 1,
  "versionNonce": 100006,
  "isDeleted": false,
  "groupIds": ["person_group_1"],
  "boundElements": null,
  "link": null,
  "locked": false,
  "containerId": "person_body",
  "lineHeight": 1.25
}
```

### Software System (Your System - Blue)
```json
{
  "type": "rectangle",
  "id": "system_main",
  "x": 200, "y": 250,
  "width": 240, "height": 140,
  "strokeColor": "#0b4884",
  "backgroundColor": "#1168bd",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 200001,
  "version": 1,
  "versionNonce": 200002,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": [{"id": "system_main_text", "type": "text"}],
  "link": null,
  "locked": false,
  "roundness": {"type": 3}
}
```

**System label (white text on blue):**
```json
{
  "type": "text",
  "id": "system_main_text",
  "x": 220, "y": 270,
  "width": 200, "height": 100,
  "text": "Internet Banking\nSystem\n[Software System]\n\nAllows customers to\nview account info",
  "originalText": "Internet Banking\nSystem\n[Software System]\n\nAllows customers to\nview account info",
  "fontSize": 14,
  "fontFamily": 3,
  "textAlign": "center",
  "verticalAlign": "middle",
  "strokeColor": "#ffffff",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 200003,
  "version": 1,
  "versionNonce": 200004,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "containerId": "system_main",
  "lineHeight": 1.25
}
```

### External System (Gray)
Same as software system but with gray colors:
- `backgroundColor`: `#999999`
- `strokeColor`: `#6b6b6b`
- `strokeStyle`: `"dashed"`

### Container (Inside System Boundary)
```json
{
  "type": "rectangle",
  "id": "container_api",
  "x": 300, "y": 300,
  "width": 220, "height": 120,
  "strokeColor": "#2e6fa0",
  "backgroundColor": "#438dd5",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 300001,
  "version": 1,
  "versionNonce": 300002,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": [{"id": "container_api_text", "type": "text"}],
  "link": null,
  "locked": false,
  "roundness": {"type": 3}
}
```

**Container label:**
```json
{
  "type": "text",
  "id": "container_api_text",
  "x": 315, "y": 315,
  "width": 190, "height": 90,
  "text": "API Application\n[Container: Node.js]\n\nProvides banking\nfunctionality via API",
  "originalText": "API Application\n[Container: Node.js]\n\nProvides banking\nfunctionality via API",
  "fontSize": 13,
  "fontFamily": 3,
  "textAlign": "center",
  "verticalAlign": "middle",
  "strokeColor": "#ffffff",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 300003,
  "version": 1,
  "versionNonce": 300004,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "containerId": "container_api",
  "lineHeight": 1.25
}
```

### Component (Lightest Blue)
Same structure as container but with:
- `backgroundColor`: `#85bbf0`
- `strokeColor`: `#5a9bd5`
- Text `strokeColor`: `#1e1e1e` (dark text on light background)
- Size: 200x100

### System/Container Boundary (Dashed Rectangle)
```json
{
  "type": "rectangle",
  "id": "boundary_system",
  "x": 50, "y": 200,
  "width": 800, "height": 500,
  "strokeColor": "#444444",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "dashed",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 200010,
  "version": 1,
  "versionNonce": 200011,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": [],
  "link": null,
  "locked": false,
  "roundness": {"type": 3}
}
```

**Boundary label (top-left):**
```json
{
  "type": "text",
  "id": "boundary_label",
  "x": 60, "y": 205,
  "width": 300, "height": 25,
  "text": "Internet Banking System [Software System]",
  "originalText": "Internet Banking System [Software System]",
  "fontSize": 16,
  "fontFamily": 3,
  "textAlign": "left",
  "verticalAlign": "top",
  "strokeColor": "#444444",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 200012,
  "version": 1,
  "versionNonce": 200013,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "containerId": null,
  "lineHeight": 1.25
}
```

### Relationship Arrow (Always Labeled)
```json
{
  "type": "arrow",
  "id": "rel_person_to_system",
  "x": 160, "y": 150,
  "width": 100, "height": 100,
  "strokeColor": "#555555",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 900001,
  "version": 1,
  "versionNonce": 900002,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "points": [[0, 0], [100, 100]],
  "startBinding": {"elementId": "person_body", "focus": 0, "gap": 2},
  "endBinding": {"elementId": "system_main", "focus": 0, "gap": 2},
  "startArrowhead": null,
  "endArrowhead": "arrow"
}
```

**Arrow label (free-floating text near arrow midpoint):**
```json
{
  "type": "text",
  "id": "rel_label_1",
  "x": 220, "y": 180,
  "width": 200, "height": 20,
  "text": "Views account balances\nusing [HTTPS]",
  "originalText": "Views account balances\nusing [HTTPS]",
  "fontSize": 12,
  "fontFamily": 3,
  "textAlign": "center",
  "verticalAlign": "top",
  "strokeColor": "#555555",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 900003,
  "version": 1,
  "versionNonce": 900004,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "containerId": null,
  "lineHeight": 1.25
}
```

---

## Layout Rules by Level

### Level 1 - System Context

```
                [Person]                     y = 30
                   |
                   v
  [Ext System] [YOUR SYSTEM] [Ext System]    y = 250
                   |
                   v
              [Ext System]                   y = 500
```

- Your system: center, 240x140
- People: above, centered
- External systems: around the edges
- All arrows labeled with what the interaction is

**Spacing**: 200px between elements vertically, 300px horizontally.

### Level 2 - Container

```
            [Person]                          y = 30
               |
  +------ System Boundary ------+            y = 180
  |                              |
  | [Web App]    [Mobile App]   |            y = 240
  |      \          /           |
  |       v        v            |
  |    [API Server]             |            y = 420
  |      |        |             |
  |      v        v             |
  |  [Database]  [Cache]        |            y = 600
  |                              |
  +------------------------------+
               |
          [Ext System]                       y = 780
```

- System boundary: dashed rectangle wrapping all containers, 60px padding
- Containers inside: arranged in rows by layer
- People and external systems: outside the boundary

**Spacing**: 250px between container rows, 250px horizontal between containers.

### Level 3 - Component

Same pattern as Level 2 but:
- Container boundary instead of system boundary
- Components inside instead of containers
- Other containers/systems outside the boundary
- Use lighter blue for components

**Spacing**: 200px between component rows, 220px horizontal.

---

## Binding Rules

1. `startBinding.elementId` = source shape `id`
2. `endBinding.elementId` = target shape `id`
3. Add `{"id": "arrow_id", "type": "arrow"}` to both shapes' `boundElements`
4. For person elements, bind arrows to the `person_body` rectangle (not the head ellipse)
5. Text inside shapes: add `{"id": "text_id", "type": "text"}` to shape's `boundElements`, set text's `containerId` to shape `id`

---

## C4 Conventions to Follow

1. **One level per diagram**: Don't mix containers and components in the same view
2. **Every arrow has a label**: Describe the relationship, not just the protocol
3. **Every element has a description**: Name alone isn't enough in C4
4. **Type annotations**: Show `[Software System]`, `[Container: Java]`, `[Component: Spring MVC Controller]` in brackets
5. **Your system vs external**: Your system is blue, external systems are gray with dashed borders
6. **Boundary labels**: System and container boundaries always have a label at the top-left
7. **People are people**: Use the head+body shape convention, not just a rectangle
8. **Direction matters**: Users at top, your system in middle, external dependencies at bottom or sides

---

## Quality Checklist

1. **Single level of abstraction**: Diagram shows only one C4 level (Context, Container, or Component)
2. **All arrows labeled**: Every relationship arrow has descriptive text explaining the interaction
3. **All elements described**: Every box has name + type annotation + brief description
4. **Your system prominent**: The focus system is visually central and uses the darkest blue
5. **External systems gray**: Things outside your control use gray fill with dashed borders
6. **Boundary present** (L2/L3): System or container boundary wraps internal elements with a clear label
7. **People recognizable**: Person elements use the head+body convention
8. **Color consistency**: Blue gradient from dark (person) to light (component) follows C4 convention
9. **Type annotations**: `[Software System]`, `[Container: Tech]`, `[Component: Type]` present on all elements
10. **Bindings correct**: All arrow bindings reference existing elements, and target elements include the arrow in `boundElements`
11. **IDs unique**: No duplicate `id` values
12. **Seeds unique**: No duplicate `seed` values
13. **Diagram title**: Clear title indicating system name and C4 level (e.g., "Banking System - System Context")
