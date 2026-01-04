"""Support for Cloudflare Workers AI Conversation with device control."""
from __future__ import annotations

import json
import logging
from typing import Any, Literal

from homeassistant.components import assist_pipeline, conversation
from homeassistant.components.conversation import ConversationEntity, ConversationInput, ConversationResult
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LLM_HASS_API, MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, intent, llm
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import ulid

from .cloudflare_api import CloudflareAPI, CloudflareAPIError
from .const import (
    CONF_LLM_MODEL,
    CONF_PROMPT,
    DEFAULT_LLM_MODEL,
    DEFAULT_PROMPT,
    DOMAIN,
    FUNCTION_CALLING_MODELS,
    LLM_MODELS,
)

_LOGGER = logging.getLogger(__name__)

MAX_TOOL_ITERATIONS = 10


def _format_tool(tool: llm.Tool) -> dict[str, Any]:
    """Format Home Assistant tool to Cloudflare function calling format."""
    # Convert to simple JSON-serializable format
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
    }
    
    # Extract parameter schema if available
    if hasattr(tool.parameters, "schema") and tool.parameters.schema:
        schema = tool.parameters.schema
        for key, value in schema.items():
            key_str = str(key)
            
            # Handle voluptuous Any() types - extract individual options
            # e.g., "Any('name', 'area', 'floor', msg=None)" -> separate name, area, floor parameters
            if "Any(" in key_str and ("'name'" in key_str or "'area'" in key_str or "'floor'" in key_str):
                # This is a voluptuous Any() - create separate parameters for each option
                for param_name in ["name", "area", "floor"]:
                    if f"'{param_name}'" in key_str:
                        desc = f"The {param_name} of the device or area to control"
                        if param_name == "name":
                            desc = "The name of the device (e.g., 'kitchen light', 'table lamp')"
                        elif param_name == "area":
                            desc = "The area name to control all devices in that area (e.g., 'kitchen', 'living room')"
                        elif param_name == "floor":
                            desc = "The floor name to control all devices on that floor (e.g., 'upstairs', 'ground floor')"
                        
                        parameters["properties"][param_name] = {
                            "type": "string",
                            "description": desc,
                        }
                continue
            
            # Regular parameter handling
            param_type = "string"  # Default
            param_desc = key_str  # Default description
            
            # Try to extract type information
            try:
                if hasattr(value, "container"):
                    container = value.container
                    if container == int or (hasattr(container, "__name__") and container.__name__ == "int"):
                        param_type = "integer"
                    elif container == float or (hasattr(container, "__name__") and container.__name__ == "float"):
                        param_type = "number"
                    elif container == bool or (hasattr(container, "__name__") and container.__name__ == "bool"):
                        param_type = "boolean"
                    elif container == list or (hasattr(container, "__name__") and container.__name__ == "list"):
                        param_type = "array"
                
                # Try to get description
                if hasattr(value, "description"):
                    param_desc = str(value.description)
            except Exception:
                # If we can't determine type, default to string
                pass
            
            # Add to properties with only JSON-serializable values
            parameters["properties"][key_str] = {
                "type": param_type,
                "description": param_desc,
            }
            
            # Check if required
            try:
                if hasattr(value, "required") and value.required:
                    parameters["required"].append(key_str)
            except Exception:
                pass
    
    return {
        "name": str(tool.name),
        "description": str(tool.description) if tool.description else f"Execute {tool.name}",
        "parameters": parameters,
    }


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cloudflare Workers AI Conversation platform."""
    api: CloudflareAPI = hass.data[DOMAIN][config_entry.entry_id]["api"]
    
    async_add_entities([CloudflareWorkersConversation(hass, api, config_entry)])


class CloudflareWorkersConversation(ConversationEntity):
    """Cloudflare Workers AI conversation entity with device control."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_name = "Cloudflare Workers AI"

    def __init__(self, hass: HomeAssistant, api: CloudflareAPI, config_entry: ConfigEntry) -> None:
        """Initialize conversation entity."""
        self._hass = hass
        self._api = api
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_conversation"
        self._attr_supported_features = conversation.ConversationEntityFeature(0)
        self._attr_device_info = dr.DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=config_entry.title,
            manufacturer="Cloudflare",
            model="Workers AI",
            entry_type=dr.DeviceEntryType.SERVICE,
        )

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return list of supported languages."""
        return MATCH_ALL

    async def async_added_to_hass(self) -> None:
        """When entity is added to Home Assistant."""
        await super().async_added_to_hass()

        # Check if model supports function calling and LLM API is configured
        model = self._config_entry.options.get(CONF_LLM_MODEL, DEFAULT_LLM_MODEL)
        llm_hass_api = self._config_entry.options.get(CONF_LLM_HASS_API)
        
        if model in FUNCTION_CALLING_MODELS and llm_hass_api and llm_hass_api != "none":
            try:
                # Just check if the API ID is valid, don't call async_get_api here
                # as it requires llm_context which we don't have yet
                if llm_hass_api in ["assist", "conversation"]:
                    self._attr_supported_features = conversation.ConversationEntityFeature.CONTROL
                    _LOGGER.info("Device control enabled for Cloudflare Workers AI")
                else:
                    self._attr_supported_features = conversation.ConversationEntityFeature(0)
            except Exception as err:
                _LOGGER.warning("LLM API %s not available: %s", llm_hass_api, err)
                self._attr_supported_features = conversation.ConversationEntityFeature(0)
        else:
            self._attr_supported_features = conversation.ConversationEntityFeature(0)
            if model not in FUNCTION_CALLING_MODELS:
                _LOGGER.info(
                    "Model %s does not support function calling. Device control disabled.",
                    model
                )

        assist_pipeline.async_migrate_engine(
            self._hass, "conversation", self._config_entry.entry_id, self.entity_id
        )
        conversation.async_set_agent(self._hass, self._config_entry, self)
        self._config_entry.async_on_unload(
            self._config_entry.add_update_listener(self._async_entry_update_listener)
        )

    async def _async_entry_update_listener(
        self, hass: HomeAssistant, entry: ConfigEntry
    ) -> None:
        """Handle options update."""
        await hass.config_entries.async_reload(entry.entry_id)

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from Home Assistant."""
        conversation.async_unset_agent(self._hass, self._config_entry)
        await super().async_will_remove_from_hass()

    async def async_process(
        self, user_input: ConversationInput
    ) -> ConversationResult:
        """Process a user input with device control support."""
        options = self._config_entry.options
        model = options.get(CONF_LLM_MODEL, DEFAULT_LLM_MODEL)
        llm_hass_api = options.get(CONF_LLM_HASS_API)
        system_prompt = options.get(CONF_PROMPT, DEFAULT_PROMPT)

        if model not in LLM_MODELS:
            _LOGGER.error("Invalid LLM model: %s", model)
            return ConversationResult(
                response=intent.IntentResponse(language=user_input.language),
                conversation_id=user_input.conversation_id or ulid.ulid(),
            )

        conversation_id = user_input.conversation_id or ulid.ulid()
        
        # Get LLM API and tools if device control is enabled
        api_instance = None
        tools = []
        if (
            model in FUNCTION_CALLING_MODELS
            and llm_hass_api
            and llm_hass_api != "none"
        ):
            try:
                # Create LLM context for the API
                llm_context = llm.LLMContext(
                    platform="cloudflare_workers_ai",
                    context=user_input.context,
                    language=user_input.language,
                    assistant=conversation.DOMAIN,
                    device_id=user_input.device_id,
                )
                
                # Get API instance which contains tools
                api_instance = await llm.async_get_api(self._hass, llm_hass_api, llm_context)
                
                # APIInstance has a tools attribute directly
                if api_instance.tools:
                    tools = [_format_tool(tool) for tool in api_instance.tools]
                    _LOGGER.info("Prepared %d tools for device control", len(tools))
                    _LOGGER.debug("Tools: %s", [t["name"] for t in tools])
                    # Debug: Log the first tool's full schema
                    if tools:
                        _LOGGER.debug("Sample tool schema (HassTurnOff): %s", 
                                     next((t for t in tools if t["name"] == "HassTurnOff"), None))
                else:
                    _LOGGER.warning(
                        "LLM HASS API configured but no tools available. "
                        "Go to Settings > Voice Assistants > Expose to expose entities."
                    )
            except Exception as err:
                _LOGGER.warning("Failed to get LLM API %s: %s", llm_hass_api, err)
                api_instance = None
                tools = []

        # Build messages with enhanced system prompt for tool usage
        enhanced_prompt = system_prompt
        if tools:
            tool_names = [t["name"] for t in tools]
            enhanced_prompt += f"\n\nIMPORTANT: You have access to these exact tools: {', '.join(tool_names)}. You MUST use these exact tool names - do not invent new tool names.\n\nCRITICAL TOOL PARAMETERS:\n- For HassTurnOn/HassTurnOff/HassLightSet: Use 'name' parameter with the EXACT device name as the user says it\n- When user says 'table', use {{'name': 'table'}}, NOT 'table light' or 'table lamp'\n- When user says 'kitchen light', use {{'name': 'kitchen light'}}\n- Use the EXACT words the user uses for the device name - do not add or change words\n- When user says 'lights', add 'domain' parameter: {{'area': 'kitchen', 'domain': 'light'}} to target only lights\n- When user says 'all lights in [area]', use: {{'area': '[area]', 'domain': 'light'}}\n- You can also use 'floor' to target all devices on a floor (e.g., {{'floor': 'upstairs', 'domain': 'light'}})\n- NEVER use 'entity_id' parameter - it's not supported\n- For HassLightSet color changes, use 'name' parameter plus 'color' parameter (e.g., {{'name': 'kitchen', 'color': 'red'}})\n- For color names: use simple color names like 'red', 'blue', 'green', 'yellow', 'purple', 'orange', 'white'\n- For 'color of the sky', use 'blue' or 'sky blue'\n- Available domains: 'light', 'switch', 'fan', 'cover', 'lock', 'climate', 'media_player'"
        
        messages = [
            {"role": "system", "content": enhanced_prompt},
            {"role": "user", "content": user_input.text},
        ]

        try:
            # Iterate to handle tool calls
            for iteration in range(MAX_TOOL_ITERATIONS):
                _LOGGER.debug("Conversation iteration %d", iteration + 1)
                
                # Log the full request (with messages)
                _LOGGER.debug("LLM Request - Model: %s, Messages count: %d, Tools count: %d", 
                             model, len(messages), len(tools) if tools else 0)
                _LOGGER.debug("LLM Request - Full messages: %s", messages)
                
                # Call Cloudflare API
                response = await self._api.conversation(
                    model=model,
                    messages=messages,
                    max_tokens=512,
                    tools=tools if tools else None,
                )
                
                # Log the full response
                _LOGGER.debug("LLM Response - Full response: %s", response)

                _LOGGER.debug("API response: %s", response)

                # Check for tool calls
                tool_calls = response.get("tool_calls", [])
                _LOGGER.info("Tool calls found: %d", len(tool_calls))
                if tool_calls:
                    _LOGGER.debug("Tool calls details: %s", tool_calls)
                
                if not tool_calls:
                    # No tool calls, extract final response
                    response_text = self._extract_response_text(response)
                    
                    intent_response = intent.IntentResponse(language=user_input.language)
                    intent_response.async_set_speech(response_text)

                    return ConversationResult(
                        response=intent_response,
                        conversation_id=conversation_id,
                    )

                # Execute tool calls
                _LOGGER.info("Checking api_instance: %s", "Available" if api_instance else "None")
                if not api_instance:
                    _LOGGER.error("Tool calls requested but API instance not available - cannot execute tools")
                    # Return error response instead of breaking
                    intent_response = intent.IntentResponse(language=user_input.language)
                    intent_response.async_set_speech(
                        "I detected your request but cannot execute it. Please check the configuration."
                    )
                    return ConversationResult(
                        response=intent_response,
                        conversation_id=conversation_id,
                    )

                _LOGGER.info("Starting tool execution for %d tool calls", len(tool_calls))

                # Add assistant message with tool calls
                # Cloudflare API requires content to be a string, not null/None
                assistant_content = response.get("response") or ""
                messages.append({
                    "role": "assistant",
                    "content": assistant_content,
                })

                _LOGGER.info("About to execute tool calls loop")
                # Execute each tool call
                for tool_call in tool_calls:
                    _LOGGER.info("In tool call loop, processing tool call")
                    tool_name = tool_call.get("name")
                    tool_args = tool_call.get("arguments", {})
                    
                    _LOGGER.info("Executing tool: %s with args: %s", tool_name, tool_args)
                    
                    try:
                        # Execute through API instance
                        tool_input = llm.ToolInput(
                            tool_name=tool_name,
                            tool_args=tool_args,
                        )
                        # Use async_call_tool method on api_instance
                        tool_result = await api_instance.async_call_tool(tool_input)
                        
                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "content": json.dumps(tool_result),
                        })
                        
                        _LOGGER.debug("Tool result: %s", tool_result)
                    except Exception as err:
                        _LOGGER.error("Error executing tool %s: %s", tool_name, err)
                        messages.append({
                            "role": "tool",
                            "content": json.dumps({"error": str(err)}),
                        })

            # Max iterations reached
            _LOGGER.warning("Max tool iterations reached")
            intent_response = intent.IntentResponse(language=user_input.language)
            intent_response.async_set_speech(
                "I tried to help but encountered too many steps. Please try again."
            )
            return ConversationResult(
                response=intent_response,
                conversation_id=conversation_id,
            )

        except CloudflareAPIError as err:
            _LOGGER.error("Error processing conversation: %s", err)
            intent_response = intent.IntentResponse(language=user_input.language)
            intent_response.async_set_speech(
                "Sorry, I encountered an error processing your request."
            )
            return ConversationResult(
                response=intent_response,
                conversation_id=conversation_id,
            )
        except Exception as err:
            _LOGGER.exception("Unexpected error in conversation: %s", err)
            intent_response = intent.IntentResponse(language=user_input.language)
            intent_response.async_set_speech(
                "Sorry, an unexpected error occurred."
            )
            return ConversationResult(
                response=intent_response,
                conversation_id=conversation_id,
            )

    def _extract_response_text(self, response: dict[str, Any]) -> str:
        """Extract response text from various API response formats."""
        # Try different response formats
        if isinstance(response, str):
            return response
        
        if "response" in response:
            return str(response["response"])
        
        if "choices" in response and isinstance(response["choices"], list):
            if len(response["choices"]) > 0:
                choice = response["choices"][0]
                if isinstance(choice, dict) and "message" in choice:
                    return str(choice["message"].get("content", ""))
        
        if "content" in response:
            return str(response["content"])
        
        # Fallback
        return "I processed your request."
