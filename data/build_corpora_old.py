"""
Canon data builder for Upstage: Loads and formats representative testbed scenes
from King Lear (target play) and Henry IV (donor play with Falstaff).
"""

import json
from pathlib import Path


def create_sample_corpora(data_dir: Path):
    data_dir.mkdir(parents=True, exist_ok=True)

    # 1. Target Play: King Lear excerpt (Act 1, Scene 4 & Act 3, Scene 2)
    king_lear_data = {
        "play_id": "king_lear",
        "title": "The Tragedy of King Lear",
        "genre": "tragedy",
        "characters": {
            "lear": {"name": "King Lear", "rank": "Abdicated Monarch"},
            "kent": {"name": "Earl of Kent", "rank": "Disguised Nobleman (Caius)"},
            "fool": {"name": "Fool", "rank": "Court Jester / Retainer"},
            "goneril": {"name": "Goneril", "rank": "Eldest Daughter / Duchess of Albany"},
            "oswald": {"name": "Oswald", "rank": "Steward to Goneril"}
        },
        "stage_events": [
            {"line_number": 1, "event_type": "ENTER", "characters": ["kent"], "description": "Enter Kent, disguised."},
            {"line_number": 8, "event_type": "ENTER", "characters": ["lear"], "description": "Enter Lear and Attendants."},
            {"line_number": 95, "event_type": "ENTER", "characters": ["fool"], "description": "Enter Fool."},
            {"line_number": 195, "event_type": "ENTER", "characters": ["goneril"], "description": "Enter Goneril."},
            {"line_number": 300, "event_type": "EXIT", "characters": ["lear", "kent"], "description": "Exit Lear with Kent and Train."},
            {"line_number": 1000, "event_type": "ENTER", "characters": ["lear", "fool"], "description": "Enter Lear and Fool, in the Storm on the Heath."},
            {"line_number": 1035, "event_type": "ENTER", "characters": ["kent"], "description": "Enter Kent looking for them in the tempest."}
        ],
        "scenes": [
            {
                "act": 1,
                "scene": 4,
                "setting": "A hall in the Duke of Albany's Palace",
                "turns": [
                    {
                        "turn_id": "KL_1_4_t1",
                        "act": 1,
                        "scene": 4,
                        "line_start": 96,
                        "line_end": 99,
                        "speaker_id": "fool",
                        "text": "Let me hire him too: here's my coxcomb.",
                        "meter_type": "prose",
                        "speech_type": "dialogue",
                        "actantial_intent": "riddle_paradox",
                        "addressee_id": "kent"
                    },
                    {
                        "turn_id": "KL_1_4_t2",
                        "act": 1,
                        "scene": 4,
                        "line_start": 100,
                        "line_end": 101,
                        "speaker_id": "lear",
                        "text": "How now, my pretty knave! how dost thou?",
                        "meter_type": "prose",
                        "speech_type": "dialogue",
                        "addressee_id": "fool"
                    },
                    {
                        "turn_id": "KL_1_4_t3",
                        "act": 1,
                        "scene": 4,
                        "line_start": 102,
                        "line_end": 105,
                        "speaker_id": "fool",
                        "text": "Sirrah, you were best take my coxcomb.",
                        "meter_type": "prose",
                        "speech_type": "dialogue",
                        "actantial_intent": "admonition",
                        "addressee_id": "kent"
                    },
                    {
                        "turn_id": "KL_1_4_t4",
                        "act": 1,
                        "scene": 4,
                        "line_start": 106,
                        "line_end": 107,
                        "speaker_id": "kent",
                        "text": "Why, fool?",
                        "meter_type": "prose",
                        "speech_type": "dialogue",
                        "addressee_id": "fool"
                    },
                    {
                        "turn_id": "KL_1_4_t5",
                        "act": 1,
                        "scene": 4,
                        "line_start": 108,
                        "line_end": 115,
                        "speaker_id": "fool",
                        "text": "Why, for taking one's part that's out of favour: nay, an thou canst not smile as the wind sits, thou'lt catch cold shortly: there, take my coxcomb: why, this fellow has banished two on's daughters, and did the third a blessing against his will; if thou follow him, thou must needs wear my coxcomb.",
                        "meter_type": "prose",
                        "speech_type": "dialogue",
                        "actantial_intent": "admonition",
                        "addressee_id": "kent"
                    },
                    {
                        "turn_id": "KL_1_4_t6",
                        "act": 1,
                        "scene": 4,
                        "line_start": 116,
                        "line_end": 118,
                        "speaker_id": "lear",
                        "text": "Take heed, sirrah; the whip.",
                        "meter_type": "prose",
                        "speech_type": "dialogue",
                        "addressee_id": "fool"
                    },
                    {
                        "turn_id": "KL_1_4_t7",
                        "act": 1,
                        "scene": 4,
                        "line_start": 119,
                        "line_end": 124,
                        "speaker_id": "fool",
                        "text": "Truth's a dog must to kennel; he must be whipped out, when Lady the brach may stand by the fire and stink.",
                        "meter_type": "prose",
                        "speech_type": "dialogue",
                        "actantial_intent": "philosophical_inquiry",
                        "addressee_id": "lear"
                    }
                ]
            },
            {
                "act": 3,
                "scene": 2,
                "setting": "Another part of the heath. Storm still.",
                "turns": [
                    {
                        "turn_id": "KL_3_2_t1",
                        "act": 3,
                        "scene": 2,
                        "line_start": 1001,
                        "line_end": 1009,
                        "speaker_id": "lear",
                        "text": "Blow, winds, and crack your cheeks! rage! blow! You cataracts and hurricanoes, spout Till you have drench'd our steeples, drown'd the cocks! You sulphurous and thought-executing fires, Vaunt-couriers to oak-cleaving thunderbolts, Singe my white head!",
                        "meter_type": "blank_verse",
                        "speech_type": "soliloquy",
                        "addressee_id": None
                    },
                    {
                        "turn_id": "KL_3_2_t2",
                        "act": 3,
                        "scene": 2,
                        "line_start": 1010,
                        "line_end": 1018,
                        "speaker_id": "fool",
                        "text": "O nuncle, court holy-water in a dry house is better than this rain-water out o' door. Good nuncle, in, and ask thy daughters' blessing: here's a night pities neither wise man nor fool.",
                        "meter_type": "prose",
                        "speech_type": "dialogue",
                        "actantial_intent": "self_preservation",
                        "addressee_id": "lear"
                    },
                    {
                        "turn_id": "KL_3_2_t3",
                        "act": 3,
                        "scene": 2,
                        "line_start": 1019,
                        "line_end": 1025,
                        "speaker_id": "lear",
                        "text": "Rumble thy bellyful! Spit, fire! spout, rain! Nor rain, wind, thunder, fire, are my daughters: I tax not you, you elements, with unkindness; I never gave you kingdom, call'd you children.",
                        "meter_type": "blank_verse",
                        "speech_type": "dialogue",
                        "addressee_id": "fool"
                    },
                    {
                        "turn_id": "KL_3_2_t4",
                        "act": 3,
                        "scene": 2,
                        "line_start": 1026,
                        "line_end": 1034,
                        "speaker_id": "fool",
                        "text": "He that has a house to put's head in has a good head-piece. The cod-piece that will house Before the head has any, The head and he shall louse; So beggars marry many.",
                        "meter_type": "song",
                        "speech_type": "dialogue",
                        "actantial_intent": "riddle_paradox",
                        "addressee_id": "lear"
                    }
                ]
            }
        ]
    }

    # 2. Donor Play: Henry IV authentic Falstaff speech turns
    falstaff_corpus = {
        "donor_id": "falstaff",
        "canonical_name": "Sir John Falstaff",
        "source_plays": ["1 Henry IV", "2 Henry IV"],
        "rank": "Knight (impoverished)",
        "turns": [
            {
                "id": "1H4_1_2_f1",
                "play": "1 Henry IV",
                "act": 1,
                "scene": 2,
                "text": "Now, Hal, what time of day is it, lad? Indeed, you come near me now, Hal; for we that take purses go by the moon and the seven stars, and not by Phoebus, he, 'that wandering knight so fair.' And, I prithee, sweet wag, when thou art a king, as, God save thy grace,—majesty I should say, for grace thou wilt have none,—let not us that are squires of the night's body be called thieves of the day's beauty."
            },
            {
                "id": "1H4_2_4_f2",
                "play": "1 Henry IV",
                "act": 2,
                "scene": 4,
                "text": "Give me a cup of sack, boy. Ere I lead this life long, I'll sew nether stocks and mend them and foot them too. A plague of all cowards! Give me a cup of sack, rogue. Is there no virtue extant? You rogue, here's lime in this sack too: there is nothing but roguery to be found in villanous man: yet a coward is worse than a cup of sack with lime in it. A groat to a shilling, there's not three good men unhanged in England; and one of them is fat and grows old: God help the while!"
            },
            {
                "id": "1H4_5_1_f3",
                "play": "1 Henry IV",
                "act": 5,
                "scene": 1,
                "text": "'Tis not due yet; I would be loath to pay him before his day. What need I be so forward with him that calls not on me? Well, 'tis no matter; honour pricks me on. Yea, but how if honour prick me off when I come on? how then? Can honour set to a leg? no: or an arm? no: or take away the grief of a wound? no. Honour hath no skill in surgery, then? no. What is honour? a word. What is in that word honour? what is that honour? air. A trim reckoning! Who hath it? he that died o' Wednesday. Doth he feel it? no. Doth he hear it? no. 'Tis insensible, then. Yea, to the dead. But will it not live with the living? no. Why? detraction will not suffer it. Therefore I'll none of it. Honour is a mere scutcheon: and so ends my catechism."
            },
            {
                "id": "2H4_1_2_f4",
                "play": "2 Henry IV",
                "act": 1,
                "scene": 2,
                "text": "Men of all sorts take a pride to gird at me: the brain of this foolish-compounded clay, man, is not able to invent anything that tends to laughter, more than I invent or is invented on me: I am not only witty in myself, but the cause that wit is in other men. I do here walk before thee like a sow that hath overwhelmed all her litter but one."
            }
        ]
    }

    with open(data_dir / "king_lear_sample.json", "w", encoding="utf-8") as f:
        json.dump(king_lear_data, f, indent=2)

    with open(data_dir / "falstaff_corpus.json", "w", encoding="utf-8") as f:
        json.dump(falstaff_corpus, f, indent=2)

    print("Canonical sample corpora generated successfully.")


if __name__ == "__main__":
    create_sample_corpora(Path("/working_dir/c_76492a59bc5952fb/upstage/data"))
