---
name: excalidraw-process-diagram
description: >
  Generate Excalidraw `.excalidraw` JSON files for business process diagrams, workflows, and flowcharts.
  Use this skill whenever the user asks for a process diagram, workflow diagram, BPMN diagram, flowchart,
  decision tree, swimlane diagram, process flow, approval workflow, onboarding flow, or any kind of
  step-by-step business process visualization. Also trigger when the user says things like "diagram this
  process", "map out the workflow", "show the approval flow", "visualize the steps", or wants to show
  how a business process works with decisions and branching. This skill produces static .excalidraw JSON
  files that open directly in excalidraw.com or the VS Code Excalidraw extension - no server or MCP needed.
---

# Excalidraw Process Diagram Generator

Generate `.excalidraw` JSON files for business process diagrams. The output opens directly in excalidraw.com or the VS Code Excalidraw extension.

## Core Philosophy

Process diagrams show **how work flows** through a system. Every shape carries semantic meaning: ellipses are events, rectangles are tasks, diamonds are decisions. The diagram should read like a story - start here, do this, decide that, end there.

The goal is clarity. A well-made process diagram lets someone unfamiliar with the process trace through it and understand what happens, who does it, and where things can go wrong.

---

## Process Patterns

Choose the pattern that fits what the user is describing. Most real processes combine several of these.

### Sequential Flow
The simplest pattern. Steps happen one after another.
```
(Start) --> [Step 1] --> [Step 2] --> [Step 3] --> (End)
```

### Decision Branching
A diamond splits the flow based on a condition. Each branch should be labeled (Yes/No, Approved/Rejected, etc.).
```
[Review] --> <Approved?> --Yes--> [Process] --> (End)
                |
               No
                |
                v
            [Revise] --> [Review]  (loops back)
```

### Swimlanes
Horizontal or vertical bands that show who is responsible for each step. Each lane has an actor label on the left.
```
|  Requester  | [Submit Request] ---------> |
|  Manager    |              [Review] ----> <Approve?> --> |
|  Finance    |                                    [Process Payment] --> (Done)
```

### Parallel Paths (Fork/Join)
A thin bar splits the flow into parallel tracks, and another bar joins them. Both paths must complete before continuing.
```
[Prepare] --> |=FORK=| --> [Task A] --> |=JOIN=| --> [Complete]
                     |--> [Task B] --|
```

### Loop/Retry
An arrow cycles back to an earlier step. Label the arrow with the retry condition.
```
[Submit] --> [Validate] --> <Valid?> --No--> [Fix Errors] --+--> [Validate]
                              |
                             Yes
                              v
                           (Done)
```

### Error/Exception Path
A dashed arrow from any step to an error-handling flow. Use red styling for exception paths.
```
[Process] --error--> [Handle Exception] --> [Notify Admin] --> (Error End)
```

---

## Design Process

### Step 1: Understand the Process
Before writing any JSON, identify:
- **Actors**: Who is involved? (for swimlanes)
- **Steps**: What are the tasks/actions?
- **Decisions**: Where does the flow branch?
- **Start/End**: What triggers the process? What are the outcomes?
- **Exceptions**: What can go wrong?

### Step 2: Choose the Layout
- **Top-to-bottom**: Best for simple sequential flows and decision trees
- **Left-to-right**: Best for swimlane diagrams and timelines
- **Hybrid**: Top-to-bottom main flow with horizontal swimlanes

### Step 3: Plan the Grid
Mentally lay out your elements on a grid before generating JSON:
- **Step spacing**: 200px vertically between sequential steps
- **Lane width**: 300px per swimlane
- **Decision clearance**: 250px below each diamond for branch labels
- **Parallel paths**: 250px horizontal gap between parallel tracks

### Step 4: Build Section by Section
For diagrams with more than ~8 elements, build the JSON one section at a time. Do NOT generate the entire file in one pass. This avoids truncation and produces better results.

1. Create the base file with the JSON wrapper and the first section of elements
2. Add one section per edit (e.g., swimlane headers, then the first lane's steps, then the second lane's steps, then cross-lane arrows)
3. Use descriptive string IDs (e.g., `"start_event"`, `"review_decision"`, `"approve_task"`)
4. Namespace seeds by section (section 1 uses 100xxx, section 2 uses 200xxx)

### Step 5: Save the File
Save as `<name>.excalidraw` to the project root or a user-specified path. Tell the user they can open it in excalidraw.com or VS Code with the Excalidraw extension.

---

## Color Palette

Every shape gets colors based on what it represents in the process.

| Element Type | Fill | Stroke | When to Use |
|---|---|---|---|
| Start Event | `#a7f3d0` | `#047857` | Process entry point |
| End Event (Success) | `#a7f3d0` | `#047857` | Successful completion |
| End Event (Error) | `#fecaca` | `#b91c1c` | Error/failure termination |
| Process Step | `#dbeafe` | `#1e40af` | Standard task or action |
| Decision Gateway | `#fef3c7` | `#b45309` | Yes/No or conditional branch |
| Subprocess | `#e0e7ff` | `#4338ca` | Grouped sub-process |
| Manual Task | `#fed7aa` | `#c2410c` | Human-performed step |
| Automated Task | `#ddd6fe` | `#6d28d9` | System/automated step |
| Error/Exception | `#fee2e2` | `#dc2626` | Error handling steps |
| Fork/Join Bar | `#1e293b` | `#1e293b` | Parallel split/merge |
| Swimlane Background | `#f8fafc` | `#94a3b8` | Actor lane (use dashed stroke) |

### Text Colors
| Level | Color | Use For |
|---|---|---|
| Title | `#1e40af` | Diagram title |
| Swimlane Label | `#334155` | Actor/role name |
| Step Label | `#374151` | Text inside shapes |
| Arrow Label | `#64748b` | Yes/No, conditions |
| Annotation | `#94a3b8` | Notes, descriptions |

---

## JSON Structure

Every `.excalidraw` file has this wrapper:

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

All elements go in the `elements` array.

---

## Element Templates

### Start/End Event (Ellipse)
```json
{
  "type": "ellipse",
  "id": "start_event",
  "x": 200, "y": 50,
  "width": 120, "height": 60,
  "strokeColor": "#047857",
  "backgroundColor": "#a7f3d0",
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
  "groupIds": [],
  "boundElements": [{"id": "start_text", "type": "text"}],
  "link": null,
  "locked": false
}
```

### Process Step (Rectangle)
```json
{
  "type": "rectangle",
  "id": "step_1",
  "x": 170, "y": 160,
  "width": 180, "height": 80,
  "strokeColor": "#1e40af",
  "backgroundColor": "#dbeafe",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 100010,
  "version": 1,
  "versionNonce": 100011,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": [{"id": "step_1_text", "type": "text"}],
  "link": null,
  "locked": false,
  "roundness": {"type": 3}
}
```

### Decision Gateway (Diamond)
```json
{
  "type": "diamond",
  "id": "decision_1",
  "x": 160, "y": 300,
  "width": 200, "height": 120,
  "strokeColor": "#b45309",
  "backgroundColor": "#fef3c7",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 100020,
  "version": 1,
  "versionNonce": 100021,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": [{"id": "decision_1_text", "type": "text"}],
  "link": null,
  "locked": false
}
```

### Text Label (Inside a Shape)
```json
{
  "type": "text",
  "id": "step_1_text",
  "x": 200, "y": 187,
  "width": 120, "height": 25,
  "text": "Submit Request",
  "originalText": "Submit Request",
  "fontSize": 16,
  "fontFamily": 3,
  "textAlign": "center",
  "verticalAlign": "middle",
  "strokeColor": "#374151",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 100012,
  "version": 1,
  "versionNonce": 100013,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "containerId": "step_1",
  "lineHeight": 1.25
}
```

### Free-Floating Text (Title, Labels)
```json
{
  "type": "text",
  "id": "title",
  "x": 100, "y": 10,
  "width": 300, "height": 30,
  "text": "Order Approval Process",
  "originalText": "Order Approval Process",
  "fontSize": 24,
  "fontFamily": 3,
  "textAlign": "left",
  "verticalAlign": "top",
  "strokeColor": "#1e40af",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 100090,
  "version": 1,
  "versionNonce": 100091,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "containerId": null,
  "lineHeight": 1.25
}
```

### Arrow (Connection)
```json
{
  "type": "arrow",
  "id": "arrow_start_to_step1",
  "x": 260, "y": 110,
  "width": 0, "height": 50,
  "strokeColor": "#1e40af",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 100030,
  "version": 1,
  "versionNonce": 100031,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "points": [[0, 0], [0, 50]],
  "startBinding": {"elementId": "start_event", "focus": 0, "gap": 2},
  "endBinding": {"elementId": "step_1", "focus": 0, "gap": 2},
  "startArrowhead": null,
  "endArrowhead": "arrow"
}
```

### Fork/Join Bar
```json
{
  "type": "rectangle",
  "id": "fork_bar",
  "x": 160, "y": 500,
  "width": 200, "height": 8,
  "strokeColor": "#1e293b",
  "backgroundColor": "#1e293b",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 100040,
  "version": 1,
  "versionNonce": 100041,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": [],
  "link": null,
  "locked": false
}
```

### Swimlane Background
```json
{
  "type": "rectangle",
  "id": "lane_requester",
  "x": 0, "y": 60,
  "width": 900, "height": 250,
  "strokeColor": "#94a3b8",
  "backgroundColor": "#f8fafc",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "dashed",
  "roughness": 0,
  "opacity": 30,
  "angle": 0,
  "seed": 100050,
  "version": 1,
  "versionNonce": 100051,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": [],
  "link": null,
  "locked": false
}
```

### Line (Structural Divider)
```json
{
  "type": "line",
  "id": "lane_divider_1",
  "x": 0, "y": 310,
  "width": 900, "height": 0,
  "strokeColor": "#94a3b8",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "dashed",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 100060,
  "version": 1,
  "versionNonce": 100061,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "points": [[0, 0], [900, 0]]
}
```

---

## Layout Rules

### Vertical Flow (Default)
```
Title (y=10)

(Start)           x=200, y=60
   |
[Step 1]          x=170, y=170     (+110 from start)
   |
<Decision?>       x=160, y=310     (+140 from step)
  / \
[Yes path]  [No path]              (+200 from decision, spread x +/-200)
   |
(End)
```

### Swimlane Layout
```
Lane Label    |  Lane Content
              |
"Requester"   |  [Submit] -----> (arrow to next lane)
y=60..310     |
--------------+------------------------------------------
"Manager"     |            [Review] --> <Approve?>
y=310..560    |
--------------+------------------------------------------
"Finance"     |                          [Process Payment]
y=560..810    |
```

### Spacing Reference
| Between | Distance |
|---|---|
| Start event to first step | 110px |
| Sequential steps | 140px (y-gap between bottom of one and top of next) |
| Step to decision | 140px |
| Decision to branch targets | 200px vertical, +/-200px horizontal |
| Swimlane height | 250px per lane |
| Parallel tracks | 250px horizontal gap |
| Fork/join bar to parallel steps | 100px |

---

## Arrow Routing

### Straight Arrows
For elements directly above/below each other, use a simple two-point arrow:
```json
"points": [[0, 0], [0, 140]]
```

### Right-Angle Arrows (for decision branches)
For Yes/No branches from a diamond, use three points to create an L-shape:
```json
"points": [[0, 0], [200, 0], [200, 100]]
```

### Loop-Back Arrows
For retry/loop patterns, route the arrow around the side:
```json
"points": [[0, 0], [250, 0], [250, -300], [0, -300]]
```

### Arrow Labels
Add a separate free-floating text element near the arrow midpoint. Position it offset from the arrow by ~20px so it doesn't overlap.

---

## Binding Rules

When an arrow connects two shapes:
1. Set `startBinding.elementId` to the source shape's `id`
2. Set `endBinding.elementId` to the target shape's `id`
3. Add `{"id": "arrow_id", "type": "arrow"}` to both shapes' `boundElements` arrays
4. When a shape contains text, add `{"id": "text_id", "type": "text"}` to the shape's `boundElements`
5. Set the text element's `containerId` to the shape's `id`

---

## Quality Checklist

Before saving the file:

1. **Every step connected**: All shapes have at least one incoming or outgoing arrow (except Start which has only outgoing, and End which has only incoming)
2. **Decision branches labeled**: Every path from a diamond has a label (Yes/No, Approved/Rejected, etc.)
3. **Start and End present**: Every process has at least one start event and one end event
4. **No orphaned elements**: Every shape is reachable from Start
5. **Swimlane consistency**: If using swimlanes, every task is inside exactly one lane
6. **Bindings match**: Every `startBinding`/`endBinding` reference points to an element that exists, and that element's `boundElements` includes the arrow
7. **Text fits**: Container shapes are wide/tall enough for their text labels
8. **IDs unique**: No duplicate `id` values across all elements
9. **Seeds unique**: No duplicate `seed` values (use namespace ranges per section)
10. **Flow direction clear**: The eye follows a consistent path (top-to-bottom or left-to-right)
