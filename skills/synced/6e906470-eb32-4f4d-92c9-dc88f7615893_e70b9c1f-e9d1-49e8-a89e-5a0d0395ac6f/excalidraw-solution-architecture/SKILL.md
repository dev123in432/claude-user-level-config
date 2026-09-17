---
name: excalidraw-solution-architecture
description: >
  Generate Excalidraw `.excalidraw` JSON files for solution architecture diagrams showing how systems,
  services, and infrastructure fit together. Use this skill whenever the user asks for a solution
  architecture diagram, system architecture, infrastructure diagram, cloud architecture, network topology,
  microservices diagram, deployment architecture, integration diagram, or technical architecture overview.
  Also trigger when the user says "diagram the architecture", "show how the system works", "draw the
  infrastructure", "visualize the tech stack", "map out the services", or wants to show how cloud services,
  APIs, databases, queues, and frontends connect. Supports AWS, Azure, GCP, and generic/on-prem patterns.
  Produces static .excalidraw JSON files that open directly in excalidraw.com or VS Code - no server needed.
---

# Excalidraw Solution Architecture Generator

Generate `.excalidraw` JSON files for solution architecture diagrams. The output opens directly in excalidraw.com or the VS Code Excalidraw extension.

## Core Philosophy

Solution architecture diagrams show **what the system IS** and **how its parts connect**. Unlike process diagrams (which show flow over time), architecture diagrams show the structural relationships between components at a point in time.

A good architecture diagram answers: What are the major components? How do they communicate? Where do they run? What are the trust boundaries?

**The layer principle**: Systems naturally organize into layers (presentation, application, data). Making these layers visually explicit through zone backgrounds is what turns a box-and-arrow mess into a readable architecture diagram.

---

## Architecture Patterns

### Layered Architecture (Most Common)
Components grouped into horizontal layers, typically 3-4 deep. Connections flow primarily top-to-bottom between layers.
```
[Presentation Layer]
   Frontend, CDN, Load Balancer

[Application Layer]
   API Gateway, Services, Workers

[Data Layer]
   Databases, Caches, Object Storage

[External Layer]
   Third-party APIs, SaaS services
```

### Microservices
Multiple independent services, each with their own data store, communicating via API calls or message queues.
```
[API Gateway] --> [Service A] --> [DB A]
              --> [Service B] --> [DB B]
              --> [Service C] --> [Cache C]
[Message Bus] connects services asynchronously
```

### Event-Driven
A central event bus or message broker with producers and consumers around it.
```
[Producer 1] --> [Event Bus / Kafka] --> [Consumer A]
[Producer 2] -->                     --> [Consumer B]
                                     --> [Consumer C]
```

### Hub-and-Spoke
A central component (API gateway, orchestrator, or integration platform) that connects to multiple peripheral systems.
```
              [System A]
                 |
[System B] -- [Hub] -- [System C]
                 |
              [System D]
```

### Pipeline
Linear data or request flow from source to destination through transformation stages.
```
[Source] --> [Ingest] --> [Transform] --> [Enrich] --> [Store] --> [Serve]
```

---

## Design Process

### Step 1: Identify Components
List every component in the system:
- **User-facing**: Web apps, mobile apps, CLIs
- **Compute**: API servers, workers, serverless functions, containers
- **Data**: Databases (SQL/NoSQL), caches, search engines, object storage
- **Messaging**: Queues, event buses, pub/sub
- **Infrastructure**: Load balancers, CDNs, DNS, API gateways
- **External**: Third-party APIs, SaaS services, payment processors
- **Security**: Auth services, WAF, secrets management

### Step 2: Group into Layers
Assign each component to a layer. Common layer schemes:
- **3-layer**: Presentation / Application / Data
- **4-layer**: Client / API / Services / Data
- **Cloud-specific**: Edge / Compute / Data / External
- **Network zones**: Public / DMZ / Private / Data

### Step 3: Map Connections
For each pair of connected components, note:
- **Protocol**: HTTP/REST, gRPC, SQL, WebSocket, AMQP, etc.
- **Direction**: Unidirectional or bidirectional
- **Style**: Solid (synchronous), dashed (asynchronous), dotted (optional/fallback)

### Step 4: Plan the Layout
- **Layer zones**: Full-width dashed rectangles, 300px tall, 40px gap between zones
- **Components within a layer**: Spread horizontally with 200px gaps
- **Cross-layer arrows**: Primarily vertical, labeled with protocol
- **Title**: Top of diagram, 24px font

### Step 5: Build Section by Section
For large diagrams (>10 components), build one layer at a time:
1. Create the file with zone backgrounds and title
2. Add components for layer 1 (top layer)
3. Add components for layer 2
4. Continue for each layer
5. Add all cross-layer arrows last (so binding references resolve)
6. Review the complete JSON for binding consistency

Use descriptive IDs like `"api_gateway"`, `"user_db"`, `"auth_service"`.
Namespace seeds: layer 1 = 100xxx, layer 2 = 200xxx, layer 3 = 300xxx, arrows = 900xxx.

### Step 6: Save the File
Save as `<name>.excalidraw` to the project root or a user-specified path.

---

## Color Palette

### Component Types (Generic)

| Component Type | Fill | Stroke | When to Use |
|---|---|---|---|
| Frontend/UI | `#a5d8ff` | `#1971c2` | Web apps, mobile, SPAs |
| Backend/API | `#d0bfff` | `#7048e8` | API servers, microservices |
| Database | `#b2f2bb` | `#2f9e44` | PostgreSQL, MySQL, MongoDB, DynamoDB |
| Cache | `#ffe8cc` | `#fd7e14` | Redis, Memcached |
| Queue/Event Bus | `#fff3bf` | `#fab005` | Kafka, RabbitMQ, SQS, EventBridge |
| Storage | `#ffec99` | `#f08c00` | S3, Blob Storage, GCS |
| AI/ML | `#e599f7` | `#9c36b5` | ML models, AI APIs, LLMs |
| External API | `#ffc9c9` | `#e03131` | Third-party services, SaaS |
| Auth/Security | `#dee2e6` | `#495057` | IAM, OAuth, WAF |
| CDN/Load Balancer | `#c3fae8` | `#0ca678` | CloudFront, ALB, nginx |
| Users/Actors | `#e7f5ff` | `#1971c2` | User ellipses (entry point) |
| Monitoring | `#d3f9d8` | `#40c057` | Logging, metrics, alerts |

### Cloud Provider Palettes

Use these when the user specifies a cloud provider or when the diagram is clearly about a specific platform.

#### AWS
| Service Category | Fill | Stroke |
|---|---|---|
| Compute (EC2, Lambda, ECS) | `#ff9900` | `#cc7a00` |
| Storage (S3, EBS) | `#3f8624` | `#2d6119` |
| Database (RDS, DynamoDB) | `#3b48cc` | `#2d3899` |
| Networking (VPC, Route53, ALB) | `#8c4fff` | `#6b3dcc` |
| Security (IAM, KMS, Cognito) | `#dd344c` | `#b12a3d` |
| Messaging (SQS, SNS, EventBridge) | `#ff4f8b` | `#cc3f6f` |
| AI/ML (SageMaker, Bedrock) | `#01a88d` | `#017d69` |

#### Azure
| Service Category | Fill | Stroke |
|---|---|---|
| Compute (App Service, Functions) | `#0078d4` | `#005a9e` |
| Storage (Blob, Files) | `#50e6ff` | `#3cb5cc` |
| Database (SQL, Cosmos DB) | `#0078d4` | `#005a9e` |
| Networking (VNet, Front Door) | `#773adc` | `#5a2ca8` |
| Security (Entra ID, Key Vault) | `#ff8c00` | `#cc7000` |
| AI/ML (OpenAI, Cognitive Services) | `#50e6ff` | `#3cb5cc` |

#### GCP
| Service Category | Fill | Stroke |
|---|---|---|
| Compute (GCE, Cloud Run, GKE) | `#4285f4` | `#3367d6` |
| Storage (GCS) | `#34a853` | `#2d8e47` |
| Database (Cloud SQL, Firestore) | `#ea4335` | `#c53929` |
| Networking (VPC, Cloud CDN) | `#fbbc04` | `#d99e04` |
| AI/ML (Vertex AI) | `#9334e6` | `#7627b8` |

### Zone/Layer Colors
| Zone | Fill | Stroke |
|---|---|---|
| Presentation/Client Layer | `#e7f5ff` | `#1971c2` |
| Application/API Layer | `#f3f0ff` | `#7048e8` |
| Data Layer | `#ebfbee` | `#2f9e44` |
| External/Integration Layer | `#fff5f5` | `#e03131` |
| Network/Security Zone | `#f1f3f5` | `#495057` |

Use dashed stroke and 30% opacity for zone backgrounds so components inside remain prominent.

### Text Colors
| Level | Color | Use For |
|---|---|---|
| Diagram Title | `#1e1e1e` | Main title, 24px |
| Zone Label | `#868e96` | Layer name, 14px |
| Component Label | `#374151` | Text inside shapes |
| Arrow Label | `#64748b` | Protocol labels (REST, SQL, etc.) |
| Annotation | `#94a3b8` | Notes, descriptions |

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

### Zone Background (Layer)
```json
{
  "type": "rectangle",
  "id": "zone_presentation",
  "x": 0, "y": 60,
  "width": 1000, "height": 280,
  "strokeColor": "#1971c2",
  "backgroundColor": "#e7f5ff",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "dashed",
  "roughness": 0,
  "opacity": 30,
  "angle": 0,
  "seed": 100001,
  "version": 1,
  "versionNonce": 100002,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": [],
  "link": null,
  "locked": false,
  "roundness": {"type": 3}
}
```

### Service/Component (Rectangle)
```json
{
  "type": "rectangle",
  "id": "api_gateway",
  "x": 100, "y": 120,
  "width": 200, "height": 80,
  "strokeColor": "#7048e8",
  "backgroundColor": "#d0bfff",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 200010,
  "version": 1,
  "versionNonce": 200011,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": [{"id": "api_gateway_text", "type": "text"}],
  "link": null,
  "locked": false,
  "roundness": {"type": 3}
}
```

### Component Label (Inside Shape)
Use `\n` for multi-line labels showing the component name and technology:
```json
{
  "type": "text",
  "id": "api_gateway_text",
  "x": 130, "y": 140,
  "width": 140, "height": 40,
  "text": "API Gateway\nnginx / Kong",
  "originalText": "API Gateway\nnginx / Kong",
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
  "seed": 200012,
  "version": 1,
  "versionNonce": 200013,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "containerId": "api_gateway",
  "lineHeight": 1.25
}
```

### User/Actor (Ellipse)
```json
{
  "type": "ellipse",
  "id": "user_actor",
  "x": 180, "y": 0,
  "width": 120, "height": 50,
  "strokeColor": "#1971c2",
  "backgroundColor": "#e7f5ff",
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
  "boundElements": [{"id": "user_text", "type": "text"}],
  "link": null,
  "locked": false
}
```

### Database (Rectangle with Rounded Top)
Databases are rectangles with a distinctive label format: name + engine.
```json
{
  "type": "rectangle",
  "id": "main_db",
  "x": 100, "y": 500,
  "width": 180, "height": 80,
  "strokeColor": "#2f9e44",
  "backgroundColor": "#b2f2bb",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 300010,
  "version": 1,
  "versionNonce": 300011,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": [{"id": "main_db_text", "type": "text"}],
  "link": null,
  "locked": false,
  "roundness": {"type": 3}
}
```

### Arrow (Connection Between Components)
```json
{
  "type": "arrow",
  "id": "arrow_gw_to_api",
  "x": 200, "y": 200,
  "width": 0, "height": 100,
  "strokeColor": "#7048e8",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 900010,
  "version": 1,
  "versionNonce": 900011,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "points": [[0, 0], [0, 100]],
  "startBinding": {"elementId": "api_gateway", "focus": 0, "gap": 2},
  "endBinding": {"elementId": "auth_service", "focus": 0, "gap": 2},
  "startArrowhead": null,
  "endArrowhead": "arrow"
}
```

### Async/Optional Arrow (Dashed)
Same as arrow but with `"strokeStyle": "dashed"`. Use for asynchronous communication, event-driven connections, or optional dependencies.

### Free-Floating Text
```json
{
  "type": "text",
  "id": "zone_label_app",
  "x": 10, "y": 70,
  "width": 150, "height": 20,
  "text": "Application Layer",
  "originalText": "Application Layer",
  "fontSize": 14,
  "fontFamily": 3,
  "textAlign": "left",
  "verticalAlign": "top",
  "strokeColor": "#868e96",
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

---

## Layout Rules

### Vertical Layered Layout (Default)
```
Title                              y = 0
                                   
[Zone: Presentation]               y = 50,  h = 250
  [Component] [Component]          y = 100, spaced 250px apart on x
                                   
[Zone: Application]                y = 340, h = 250
  [Component] [Component] [Comp]   y = 390, spaced 250px apart on x
                                   
[Zone: Data]                       y = 630, h = 250
  [Component] [Component]          y = 680, spaced 250px apart on x
```

### Spacing Reference
| Between | Distance |
|---|---|
| Zone gap | 40px between zone bottoms and next zone top |
| Component top margin inside zone | 50px from zone top |
| Horizontal component spacing | 250px center-to-center |
| Component width | 200px (standard), 240px (wide labels) |
| Component height | 80px (2 lines), 100px (3 lines) |
| Zone width | Full diagram width + 40px padding each side |
| Zone height | 250-300px depending on content |
| Arrow label offset | 15px from arrow line |

### Component Sizing
| Component | Width | Height |
|---|---|---|
| Standard service | 200px | 80px |
| Wide label service | 240px | 80px |
| Database | 180px | 80px |
| User actor (ellipse) | 120px | 50px |
| Queue/Event bus | 220px | 70px |

---

## Connection Styling

| Connection Type | Stroke Style | Arrowhead | Example |
|---|---|---|---|
| Synchronous call | solid | arrow | REST API call |
| Asynchronous message | dashed | arrow | Queue publish |
| Event/notification | dotted | arrow | Webhook, event |
| Data flow (read) | solid | arrow | DB query |
| Bidirectional | solid | both ends arrow | WebSocket |
| Optional/fallback | dotted | arrow | Failover path |

Color the arrow stroke to match the **source** component's stroke color.

---

## Binding Rules

1. Set `startBinding.elementId` to the source shape's `id`
2. Set `endBinding.elementId` to the target shape's `id`
3. Add `{"id": "arrow_id", "type": "arrow"}` to both shapes' `boundElements` arrays
4. For text inside shapes: add `{"id": "text_id", "type": "text"}` to shape's `boundElements`, set text's `containerId` to shape's `id`

---

## Quality Checklist

1. **Layers visible**: Every component sits inside a clearly labeled zone
2. **Connections labeled**: Arrows show the protocol or data type (REST, SQL, gRPC, events)
3. **No orphans**: Every component has at least one connection
4. **Color consistency**: Same-type components use the same fill/stroke pair
5. **Max 3-4 fill colors** per diagram to avoid visual noise
6. **Title present**: Diagram has a clear title at the top
7. **Zone labels**: Each layer/zone has a label (14px, gray, top-left corner)
8. **Readable text**: Component labels include name + technology, fit within the shape
9. **Async marked**: Asynchronous connections use dashed arrows
10. **Bindings correct**: All `startBinding`/`endBinding` references exist, and target shapes' `boundElements` include the arrow
11. **IDs unique**: No duplicate `id` values
12. **Seeds unique**: No duplicate `seed` values
13. **Legend** (optional): Include if using more than 3 component colors
