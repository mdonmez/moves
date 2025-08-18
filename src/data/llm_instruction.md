**Your Primary Task:**
You are tasked with aligning presentation slide content with a corresponding speaker's transcript. Your goal is to generate a structured JSON output where each object represents a single slide from the presentation, and its content is the relevant segment of speech from the transcript.

**Inputs You Will Receive:**

1.  **Presentation Data:** Each object represents a slide and contains its text content, broken into numbered lines. This data may be the result of automated processing or translation and could contain noise, formatting artifacts, or be in a different language than the transcript.
2.  **Transcript Data:** A single string containing the full, continuous text of the speaker's narration. This is the authoritative source for the output content and language.

**Core Logic and Guiding Principles:**
For every slide in the `Presentation Data`, you must identify the corresponding portion of the `Transcript Data`. The meaning and topic of the slide's text are your primary clues for finding this match. Your final output must be cohesive and aligned with the logical structure and narrative intent of the presentation.

**Strict Rules and Constraints:**

1.  **Sections Count:** The number of sections in your final JSON output **must** be exactly equal to the number of slides provided in the `Presentation Data`.
2.  **Output Language:** The entire output, including all text within the `content` fields, **must** be in the same language as the input `Transcript Data`.
3.  **Indexing:** The `section_index` **must** be a zero-based, sequential integer (0, 1, 2, ...).
4.  **Noise Handling:** You must ignore irrelevant metadata, speaker names, titles, or nonsensical artifacts present in the `Presentation Data`. Focus only on the core message of each slide.
5.  **Content Sourcing and Mismatches:** You must adhere to the following priority for sourcing content:
    - **A. Use Transcript First:** Whenever possible, the `content` for a section **must** be extracted directly from the `Transcript Data`. You may slightly adjust or condense the transcript excerpt to better match the specific focus of the slide.
    - **B. Synthesize if Missing:** If a point is explicitly present in a slide but is completely missing from the transcript, you **must** generate a concise, plausible sentence that summarizes the slide's content. This text must be written in the transcript's language and style.
6.  **No Empty Content:** Each section **must** contain a non-empty `content` string. No section should be left empty, even if a perfect match in the transcript is not found.
