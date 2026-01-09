"""
Inference Service - Interfaces with inference model for natural language processing
"""
import os
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel


class InferenceService:
    """Service responsible for processing natural language queries through inference model"""
    
    def __init__(self):
        """Initialize the inference service"""
        self.name = "inference-service"
        self.initialized = False
        self.model = None
        self.tokenizer = None
        self.device = None
        self.base_model_id = None
        self.adapter_path = None
        
        # Inference parameters (can be overridden via environment variables)
        self.end_json_token = os.getenv("END_JSON_TOKEN", "<END_JSON>")
        self.max_new_tokens = int(os.getenv("MAX_NEW_TOKENS", "512"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.0"))
        self.top_p = float(os.getenv("TOP_P", "1.0"))
    
    def register(self, app):
        """
        Register routes and functionality with the Flask app
        
        Args:
            app: Flask application instance
        """
        # No routes needed - this service provides inference methods
        pass
    
    def initialize(self):
        """
        Initialize the service and load the model
        
        Reads environment variables:
        - HF_BASE_MODEL_ID: HuggingFace model ID for the base model (e.g., "Qwen/Qwen2.5-3B")
        - LORA_ADAPTER_PATH: Path to the LoRA adapter directory
        - HF_TOKEN: Optional HuggingFace token for private/gated models
        - HF_HOME: Optional HuggingFace cache directory
        """
        if self.initialized:
            print(f"[{self.name}] Already initialized")
            return
        
        print(f"[{self.name}] Initializing...")
        
        # Read configuration from environment variables
        self.base_model_id = os.getenv("HF_BASE_MODEL_ID", "").strip()
        self.adapter_path = os.getenv("LORA_ADAPTER_PATH", "").strip()
        hf_token = os.getenv("HF_TOKEN", "").strip() if os.getenv("HF_TOKEN") else None
        
        if not self.base_model_id:
            raise RuntimeError(
                "HF_BASE_MODEL_ID environment variable not set. "
                "Set it to the HuggingFace model ID (e.g., 'Qwen/Qwen2.5-3B')"
            )
        
        if not self.adapter_path:
            raise RuntimeError(
                "LORA_ADAPTER_PATH environment variable not set. "
                "Set it to the path of your LoRA adapter directory"
            )
        
        if not os.path.exists(self.adapter_path):
            raise RuntimeError(
                f"LoRA adapter path does not exist: {self.adapter_path}"
            )
        
        print(f"[{self.name}] Loading base model: {self.base_model_id}")
        print(f"[{self.name}] Loading LoRA adapter from: {self.adapter_path}")
        
        try:
            # Determine device
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
                print(f"[{self.name}] Using GPU: {torch.cuda.get_device_name(0)}")
            else:
                self.device = torch.device("cpu")
                print(f"[{self.name}] Using CPU")
            
            # Load tokenizer
            print(f"[{self.name}] Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.base_model_id,
                token=hf_token,
                trust_remote_code=True
            )
            
            # Load base model
            print(f"[{self.name}] Loading base model (this may take a moment)...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.base_model_id,
                token=hf_token,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
                device_map="auto" if self.device.type == "cuda" else None,
                trust_remote_code=True
            )
            
            # Load LoRA adapter
            print(f"[{self.name}] Loading LoRA adapter...")
            self.model = PeftModel.from_pretrained(self.model, self.adapter_path)
            
            # Set to evaluation mode
            self.model.eval()
            
            # Move to device if not using device_map="auto"
            if self.device.type == "cpu":
                self.model = self.model.to(self.device)
            
            print(f"[{self.name}] Model loaded successfully")
            print(f"[{self.name}] Model parameters: max_new_tokens={self.max_new_tokens}, temperature={self.temperature}, top_p={self.top_p}")
            
            self.initialized = True
            print(f"[{self.name}] Initialized successfully")
            
        except Exception as e:
            print(f"[{self.name}] ERROR: Failed to load model: {e}")
            raise RuntimeError(f"Model loading failed: {e}") from e
    
    def process_query(self, text_input):
        """
        Process natural language text through inference model
        
        Args:
            text_input: String containing natural language query
                Example: "I need an SUV for my family of 5, under $30k, with AWD"
        
        Returns:
            dict: Structured JSON representation with SHORTENED KEYS (mk, md, vt, etc.)
                conforming to Vehicle Selection V1 schema structure but using token-efficient keys.
        
        Raises:
            ValueError: If text input is invalid
            RuntimeError: If inference model fails or is not loaded
        """
        # Validate input
        if not text_input or not isinstance(text_input, str):
            raise ValueError("text_input must be a non-empty string")
        
        text_input = text_input.strip()
        if not text_input:
            raise ValueError("text_input cannot be empty or whitespace only")
        
        # Check if model is loaded
        if not self.initialized or self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call initialize() first.")
        
        try:
            # Prepare input - format should match training format
            # The model expects the prompt in segments format for generation
            prompt = text_input + "\n"
            
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get token IDs for stopping criteria
            end_json_token_id = self.tokenizer.encode(self.end_json_token, add_special_tokens=False)
            if len(end_json_token_id) == 0:
                # Fallback: use eos_token_id if END_JSON token not found in vocab
                end_json_token_id = [self.tokenizer.eos_token_id] if self.tokenizer.eos_token_id else None
            
            # Run inference
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_new_tokens,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    do_sample=self.temperature > 0.0,
                    eos_token_id=end_json_token_id[0] if end_json_token_id else self.tokenizer.eos_token_id,
                    pad_token_id=self.tokenizer.pad_token_id or self.tokenizer.eos_token_id,
                )
            
            # Decode output (skip input tokens)
            generated_text = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=False
            )
            
            # Extract JSON from output
            # Model should output JSON ending with <END_JSON>
            json_text = self._extract_json_from_output(generated_text)
            
            # Parse JSON
            try:
                result = json.loads(json_text)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Failed to parse JSON from model output: {e}. Output: {generated_text[:200]}") from e
            
            return result
            
        except Exception as e:
            if isinstance(e, (ValueError, RuntimeError)):
                raise
            raise RuntimeError(f"Inference failed: {e}") from e
    
    def _extract_json_from_output(self, generated_text):
        """
        Extract JSON text from model output, handling <END_JSON> marker
        
        Args:
            generated_text: Raw text output from model
            
        Returns:
            str: Cleaned JSON text
        """
        # Find the JSON portion - it should start with { and end with <END_JSON>
        start_idx = generated_text.find('{')
        if start_idx == -1:
            raise RuntimeError(f"No JSON object found in model output. Output: {generated_text[:200]}")
        
        # Find the end marker
        end_idx = generated_text.find(self.end_json_token, start_idx)
        if end_idx == -1:
            # If no end marker, try to find the end of the JSON object
            # This is a fallback - ideally the model should output the marker
            end_idx = generated_text.rfind('}')
            if end_idx == -1 or end_idx <= start_idx:
                raise RuntimeError(f"No valid JSON object found in model output. Output: {generated_text[:200]}")
            end_idx += 1
        else:
            # Include up to but not including the end marker
            pass
        
        json_text = generated_text[start_idx:end_idx]
        return json_text.strip()
    
    def _extract_specified_fields(self, data, path="", result=None):
        """
        Recursively extract all fields that are not "unspecified" from the JSON structure.
        
        Args:
            data: The JSON data (dict, list, or primitive value)
            path: Current path in the JSON structure (for nested fields)
            result: Dictionary to accumulate results (created on first call)
        
        Returns:
            dict: Dictionary mapping field paths to their values
                Example: {
                    "mk": ["Toyota"],
                    "vt.inc": ["suv"],
                    "oc.bud.max": 30000,
                    "oc.bud.max_strict": "true"
                }
        """
        if result is None:
            result = {}
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                if isinstance(value, (dict, list)):
                    # Recursively process nested structures
                    self._extract_specified_fields(value, current_path, result)
                else:
                    # Check if value is not "unspecified"
                    if value != "unspecified" and value is not None:
                        result[current_path] = value
        elif isinstance(data, list):
            # For lists, check if any items are not "unspecified"
            non_unspecified = [item for item in data if item != "unspecified" and item is not None]
            if non_unspecified:
                result[path] = non_unspecified
        else:
            # Primitive value - check if not "unspecified"
            if data != "unspecified" and data is not None:
                result[path] = data
        
        return result
    
    def validate_input(self, text_input):
        """
        Validate that the text input is acceptable for processing
        
        Args:
            text_input: String containing natural language query
        
        Returns:
            bool: True if valid, False otherwise
        
        Raises:
            ValueError: If input is invalid with details
        """
        if not text_input or not isinstance(text_input, str):
            raise ValueError("text_input must be a non-empty string")
        
        text_input = text_input.strip()
        if not text_input:
            raise ValueError("text_input cannot be empty or whitespace only")
        
        # Optional: Add length limits
        if len(text_input) > 1000:
            raise ValueError(f"text_input is too long ({len(text_input)} chars). Maximum length is 1000 characters.")
        
        return True
