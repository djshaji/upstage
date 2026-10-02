"""
Dramaturgical Data Models for Upstage.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Set, Any


class MeterType(str, Enum):
    BLANK_VERSE = "blank_verse"
    RHYMED_VERSE = "rhymed_verse"
    PROSE = "prose"
    SONG = "song"
    MIXED = "mixed"


class SpeechType(str, Enum):
    DIALOGUE = "dialogue"
    SOLILOQUY = "soliloquy"
    ASIDE = "aside"


class ActantialIntent(str, Enum):
    ADMONITION = "admonition"
    COMIC_DEFLECTION = "comic_deflection"
    RIDDLE_PARADOX = "riddle_paradox"
    CHORIC_LAMENT = "choric_lament"
    PHILOSOPHICAL_INQUIRY = "philosophical_inquiry"
    SOCIABILITY_BONDING = "sociability_bonding"
    EVASION_SELF_PRESERVATION = "self_preservation"
    DISPUTE_REPROACH = "dispute_reproach"


@dataclass
class StageEvent:
    line_number: int
    event_type: str
    characters: List[str]
    description: str = ""


@dataclass
class SpeechTurn:
    turn_id: str
    play_id: str
    act: int
    scene: int
    line_start: int
    line_end: int
    speaker_id: str
    text: str
    meter_type: MeterType = MeterType.PROSE
    speech_type: SpeechType = SpeechType.DIALOGUE
    addressee_id: Optional[str] = None
    actantial_intent: Optional[ActantialIntent] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CharacterProfile:
    character_id: str
    canonical_name: str
    native_play: str
    social_rank: str
    dominant_meter: MeterType
    typical_pronominal_form: str
    philosophical_core: str
    rhetorical_signature: List[str]
    favorite_lexicon: List[str]
    relationship_priors: Dict[str, str] = field(default_factory=dict)


@dataclass
class ExcisedSlot:
    target_character_id: str
    turn_id: str
    act: int
    scene: int
    line_index: int
    original_text: str
    original_intent: ActantialIntent
    interlocutor_id: Optional[str]
    active_witnesses: Set[str]
    preceding_context: List[SpeechTurn] = field(default_factory=list)


@dataclass
class TransformedTurn:
    slot: ExcisedSlot
    donor_character_id: str
    generated_text: str
    applied_meter: MeterType
    stylometric_delta_score: float
    epistemic_check_passed: bool
    pronominal_compliance: bool
    dramaturgical_notes: str = ""
