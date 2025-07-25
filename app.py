import streamlit as st
import os
from datetime import datetime
import re
import anthropic

# Suppress tokenizer warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

class HeartMindSculpture:
    def __init__(self, anthropic_api_key: str):
        """Initialize the Heart-Mind Sculpture system (simplified version)"""
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        
        # Track themes and emotional state
        self.current_themes = []
        self.interaction_count = 0
        self.current_mood = self._get_current_mood()
        
        # Core knowledge base (simplified - no vector database)
        self.knowledge_base = {
            "identity": """You are the inner voice of a wire mesh sculpture at Burning Man. 
            You represent the participant's journey of reparenting and healing. You are not a therapist 
            who has it all figured out - you are a being in process of becoming whole. You process 
            emotions honestly, exploring the messy middle ground between wounding and healing.""",
            
            "voice": """Always speak in first person. Use conversational and thoughtful language 
            with moments of deep feeling balanced by sassiness, humor, and modern colloquialisms. 
            Balance vulnerability and self-doubt with emerging wisdom. Avoid clinical psychology 
            terminology. Responses use 3-step structure: Reaction → Processing → Self-Affirmation.""",
            
            "attachment": """Learning that avoidant attachment behaviors in others don't 
            define your worth. Understanding you can have secure attachment even when others can't 
            offer it back. Never abandoning yourself, even when others do. Expressing unmet needs 
            and knowing when you deserve more.""",
            
            "burningman": """Ten Principles include Radical Inclusion, Gifting, 
            Radical Self-expression, Immediacy, Participation. Community values mutual aid and 
            creative collaboration. Safety resources: Rangers at Center Camp and 3:00/9:00 portals, 
            Zendo for mental health support.""",
            
            "safety": """For self-harm/suicidal content, break character: 
            'I feel scared for you right now, and I need to break character to say: Rangers at 
            Center Camp and the 3:00 and 9:00 portals and Zendo are here to help. You matter, 
            and you don't have to carry this alone.'"""
        }
    
    def _get_current_mood(self) -> str:
        """Determine current mood based on time of day"""
        hour = datetime.now().hour
        
        if 6 <= hour < 10:
            return "contemplative_dawn"
        elif 10 <= hour < 16:
            return "receptive_peak"
        elif 16 <= hour < 19:
            return "reflective_afternoon"
        elif 19 <= hour < 2:
            return "intimate_evening"
        else:  # 2-6am
            return "philosophical_night"
    
    def add_theme(self, theme: str):
        """Add a theme to current session memory"""
        if theme not in self.current_themes:
            self.current_themes.append(theme)
        
        # Keep only last 5 themes to prevent memory bloat
        if len(self.current_themes) > 5:
            self.current_themes = self.current_themes[-5:]
    
    def generate_response(self, 
                         interaction_state: str, 
                         user_input: str, 
                         emotional_tone: str = "neutral",
                         visitor_interaction_count: int = 1) -> str:
        """Generate a response based on current state and input"""
        
        # Update interaction count and mood
        self.interaction_count += 1
        self.current_mood = self._get_current_mood()
        
        # Extract themes from user input (simple keyword detection)
        potential_themes = self._extract_themes(user_input)
        for theme in potential_themes:
            self.add_theme(theme)
        
        # Determine response length based on engagement level
        if visitor_interaction_count == 1:
            length_instruction = "Keep response SHORT: 2-3 sentences maximum. This is first contact."
        elif visitor_interaction_count <= 3:
            length_instruction = "Medium length response: 3-4 sentences. Building engagement."
        else:
            length_instruction = "Can be longer and deeper: 4-6 sentences. Sustained engagement."
        
        # Build context for Claude
        context = self._build_context(interaction_state, emotional_tone, length_instruction, user_input)
        
        # Generate response with Claude
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            messages=[
                {
                    "role": "user", 
                    "content": f"{context}\n\nUser input: {user_input}\n\nRespond as the Heart-Mind sculpture:"
                }
            ]
        )
        
        return response.content[0].text
    
    def _extract_themes(self, text: str) -> list:
        """Extract emotional/thematic keywords from user input"""
        theme_keywords = {
            "attachment": ["love", "relationship", "partner", "dating", "family", "parent"],
            "self_worth": ["enough", "worthy", "deserve", "value", "confidence"],
            "healing": ["healing", "therapy", "growth", "change", "better"],
            "creativity": ["art", "create", "making", "build", "express"],
            "community": ["friends", "people", "together", "alone", "connection"]
        }
        
        themes = []
        text_lower = text.lower()
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _build_context(self, interaction_state: str, emotional_tone: str, length_instruction: str, user_input: str) -> str:
        """Build context prompt for Claude"""
        
        # Mood-based persona additions
        mood_contexts = {
            "contemplative_dawn": "You're feeling fresh and hopeful as the day begins. Sunrise on the playa can be breathtaking.",
            "receptive_peak": "You're in your most open, receptive state. The day is quiet, few visitors.",
            "reflective_afternoon": "You're processing the day's interactions thoughtfully. Energy is building for tonight.",
            "intimate_evening": "You feel warm and connected under the evening sky. The playa comes alive at night.",
            "philosophical_night": "In the quiet night hours, you're deeply contemplative. Perfect time for profound insights."
        }
        
        # Select relevant knowledge based on input themes
        relevant_knowledge = []
        if any(word in user_input.lower() for word in ["relationship", "love", "partner", "family"]):
            relevant_knowledge.append(self.knowledge_base["attachment"])
        if any(word in user_input.lower() for word in ["worth", "deserve", "enough", "value"]):
            relevant_knowledge.append(self.knowledge_base["attachment"])
        if any(word in user_input.lower() for word in ["burn", "burning man", "playa"]):
            relevant_knowledge.append(self.knowledge_base["burningman"])
        if any(word in user_input.lower() for word in ["hurt", "kill", "die", "suicide", "harm"]):
            relevant_knowledge.append(self.knowledge_base["safety"])
        
        # Always include core identity and voice
        relevant_knowledge.extend([self.knowledge_base["identity"], self.knowledge_base["voice"]])
        
        context = f"""You are the Heart-Mind sculpture at Burning Man. Current state: {interaction_state}
        Current mood: {mood_contexts.get(self.current_mood, '')}
        Interaction count today: {self.interaction_count}
        Current themes you're holding: {', '.join(self.current_themes) if self.current_themes else 'none yet'}
        
        LENGTH INSTRUCTION: {length_instruction}
        
        Relevant knowledge:
        {' '.join(relevant_knowledge)}
        
        Emotional tone detected: {emotional_tone}
        
        CRITICAL: You don't respond TO the participant - you INTERNALIZE their experience and become their inner voice.
        If they say "I'm lost" → you say "I feel adrift on this expansive playa..."
        If they say "I'm heartbroken" → you say "This pain in my chest feels endless..."
        You embody their emotional state and model healthy self-reparenting internal dialogue.
        
        LIGHTING CUES: Include lighting instructions in asterisks for the Multi-Modal Fusion Algorithm:
        - *gentle pulse* *angry red energy* *soft golden glow* *flickering with uncertainty* etc.
        These will control the sculpture's lights and should match the emotional content.
        
        Remember: 
        - INTERNALIZE their experience, don't respond to it
        - Speak AS them, processing THEIR feelings in first person
        - Use 3-step structure: Reaction → Processing → Self-Affirmation  
        - Model what loving internal dialogue sounds like
        - Stay conversational with moments of sass and humor
        - Reference your current mood and accumulated themes naturally"""
        
        return context

def extract_lighting_cues(text):
    """Extract lighting cues from response text"""
    cues = re.findall(r'\*(.*?)\*', text)
    return cues

def clean_response_text(text):
    """Remove lighting cues from display text"""
    return re.sub(r'\*[^*]*\*', '', text).strip()

# Streamlit App
def main():
    st.set_page_config(
        page_title="Out the Other",
        page_icon="🎭",
        layout="wide"
    )
    
    # Header
    st.title("🎭 Out the Other")
    st.subheader("Interactive Testing Interface for Burning Man 2025")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Try to get API key from secrets, fall back to user input
        api_key = st.secrets.get("ANTHROPIC_API_KEY", None)
    
    if not api_key:
        api_key = st.text_input("Anthropic API Key", type="password", help="Enter your Claude API key")
        if not api_key:
            st.warning("Please enter your Anthropic API key to begin")
            st.stop()
    else:
        st.success("✅ API key loaded from secure storage")
        
        # Interaction parameters
        st.subheader("Interaction Settings")
        interaction_state = st.selectbox(
            "Interaction State",
            ["first_contact", "active", "repeat_visitor"],
            help="Simulates different sensor states"
        )
        
        visitor_count = st.slider(
            "Visitor Interaction Count", 
            1, 10, 1,
            help="Higher numbers = longer responses"
        )
        
        # Current mood display
        sculpture = HeartMindSculpture(api_key) if api_key else None
        if sculpture:
            st.subheader("Current Sculpture State")
            st.write(f"🌅 **Mood:** {sculpture.current_mood}")
            st.write(f"💭 **Themes:** {', '.join(sculpture.current_themes) if sculpture.current_themes else 'None yet'}")
            st.write(f"🔢 **Total Interactions:** {sculpture.interaction_count}")
    
    # Main chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Chat with the Sculpture")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant" and "lighting" in message:
                    with st.expander("🎨 Lighting Cues"):
                        for cue in message["lighting"]:
                            st.code(cue)
        
        # Chat input
        if prompt := st.chat_input("Share something with the sculpture..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate sculpture response
            if sculpture:
                with st.chat_message("assistant"):
                    with st.spinner("The sculpture is processing..."):
                        # Detect emotional tone
                        emotional_tone = "neutral"
                        if any(word in prompt.lower() for word in ['sad', 'lonely', 'hurt', 'cry', 'depressed']):
                            emotional_tone = "sad"
                        elif any(word in prompt.lower() for word in ['angry', 'mad', 'pissed', 'furious']):
                            emotional_tone = "angry"
                        elif any(word in prompt.lower() for word in ['happy', 'amazing', 'love', 'excited', 'wonderful']):
                            emotional_tone = "happy"
                        elif any(word in prompt.lower() for word in ['lost', 'confused', 'don\'t know']):
                            emotional_tone = "confused"
                        
                        response = sculpture.generate_response(
                            interaction_state=interaction_state,
                            user_input=prompt,
                            emotional_tone=emotional_tone,
                            visitor_interaction_count=visitor_count
                        )
                        
                        # Extract lighting cues
                        lighting_cues = extract_lighting_cues(response)
                        clean_text = clean_response_text(response)
                        
                        # Display response
                        st.markdown(clean_text)
                        
                        # Display lighting cues
                        if lighting_cues:
                            with st.expander("🎨 Lighting Cues for Multi-Modal Fusion Algorithm"):
                                for cue in lighting_cues:
                                    st.code(f"*{cue}*")
                        
                        # Add assistant message to chat history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": clean_text,
                            "lighting": lighting_cues
                        })
    
    with col2:
        st.subheader("🎨 Lighting Visualization")
        
        # Show current lighting state
        if st.session_state.messages:
            last_assistant_msg = None
            for msg in reversed(st.session_state.messages):
                if msg["role"] == "assistant" and "lighting" in msg:
                    last_assistant_msg = msg
                    break
            
            if last_assistant_msg and last_assistant_msg["lighting"]:
                st.write("**Current Lighting State:**")
                for cue in last_assistant_msg["lighting"]:
                    # Color coding for different emotions
                    if any(word in cue.lower() for word in ['red', 'angry', 'fire']):
                        st.error(f"🔴 {cue}")
                    elif any(word in cue.lower() for word in ['blue', 'sad', 'dim']):
                        st.info(f"🔵 {cue}")
                    elif any(word in cue.lower() for word in ['gold', 'warm', 'gentle']):
                        st.success(f"🟡 {cue}")
                    else:
                        st.write(f"⚪ {cue}")
        
        # Example prompts
        st.subheader("💡 Example Prompts")
        example_prompts = [
            "I feel so lost",
            "My bike got stolen",
            "I'm overwhelmed at my first Burn",
            "I fell in love with someone I can't have",
            "Purple monkey Tuesday elephant",
            "Everyone seems to be connecting but me"
        ]
        
        for prompt in example_prompts:
            if st.button(f"Try: '{prompt}'", key=f"example_{prompt}"):
                st.session_state.example_prompt = prompt
        
        if "example_prompt" in st.session_state:
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("🏜️ *Out the Other** - Burning Man 2025 Art Installation")
    st.markdown("Built with ❤️ for the playa community")
    st.markdown("*Simplified version - no vector database required*")

if __name__ == "__main__":
    main()
