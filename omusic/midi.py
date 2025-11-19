"""Utilities that play MIDI notes.
"""
from typing import Sequence
import mido  # type: ignore[import-untyped]
import mido.backends.rtmidi as rtmidi  # type: ignore[import-untyped]
import random

from . import note_s2i
from enum import IntEnum
from time import sleep

from concurrent.futures import ThreadPoolExecutor


from typing import Self


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


DEFAULT_PORT: str = mido.get_output_names()[0]  # type: ignore


def port():
    return DEFAULT_PORT


class Player:
    def __init__(self: Self,
                 port: str = DEFAULT_PORT,
                 pool_size: int = 10):
        self.port: rtmidi.Output = mido.open_output(port)  # type: ignore
        self.pool: ThreadPoolExecutor = ThreadPoolExecutor(pool_size)

    def __enter__(self: Self) -> 'Player':
        return self

    def __exit__(self: Self, exc_type, exc_val, exc_tb) -> bool:
        print("closing")
        self.pool.__exit__(exc_type, exc_val, exc_tb)
        self.port.__exit__(exc_type, exc_val, exc_tb)
        return True


def note_on(note: int,
            time: int = 1,
            velocity: int = 64,) -> mido.Message:
    velocity_modification = random.randint(-10, 10)
    return mido.Message(
        "note_on",
        note=note,
        velocity=velocity + velocity_modification,
        time=time)


def note_off(note: int, velocity: int = 64, time: int = 2) -> mido.Message:
    return mido.Message("note_off", note=note, velocity=velocity, time=time)


def pause() -> None:
    pass
    # sleep(random.random() * .005)


def play_notes(output: rtmidi.Output,
               pitches: Sequence[int],
               duration: int,
               velocity: int):

    for s in pitches:
        output.send(note_on(s, duration, velocity))
        pause()

    sleep(duration)

    for s in pitches:
        output.send(note_off(s))


def play(player: Player,
         sound: str | list[str],
         duration: int,
         velocity: int = 64) -> None:

    sound_int: int | Sequence[int] = note_s2i(sound)
    if isinstance(sound_int, int):
        sound_int = [sound_int]

    player.pool.submit(play_notes,
                       output=player.port,
                       pitches=sound_int,
                       duration=duration,
                       velocity=velocity)

# def play(output: rtmidi.Output,
#          sound: str | Sequence[str],
#          duration: int,
#          velocity: int = 64) -> None:


def change_instrument(player: Player,
                      instrument: Instrument) -> None:

    player.port.send(mido.Message('program_change',
                                  program=instrument))
