clean up the app.py's try-except blocks and syntax
add keyboard listener to the presentation controller
add documentation
add test

---

In the app.py:

Remove unnecessary validate_speaker_resolution function and replace it with the speaker_manager.resolve function usages in commands, so it does same things, just adjust the command logic accordingly or edit speaker_manager.resolve implementation if needed.

Merge all try-except blocks' expect commands only one same as 'except Exception as e', don't make separate except blocks like 'except ValueError as e' for each command. All should use 'except Exception as e' in high level, no extra exception blocks.
Don't make extra catches like this:
except typer.Exit: # Re-raise typer.Exit to avoid catching it in the generic handler
raise

Just catch them with `except Exception as e:`

Remove masking in API key

Clean up the code to be more concise and readable, avoid long comments and docstrings. Apply KISS, DRY, and YAGNI principles.
