import threading
import time
from pathlib import Path
from collections import deque

import sounddevice as sd
from pynput.keyboard import Key, Controller
from sherpa_onnx import OnlineRecognizer

from ..data.models import Section
from ..utils import text_normalizer
from .components import chunk_producer
from .components.similarity_calculator import SimilarityCalculator


class PresentationController:
    def __init__(
        self,
        sections: list[Section],
        start_section: Section,
        window_size: int = 12,
    ):
        self.frame_duration = 0.1
        self.sample_rate = 16000
        self.window_size = window_size

        self.similarity_calculator = SimilarityCalculator()

        self.sections = sections
        self.current_section = start_section
        self.chunks = chunk_producer.generate_chunks(sections, window_size)

        self.audio_queue = deque(maxlen=5)
        self.shutdown_flag = threading.Event()

        self.recognizer = OnlineRecognizer.from_transducer(
            tokens=str(Path("src/core/components/ml_models/stt/tokens.txt")),
            encoder=str(Path("src/core/components/ml_models/stt/encoder.int8.onnx")),
            decoder=str(Path("src/core/components/ml_models/stt/decoder.int8.onnx")),
            joiner=str(Path("src/core/components/ml_models/stt/joiner.int8.onnx")),
            num_threads=8,
            decoding_method="greedy_search",
        )

        self.stream = self.recognizer.create_stream()

        self.recent_words: deque[str] = deque(maxlen=window_size)
        self.previous_recent_words: list[str] = []

        self.keyboard_controller = Controller()
        self.navigator_working = False

        self.navigator = threading.Thread(
            target=self.navigate_presentation, daemon=True
        )

    def process_audio(self):
        while not self.shutdown_flag.is_set():
            try:
                if self.audio_queue:
                    chunk = self.audio_queue.popleft()
                else:
                    self.shutdown_flag.wait(0.001)
                    continue

                self.stream.accept_waveform(self.sample_rate, chunk)

                while self.recognizer.is_ready(self.stream):
                    self.recognizer.decode_stream(self.stream)

                if text := self.recognizer.get_result(self.stream):
                    normalized_text = text_normalizer.normalize_text(text)
                    words = normalized_text.strip().split()[-self.window_size :]
                    if words and words != list(self.recent_words):
                        self.recent_words.clear()
                        self.recent_words.extend(words)

            except Exception as e:
                raise RuntimeError(f"Audio processing error: {e}") from e

    def navigate_presentation(self):
        while not self.shutdown_flag.is_set():
            try:
                current_words = list(self.recent_words)

                if len(current_words) < self.window_size:
                    self.shutdown_flag.wait(0.001)
                    continue

                if (
                    current_words != self.previous_recent_words
                    and not self.navigator_working
                ):
                    self.navigator_working = True

                    try:
                        candidate_chunks = chunk_producer.get_candidate_chunks(
                            self.current_section, self.chunks
                        )

                        if not candidate_chunks:
                            continue

                        input_text = " ".join(current_words)
                        similarity_results = self.similarity_calculator.compare(
                            input_text, candidate_chunks
                        )

                        best_result = similarity_results[0]
                        best_chunk = best_result.chunk
                        confidence = best_result.score

                        target_section = best_chunk.source_sections[-1]

                        current_idx = self.current_section.section_index
                        target_idx = target_section.section_index
                        navigation_distance = target_idx - current_idx

                        self.update_live_display(
                            speech=" ".join(current_words[-7:]),
                            chunk=" ".join(
                                best_chunk.partial_content.strip().split()[-7:]
                            ),
                            confidence=f"{confidence:.4f}",
                            navigation=f"{navigation_distance}",
                            matched_section=f"{target_section.section_index}",
                        )
                        if navigation_distance != 0:
                            key = Key.right if navigation_distance > 0 else Key.left
                            abs_distance = abs(navigation_distance)

                            for _ in range(abs_distance):
                                self.keyboard_controller.press(key)
                                self.keyboard_controller.release(key)

                                if abs_distance > 1 and _ < abs_distance - 1:
                                    time.sleep(0.01)

                        self.current_section = target_section
                        self.previous_recent_words = current_words.copy()

                    except Exception as e:
                        raise RuntimeError(f"Navigation execution error: {e}") from e
                    finally:
                        self.navigator_working = False

                self.shutdown_flag.wait(0.001)

            except Exception as e:
                raise RuntimeError(f"Navigation error: {e}") from e

    def update_live_display(
        self,
        status="Listening...",
        speech="-",
        chunk="-",
        confidence="-",
        navigation="-",
        matched_section="-",
    ):
        from rich.table import Table
        from rich.panel import Panel
        from rich.live import Live
        from rich.layout import Layout
        from rich.console import Console

        console = Console()

        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(ratio=1, name="main"),
            Layout(size=3, name="footer"),
        )

        layout["main"].split_row(Layout(name="side"), Layout(name="body", ratio=2))

        header_table = Table(show_header=False, show_border=False, expand=True)
        header_table.add_column(justify="center")
        header_table.add_row(
            f"[bold cyan]Presentation Control[/bold] | Status: [green]{status}[/green]"
        )

        footer_table = Table(show_header=False, show_border=False, expand=True)
        footer_table.add_column(justify="center")
        footer_table.add_row(
            f"Press [bold]Ctrl+C[/bold] to stop | Current Section: [bold]{self.current_section.section_index}[/bold] | Total Sections: [bold]{len(self.sections)}[/bold]"
        )

        side_panel = Panel(
            f"""
[bold]Speech:[/bold] [green]{speech}[/green]
[bold]Chunk:[/bold] [yellow]{chunk}[/yellow]
            """,
            title="Real-time Transcription",
            border_style="blue",
        )

        body_panel = Panel(
            f"""
[bold]Confidence:[/bold] {confidence}
[bold]Navigation:[/bold] {navigation}
[bold]Matched Section:[/bold] {matched_section}
            """,
            title="Navigation Details",
            border_style="magenta",
        )

        layout["header"].update(header_table)
        layout["footer"].update(footer_table)
        layout["side"].update(side_panel)
        layout["body"].update(body_panel)

        if not hasattr(self, "live_display"):
            self.live_display = Live(layout, console=console, screen=True)
            self.live_display.start()
        else:
            self.live_display.update(layout)

    def control(self):
        self.update_live_display(status="Initializing...")

        audio_thread = threading.Thread(target=self.process_audio, daemon=True)
        audio_thread.start()
        self.navigator.start()

        self.update_live_display()

        blocksize = int(self.sample_rate * self.frame_duration)

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                blocksize=blocksize,
                dtype="float32",
                channels=1,
                callback=lambda indata, *_: self.audio_queue.append(
                    indata[:, 0].copy()
                ),
                latency="low",
            ):
                while not self.shutdown_flag.is_set():
                    sd.sleep(20)

        except KeyboardInterrupt:
            pass

        finally:
            if hasattr(self, "live_display"):
                self.live_display.stop()

            self.shutdown_flag.set()

            if audio_thread.is_alive():
                audio_thread.join(timeout=1.0)
            if self.navigator.is_alive():
                self.navigator.join(timeout=1.0)


if __name__ == "__main__":
    test_sections = [
        Section(content="The Ability to Say “No”", section_index=0),
        Section(
            content="Have you ever struggled when you tried to say no to someone?",
            section_index=1,
        ),
        Section(
            content="Or perhaps you couldn’t say no to a person because you felt bad for them.",
            section_index=2,
        ),
        Section(
            content="It seems like it’s not a big deal, but sometimes it can cause really serious problems.",
            section_index=3,
        ),
        Section(
            content="Learning to say no is one of the skills which empowers us the most we that can improve. It allows us to take control of our lives, set boundaries, and prioritize what truly matters.",
            section_index=4,
        ),
        Section(
            content="Let’s begin by addressing the question: “Why is it so hard to say no?”",
            section_index=5,
        ),
        Section(
            content="From a young age, most of us are taught to be agreeable, to avoid conflict, and to please others. Saying yes often feels like the easier, safer option.",
            section_index=6,
        ),
        Section(
            content="This fear of rejection or judgment often leads us to overcommit, even when it comes at the expense of our own well-being.",
            section_index=7,
        ),
        Section(
            content="We worry about disappointing people, damaging relationships, or being perceived as selfish.",
            section_index=8,
        ),
        Section(
            content="Saying yes makes us feel useful, wanted, and accepted. But in trying to be everything to everyone, we risk losing ourselves.",
            section_index=9,
        ),
        Section(
            content="Now, let’s talk about what happens when we say yes too often. On the surface, agreeing to every request might seem like the polite or productive thing to do. However, over time, it can lead to burnout, stress, and resentment.",
            section_index=10,
        ),
        Section(
            content="Imagine this: You’re juggling work deadlines, family responsibilities, and personal goals. A friend asks you to help them with a project. Someone wants you to take part of their presentation.",
            section_index=11,
        ),
        Section(
            content="Your friend invites you to an event you don’t have the energy to attend. Instead of saying no, you say yes to all of them. The result?",
            section_index=12,
        ),
        Section(
            content="You spread yourself too thin. You feel exhausted, overwhelmed, and frustrated - not just with others but with yourself.",
            section_index=13,
        ),
        Section(
            content="When we say yes to things that don’t align with our priorities, we’re effectively saying no to the things that do. We sacrifice our time, energy, and even our mental health.",
            section_index=14,
        ),
        Section(
            content="Think about the most successful people you admire. They didn’t get there by agreeing to everything.",
            section_index=15,
        ),
        Section(
            content="They got there by focusing their time and energy on what mattered most to them. They understood that saying no to distractions and unnecessary obligations was the key to achieving their dreams.",
            section_index=16,
        ),
        Section(
            content="Of course, knowing the importance of saying no is one thing; actually doing it, is another.",
            section_index=17,
        ),
        Section(
            content="So, how can we say no effectively, without feeling guilty or causing unnecessary conflict?",
            section_index=18,
        ),
        Section(
            content='First of all, we should be clear, direct and avoid long explanations or excuses. A simple, polite response like "I’m sorry, I can’t do this right now" is often enough.',
            section_index=19,
        ),
        Section(
            content='You can also offer an alternative if it’s appropriate. If you genuinely want to help but can’t fulfill the request, suggest another solution. For example, "I can’t do it, but maybe someone else on the team can help."',
            section_index=20,
        ),
        Section(
            content="And never forget to stand firm. People may try to convince you to change your mind, but remember: you have the right to prioritize yourself. Saying no doesn’t make you a bad person, it makes you a responsible one.",
            section_index=21,
        ),
        Section(
            content="When you start saying no more often, you’ll notice some incredible changes in your life.",
            section_index=22,
        ),
        Section(
            content="You’ll have more time and energy to dedicate to the things that truly matter to you. People will value your time and honesty.",
            section_index=23,
        ),
        Section(
            content="You’ll feel less overwhelmed and more in control of your life.",
            section_index=24,
        ),
        Section(
            content="One of the biggest obstacles to saying no is guilt. We worry about letting others down or being perceived as unkind.",
            section_index=25,
        ),
        Section(
            content="But saying no doesn’t mean you don’t care about others. It means you care enough about yourself to prioritize your needs.",
            section_index=26,
        ),
        Section(
            content="Think about it this way: You can’t pour from an empty cup.",
            section_index=27,
        ),
        Section(
            content="If you constantly say yes to everyone else, you’ll eventually run out of time and energy for yourself. And when you’re depleted, you’re no longer good to anyone.",
            section_index=28,
        ),
        Section(
            content="So, the next time you’re faced with a request that you don’t want to accept, remember this: Saying no isn’t selfish, it’s necessary. It’s a powerful act of self-care that allows you to say yes to what truly matters.",
            section_index=29,
        ),
        Section(
            content="Let’s start viewing ‘’no’’ not as a negative word, but as a positive step toward a more meaningful life.",
            section_index=30,
        ),
        Section(
            content="Because every time you say no to something that doesn’t align with your goals, you’re saying yes to your own happiness, health, and growth.",
            section_index=31,
        ),
        Section(content="Thank you!", section_index=32),
    ]

    start_section = test_sections[0]

    controller = PresentationController(
        sections=test_sections, start_section=start_section
    )
    controller.control()

    # todo: klavye dinleyicisi yapılacak ve section kontrolü supervised hale getirilecek
