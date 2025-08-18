from ...utils import text_normalizer
from ...data.models import Section, Chunk


def generate_chunks(sections: list[Section], window_size: int = 12) -> list[Chunk]:
    words_with_sources = [
        (word, section) for section in sections for word in section.content.split()
    ]
    if len(words_with_sources) < window_size:
        return []

    return [
        Chunk(
            partial_content=text_normalizer.normalize_text(
                " ".join(word for word, _ in words_with_sources[i : i + window_size])
            ),
            source_sections=sorted(
                {section for _, section in words_with_sources[i : i + window_size]},
                key=lambda s: s.section_index,
            ),
        )
        for i in range(len(words_with_sources) - window_size + 1)
    ]


def get_candidate_chunks(
    current_section: Section, all_chunks: list[Chunk]
) -> list[Chunk]:
    idx = int(current_section.section_index)
    start, end = idx - 2, idx + 3

    return [
        chunk
        for chunk in all_chunks
        if all(start <= int(s.section_index) <= end for s in chunk.source_sections)
        and not (
            len(chunk.source_sections) == 1
            and int(chunk.source_sections[0].section_index) in (start, end)
        )
    ]


if __name__ == "__main__":
    sections = [
        Section(
            content="the ability to say no",
            section_index=0,
        ),
        Section(
            content="have you ever struggled when you tried to say no to someone",
            section_index=1,
        ),
        Section(
            content="or perhaps you couldnt say no to a person because you felt bad for them",
            section_index=2,
        ),
        Section(
            content="it seems like its not a big deal but sometimes it can cause really serious problems",
            section_index=3,
        ),
        Section(
            content="learning to say no is one of the skills which empowers us the most we that can improve it allows us to take control of our lives set boundaries and prioritize what truly matters",
            section_index=4,
        ),
        Section(
            content="lets begin by addressing the question why is it so hard to say no",
            section_index=5,
        ),
        Section(
            content="from a young age most of us are taught to be agreeable to avoid conflict and to please others saying yes often feels like the easier safer option",
            section_index=6,
        ),
        Section(
            content="we worry about disappointing people damaging relationships or being perceived as selfish this fear of rejection or judgment often leads us to overcommit even when it comes at the expense of our own well being",
            section_index=7,
        ),
    ]

    chunks = generate_chunks(sections)
    print(f"Generated {len(chunks)} chunks. First 3: {chunks[:3]}")

    current_section = sections[4]
    candidate_chunks = get_candidate_chunks(current_section, chunks)
    print(
        f"Found {len(candidate_chunks)} candidate chunks for section {current_section.section_index}. First 3: {candidate_chunks[:3]}"
    )
