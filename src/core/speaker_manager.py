import asyncio
import json
from dataclasses import asdict
from pathlib import Path

from ..data.models import Speaker, ProcessResult
from ..utils import id_generator, data_handler
from .components import section_producer


class SpeakerManager:
    def __init__(self):
        self.SPEAKERS_PATH = data_handler.DATA_FOLDER.resolve() / "speakers"

    def add(
        self, name: str, source_presentation: Path, source_transcript: Path
    ) -> Speaker:
        current_speakers = self.list()
        speaker_ids = [speaker.speaker_id for speaker in current_speakers]

        if name in speaker_ids:
            raise ValueError(
                f"Given name '{name}' can't be a same with one of the existing speakers' IDs."
            )

        speaker_id = id_generator.generate_speaker_id(name)
        speaker_path = self.SPEAKERS_PATH / speaker_id
        speaker = Speaker(
            name=name,
            speaker_id=speaker_id,
            source_presentation=source_presentation.resolve(),
            source_transcript=source_transcript.resolve(),
        )

        data = {
            k: str(v) if isinstance(v, Path) else v for k, v in asdict(speaker).items()
        }
        data_handler.write(speaker_path / "speaker.json", json.dumps(data, indent=4))
        return speaker

    def edit(
        self,
        speaker: Speaker,
        source_presentation: Path | None = None,
        source_transcript: Path | None = None,
    ) -> Speaker:
        speaker_path = self.SPEAKERS_PATH / speaker.speaker_id

        if source_presentation:
            speaker.source_presentation = source_presentation.resolve()
        if source_transcript:
            speaker.source_transcript = source_transcript.resolve()

        data = {
            k: str(v) if isinstance(v, Path) else v for k, v in asdict(speaker).items()
        }
        data_handler.write(speaker_path / "speaker.json", json.dumps(data, indent=4))
        return speaker

    def resolve(self, speaker_pattern: str) -> Speaker | list[Speaker]:
        speakers = self.list()
        speaker_ids = [speaker.speaker_id for speaker in speakers]

        if speaker_pattern in speaker_ids:
            return speakers[speaker_ids.index(speaker_pattern)]

        matched_speakers = [
            speaker for speaker in speakers if speaker.name == speaker_pattern
        ]
        if matched_speakers:
            if len(matched_speakers) == 1:
                return matched_speakers[0]
            else:
                return matched_speakers

        return []

    def process(
        self, speakers: list[Speaker], llm_model: str, llm_api_key: str
    ) -> list[ProcessResult]:
        async def run():
            speaker_paths = [
                self.SPEAKERS_PATH / speaker.speaker_id for speaker in speakers
            ]

            for speaker, speaker_path in zip(speakers, speaker_paths):
                source_presentation = speaker.source_presentation
                source_transcript = speaker.source_transcript
                local_presentation = speaker_path / "presentation.pdf"
                local_transcript = speaker_path / "transcript.pdf"
                if not (
                    (source_presentation.exists() and source_transcript.exists())
                    or (local_presentation.exists() and local_transcript.exists())
                ):
                    raise FileNotFoundError(
                        f"Missing files for speaker {speaker.name} ({speaker.speaker_id})"
                    )

            async def process_speaker(speaker, speaker_path, delay):
                await asyncio.sleep(delay)

                source_presentation = speaker.source_presentation
                source_transcript = speaker.source_transcript

                local_presentation = speaker_path / "presentation.pdf"
                local_transcript = speaker_path / "transcript.pdf"

                presentation_path, transcript_path = None, None
                transcript_from, presentation_from = None, None

                # Handle presentation file
                if source_presentation.exists():
                    data_handler.copy(source_presentation, speaker_path)
                    data_handler.rename(
                        speaker_path / source_presentation.name, "presentation.pdf"
                    )
                    presentation_path = speaker_path / "presentation.pdf"
                    presentation_from = "SOURCE"
                elif local_presentation.exists():
                    presentation_path = local_presentation
                    presentation_from = "LOCAL"
                else:
                    raise FileNotFoundError(f"Missing presentation file for speaker {speaker.name}")

                # Handle transcript file
                if source_transcript.exists():
                    data_handler.copy(source_transcript, speaker_path)
                    data_handler.rename(
                        speaker_path / source_transcript.name, "transcript.pdf"
                    )
                    transcript_path = speaker_path / "transcript.pdf"
                    transcript_from = "SOURCE"
                elif local_transcript.exists():
                    transcript_path = local_transcript
                    transcript_from = "LOCAL"
                else:
                    raise FileNotFoundError(f"Missing transcript file for speaker {speaker.name}")

                sections = await asyncio.to_thread(
                    section_producer.generate_sections,
                    presentation_path=presentation_path,
                    transcript_path=transcript_path,
                    llm_model=llm_model,
                    llm_api_key=llm_api_key,
                )

                data_handler.write(
                    speaker_path / "sections.json",
                    json.dumps(section_producer.convert_to_list(sections), indent=2),
                )

                return ProcessResult(
                    section_count=len(sections),
                    transcript_from=transcript_from,
                    presentation_from=presentation_from,
                )

            tasks = [
                process_speaker(speaker, speaker_path, idx)
                for idx, (speaker, speaker_path) in enumerate(
                    zip(speakers, speaker_paths)
                )
            ]
            results = await asyncio.gather(*tasks)
            return results

        return asyncio.run(run())

    def delete(self, speaker: Speaker) -> bool:
        speaker_path = self.SPEAKERS_PATH / speaker.speaker_id
        return bool(data_handler.delete(speaker_path))

    def list(self) -> list[Speaker]:
        speakers = []
        for folder in data_handler.list(self.SPEAKERS_PATH):
            if folder.is_dir():
                speaker_json = folder / "speaker.json"
                if speaker_json.exists():
                    data = json.loads(data_handler.read(speaker_json))
                    for k, v in data.items():
                        if isinstance(v, str) and ("/" in v or "\\" in v):
                            data[k] = Path(v)
                    speakers.append(Speaker(**data))
        return speakers
