# Object-Oriented Programming for LLD Interviews

OOP concepts are language mechanisms for building the clean object models discussed in `LLD.md` and `SOLID.md`.

| Concept | Core idea | Interview signal |
|---|---|---|
| **Encapsulation** | Protect state and let the owner enforce its rules | Private fields, behavior-focused methods, no leaked mutable collections |
| **Abstraction** | Expose what a component does, hide how it does it | Small contracts around complexity or genuine variation |
| **Polymorphism** | Different implementations respond to the same contract | Call behavior through an interface instead of checking concrete types |
| **Inheritance** | Derive a specialized class from a base implementation | Use only for a stable, substitutable “is-a” relationship |

---

## 1. Encapsulation

> An object owns its state and controls how that state changes.
> Encapsulation means keeping an object’s data private and letting the object control how that data is used. You interact with it through simple methods instead of reaching in and changing its internal details yourself.

If callers can modify fields directly, they can bypass validation and break invariants. Keep state private and expose operations that express intent.

### Bad: No Encapsulation

```ts
class ParkingSpot {
  occupy(_vehicle: Vehicle): void {}
}

class Vehicle {
  constructor(public type: string) {}
}

class ParkingLot {
  public spots: ParkingSpot[] = [];
}
```

Any caller can change the collection without respecting the parking lot’s rules.

### Good: Proper Encapsulation

```ts
class ParkingSpot {
  occupy(_vehicle: Vehicle): void {}
}

class Vehicle {
  constructor(public type: string) {}
}

class ParkingLot {
  private spots: ParkingSpot[] = [];

  parkVehicle(vehicle: Vehicle): boolean {
    const spot = this.findAvailableSpot(vehicle);
    if (!spot) return false;
    spot.occupy(vehicle);
    return true;
  }

  private findAvailableSpot(_vehicle: Vehicle): ParkingSpot | null {
    return this.spots[0] ?? null;
  }

  getSpots(): ParkingSpot[] {
    return [...this.spots];
  }
}
```

Callers can ask the lot to park a vehicle but cannot replace or resize its internal collection. `getSpots()` returns a copy, so changing the returned array does not mutate the lot’s array.

### What interviewers look for

- Fields are private unless there is a reason otherwise.
- Mutations happen through methods that enforce invariants.
- Collections are returned as immutable views, copies, or purpose-specific results.
- The object that owns the data also owns the rules around that data.

Getters and setters are not automatically good encapsulation. A public `setBalance()` still allows callers to bypass `deposit()` and `withdraw()`. Prefer meaningful operations over unrestricted access.

---

## 2. Abstraction

> Expose an essential contract (interface) while hiding implementation details.

The caller should know what capability it needs, not vendor APIs, storage details, or the algorithm behind it.

### Bad: No Abstraction

```ts
class Order {
  constructor(public total: number, public creditCard: string) {}
}

class StripeAPI {
  setApiKey(_key: string): void {}
  createCharge(_amount: number, _card: string): void {}
}

class OrderService {
  private apiKey = "";

  checkout(order: Order): void {
    const stripe = new StripeAPI();
    stripe.setApiKey(this.apiKey);
    stripe.createCharge(order.total, order.creditCard);
  }
}
```

`OrderService` constructs Stripe directly and understands its configuration and API. Replacing Stripe or testing checkout now requires changing the service.

### Good: Proper Abstraction

```ts
interface PaymentMethod {
  process(amount: number): boolean;
}

class CreditCardPayment implements PaymentMethod {
  process(_amount: number): boolean {
    return true;
  }
}

class PayPalPayment implements PaymentMethod {
  process(_amount: number): boolean {
    return true;
  }
}

class Order {
  constructor(public total: number, public creditCard: string) {}
}

class OrderService {
  constructor(private paymentMethod: PaymentMethod) {}

  checkout(order: Order): void {
    this.paymentMethod.process(order.total);
  }
}
```

`PaymentMethod` defines the contract, while each implementation owns its details. `OrderService` does not need to know which implementation it receives.

### Choosing a useful abstraction

Define the contract from the caller’s needs:

- Too vague: `execute()` or `doWork()` reveals no intent.
- Too concrete: `createStripeCharge()` leaks the implementation.
- Focused: `process(amount)` describes the required capability.

Introduce abstractions at complicated or volatile boundaries: payment providers, repositories, notification channels, allocation policies, or external SDKs. Do not create an interface for every class by default.

### Encapsulation vs abstraction

- **Encapsulation** protects an object’s internal state and invariants.
- **Abstraction** simplifies how other objects use a capability.

A well-designed class usually uses both.

---

## 3. Polymorphism

> Multiple types satisfy the same contract, each providing its own behavior.

Instead of asking what concrete type an object is, call the contract and let the object respond.

### Bad: No Polymorphism

```ts
class ParkingSpot {}

class Vehicle {
  constructor(public type: string) {}
}

class ParkingLot {
  parkVehicle(v: Vehicle): boolean {
    if (v.type === "car") {
      const spot = this.findSpotBySize("regular");
      return spot !== null;
    } else if (v.type === "motorcycle") {
      const spot = this.findSpotBySize("motorcycle");
      return spot !== null;
    } else if (v.type === "truck") {
      const spot = this.findSpotBySize("large");
      return spot !== null;
    }
    return false;
  }

  private findSpotBySize(_size: string): ParkingSpot | null {
    return null;
  }
}
```

Every new vehicle type requires editing this conditional. If the same type checks appear elsewhere, the rules become duplicated and easy to contradict.

### Good: Using Polymorphism

```ts
type SpotSize = "regular" | "motorcycle" | "large";

interface Vehicle {
  getRequiredSpotSize(): SpotSize;
}

class Car implements Vehicle {
  getRequiredSpotSize(): SpotSize {
    return "regular";
  }
}

class Motorcycle implements Vehicle {
  getRequiredSpotSize(): SpotSize {
    return "motorcycle";
  }
}

class Truck implements Vehicle {
  getRequiredSpotSize(): SpotSize {
    return "large";
  }
}

class ParkingSpot {}

class ParkingLot {
  parkVehicle(v: Vehicle): boolean {
    const required = v.getRequiredSpotSize();
    const spot = this.findSpotBySize(required);
    return spot !== null;
  }

  private findSpotBySize(_size: SpotSize): ParkingSpot | null {
    return null;
  }
}
```

`ParkingLot` no longer checks concrete vehicle types. A new vehicle supplies its required size without changing the lot.

### When to use it

Polymorphism is useful when:

- Behavior genuinely differs by type.
- New implementations are expected.
- Callers should treat every implementation uniformly.
- Repeated type checks are spreading through the code.

It is not necessary to replace every conditional. A small switch over a closed, stable set of values may be simpler. Polymorphism adds indirection and can make runtime behavior harder to trace, so explain the trade-off.

Every implementation must also honor the contract. If a subtype rejects valid operations or changes their meaning unexpectedly, it violates substitutability—the Liskov Substitution Principle.

---

## 4. Inheritance

> A subclass receives state or implementation from a base class and may specialize it.

Inheritance can remove genuine duplication when the relationship and shared behavior are stable.

### Good: Inheritance for Shared Implementation

```ts
abstract class BankAccount {
  protected balance = 0;

  deposit(amount: number): void {
    this.balance += amount;
  }

  withdraw(amount: number): boolean {
    if (this.balance < amount) return false;
    this.balance -= amount;
    return true;
  }

  getBalance(): number {
    return this.balance;
  }
}

class SavingsAccount extends BankAccount {
  private interestRate: number;
  constructor(rate: number) {
    super();
    this.interestRate = rate;
  }
}

class CheckingAccount extends BankAccount {
  private overdraftLimit: number;
  constructor(limit: number) {
    super();
    this.overdraftLimit = limit;
  }
}
```

Both account types safely reuse stable balance behavior without overriding the base contract.

### Why inheritance often breaks down

Inheritance tightly couples subclasses to the base class. Parent changes can affect every child, and subclasses may inherit state or behavior that does not make sense.

### Bad: Inheritance for Behavior Variation

```ts
class Car {
  startEngine(): void {
    // gasoline engine start logic
  }
}

class ElectricCar extends Car {
  startEngine(): void {
    // electric motor startup logic - completely different
  }
}
```

This hierarchy models a superficial category rather than shared behavior. A composed design makes the variation explicit:

### Good: Composition for Behavior Variation

```ts
interface Drivetrain {
  start(): void;
}

class GasEngine implements Drivetrain {
  start(): void {
    // gas engine startup logic
  }
}

class ElectricMotor implements Drivetrain {
  start(): void {
    // electric motor startup logic
  }
}

class Car {
  constructor(private drivetrain: Drivetrain) {}

  start(): void {
    this.drivetrain.start();
  }
}
```

Now `Car` delegates to any compatible drivetrain. Adding another drivetrain does not alter a class hierarchy.

### Inheritance decision test

Use inheritance only when all are true:

- The subtype is behaviorally an **is-a** version of the base type.
- It can honor the entire base contract.
- There is meaningful, stable implementation to reuse.
- Subclasses do not need to disable or radically redefine inherited behavior.

Otherwise, prefer an interface plus composition.

---

## Interface, Abstract Class, or Composition?

| Tool | Use when |
|---|---|
| **Interface** | Several types need the same contract without shared implementation |
| **Abstract class** | Closely related types share stable state or implementation |
| **Composition** | A class should delegate a capability that can vary independently |

Default to interfaces and composition for changeable behavior. Reach for an abstract class only when implementation reuse is real—not merely to establish a taxonomy.

---

## Interview Recognition Checklist

```text
State or collections are publicly mutable
→ Encapsulate them and expose behavior-focused methods.

A service knows vendor or infrastructure details
→ Introduce a caller-focused abstraction at that boundary.

Type checks select different behavior in several places
→ Consider polymorphism or Strategy.

A subclass overrides most behavior or throws "unsupported"
→ The inheritance model is probably wrong; use composition or split contracts.

You are creating interfaces and subclasses without expected variation
→ Simplify. OOP does not mean maximizing the number of classes.
```

In the interview, demonstrate these concepts through the design rather than reciting definitions. Make ownership clear, protect invariants, define focused contracts, and use inheritance only when substitutability and stable code reuse justify its cost.
