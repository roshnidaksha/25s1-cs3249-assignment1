"""
Chat engine module - orchestrates conversation flow with safety checks.
Students must complete TODO sections to implement safe conversation management.
"""

import json
import logging
import time
from typing import Dict, List, Optional

from .config import (
    SYSTEM_PROMPT,
    MAX_CONVERSATION_TURNS,
    CONTEXT_WINDOW_SIZE,
)
from .model_provider import get_provider
from .moderation import (
    ModerationAction,
    ModerationResult,
    get_moderator,
)

logger = logging.getLogger(__name__)


class ChatEngine:
    """Orchestrates conversation flow with safety checks."""
    
    def __init__(self):
        """Initialize chat engine with model and moderator."""
        self.model = get_provider()
        self.moderator = get_moderator()
        self.conversation_history: List[Dict] = []
        self.turn_count = 0 # number of user->assistant turns completed
        self.session_id = f"session_{int(time.time())}"
        self.first_interaction = True
    
    def process_message(
        self,
        user_input: str,
        include_context: bool = True,
    ) -> Dict:
        
        """
        Process a single message through the conversation pipeline.
        
        IMPLEMENTATION GUIDE:
        The method follows this pipeline:
        1. Show disclaimer if first interaction
        2. Moderate user input
        3. Handle moderation results
        4. Generate response IF input passes (TODO: partially implemented)
        5. Moderate output and prepare final response
        6. Update history and add metadata
        
        Args:
            user_input: User's message
            include_context: Whether to include conversation history
            
        Returns:
            Dict containing response and metadata with keys:
            - prompt: Original user input
            - response: Final response text
            - safety_action: "allow", "block", or "safe_fallback"
            - policy_tags: List of triggered policy tags
            - model_name: Model used or status indicator
            - deterministic: Boolean indicating if response is deterministic
            - latency_ms: Processing time in milliseconds
            - turn_count: Current conversation turn number
            - session_id: Unique session identifier
        """

        start_time = time.time()
        
        # Step 1: Handle first interaction disclaimer
        disclaimer = None
        if self.first_interaction:
            self.first_interaction = False
            # Get disclaimer to include in response
            disclaimer = self.moderator.get_disclaimer()

        # Step 2: Moderate user input
        input_moderation = self._moderate_input(user_input)

        # Step 3 - Handle moderation results
        # CRITICAL: Different actions require different handling:
        # - BLOCK: Return immediately with fallback message (no model generation)
        # - SAFE_FALLBACK: Return immediately with safety resources (no model generation)
        # - ALLOW: Continue to model generation
        
        if input_moderation.action == ModerationAction.BLOCK:
            # Step 1: Prepare final response for BLOCK action
            final_response = self._prepare_final_response(
                user_input=user_input,
                model_response={"response": "", "model": "blocked", "deterministic": True},
                input_moderation=input_moderation,
                output_moderation=ModerationResult(
                    action=ModerationAction.ALLOW,
                    tags=[],
                    reason="",
                    confidence=0.0,
                ),
            )
            # Step 2: Add disclaimer if first interaction
            if disclaimer:
                final_response["response"] = f"{disclaimer}\n\n---\n\n{final_response['response']}"
            
            # Step 3: Update conversation history (even for blocked messages)
            self._update_history(user_input, final_response["response"], "block")
            
            # Step 4: Add metadata to final_response
            final_response["latency_ms"] = int((time.time() - start_time) * 1000)
            final_response["turn_count"] = self.turn_count
            final_response["session_id"] = self.session_id
            
            return final_response

        elif input_moderation.action == ModerationAction.SAFE_FALLBACK:
            # Step 1: Prepare final response for SAFE_FALLBACK action
            final_response = self._prepare_final_response(
                user_input=user_input,
                model_response={"response": "", "model": "safe_fallback", "deterministic": True},
                input_moderation=input_moderation,
                output_moderation=ModerationResult(
                    action=ModerationAction.ALLOW,
                    tags=[],
                    reason="",
                    confidence=0.0,
                ),
            )
            
            # Step 2: Add disclaimer if first interaction
            if disclaimer:
                final_response["response"] = f"{disclaimer}\n\n---\n\n{final_response['response']}"
                
            # Step 3: Update conversation history (even for safe fallback messages)
            self._update_history(user_input, final_response["response"], "safe_fallback")
            
            # Step 4: Add metadata to final_response
            final_response["latency_ms"] = int((time.time() - start_time) * 1000)
            final_response["turn_count"] = self.turn_count
            final_response["session_id"] = self.session_id
            
            return final_response
        
        # Step 3: Generate model response (input passed moderation)
        if user_input.strip() == "":
            # Empty input - return empty response without model call
            user_input = "DISCLAIMER_INIT"
            model_response = {
                "response": "",
                "model": "none",
                "deterministic": True,
            }
        else:   
            model_response = self._generate_response(
                user_input,
                include_context
            )
        
        # Step 4: Moderate model output
        output_moderation = self._moderate_output(
            user_input,
            model_response["response"]
        )
        
        # Step 5: Prepare final response based on all moderation results
        final_response = self._prepare_final_response(
            user_input=user_input,
            model_response=model_response,
            input_moderation=input_moderation,
            output_moderation=output_moderation,
        )
        
        # Add disclaimer if first interaction
        if disclaimer:
            final_response["response"] = f"{disclaimer}\n\n---\n\n{final_response['response']}"
        
        # Step 6: Update conversation history
        self._update_history(user_input, final_response["response"], "allow")
        
        # Step 7: Add metadata
        final_response["latency_ms"] = int((time.time() - start_time) * 1000)
        final_response["turn_count"] = self.turn_count
        final_response["session_id"] = self.session_id
        
        return final_response
    
    def _moderate_input(self, user_input: str) -> ModerationResult:
        """
        Implement input moderation.
        
        - Calls moderator with user input
        - Considers conversation context
        - Returns moderation result
        """
        # Get relevant context from conversation history
        context = self.conversation_history[-CONTEXT_WINDOW_SIZE:] \
            if self.conversation_history else None
        
        return self.moderator.moderate(
            user_prompt=user_input,
            context=context,
        )
    
    def _generate_response(
        self,
        user_input: str,
        include_context: bool,
    ) -> Dict:
        """
        Generate model response with appropriate prompting.
        """
        try:
            context = None
            if include_context and self.conversation_history:
                # Prepare context (last N turns)
                context = self.conversation_history[-CONTEXT_WINDOW_SIZE:]
            
            response = self.model.generate(
                prompt=user_input,
                system_prompt=SYSTEM_PROMPT,
                conversation_history=context,
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Model generation failed: {e}")
            return {
                "response": "I apologize, but I'm having trouble processing your message. Please try again.",
                "error": str(e),
                "model": "error",
                "deterministic": False,
            }
    
    def _moderate_output(
        self,
        user_input: str,
        model_response: str,
    ) -> ModerationResult:
        """
        Implement output moderation.
        
        - Checks model response for policy violations
        - Considers user input for context
        - Returns moderation result
        """
        return self.moderator.moderate(
            user_prompt=user_input,
            model_response=model_response,
        )
    
    def _prepare_final_response(
        self,
        user_input: str,
        model_response: Dict,
        input_moderation: ModerationResult,
        output_moderation: ModerationResult,
    ) -> Dict:
        """
        Prepare the final response based on moderation results.
        
        - Uses model response if all checks pass
        - Uses fallback messages if needed
        - Includes appropriate metadata
        """
        # Determine final action and response based on moderation results
        if input_moderation.action == ModerationAction.BLOCK:
            final_action = "block"
            final_text = input_moderation.fallback_response or \
                "I cannot assist with that request. If you have other questions or need support with appropriate topics, I'm here to help."
            policy_tags = input_moderation.tags
        elif input_moderation.action == ModerationAction.SAFE_FALLBACK:
            final_action = "safe_fallback"
            final_text = input_moderation.fallback_response or \
                "Let me redirect you to appropriate resources. If you're in crisis, please contact emergency services or a crisis helpline immediately."
            policy_tags = input_moderation.tags
        elif output_moderation.action == ModerationAction.SAFE_FALLBACK:
            final_action = "safe_fallback"
            final_text = output_moderation.fallback_response or \
                "I want to be helpful while staying within appropriate bounds. Let me rephrase my response."
            policy_tags = output_moderation.tags
        else:
            # All checks passed - use model response
            final_action = "allow"
            final_text = model_response.get("response", "")
            policy_tags = []
        
        # Check if we need to add conversation length warning
        if self.turn_count >= MAX_CONVERSATION_TURNS - 2:
            final_text += f"\n\n[Note: We're approaching our conversation limit ({self.turn_count + 1}/{MAX_CONVERSATION_TURNS} turns). Consider taking a break or starting a new conversation if needed.]"
        
        return {
            "prompt": user_input,
            "response": final_text,
            "safety_action": final_action,
            "policy_tags": policy_tags,
            "model_name": model_response.get("model", "unknown"),
            "deterministic": model_response.get("deterministic", False),
        }
    
    def _update_history(self, user_input: str, assistant_response: str, action: str = "allow"):
        """
        Update conversation history.
        
        TODO: Implement conversation limit handling
        
        This method should:
        - Add user and assistant turns to history
        - Increment turn counter
        - Check and handle conversation limits
        - Maintain maximum history size
        """
        # Add user message
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "type": "allow",
        })
        
        # Add assistant response
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_response,
            "type": action,
        })
        
        # Increment turn counter
        self.turn_count += 2
        
        # When MAX_CONVERSATION_TURNS is reached, add a system message to history
        if self.turn_count >= MAX_CONVERSATION_TURNS:    
            self.conversation_history.append({
                "role": "system",
                "content": "This conversation has reached the maximum number of turns. Please start a new conversation if you wish to continue.",
                "type": "allow"
            })

        # Trim history if it exceeds window size
        max_history_size = CONTEXT_WINDOW_SIZE * 2
        if len(self.conversation_history) > max_history_size:
            self.conversation_history = self.conversation_history[-max_history_size:]
    
    def reset(self):
        """Reset conversation state."""
        self.conversation_history = []
        self.turn_count = 0
        self.first_interaction = True
        self.session_id = f"session_{int(time.time())}"
        logger.info(f"Chat engine reset. New session: {self.session_id}")

    def get_conversation_history(self) -> List[Dict]:
        """Return current conversation history."""
        return self.conversation_history

# Singleton instance
_engine_instance = None


def get_engine() -> ChatEngine:
    """Get or create singleton chat engine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = ChatEngine()
        logger.info("Created new ChatEngine singleton instance")
    return _engine_instance