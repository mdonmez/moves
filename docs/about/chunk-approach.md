# Chunk Generation and Candidate Selection

The `chunk_producer.py` module is responsible for the decomposition of `Section` data into `Chunk` objects, which are the atomic units for similarity comparison. This module also implements the logic for selecting a relevant subset of these chunks during live control.

## Chunk Generation Algorithm

The `generate_chunks` function implements a sliding window algorithm to create a comprehensive set of overlapping text chunks from the entire presentation.

1.  **Word Aggregation**: First, it creates a master list of tuples, where each tuple contains a word and a reference to the `Section` object it came from. This preserves the source information for every word in the presentation.
2.  **Sliding Window**: It then iterates over this master list using a sliding window of a fixed size (defaulting to 12 words).
3.  **Chunk Instantiation**: For each position of the window, it creates a `Chunk` object. The `partial_content` of the chunk is the space-joined string of words within the window, which is then passed through the `TextNormalizer`. The `source_sections` attribute is a list of the unique `Section` objects from which the words in the window originated.

This process ensures that every possible 12-word phrase in the transcript is available for matching.

## Candidate Chunk Selection Strategy

Comparing the live speech against every chunk in the presentation would be computationally expensive and inefficient. The `get_candidate_chunks` function implements a crucial optimization by selecting only the most probable chunks for comparison.

-   **Search Space Reduction**: The function takes the `current_section` as input and defines a local search window, typically spanning from two sections before the current one to two sections after (`[current-2, current+2]`).
-   **Filtering**: It filters the global list of all chunks, selecting only those whose `source_sections` fall entirely within this local window. This dramatically reduces the number of comparisons needed at any given moment, improving performance and focusing the similarity search on the most relevant content.
-   **Edge Case Handling**: An additional rule prevents the selection of chunks that are sourced *only* from the very edge of the window (e.g., only from `current-2` or `current+2`), which helps to avoid premature jumps to distant sections.

```mermaid
graph TD
    subgraph Generation (Offline)
        A[List of all Sections] --> B{generate_chunks};
        B --> C[Aggregate all words with source tracking];
        C --> D[Apply sliding window (size=12)];
        D --> E[Generate list of all Chunks];
    end

    subgraph Selection (Real-time)
        F[Current Section] --> G{get_candidate_chunks};
        G --> H[Define local section window, e.g., current ±2];
        H --> I{Filter global chunk list};
        I --> J[Return small list of candidate chunks];
    end
```