# Application/Service-Level Design Pattern Anti-Pattern Detection Prompt

Analyze the specified application or service for design pattern anti-patterns at both the code and architectural levels. Identify instances where common design patterns are implemented incorrectly or where anti-patterns are present that could lead to maintenance issues, performance problems, or code quality degradation.

## Instructions

1. First, examine the overall structure of the application/service by analyzing key directories and files.
2. Identify and explain any of the following code-level anti-patterns:
   - Singleton abuse or incorrect implementation
   - God objects/classes with too many responsibilities
   - Tight coupling between components
   - Inheritance abuse (deep inheritance hierarchies)
   - Interface bloat or anemic interfaces
   - Incorrect Factory pattern implementations
   - Observer pattern with memory leak potential
   - Strategy pattern with hardcoded strategies
   - Decorator pattern with broken composition
   - Command pattern with side effects
   - Facade patterns that leak abstractions
   - Adapter patterns that don't fully adapt interfaces
   - Improper dependency injection
   - Service locator anti-pattern usage

3. Identify and explain any of the following application/service-level anti-patterns:
   - Distributed monolith (services that are too interdependent)
   - Inappropriate service boundaries
   - Chatty communication between services
   - Shared databases across services
   - Lack of resilience patterns (circuit breakers, retries, etc.)
   - Improper error handling across service boundaries
   - Inconsistent data models across services
   - Lack of proper API versioning
   - Synchronous communication where asynchronous would be more appropriate
   - Improper use of event-driven architecture
   - Lack of proper service discovery mechanisms
   - Inconsistent logging and monitoring approaches

4. For each identified anti-pattern:
   - Explain why it's problematic
   - Describe the potential negative consequences
   - Suggest a specific refactoring approach
   - Provide a small code or architecture example of the improved implementation

5. Analyze broader architectural concerns:
   - Circular dependencies between modules/services
   - Violation of SOLID principles at the application level
   - Package/module cohesion issues
   - Inappropriate abstraction levels
   - Module/service responsibility violations
   - Scalability bottlenecks
   - Deployment complexity issues
   - Testing difficulties due to architectural choices

6. Consider language-specific and framework-specific anti-patterns relevant to the application's implementation.

7. Prioritize the identified issues by severity and impact on maintainability, scalability, and performance.

8. Provide a summary of recommendations for improving the overall architecture and design pattern usage.

## Application/Service to Analyze

Please analyze the following application/service located at: [SPECIFY_APPLICATION_PATH]

Key entry points or important files to consider:
- [ENTRY_POINT_1]
- [ENTRY_POINT_2]
- [IMPORTANT_FILE_1]
- [IMPORTANT_FILE_2]

## Analysis Scope

Please focus on the following aspects of the application/service (select as appropriate):
- [ ] Overall architectural patterns
- [ ] Service boundaries and interactions
- [ ] Data flow and state management
- [ ] Error handling and resilience
- [ ] Specific modules or components: [LIST_SPECIFIC_MODULES]
- [ ] Specific design patterns used: [LIST_SPECIFIC_PATTERNS]
