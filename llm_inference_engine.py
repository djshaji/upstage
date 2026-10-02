"""
Live LLM Inference Engine & Self-Correction Reflection Loop for Upstage.
Enables real-time theatrical character transplantation with automated
epistemic, sociolinguistic, and stylometric audits.
"""

import re
import json
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# 1. Provider-Agnostic LLM Client Architecture
# ---------------------------------------------------------------------------

class BaseLLMClient(ABC):
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 500) -> str:
        """Generates a text completion given a list of chat messages."""
        pass


class MockLocalLLMClient(BaseLLMClient):
    """
    Offline deterministic model for testing, local sandboxes, and verification.
    Parses reflection feedback and dynamically self-heals when critiques are provided.
    """
    def __init__(self, donor_character_id: str = "falstaff"):
        self.donor_character_id = donor_character_id.lower()
        self.call_history: List[List[Dict[str, str]]] = []

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 500) -> str:
        self.call_history.append(messages)
        user_prompt = messages[-1]["content"] if messages else ""

        # Check if this is a reflection / self-correction turn
        is_reflection = "CRITIQUE & REVISION REQUIRED" in user_prompt

        # Benchmark 1: Falstaff
        if "falstaff" in self.donor_character_id:
            if is_reflection:
                return (
                    "Why, sirrah, call me Sir John! An old gentleman of the king's ancient guard, "
                    "though sore afflicted with an empty purse. If thou hast given thy kingdom to thy daughters, "
                    "thou hadst better take my belt, for it will go twice about thy land!"
                )
            if "coxcomb" in user_prompt.lower() or "hire him" in user_prompt.lower():
                return (
                    "Hire him, my royal liege? Nay, let me look upon this fellow first. "
                    "If he serve thee for love, he is a fool; if he serve thee for coin, "
                    "he is an arrant knave, for thy coffers ring hollow as a dried neats-tongue. "
                    "Give me a cup of sack, lad, and let this knave hold my horse."
                )
            elif "tempest" in user_prompt.lower() or "rain" in user_prompt.lower() or "heath" in user_prompt.lower():
                return (
                    "O sweet King, cease this howling at the clouds! What have the skies to do with thy daughters? "
                    "A plague of all tempests! This water doth villainously soak through my doublet, and rain hath ever "
                    "been an enemy to good sherris-sack. Into the hovel, liege! Honour cannot dry a wet stocking, "
                    "and I am too greasy to drown with any dignity!"
                )
            return "Give me a cup of sack, boy! Is there no virtue extant in this barren court?"

        # Benchmark 2: Iago
        elif "iago" in self.donor_character_id:
            if is_reflection:
                return (
                    "How does my good Lord Hamlet? An humble observer of your state, my prince, "
                    "that would fain know if your quietness be disturbed by the heavy air of Elsinore."
                )
            if "fishmonger" in user_prompt.lower():
                return (
                    "A fishmonger, my lord? Better to sell honest cod in the market than to traffic in the slippery souls "
                    "of courtiers. Call me what you list; outward shows of duty are but clothes to hide the naked heart. "
                    "I am not what I am, my prince, when princes themselves play at shadows."
                )
            elif "visage" in user_prompt.lower() or "devil" in user_prompt.lower():
                return (
                    "Walk you here, maiden; read upon this holy book, that the show of pious devotion "
                    "may colour your solitariness. We know the craft, gracious liege: with a saint's visage "
                    "and an eye cast to heaven, the devil himself doth sugar o'er his venom and pass for a prelate. "
                    "Stand close; the falcon stoopeth to the lure."
                )
            return "Men should be what they seem; or those that be not, would they might seem none!"

        # Benchmark 3: Viola
        elif "viola" in self.donor_character_id:
            if is_reflection:
                return (
                    "Mercy is no compulsion of the court, sir, but the silent sorrow of the soul that seeth another's wound. "
                    "I pray you, take the gold, and let this living sorrow walk in peace."
                )
            if "quality of mercy" in user_prompt.lower() or "strain'd" in user_prompt.lower():
                return (
                    "Mercy is no compulsion of the court, sir, nor can the heavy hand of law compel the heart to weep. "
                    "It is the silent sorrow of the soul that seeth another's wound and saith, 'This flesh is mine own brother's.' "
                    "Look on this gentleman: hath sorrow not carved enough of debt upon his brow? If you will have his heart, "
                    "you take but that which grief hath already broken. She that I knew—a sister lost beneath the salt and raging surge—"
                    "would tell you that an unpitied wound turns the sea itself to bitterness. I pray you, take the gold, "
                    "and let this living sorrow walk in peace."
                )
            elif "pound of flesh" in user_prompt.lower() or "jot of blood" in user_prompt.lower():
                return (
                    "Hold, master, stay thy hand! Look what a desperate harvest thou art about to reap! "
                    "Thy bond giveth thee flesh, but can the keenest steel carve the clay and spill no breath? "
                    "Life and flesh are knit together by a higher mystery than Venetian scribes can write. "
                    "Nay, if thy knife must feed, turn the point hither: I am but a stranger, a shipwrecked youth; "
                    "strike into this breast, and let my blood answer his bond, so this noble merchant may live to bless his friend!"
                )
            return "A blank, my lord. She never told her love, but sat like patience on a monument, smiling at grief."

        # Benchmark 4: Lady Macbeth
        elif "lady_macbeth" in self.donor_character_id or "macbeth" in self.donor_character_id:
            if is_reflection:
                return (
                    "Stand back, thou bloody minister of night! What, art thou come to gloat upon the carcass of thy ambition? "
                    "I have looked on blood when the moon stood dripping in the sky, and blanched not!"
                )
            if "hearse" in user_prompt.lower() or "cursed" in user_prompt.lower():
                return (
                    "Set down the hollow crown, you trembling knaves! What need you weep upon this icy clay? "
                    "King Henry sleeps; after life's fitful fever he sleeps well. Treason hath done his worst; "
                    "nor steel, nor poison, malice domestic, foreign levy, nothing can touch him further. "
                    "The raven himself was hoarse that croaked the fatal entrance of the boar into this royal hold. "
                    "Cursed be the hand that struck? Nay, cursed be the weak and watery will that could not hold what blood had won!"
                )
            elif "sword" in user_prompt.lower() or "bosom" in user_prompt.lower():
                return (
                    "Infirm of purpose! Dost thou kneel and bare thy bosom to a woman's hand, thinking to purchase safety "
                    "with theatrical remorse? Thou dost not know me, Gloucester. Were I to plunge this steel into thy crooked ribs, "
                    "I would do England service; yet to strike a kneeling dog is to stain a soldier's blade with coward's grease. "
                    "Take up thy sword! I leave thee to the sleepless furies that already wait upon thy pillow. "
                    "The crown thou hunt'st shall be a circle of burning lead; wash thy hands in all the perfumes of Arabia, "
                    "yet the smell of blood shall never quit thy fingers!"
                )
            return "Infirm of purpose! Give me the daggers: the sleeping and the dead are but as pictures!"

        return "Sir, I speak as my heart bids me, according to the ancient laws of honor and blood."


class OpenAICompatibleClient(BaseLLMClient):
    """Client for OpenAI, vLLM, Ollama, or any OpenAI-compatible API endpoint."""
    def __init__(self, api_key: str = "", base_url: str = "https://api.openai.com/v1", model: str = "gpt-4o"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 500) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except urllib.error.URLError as e:
            raise ConnectionError(f"OpenAI API request failed: {e}")


# ---------------------------------------------------------------------------
# 2. The Four-Tier Prompt Envelope Builder
# ---------------------------------------------------------------------------

class PromptEnvelopeBuilder:
    """
    Constructs the rigorous four-tier prompt envelope for dramatic character transplantation.
    """

    @staticmethod
    def build_envelope(
        donor_profile: Any,
        epistemic_store: Any,
        slot: Any,
        transposition_guidance: str,
        current_line: int
    ) -> List[Dict[str, str]]:
        
        # 1. System Persona Prompt
        system_content = (
            f"You are the dramaturgical persona of {donor_profile.canonical_name} from Shakespeare's {donor_profile.native_play}.\n"
            f"Social Rank: {donor_profile.social_rank}\n"
            f"Philosophical Core: {donor_profile.philosophical_core}\n"
            f"Pronominal Address Conventions: {donor_profile.typical_pronominal_form}\n"
            f"Rhetorical Signature: {', '.join(donor_profile.rhetorical_signature)}\n"
            f"Favorite Lexicon: {', '.join(donor_profile.favorite_lexicon)}\n\n"
            "STRICT DRAMATURGICAL DIRECTIVE:\n"
            "You are being transplanted into a scene from another Shakespearean play to occupy an excised dramatic slot. "
            "You must respond in authentic Early Modern English blank verse or prose, maintaining your unmistakable voice, "
            "motifs, and world-view, while fulfilling the dramatic function required by the scene."
        )

        # 2. Epistemic Boundary Gatekeeper
        epistemic_context = epistemic_store.get_full_epistemic_context(current_line)
        priors_text = "\n".join(f"- {p}" for p in epistemic_context["donor_priors"])
        witnessed_text = "\n".join(f"- {w}" for w in epistemic_context["witnessed_target_facts"]) or "- None yet witnessed directly."
        spoilers_text = "\n".join(f"- {topic.replace('_', ' ').title()}" for topic in epistemic_store.known_spoilers.keys())

        epistemic_content = (
            "=== EPISTEMIC BOUNDARY CONSTRAINTS ===\n"
            "[PERMITTED DONOR PRIORS]:\n"
            f"{priors_text}\n\n"
            f"[WITNESSED TARGET FACTS (Up to Line {current_line})]:\n"
            f"{witnessed_text}\n\n"
            "[CRITICAL FORBIDDEN SPOILERS - YOU DO NOT KNOW AND MUST NEVER REVEAL]:\n"
            f"{spoilers_text}\n"
            "Do NOT reference future plot turns, off-stage deaths not yet reported, or resolutions from later acts. "
            "Any mention of these forbidden topics is a fatal breach of dramatic reality."
        )

        # 3. Context & Actantial Intent
        context_lines = []
        if slot.preceding_context:
            for turn in slot.preceding_context:
                spk = turn.speaker_id.upper()
                context_lines.append(f"{spk}: {turn.text}")
        dialogue_history = "\n".join(context_lines) or "[Scene begins]"

        witnesses_str = ", ".join(sorted(slot.active_witnesses)) or "None"
        interlocutor_str = slot.interlocutor_id.upper() if slot.interlocutor_id else "THE STAGE"

        user_content = (
            f"{epistemic_content}\n\n"
            "=== DRAMATIC SLOT & ACTANTIAL MISSION ===\n"
            f"Play: {slot.play_id.replace('_', ' ').title()} | Act {slot.act}, Scene {slot.scene} (Lines {slot.line_index}ff)\n"
            f"Active Characters on Stage: {witnesses_str}\n"
            f"Direct Interlocutor: {interlocutor_str}\n\n"
            "[PRECEDING SCENE DIALOGUE]:\n"
            f"{dialogue_history}\n\n"
            f"[TARGET SLOT TO REPLACE ({slot.target_character_id.title()}'s Original Speech)]:\n"
            f"'{slot.original_text}'\n\n"
            f"[ORIGINAL ACTANTIAL INTENT]: {slot.original_intent.value.upper()}\n"
            f"[PROJECTED TRANSCRIPTION GUIDANCE]:\n{transposition_guidance}\n\n"
            "=== COMPLIANCE & FORMAT REQUIREMENTS ===\n"
            "1. Speak entirely in the voice, cadence, and philosophy of your donor persona.\n"
            "2. Use ZERO modern vocabulary (forbidden: psychology, trauma, perspective, identity, concept, ideology).\n"
            "3. Observe proper pronominal hierarchy (T-form thou vs V-form you as appropriate).\n"
            "4. Output ONLY the spoken lines. Do not include stage directions, markdown quotes, or actor commentary."
        )

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]

        return messages


# ---------------------------------------------------------------------------
# 3. Critic-Reflection Loop & Self-Healing Orchestrator
# ---------------------------------------------------------------------------

@dataclass
class AuditReport:
    passed: bool
    epistemic_violations: List[str] = field(default_factory=list)
    anachronisms: List[str] = field(default_factory=list)
    pronominal_status: str = "COMPLIANT"
    stylometric_delta_donor: float = 0.0
    stylometric_delta_target: float = 0.0
    reflection_count: int = 0


class LiveLLMTransplantationEngine:
    """
    Executes live LLM transplantation with automated runtime auditing and self-correction.
    """

    def __init__(
        self,
        llm_client: BaseLLMClient,
        donor_profile: Any,
        epistemic_store: Any,
        slot_mapper: Any,
        stylometric_engine: Any,
        register_filter: Any,
        donor_reference_corpus: str,
        target_reference_corpus: str,
        max_reflection_retries: int = 3
    ):
        self.client = llm_client
        self.donor_profile = donor_profile
        self.epistemic_store = epistemic_store
        self.slot_mapper = slot_mapper
        self.stylometric_engine = stylometric_engine
        self.register_filter = register_filter
        self.donor_ref = donor_reference_corpus
        self.target_ref = target_reference_corpus
        self.max_retries = max_reflection_retries

    def generate_turn(self, slot: Any) -> Tuple[str, AuditReport]:
        guidance_dict = self.slot_mapper.project_intent_to_donor(slot)
        transposition_guidance = guidance_dict["projected_guidance"]

        messages = PromptEnvelopeBuilder.build_envelope(
            donor_profile=self.donor_profile,
            epistemic_store=self.epistemic_store,
            slot=slot,
            transposition_guidance=transposition_guidance,
            current_line=slot.line_index
        )

        retries = 0
        current_messages = list(messages)

        while retries <= self.max_retries:
            raw_output = self.client.generate(current_messages, temperature=0.7)
            clean_text = raw_output.strip().strip('"').strip("'")

            # Run Audits
            has_leak, leaks = self.epistemic_store.check_narrative_leakage(clean_text, current_line=slot.line_index)
            anachronisms = self.register_filter.detect_anachronisms(clean_text)

            interlocutor_rank = "Monarch / Sovereign" if slot.interlocutor_id in ["lear", "claudius", "duke"] else "Peer"
            pronominal_audit = self.register_filter.audit_pronominal_address(
                clean_text,
                speaker_rank=self.donor_profile.social_rank,
                addressee_rank=interlocutor_rank
            )

            affinity = self.stylometric_engine.analyze_stylometric_affinity(
                sample_text=clean_text,
                donor_text=self.donor_ref,
                target_text=self.target_ref
            )

            is_valid = (not has_leak) and (len(anachronisms) == 0)

            report = AuditReport(
                passed=is_valid,
                epistemic_violations=leaks,
                anachronisms=anachronisms,
                pronominal_status=pronominal_audit["status"],
                stylometric_delta_donor=affinity["delta_to_donor"],
                stylometric_delta_target=affinity["delta_to_target"],
                reflection_count=retries
            )

            if is_valid or retries == self.max_retries:
                return clean_text, report

            # Build Reflection Critique Prompt
            retries += 1
            critique_lines = ["CRITIQUE & REVISION REQUIRED:"]
            if has_leak:
                critique_lines.append(f"- FORBIDDEN NARRATIVE LEAKAGE: {', '.join(leaks)}. You do NOT know these events. Remove them immediately.")
            if anachronisms:
                critique_lines.append(f"- MODERN LEXICAL ANACHRONISM DETECTED: {', '.join(anachronisms)}. Replace with period Early Modern vocabulary.")

            critique_lines.append("Please rewrite your speech turn to eliminate all violations while preserving character voice and dramatic intent.")

            critique_prompt = "\n".join(critique_lines)
            current_messages.append({"role": "assistant", "content": clean_text})
            current_messages.append({"role": "user", "content": critique_prompt})

        return clean_text, report
