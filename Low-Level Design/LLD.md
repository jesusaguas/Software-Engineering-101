# Low-Level Design / Object-Oriented Design Interview Guide

An LLD interview tests whether you can turn an ambiguous prompt into a small, correct, and extensible object model while communicating your decisions clearly.

| Phase | Time | Deliverable |
|---|---:|---|
| 1. Requirements | ~5 min | Confirmed scope and behavioral rules |
| 2. Entities and relationships | ~3 min | Core objects, ownership, and dependencies |
| 3. Class design | ~10–15 min | State and public behavior for each class |
| 4. Implementation and verification | ~10 min | Core logic, edge cases, and a scenario walkthrough |
| 5. Extensibility | ~5 min, if time allows | Clean responses to follow-up requirements |

Treat the timing as a guide. Follow the interviewer when they want to explore something, then return to the framework so no essential phase is missed.

The running example is:

> Design an in-memory parking lot that assigns a compatible parking spot when a vehicle enters and releases it when the vehicle exits.

---

## 1. Clarify Requirements

Do not begin with classes. Turn the one-line prompt into a concrete specification by asking about:

- **Primary capabilities:** What must users be able to do?
- **Rules and completion:** What makes an operation valid or complete?
- **Error handling:** What happens for invalid or impossible operations?
- **Scope boundaries:** Are persistence, UI, networking, concurrency, and extensions included?

Ask only questions that can affect the design. State sensible assumptions when the interviewer has no preference.

### Example

Useful questions:

- Which vehicle and spot types exist?
- Which vehicles can use which spots?
- How should a compatible spot be selected?
- Can the same vehicle enter twice?
- What identifies an active parking session?
- What should happen if no compatible spot exists or a ticket is invalid?
- Are pricing, multiple floors, persistence, and concurrent entrances in scope?

Confirmed specification:

```text
Requirements
1. Support motorcycles, cars, and trucks.
2. Support motorcycle, compact, and large spots.
3. A motorcycle fits any spot; a car fits compact or large; a truck fits large.
4. park(vehicle) assigns the first compatible available spot and returns a ticket.
5. exit(ticketId) releases the assigned spot.
6. Reject duplicate entry, unavailable capacity, and invalid tickets.
7. Expose the number of currently available spots.

Out of scope
- Pricing and payment
- Reservations
- Multiple floors
- Persistence, networking, and UI
- Concurrent entrance requests
```

Confirm this list with the interviewer. It becomes the source of truth for every class and method that follows.

---

## 2. Identify Entities and Relationships

Scan the requirements for meaningful nouns, but do not turn every noun into a class.

An object likely deserves its own entity when it:

- Maintains changing state.
- Enforces rules around that state.
- Has an identity or lifecycle.

Simple descriptive information can remain a value or field.

### Example

```text
ParkingLot       Orchestrates entry and exit; owns spots and active tickets.
ParkingSpot      Owns occupancy and vehicle-compatibility rules.
Vehicle          Immutable value: license plate and vehicle type.
ParkingTicket    Immutable record linking a vehicle to its assigned spot.

Relationships
ParkingLot contains many ParkingSpots.
ParkingLot creates and tracks ParkingTickets.
ParkingSpot may contain one Vehicle.
ParkingTicket references a spot and vehicle by identifier.
```

`ParkingLot` is the orchestrator because it drives the main workflow. `ParkingSpot` owns compatibility and occupancy because it owns the relevant state. `Vehicle` does not need subclasses: its types have data-driven compatibility rules but no distinct behavior yet.

A list and a few arrows are enough. Use formal UML only if the interviewer requests it.

---

## 3. Design Classes: State and Behavior

Work top-down from the orchestrator. For every class, derive:

1. **State:** What must it remember to satisfy its requirements?
2. **Behavior:** What actions or queries must it support?

Keep rules with the object that owns the required state. Prefer telling an object to perform an operation over retrieving its data and changing it elsewhere.

### Example class outline

```text
ParkingLot
  State:
    spotsById
    activeTicketsById
    activeTicketByLicensePlate
    nextTicketNumber
  Behavior:
    park(vehicle) -> ParkingTicket
    exit(ticketId) -> void
    availableSpotCount() -> number

ParkingSpot
  State:
    id
    type
    parkedVehicle
  Behavior:
    isAvailable() -> boolean
    canFit(vehicle) -> boolean
    park(vehicle) -> void
    vacate() -> Vehicle

Vehicle
  State:
    licensePlate
    type

ParkingTicket
  State:
    id
    spotId
    licensePlate
    issuedAt
```

Check the outline against the requirements:

- Spot compatibility belongs in `ParkingSpot`.
- Duplicate-entry detection requires an active ticket lookup by license plate.
- Exiting by ticket requires tickets and spots to be retrievable by ID.
- Ticket numbering is creation state owned by `ParkingLot`.

This traceability prevents speculative fields and pattern-driven overengineering.

Before coding, ask whether the interviewer expects pseudocode, core methods, or complete compilable code.

---

## 4. Implement the Core Flow

Implement the methods that best demonstrate object collaboration and state transitions. Start with the happy path, then add failures and invariants.

### TypeScript implementation

```ts
enum VehicleType {
  Motorcycle,
  Car,
  Truck,
}

enum SpotType {
  Motorcycle,
  Compact,
  Large,
}

type Vehicle = Readonly<{
  licensePlate: string;
  type: VehicleType;
}>;

type ParkingTicket = Readonly<{
  id: string;
  spotId: string;
  licensePlate: string;
  issuedAt: Date;
}>;

class ParkingSpot {
  private parkedVehicle?: Vehicle;

  constructor(
    readonly id: string,
    readonly type: SpotType,
  ) {}

  isAvailable(): boolean {
    return this.parkedVehicle === undefined;
  }

  canFit(vehicle: Vehicle): boolean {
    switch (vehicle.type) {
      case VehicleType.Motorcycle:
        return true;
      case VehicleType.Car:
        return this.type === SpotType.Compact ||
          this.type === SpotType.Large;
      case VehicleType.Truck:
        return this.type === SpotType.Large;
    }
  }

  park(vehicle: Vehicle): void {
    if (!this.isAvailable()) {
      throw new Error(`Spot ${this.id} is occupied`);
    }
    if (!this.canFit(vehicle)) {
      throw new Error(`Vehicle cannot fit in spot ${this.id}`);
    }
    this.parkedVehicle = vehicle;
  }

  vacate(): Vehicle {
    if (!this.parkedVehicle) {
      throw new Error(`Spot ${this.id} is already empty`);
    }

    const vehicle = this.parkedVehicle;
    this.parkedVehicle = undefined;
    return vehicle;
  }
}

class ParkingLot {
  private readonly spotsById: Map<string, ParkingSpot>;
  private readonly activeTicketsById = new Map<string, ParkingTicket>();
  private readonly activeTicketByLicensePlate =
    new Map<string, ParkingTicket>();
  private nextTicketNumber = 1;

  constructor(spots: ParkingSpot[]) {
    this.spotsById = new Map(
      spots.map(spot => [spot.id, spot] as const),
    );

    if (this.spotsById.size !== spots.length) {
      throw new Error("Spot IDs must be unique");
    }
  }

  park(vehicle: Vehicle): ParkingTicket {
    if (this.activeTicketByLicensePlate.has(vehicle.licensePlate)) {
      throw new Error("Vehicle is already parked");
    }

    const spot = this.findCompatibleSpot(vehicle);
    if (!spot) {
      throw new Error("No compatible spot is available");
    }

    spot.park(vehicle);

    const ticket: ParkingTicket = {
      id: `T-${this.nextTicketNumber++}`,
      spotId: spot.id,
      licensePlate: vehicle.licensePlate,
      issuedAt: new Date(),
    };

    this.activeTicketsById.set(ticket.id, ticket);
    this.activeTicketByLicensePlate.set(vehicle.licensePlate, ticket);
    return ticket;
  }

  exit(ticketId: string): void {
    const ticket = this.activeTicketsById.get(ticketId);
    if (!ticket) {
      throw new Error("Ticket is invalid or already used");
    }

    const spot = this.spotsById.get(ticket.spotId);
    if (!spot) {
      throw new Error("Assigned spot does not exist");
    }

    spot.vacate();
    this.activeTicketsById.delete(ticket.id);
    this.activeTicketByLicensePlate.delete(ticket.licensePlate);
  }

  availableSpotCount(): number {
    return [...this.spotsById.values()]
      .filter(spot => spot.isAvailable())
      .length;
  }

  private findCompatibleSpot(vehicle: Vehicle): ParkingSpot | undefined {
    return [...this.spotsById.values()]
      .find(spot => spot.isAvailable() && spot.canFit(vehicle));
  }
}
```

The important discussion is not the syntax. Explain the flow:

1. `ParkingLot` rejects a duplicate vehicle.
2. It finds a compatible available spot.
3. `ParkingSpot` validates and changes its own occupancy.
4. `ParkingLot` creates indexes needed by the exit workflow.
5. `exit` vacates the spot and removes the active ticket.

Also call out the complexity: parking currently scans spots in `O(n)` time, while ticket lookup and exit are `O(1)`.

### Verify with a concrete scenario

Spend one or two minutes tracing a non-trivial example:

```ts
const lot = new ParkingLot([
  new ParkingSpot("M1", SpotType.Motorcycle),
  new ParkingSpot("C1", SpotType.Compact),
  new ParkingSpot("L1", SpotType.Large),
]);

const truck = { licensePlate: "TRK-1", type: VehicleType.Truck };
const ticket = lot.park(truck);

// M1 and C1 are incompatible, so the truck receives L1.
// availableSpotCount() is now 2.

lot.exit(ticket.id);

// L1 is available again and the ticket cannot be reused.
```

Then name edge cases rather than coding every one:

- A second truck arrives while `L1` is occupied.
- The same license plate calls `park` twice.
- An unknown or already-used ticket calls `exit`.
- The lot is created with duplicate spot IDs.

If the walkthrough reveals a flaw, correct it openly. Self-verification is a positive interview signal.

---

## 5. Handle Extensibility Follow-Ups

Senior candidates should expect “What if we add...?” questions. Stay high-level first: identify what changes, which boundary absorbs it, and whether the existing model remains valid. Do not rewrite the whole solution unless asked.

### Different spot-assignment policies

If the system must support nearest-first, smallest-compatible, or accessibility-aware allocation, extract the changing algorithm:

```ts
interface SpotAssignmentStrategy {
  select(spots: ParkingSpot[], vehicle: Vehicle): ParkingSpot | undefined;
}

class FirstCompatibleSpot implements SpotAssignmentStrategy {
  select(spots: ParkingSpot[], vehicle: Vehicle): ParkingSpot | undefined {
    return spots.find(spot =>
      spot.isAvailable() && spot.canFit(vehicle)
    );
  }
}
```

Inject the strategy into `ParkingLot` and delegate `findCompatibleSpot` to it. This is justified now because a real variation point has appeared.

### Other common follow-ups

| New requirement | Likely evolution |
|---|---|
| Multiple floors | Add a `ParkingFloor` that owns spots; let the lot coordinate floors |
| Pricing and payment | Add exit time and a `FeePolicy`; keep payment behind a gateway |
| Faster allocation | Index available spots by type instead of scanning every spot |
| Reservations | Model a reservation lifecycle and distinguish reserved from occupied |
| Concurrent entrances | Make find-and-occupy atomic using a lock or storage transaction |
| Persistence | Put ticket/spot storage behind focused repository contracts |

Do not claim that an in-memory Singleton solves cross-server coordination. Under concurrency, spot allocation is a critical section: two requests must not observe and claim the same available spot.

---

## Interview Checklist

```text
Requirements
□ Clarify capabilities, rules, errors, and scope.
□ Write and confirm a short specification.

Entities and relationships
□ Select only objects with meaningful state or behavior.
□ Identify the orchestrator, ownership, and dependencies.

Class design
□ Derive state and methods directly from requirements.
□ Keep invariants with the object that owns the state.
□ Prefer small APIs and composition over speculative abstractions.

Implementation
□ Confirm the expected coding depth.
□ Implement the core happy path, then important failures.
□ Explain collaboration, state transitions, and complexity.
□ Trace one concrete scenario.

Extensibility
□ Follow the interviewer’s proposed change.
□ Identify the variation point and explain the smallest clean evolution.
□ State trade-offs; do not force a design pattern.
```

The goal is not to produce the most elaborate class diagram. It is to show a disciplined path from requirements to a correct object model, make ownership and invariants obvious, and evolve the design without unnecessary complexity.
