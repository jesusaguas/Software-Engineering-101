# SOLID Principles for LLD/OOD Interviews

SOLID is a set of design principles for making object-oriented code easier to read, change/extend, test. In an interview, use them to justify design decisions—not as rules that force every class to be tiny or every dependency to have an interface.

| Principle | Core idea | Question to ask |
|---|---|---|
| **S**ingle Responsibility | One reason to change | Does this class own more than one concern? |
| **O**pen/Closed | Extend behavior without rewriting stable code | Can I add a variant without editing a large conditional? |
| **L**iskov Substitution | Subtypes must honor the base contract | Can callers use any implementation without surprises? |
| **I**nterface Segregation | Prefer small, client-focused contracts | Is a client forced to depend on methods it does not use? |
| **D**ependency Inversion | Business policy depends on abstractions | Can I replace infrastructure without changing domain logic? |

---

## 1. Single Responsibility Principle (SRP)

> A module/class should have one reason to change.

Separate responsibilities that change for different reasons. A checkout service should coordinate checkout, not also format receipts, write SQL, and send email.

```ts
class CheckoutService {
  constructor(
    private orders: OrderRepository,
    private payments: PaymentGateway,
    private receipts: ReceiptSender,
  ) {}

  async checkout(cart: Cart): Promise<Order> {
    const order = Order.from(cart);
    await this.payments.charge(order.total);
    await this.orders.save(order);
    await this.receipts.send(order);
    return order;
  }
}
```

Each collaborator has a distinct responsibility. `CheckoutService` retains one clear job: orchestrating the use case.

**Interview signal:** Describe the responsibility in one sentence. Split a class when it mixes concerns with different actors or rates of change—not merely because it has many methods.

---

## 2. Open/Closed Principle (OCP)

> Software should be open for extension and closed for modification.

New behavior should usually be added through a new implementation rather than by repeatedly editing stable code.

```ts
interface DiscountPolicy {
  discountFor(order: Order): Money;
}

class SeasonalDiscount implements DiscountPolicy {
  discountFor(order: Order): Money {
    return order.total.multiply(0.10);
  }
}

class PriceCalculator {
  constructor(private policies: DiscountPolicy[]) {}

  totalFor(order: Order): Money {
    const discount = this.policies
      .map(policy => policy.discountFor(order))
      .reduce((sum, value) => sum.add(value), Money.zero());

    return order.total.subtract(discount);
  }
}
```

A new discount is a new `DiscountPolicy`; the calculator stays unchanged.

**Interview signal:** Look for conditionals that select behavior by type, such as `if (paymentType === ...)`. Strategy, polymorphism, or composition may create a useful extension point. Do not introduce one until variation is expected.

---

## 3. Liskov Substitution Principle (LSP)

> Any implementation of a contract must be safely usable wherever that contract is expected.
> Subclasses should be substitutable for their base classes without breaking the application.

A subtype must preserve the observable behavior promised by its parent:

- Accept all valid inputs the contract accepts.
- Fulfill its promised outputs and effects.
- Preserve invariants.
- Avoid introducing unexpected failures or unsupported operations.

```ts
interface PaymentMethod {
  pay(amount: Money): Promise<PaymentResult>;
}

class CreditCard implements PaymentMethod {
  async pay(amount: Money): Promise<PaymentResult> {
    return chargeCard(amount);
  }
}
```

An implementation that throws `UnsupportedOperationError` for a valid positive amount violates the contract. If some payment methods only authorize while others immediately capture, model those as different capabilities instead of pretending they are interchangeable.

**Classic warning:** Modeling `Square extends Rectangle` often breaks LSP because independently setting width and height conflicts with a square’s invariant. Prefer separate shapes implementing a shared `area()` contract.

**Interview signal:** State the behavioral contract, not just the method signatures. Composition is often safer than inheritance when subtype behavior differs.

---

## 4. Interface Segregation Principle (ISP)

> Clients should not depend on methods they do not need.

Prefer focused interfaces shaped around client needs.

```ts
interface OrderReader {
  findById(id: string): Promise<Order | null>;
}

interface OrderWriter {
  save(order: Order): Promise<void>;
}

class OrderQueryService {
  constructor(private orders: OrderReader) {}
}
```

The query service does not depend on `save`, `delete`, or administrative operations. Implementations may still implement multiple focused interfaces.

**Interview signal:** A large interface with irrelevant methods, no-op implementations, or `UnsupportedOperationError` is a strong smell. Split by capability or use case, not mechanically into one-method interfaces.

---

## 5. Dependency Inversion Principle (DIP)

> High-level business policy should not depend directly on low-level infrastructure. Both should depend on abstractions owned around the business need.
> Depend on abstractions (interfaces), not concretions (specific classes).

```ts
interface OrderRepository {
  save(order: Order): Promise<void>;
}

class SqlOrderRepository implements OrderRepository {
  async save(order: Order): Promise<void> {
    // SQL-specific implementation.
  }
}

interface PaymentGateway {
  charge(amount: Money): Promise<void>;
}

class StripePaymentGateway implements PaymentGateway {
  async charge(amount: Money): Promise<void> {
    // Stripe-specific implementation.
  }
}

class CheckoutService {
  constructor(
    private orders: OrderRepository,
    private payments: PaymentGateway,
    private receipts: ReceiptSender,
  ) {}
}

const service = new CheckoutService(
  new SqlOrderRepository(),
  new StripePaymentGateway(),
  new EmailReceiptSender(),
);
```

`CheckoutService` knows what it needs, not whether orders use PostgreSQL or payments use Stripe. Concrete dependencies are supplied at the composition root.

**DIP vs dependency injection:** DIP is the design principle; dependency injection is a technique for providing dependencies. Constructor injection makes required collaborators explicit and simplifies testing.

**Interview signal:** Keep domain/use-case code independent of databases, frameworks, and external APIs. Introduce an abstraction at a volatile boundary or when multiple implementations/testing justify it—not for every class.

---

## Applying SOLID in an Interview

1. Start from requirements and identify likely changes: payment providers, notification channels, pricing rules, persistence.
2. Model core entities and behavioral contracts.
3. Use composition and focused interfaces at genuine variation points.
4. Keep business rules separate from infrastructure.
5. Explain the trade-off: extra abstractions cost complexity, so begin simple and refactor when change pressure appears.

A strong explanation sounds like:

> “Payment providers vary independently from checkout. I’ll define a small `PaymentGateway` contract and inject it into `CheckoutService`. This keeps checkout focused, lets us add providers without changing its workflow, and makes the use case testable with a fake gateway.”

Avoid:

- Naming principles without connecting them to a concrete design decision.
- Creating an interface for every class “because SOLID.”
- Deep inheritance hierarchies; prefer composition for independently varying behavior.
- Splitting cohesive logic so aggressively that the flow becomes hard to follow.
- Claiming a design is universally correct—state assumptions and trade-offs.

The goal is not maximum abstraction. It is a design whose responsibilities and contracts are clear, whose expected changes are localized, and whose complexity is justified.
