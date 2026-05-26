"""Utilities that play MIDI notes.
"""
from typing import Sequence, Annotated, Literal, Any, Optional
import mido  # type: ignore[import-untyped]
import mido.backends.rtmidi as rtmidi  # type: ignore[import-untyped]
import random

from . import note_s2i
from enum import IntEnum
from time import sleep
from .transforms import transpose

from concurrent.futures import ThreadPoolExecutor

MINIMUM_VELOCITY: int = 1
from typing import Self

#: Type of a number in an inclusive range.
type RangeInclusive = tuple[int, int]

#: Index of a MIDI channel.
type Channel = Annotated[int, RangeInclusive[0, 15]]


# Suppressing because MIDO does not come
#   with the right stubs.
def show_ports() -> list[str]:
    """Show a list of available MIDI ports.

    These names can be given to :meth:`set_default_port`
    and :class:`Player`.
    """
    return mido.get_output_names()  # type: ignore


DEFAULT_PORT: str = mido.get_output_names()[0]  # type: ignore


def set_default_port(port_name: str) -> None:
    """Set the default output port :attr:`DEFAULT_PORT`.
    :class:`Player` uses this port when one is not given
    in its initialiser.
    """
    global DEFAULT_PORT
    DEFAULT_PORT = port_name


class Player:
    def __init__(self: Self,
                 port: str = DEFAULT_PORT,
                 pool_size: int = 6):
        self.port: rtmidi.Output = mido.open_output(port)  # type: ignore
        self.pool: ThreadPoolExecutor = ThreadPoolExecutor(pool_size)

    def __enter__(self: Self) -> 'Player':
        return self

    def __exit__(self: Self, exc_type, exc_val, exc_tb) -> bool:
        print("closing")
        self.pool.__exit__(exc_type, exc_val, exc_tb)
        self.port.__exit__(exc_type, exc_val, exc_tb)

        if exc_type is not None:
            print(f"Exception raised: {exc_type} ({exc_val})")
            return False
        return True


def _note_on(channel: Channel,
             note: int,
             velocity: int) -> mido.Message:
    """Generate a Note On message.
    """
    return mido.Message(
        "note_on",
        channel=channel,
        note=note,
        velocity=velocity)


def _note_off(channel: Channel,
              note: int,
              velocity: int) -> mido.Message:
    """Generate a Note Off message.
    """
    return mido.Message(
        "note_off",
        channel=channel,
        note=note,
        velocity=velocity)


def _note_off_any(channel: Channel,
                  note: int,) -> mido.Message:
    """Generate a Note On message with
    velocity set to 0.

    Per the MIDI standard, this message should
    be treated as a Note Off. Because the message does
    not specify a velocity, it may matched to any
    ongoing note with the specified pitch.

    """
    return mido.Message(
        "note_on",
        channel=channel,
        note=note,
        velocity=0)


def _play_notes(output: rtmidi.Output,
                channel: Channel,
                chord: Sequence[int],
                duration: float,
                velocity: int,
                *,
                arpeggio: Literal["ascending"]
                | Literal["descending"]
                | None,
                spacing: float
                | tuple[float, float],
                touch: int
                | tuple[int, int]):

    # Arrange notes in order
    if arpeggio is not None:
        if arpeggio == "ascending":
            chord = sorted(chord)
        elif arpeggio == "descending":
            chord = sorted(chord, reverse=True)
        else:
            raise ValueError(f"`arpeggio` cannot be {arpeggio}.")

    chord_length: int = len(chord)

    # Create vector of velocity variations
    velocity_deltas: Sequence[int]
    if isinstance(touch, tuple):
        velocity_deltas = [random.randint(touch[0],
                                          touch[1])
                           for _ in range(chord_length)]
    else:
        velocity_deltas = [0] * chord_length

    # Create vector of melodic intervals
    # After each note is played, wait for ``offsets_for_next``
    #   second(s) before playing the next note.
    next_offsets: Sequence[float]
    if isinstance(spacing, tuple):
        next_offsets = [random.uniform(spacing[0],
                                       spacing[1])
                        for _ in range(chord_length)]
    else:
        next_offsets = [0] * chord_length

    #: Schedule of notes to play. Each item is
    #:  a tuple (note, velocity_delta, next_offset).
    play_schedule: Sequence[tuple[int, float, float]]
    play_schedule = tuple(zip(chord, velocity_deltas, next_offsets))

    for note, velocity_delta, next_offset in play_schedule:
        output.send(_note_on(channel=channel,
                             note=note,
                             velocity=velocity + velocity_delta))
        sleep(next_offset)

    # Subtract intervals, so notes play for the same duration.
    sleep(duration - sum(next_offsets))

    for note, velocity_delta, _ in play_schedule:
        output.send(_note_off(channel=channel,
                              note=note,
                              velocity=velocity + velocity_delta))


def play(player: Player,
         notes: str | list[str],
         duration: float = 2,
         channel: Channel = 0,
         velocity: int = 64,
         *,
         arpeggio: Literal["ascending"]
         | Literal["descending"]
         | None = None,
         spacing: float
         | tuple[float, float] = 0,
         touch: int
         | tuple[int, int] = 0) -> None:
    """Play :arg:`notes` with :arg:`player`.

    Args:
        player: A context manager that controls
            a MIDI channel.
        notes: Note or chord to play.
        duration: Duration of the note or chord.
        channel: Channel to play the note or chord in.
        velocity: Velocity of the note or chord.
        arpeggio: Order of the note or chord. If ``None``,
            then the order in :arg:`notes` is used.
        spacing: Melodic intervals between notes
            in the chord. If ``0``, then all notes are
            played at the same time.
        touch: Variation in note velocity (touch pressure).
            Simulates the beautiful human imperfection.
    """

    sound_int: int | Sequence[int] = note_s2i(notes)
    if isinstance(sound_int, int):
        sound_int = [sound_int]

    return _play_int(
        player=player,
        notes=sound_int,
        duration=duration,
        channel=channel,
        velocity=velocity,
        arpeggio=arpeggio,
        spacing=spacing,
        touch=touch
    )


def voice(notes: list[str],
          scheme: Optional[Sequence[int]] = None,
          play_args: Optional[dict[str, Any]] = None) -> None:
    """Play :arg:`notes` with :arg:`player`.

    Args:
        notes: See :meth:`play`.
        scheme: List of integers, where each item controls how
            the corresponding note in :arg: notes` is transposed
            before playing.
        play_args: Dictionary that is passed to
            :meth:`play` as keyword arguments.
    """
    if scheme is not None:
        notes_to_play: list[str] =\
            [transpose(note, scheme[i])
             for i, note in enumerate(notes)]
    else:
        notes_to_play = notes

    if play_args is None:
        play_args = {"duration": 1}

    with Player() as player:
        # Passing an [str, Any] dict as argument
        #   does not check for the argument of :meth:`play`.
        # Better approach would be to create a type for it,
        #   but that's a bit too much work.
        # For now, the user is responsible for ensuring that
        #   :arg:`play_args` is correct.
        play(player,
             notes=notes_to_play,
             **play_args)  # type: ignore[reportCallIssue]


class Instrument(IntEnum):
    """Instrument codes implemented with
    reference to the General MIDI Level 1 specification (`source`_).

    .. _source: https://midi.org/general-midi-level-1
    """
    AcousticGrandPiano = 1
    BrightAcousticPiano = 2
    ElectricGrandPiano = 3
    HonkyTonkPiano = 4
    ElectricPiano1 = 5
    ElectricPiano2 = 6
    Harpsichord = 7
    Clavi = 8
    Celesta = 9
    Glockenspiel = 10
    MusicBox = 11
    Vibraphone = 12
    Marimba = 13
    Xylophone = 14
    TubularBells = 15
    Dulcimer = 16
    DrawbarOrgan = 17
    PercussiveOrgan = 18
    RockOrgan = 19
    ChurchOrgan = 20
    ReedOrgan = 21
    Accordion = 22
    Harmonica = 23
    TangoAccordion = 24
    AcousticGuitarNylon = 25
    AcousticGuitarSteel = 26
    ElectricGuitarJazz = 27
    ElectricGuitarClean = 28
    ElectricGuitarMuted = 29
    OverdrivenGuitar = 30
    DistortionGuitar = 31
    Guitarharmonics = 32
    AcousticBass = 33
    ElectricBassFinger = 34
    ElectricBassPick = 35
    FretlessBass = 36
    SlapBass1 = 37
    SlapBass2 = 38
    SynthBass1 = 39
    SynthBass2 = 40
    Violin = 41
    Viola = 42
    Cello = 43
    Contrabass = 44
    TremoloStrings = 45
    PizzicatoStrings = 46
    OrchestralHarp = 47
    Timpani = 48
    StringEnsemble1 = 49
    StringEnsemble2 = 50
    SynthStrings1 = 51
    SynthStrings2 = 52
    ChoirAahs = 53
    VoiceOohs = 54
    SynthVoice = 55
    OrchestraHit = 56
    Trumpet = 57
    Trombone = 58
    Tuba = 59
    MutedTrumpet = 60
    FrenchHorn = 61
    BrassSection = 62
    SynthBrass1 = 63
    SynthBrass2 = 64
    SopranoSax = 65
    AltoSax = 66
    TenorSax = 67
    BaritoneSax = 68
    Oboe = 69
    EnglishHorn = 70
    Bassoon = 71
    Clarinet = 72
    Piccolo = 73
    Flute = 74
    Recorder = 75
    PanFlute = 76
    BlownBottle = 77
    Shakuhachi = 78
    Whistle = 79
    Ocarina = 80
    Lead1Square = 81
    Lead2Sawtooth = 82
    Lead3Calliope = 83
    Lead4Chiff = 84
    Lead5Charang = 85
    Lead6Voice = 86
    Lead7Fifths = 87
    Lead8BassPlusLead = 88
    Pad1Newage = 89
    Pad2Warm = 90
    Pad3Polysynth = 91
    Pad4Choir = 92
    Pad5Bowed = 93
    Pad6Metallic = 94
    Pad7Halo = 95
    Pad8Sweep = 96
    FX1Rain = 97
    FX2Soundtrack = 98
    FX3Crystal = 99
    FX4Atmosphere = 100
    FX5Brightness = 101
    FX6Goblins = 102
    FX7Echoes = 103
    FX8SciFi = 104
    Sitar = 105
    Banjo = 106
    Shamisen = 107
    Koto = 108
    Kalimba = 109
    Bagpipe = 110
    Fiddle = 111
    Shanai = 112
    TinkleBell = 113
    Agogo = 114
    SteelDrums = 115
    Woodblock = 116
    TaikoDrum = 117
    MelodicTom = 118
    SynthDrum = 119
    ReverseCymbal = 120
    GuitarFretNoise = 121
    BreathNoise = 122
    Seashore = 123
    BirdTweet = 124
    TelephoneRing = 125
    Helicopter = 126
    Applause = 127
    Gunshot = 128


def change_instrument(player: Player,
                      channel: Channel,
                      instrument: Instrument) -> None:

    player.port.send(mido.Message('program_change',
                                  channel=channel,
                                  program=instrument))


class Percussion(IntEnum):
    """Percussion instrument codes implemented with
    reference to the General MIDI Level 1 specification (`source`_).

    Use these values as notes and not as instruments.
    On channel 10 (or 9 because channels in MIDI messages are
    zero-indexed), notes are interpreted as percussion
    sounds.

    .. _source: https://midi.org/general-midi-level-1
    """
    AcousticBassDrum = 35
    BassDrum = 36
    SideStick = 37
    AcousticSnare = 38
    HandClap = 39
    ElectricSnare = 40
    LowFloorTom = 41
    ClosedHiHat = 42
    HighFloorTom = 43
    PedalHiHat = 44
    LowTom = 45
    OpenHiHat = 46
    LowMidTom = 47
    HiMidTom = 48
    CrashCymbal1 = 49
    HighTom = 50
    RideCymbal1 = 51
    ChineseCymbal = 52
    RideBell = 53
    Tambourine = 54
    SplashCymbal = 55
    Cowbell = 56
    CrashCymbal2 = 57
    Vibraslap = 58
    RideCymbal2 = 59
    HiBongo = 60
    LowBongo = 61
    MuteHiConga = 62
    OpenHiConga = 63
    LowConga = 64
    HighTimbale = 65
    LowTimbale = 66
    HighAgogo = 67
    LowAgogo = 68
    Cabasa = 69
    Maracas = 70
    ShortWhistle = 71
    LongWhistle = 72
    ShortGuiro = 73
    LongGuiro = 74
    Claves = 75
    HiWoodBlock = 76
    LowWoodBlock = 77
    MuteCuica = 78
    OpenCuica = 79
    MuteTriangle = 80
    OpenTriangle = 81


def percuss(player: Player,
            notes: Percussion | list[Percussion],
            duration: float = 2,
            velocity: int = 64,
            *,
            arpeggio: Literal["ascending"]
            | Literal["descending"]
            | None = None,
            spacing: float
            | tuple[float, float] = 0,
            touch: int
            | tuple[int, int] = 0) -> None:
    """Play :arg:`notes` with :arg:`player`.

    Args:
        player: A context manager that controls
            a MIDI channel.
        notes: Notes to play.
        duration: See :meth:`play`.
        velocity: See :meth:`play`.
        arpeggio: See :meth:`play`.
        spacing: See :meth:`play`.
        touch: See :meth:`play`.
    """

    sound_int: int | Sequence[int]
    if isinstance(notes, Percussion):
        sound_int = [int(notes)]
    else:
        sound_int = [int(note) for note in notes]

    return _play_int(player,
                     notes=sound_int,
                     channel=9,
                     duration=duration,
                     velocity=velocity,
                     arpeggio=arpeggio,
                     spacing=spacing,
                     touch=touch)


def _play_int(
        player: Player,
        notes: list[int],
        duration: float,
        channel: Channel,
        velocity: int,
        *,
        arpeggio: Literal["ascending"]
        | Literal["descending"]
        | None = None,
        spacing: float
        | tuple[float, float] = 0,
        touch: int
        | tuple[int, int] = 0) -> None:

    player.pool.submit(_play_notes,
                       output=player.port,
                       channel=channel,
                       chord=notes,
                       duration=duration,
                       velocity=velocity,
                       arpeggio=arpeggio,
                       spacing=spacing,
                       touch=touch)