# Design Patterns for LLD/OOD Interviews

Design patterns are reusable ways to organize collaborating objects. They are not goals by themselves: start from the requirements, identify what varies, and apply a pattern only when it makes responsibilities or change easier to manage.

For most Senior Software Engineer interviews, knowing the following patterns—and their trade-offs—is more valuable than memorizing the entire Gang of Four catalog.

| Design pattern | Design problem | Use cases |
|---|---|---|
| **Strategy** | Choose one of several interchangeable behaviors | Pricing, routing, payment methods |
| **Factory** | Centralize creation of related implementations | Payment providers, notification senders, parsers |
| **Builder** | Construct a complex object step by step | Queries, requests, configuration objects |
| **Singleton** | Ensure one shared instance within a process | Configuration, registries, in-process resource managers |
| **Adapter** | Make an incompatible API fit your contract | Third-party APIs, legacy integrations |
| **Facade** | Provide a simple entry point to a complex subsystem | Checkout workflows, media processing, SDKs |
| **Decorator** | Add optional behavior by wrapping an object | Caching, logging, metrics, retries |
| **Observer** | Notify multiple interested consumers | Domain events, UI events, notifications |
| **State** | Change behavior as an object changes state | Orders, tickets, vending machines, elevators |
| **Command** | Treat an action as data | Job queues, scheduling, retries, undo |
| **Composite** | Represent part-whole trees uniformly | File systems, UI trees, product bundles |

---

## 1. Strategy

> Encapsulate interchangeable algorithms behind a common contract.

```ts
interface PricingStrategy {
  priceFor(ride: Ride): Money;
}

class StandardPricing implements PricingStrategy {
  priceFor(ride: Ride): Money {
    return ride.distance.multiply(STANDARD_RATE);
  }
}

class SurgePricing implements PricingStrategy {
  priceFor(ride: Ride): Money {
    return ride.distance.multiply(SURGE_RATE);
  }
}

class FareCalculator {
  constructor(private pricing: PricingStrategy) {}

  calculate(ride: Ride): Money {
    return this.pricing.priceFor(ride);
  }
}
```

Use it when business rules vary independently: pricing, routing, ranking, validation, payment, or retry policies. It replaces growing conditionals with composable behavior.

**Trade-off:** More types and indirection. A small, stable conditional is often clearer.

**Interview signal:** Explain who selects the strategy and when—configuration, request type, or runtime context.

---

## 2. Factory

> Centralize creation when callers should not know which concrete implementation to construct.
> Instead of `new XClass()` to instatiate an object, you use a function to do it;

```ts
// Without factory
const button1 = platform === "ios" ? new IOSButton() : new AndroidButton();
const button2 = platform === "ios" ? new IOSButton() : new AndroidButton();

// With factory
class ButtonFactory {
  static createButton(platform: string) {
    switch (platform) {
      case "ios": return new IOSButton();
      case "android": return new AndroidButton();
    }
  }
}
const button1 = ButtonFactory.createButton(platform);
const button2 = ButtonFactory.createButton(platform);
``` 

The conditional has not disappeared; it is isolated at the creation boundary.

Use a simple factory when creation depends on a type or configuration. A **Factory Method** lets subclasses choose what to create, but inheritance is rarely necessary. An **Abstract Factory** creates families of related objects and is useful only when those families must remain consistent.

**Trade-off:** Do not create a factory for a single trivial constructor. Dependency injection can supply known dependencies directly; it complements rather than replaces factories.

---

## 3. Builder

> Construct a complex object through readable, validated steps.

```ts
class SearchRequestBuilder {
  private query?: string;
  private filters: Record<string, string> = {};
  private page?: number;
  private pageSize?: number;

  withQuery(query: string): this {
    this.query = query;
    return this;
  }

  withFilter(key: string, value: string): this {
    this.filters[key] = value;
    return this;
  }

  withPagination(page: number, pageSize: number): this {
    this.page = page;
    this.pageSize = pageSize;
    return this;
  }

  build(): SearchRequest {
    if (!this.query) throw new Error("Query is required");
    return new SearchRequest(this.query, this.filters, this.page, this.pageSize);
  }
}

const request = new SearchRequestBuilder()
  .withQuery("design patterns")
  .withFilter("language", "typescript")
  .withPagination(0, 20)
  .build();
```

Use it when construction has many optional parameters, must occur in stages, or needs final cross-field validation. The built object should usually be immutable and valid.

**Trade-off:** Named parameters or a typed options object are simpler when there are few fields. Avoid builders that allow `build()` to produce invalid objects.

---

## 4. Singleton

> Ensure a class has one instance within a process and provide a shared access point to it.

```ts
class Settings {
  private static instance?: Settings;
  public readonly darkMode: boolean = true;

  // prevent new() with private constructor
  private constructor() {}

  static getInstance(): Settings {
    if (!Settings.instance) {
      Settings.instance = new Settings();
    }
    return Settings.instance;
  }
}
```

In Javascript/TypeScript, we have object literals and the concept of global data, so objects are passed around by reference. We get the same characteristics of a singleton by simply creating a global object literal and exporting it. This is a simpler approach than creating a singleton class.
```ts
export const settings = {
  darkMode: true,
};
```

In other languages, a singleton class is often implemented with a private constructor and a static accessor.

Use it when exactly one in-process instance represents a shared resource or registry. In multithreaded languages, initialization must also be thread-safe.

**Trade-off:** Global access hides dependencies, couples tests through shared mutable state, and complicates concurrency. Prefer creating one instance at the application’s composition root and injecting it. Also remember that a Singleton is **one instance per process**, not one across multiple servers; distributed uniqueness requires coordination such as a database constraint, lock, or leader election.

---

## 5. Adapter

> Translate an external or incompatible interface into the interface your application expects.

```ts
interface PaymentGateway {
  charge(amount: Money): Promise<PaymentResult>;
}

class StripeAdapter implements PaymentGateway {
  constructor(private stripe: StripeClient) {}

  async charge(amount: Money): Promise<PaymentResult> {
    const response = await this.stripe.createPaymentIntent({
      amount: amount.inCents(),
    });
    return PaymentResult.fromStripe(response);
  }
}


const paymentGateway: PaymentGateway = new StripeAdapter(new StripeClient("sk_test_..."));
const result = await paymentGateway.charge(new Money(10, "USD"));
```

The adapter contains vendor-specific types, calls, and error translation. Domain code remains stable if the external API changes or another provider is introduced.

**Trade-off:** An adapter should translate boundaries, not accumulate unrelated business logic.

**Interview signal:** Adapters are especially credible around payment providers, storage SDKs, messaging clients, and legacy APIs.

---

## 6. Facade

> Expose a simple interface over a set of more complex subsystem interactions (dependencies).
> Simplified API to hide low-level details.

```ts
class House {
    private plumbing: PlumbingSystem;
    private electrical: ElectricalSystem;

    constructor() {
        this.plumbing = new PlumbingSystem();
        this.electrical = new ElectricalSystem();
    }

    public turnOn(): void {
        this.plumbing.setPressure(500);
        this.plumbing.turnOnWater();
        this.electrical.setVoltage(120);
        this.electrical.turnOnPower();
    }
    public turnOff(): void {
        this.plumbing.turnOffWater();
        this.electrical.turnOffPower();
    }
}

const client = new House();
client.turnOn();   // Low-level details are hidden from the client
client.turnOff(); 
```

**Trade-off:** A facade can become a “god object” if it absorbs business rules from every component. Keep it focused on simplifying and coordinating a cohesive workflow.

**Facade vs Adapter:** A facade simplifies a subsystem’s interface; an adapter translates an incompatible interface into the contract a client expects.

---

## 7. Decorator

> Structural design pattern that allows you to dynamically attach new behaviors to an object by placing it inside special wrapper objects.

![](../images/Low-Level%20Design/decorator.jpeg)


```ts
interface Coffee {
    getDescription(): string;
    getCost(): number;
    getBrand(): string;
}

class SimpleCoffee implements Coffee {
    getDescription(): string { return "Simple Coffee";}
    getCost(): number { return 5; }
    getBrand(): string { return "Generic"; }
}

abstract class CoffeeDecorator implements Coffee {
    // We use 'protected' so child classes can access the wrapped coffee object
    constructor(protected coffee: Coffee) {}

    // "abstract" keyword forces child classes to implement these methods
    abstract getDescription(): string;
    abstract getCost(): number;

    getBrand(): string {
        return this.coffee.getBrand(); // We are not changing the brand, so we can delegate this method to the wrapped coffee object
    }
}

class MilkDecorator extends CoffeeDecorator {
    constructor(coffee: Coffee) { super(coffee); }

    getDescription(): string { return this.coffee.getDescription() + ", Milk"; }
    getCost(): number { return this.coffee.getCost() + 2; }
}

class SugarDecorator extends CoffeeDecorator {
    constructor(coffee: Coffee) { super(coffee); }

    getDescription(): string { return this.coffee.getDescription() + ", Sugar"; }
    getCost(): number { return this.coffee.getCost() + 1; }
}

const simpleCoffee = new SimpleCoffee();
// Add milk to the coffee
const milkCoffee = new MilkDecorator(simpleCoffee);
// Add sugar to the coffee with milk
const sugarMilkCoffee = new SugarDecorator(milkCoffee);
// Get the description and cost of the final coffee
console.log(sugarMilkCoffee.getDescription()); // Simple Coffee, Milk, Sugar
console.log(sugarMilkCoffee.getCost()); // 8
```

Decorators work well for caching, logging, metrics, authorization, retries, or compression. Multiple decorators can be composed without modifying the core implementation.

**Trade-off:** Wrapper order can affect behavior, and a deep chain is harder to debug. Cross-cutting concerns may instead belong in framework middleware.

**Decorator vs Adapter:** A decorator preserves the contract and adds behavior; an adapter changes one contract into another.

---

## 8. Observer

> Let multiple subscribers react when a publisher emits an event.

```ts
// A callback function that handles an order placed event
type OrderPlacedHandler = (order: Order) => Promise<void>;

class OrderEvents {
  private handlers: OrderPlacedHandler[] = [];

  subscribe(handler: OrderPlacedHandler): void {
    this.handlers.push(handler);
  }

// call all the callback functions of the suscribers when an order is placed
  async orderPlaced(order: Order): Promise<void> {
    await Promise.all(this.handlers.map(handler => handler(order)));
  }
}
```

Use it when one event has several independent reactions, such as sending a receipt, updating analytics, and reserving inventory.

**Trade-off:** Decide whether delivery is synchronous or asynchronous, how failures are isolated, whether ordering matters, and how subscribers unsubscribe. For durable distributed workflows, an in-memory observer is insufficient; use a queue or event broker and address retries, idempotency, and delivery guarantees.

---

## 9. State

> Give an object different behavior for each state without scattering state checks across its methods.

```ts
interface OrderState {
  cancel(order: Order): void;
}

class PendingState implements OrderState {
  cancel(order: Order): void {
    order.transitionTo(new CancelledState());
  }
}

class ShippedState implements OrderState {
  cancel(): void {
    throw new InvalidOrderTransition("A shipped order cannot be cancelled");
  }
}
```

Use it when an entity has meaningful states, state-specific operations, and constrained transitions: orders, documents, vending machines, elevators, or support tickets.

**Trade-off:** For a few stable states, an enum plus explicit transition table may be clearer. Use State when conditionals are duplicated or each state owns substantial behavior.

**State vs Strategy:** Both delegate behavior. A strategy is usually selected from outside to vary an algorithm; state changes internally as the object moves through its lifecycle.

---

## 10. Command

> Represent a request as an object.
> Behavioral design pattern that takes an action (a request, a behavior, or an operation) and wraps it inside a standalone object, with an execute() method and optionally an undo() method. This allows you to decouple the object that invokes the operation from the one that knows how to perform it.

```ts
// Imagine you have a UI with different actions to perform, each with a button to do and undo. Instead of having the button directly call the action, you can create a command object that encapsulates the action and pass it to the button. This way, the button doesn't need to know how to perform the action, it just needs to know how to execute the command.
interface ICommand {
  execute(): Promise<void>;
  undo?(): Promise<void>;
}

class SendReminder implements ICommand {
  constructor(
    private notifications: NotificationSender,
    private message: Message,
  ) {}

  async execute(): Promise<void> {
    await this.notifications.send(this.message);
  }

  async undo(): Promise<void> {
    await this.notifications.cancel(this.message);
  }
}


const command = new SendReminder(notifications, message);
await command.execute(); // Send the reminder
await command.undo(); // Cancel the reminder
```

Use Command when actions must be queued, scheduled, logged, retried, authorized, or undone. It is common in job systems, editors, and workflow engines.

**Trade-off:** If the action is executed immediately and needs no lifecycle of its own, a normal method call is simpler. For retries, define idempotency and failure behavior.

---

## 11. Composite

> Treat individual objects and groups uniformly through the same contract.
> Structural design pattern used to build tree-like structures (part-whole hierarchies).

```ts
interface IFileSystemNode {
  readonly name: string;
  size(): number;
}

class File implements IFileSystemNode {
  constructor(public name: string, public bytes: number) {}
  
  size(): number { return this.bytes; }
}

class Directory implements IFileSystemNode {
    private entries: IFileSystemNode[] = [];

    constructor(public name: string) {}

    add(node: IFileSystemNode): void {
        this.entries.push(node);
    }

    size(): number {
        return this.entries.reduce((total, entry) => total + entry.size(), 0);
    }
}

// 1. Create the individual files (Leaves)
const resume = new File("resume.pdf", 500);
const coverLetter = new File("cover_letter.docx", 200);

// 2. Create the directories (Composites)
const rootDrive = new Directory("C:");
const documents = new Directory("Documents");

// 3. Build the tree structure
documents.add(resume);
documents.add(coverLetter);
rootDrive.add(documents);
```

Use it for genuine recursive part-whole structures: files and directories, UI trees, organization hierarchies, or nested product bundles.

**Trade-off:** Do not force unrelated leaf and container operations into one interface. Preserve substitutability.

---

## How to Apply Patterns in an Interview

1. Identify responsibilities, constraints, and what is likely to vary.
2. Start with the simplest working object model.
3. Name the design problem before naming the pattern.
4. Introduce the pattern and show how objects collaborate.
5. State its cost and when you would keep the simpler design.

A strong explanation sounds like:

> “Pricing rules vary and more will be added. I’ll isolate them behind a `PricingStrategy`, selected when the ride is created. That keeps fare calculation closed to repeated edits while making each rule independently testable.”
