# Data Models

The application uses a set of Pydantic models to ensure data consistency and type safety. These models are defined in `src/data/models.py`.

## Core Models

- **`Section`**: Represents a segment of the presentation transcript that corresponds to a single slide. It contains the text content and the index of the section.

- **`Chunk`**: A small, overlapping piece of text generated from the `Section` content. Chunks are used as the basis for similarity comparison during live presentation control. Each chunk contains a small string of text (`partial_content`) and a list of the source sections it was derived from.

- **`Speaker`**: Represents a speaker's profile, containing their name, a unique speaker ID, and the file paths to their source presentation and transcript.

- **`Settings`**: Holds the application's configuration, including the selected LLM model and the corresponding API key.

## Supporting Models

- **`SimilarityResult`**: A simple data structure to hold the result of a similarity comparison, containing a `Chunk` and the calculated similarity score.

- **`ProcessResult`**: Contains information about the result of a speaker processing job, such as the number of sections created and the source of the transcript and presentation files.

## Type Aliases

- **`SpeakerId`**: A type alias for a string, representing a unique speaker ID.

- **`HistoryId`**: A type alias for a string, representing a unique ID for a presentation control session history.
