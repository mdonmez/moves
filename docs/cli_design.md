### **The "Direct Summary" CLI Design System: Documentation & Principles**

This document outlines the final design philosophy and complete reference for the `moves` CLI. The system is crafted to be clean, direct, and highly readable, providing a professional and consistent user experience for both beginners and power users.

#### **Core Principles**

1.  **Direct Summary Headline:** Every command's output begins with a single, clear sentence that summarizes the result. It immediately answers the user's primary question: "Did it work?". Failure is communicated just as directly as success.

2.  **Cascading Details:** Supporting information is always presented below the summary headline. A consistent four-space indent creates a clear visual hierarchy, and the `->` arrow serves as a lightweight, elegant separator for key-value pairs. This creates a cascading flow of information that is easy to scan.

3.  **Minimalist Structure:** The design intentionally avoids visual clutter. There are no boxes, borders, or excessive symbols (`✓`, `✗`). The structure is defined purely by whitespace and a simple, consistent layout, making the output feel clean and integrated with the native terminal environment.

4.  **Clarity and Consistency:** The language is active and direct. The format for every command is predictable. A user who has learned one command intuitively understands how to read the output of any other command in the application.

---

### **The Final Design Reference**

Here is the complete and finalized output design for every command in the `moves` CLI.

#### **`moves speaker add`**

**Success:**

```
Speaker 'nehir' (nehir-IJZrw) added
    ID -> nehir-IJZrw
    Presentation -> C:\Users\...\input_presentation.pdf
    Transcript -> C:\Users\...\input_transcript.pdf
```

**Failure:**

```
Could not add speaker 'nehir'.
    File not found or permission denied.
```

---

#### **`moves speaker edit`**

**Success:**

```
Speaker 'nehir' updated.
    Presentation -> C:\Users\...\new_presentation.pdf
```

---

#### **`moves speaker list`**

```
Registered Speakers (2)

ID              NAME    STATUS
─────────────── ──────  ──────────
nehir-IJZrw     nehir   Ready
john-4a8bF      john    Not Ready
```

**No Speakers:**

```
No speakers are registered.
```

---

#### **`moves speaker show`**

```
Showing details for speaker 'nehir' (nehir-IJZrw)
    ID -> nehir-IJZrw
    Name -> nehir
    Status -> Ready
    Presentation -> C:\Users\...\input_presentation.pdf
    Transcript -> C:\Users\...\input_transcript.pdf
```

---

#### **`moves speaker process`**

**During Processing (Single Speaker):**

```
Processing speaker 'nehir' (nehir-IJZrw)...
```

**During Processing (Multiple Speakers):**

```
Processing 2 speakers...
```

**Success (Single Speaker):**

```
Speaker 'nehir' (nehir-IJZrw) processed.
    65 sections created.
```

**Success (Multiple Speakers):**

```
2 speakers processed.
    'nehir' (nehir-IJZrw) ->  65 sections created.
    'john' (john-4a8bF) -> 42 sections created.
```

**Failure:**

```
Processing failed for 'nehir' (nehir-IJZrw).
    Something occured during processing.
```

---

#### **`moves speaker delete`**

```
Speaker 'nehir' (nehir-IJZrw) deleted.
```

---

#### **`moves presentation control`**

**Start-up:**

```
Starting presentation control for 'nehir' (nehir-IJZrw).
    65 sections loaded
    READY & LISTENING...
---
```

**Live Status (Single, Overwriting Line):**
_This line should constantly update in place, not print new lines. (Streaming Mode)_

_Initial State:_

```
[ 1/65 ]
```

_While Hearing Speech:_

```
[ 1/65 ]
Speech -> "giant future imagine a world where tiny"
Match  -> "giant future imagine a world where tiny"
```

_When a new section is Confirmed:_

```
[ 2/65 ]
Speech -> "giant future imagine a world where tiny"
Match  -> "giant future imagine a world where tiny"

```

**Shutdown:**

```
Presentation control stopped.
```

---

#### **`moves settings list`**

```
Application Settings.
    model (LLM Model) -> gemini-2.5-flash-lite
    key (API Key) -> AIzaSyAU...77QA
```

**With a missing value:**

```
Application Settings.
    model (LLM Model) -> gemini-2.5-flash-lite
    key (API Key) -> Not configured
```

---

#### **`moves settings set`**

```
Setting 'model' updated.
    New Value -> gemini/gemini-2.5-flash-lite
```

---

#### **`moves settings unset`**

```
Setting 'key' reset to default.
    New Value -> Not configured
```
