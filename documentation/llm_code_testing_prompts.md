# LLM-Based Code Testing Prompts

A collection of prompts for lightweight semantic code analysis. Each prompt tests for specific patterns and potential issues in your code.

## 1. Import Analysis
```
Analyze the imports in this file and explain:
1. What each imported library/module is used for
2. Are there any unused or redundant imports?
3. Are there any imports that might cause compatibility issues?

[PASTE CODE HERE]
```

## 2. Function & Resource Analysis
```
For each function and global resource in this code:
1. Summarize what it does in one sentence
2. Identify its inputs and outputs
3. Note any side effects
4. Highlight any potential edge cases or error conditions

[PASTE CODE HERE]
```

## 3. Dependency Check
```
Analyze this code and identify:
1. What external dependencies does it require to run?
2. Are there any implicit dependencies not clearly imported?
3. Which parts of the code could run independently?

[PASTE CODE HERE]
```

## 4. Consistency Check
```
Compare these two files and identify:
1. Are there any inconsistencies in how they interact?
2. Do they make compatible assumptions about data structures?
3. Are there any potential race conditions or timing issues?

File 1:
[PASTE CODE 1]

File 2:
[PASTE CODE 2]
```

## 5. Issue Detection
```
Review this code and identify potential issues:
1. Are there any logical errors or bugs?
2. Any performance concerns?
3. Security vulnerabilities?
4. Error handling gaps?
5. Maintainability concerns?

[PASTE CODE HERE]
```

## 6. Test Case Generation
```
Based on this code, suggest test cases that would:
1. Cover the main functionality
2. Test edge cases
3. Verify error handling
4. Check performance under load (if applicable)

[PASTE CODE HERE]
```

## 7. Documentation Assessment
```
Evaluate the documentation in this code:
1. Are functions and classes adequately documented?
2. Do docstrings explain parameters and return values?
3. Are complex sections of code explained with comments?
4. What documentation is missing or could be improved?

[PASTE CODE HERE]
```

## 8. API Usage Check
```
For the external libraries used in this code:
1. Are they being used according to best practices?
2. Are there any deprecated methods or parameters?
3. Are there newer/better alternatives to the APIs being used?

[PASTE CODE HERE]
```

## Usage Tips

- Copy-paste your code into these prompts when interacting with Amazon Q
- For larger files, consider analyzing sections separately
- Provide additional context about your project when necessary
- Use the results as guidance, not as a replacement for proper testing
- Combine multiple prompts for more comprehensive analysis
