if there are errors

send errors to llm chat and ask it to create specific prompt based on errors. then go to claude or another ask it to fix.



can you create a valuation prompt that that expects to receive bad code and now has to instruct Claude or another model directly to fix


ChatGPT said:
Absolutely — here’s a purpose-built LLM prompt that:

Assumes you're feeding in code that failed validation

Automatically switches the LLM into repair mode

Gives clear structured feedback + next actions