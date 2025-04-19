# File-Level Design Pattern Anti-Pattern Detection Prompt

Analyze the specified file(s) for design pattern anti-patterns. Identify instances where common design patterns are implemented incorrectly or where anti-patterns are present that could lead to maintenance issues, performance problems, or code quality degradation.

## Instructions

1. First, read and analyze the content of the specified file path(s).
2. Identify and explain any of the following anti-patterns:
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

3. For each identified anti-pattern:
   - Explain why it's problematic
   - Describe the potential negative consequences
   - Suggest a specific refactoring approach
   - Provide a small code example of the improved implementation

4. Analyze code-level architecture concerns:
   - Circular dependencies
   - Violation of SOLID principles
   - Class cohesion issues
   - Inappropriate abstraction levels
   - Class/method responsibility violations

5. Consider language-specific anti-patterns relevant to the code's implementation language.

6. Prioritize the identified issues by severity and impact on maintainability.

7. Provide a summary of recommendations for improving the overall design pattern usage.

## File(s) to Analyze

Please analyze the following file path(s):
- [SPECIFY_FILE_PATH_1]
- [SPECIFY_FILE_PATH_2] (optional)
- [SPECIFY_FILE_PATH_3] (optional)

## Analysis Focus

Please focus on the following aspects (select as appropriate):
- [ ] Class design and responsibilities
- [ ] Method design and responsibilities
- [ ] Interface design
- [ ] Inheritance hierarchies
- [ ] Dependency management
- [ ] Specific design patterns: [LIST_SPECIFIC_PATTERNS]
