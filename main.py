import time
import os
import threading
from . import config
from .audio_input import AudioInput
from .stt_module import STTModule
from .llm_module import get_llm_response
from .tts_module import TTSModule
from .audio_output import AudioOutput
from .video_input import VideoInput
from .vision_module import VisionModule

# Global state
current_language = config.DEFAULT_LANGUAGE
stop_interaction_flag = threading.Event()

# --- Initialization of Modules ---
try:
    print("Initializing assistant modules...")
    audio_in = AudioInput(sample_rate=config.AUDIO_SAMPLE_RATE, device_index=config.AUDIO_INPUT_DEVICE_INDEX)
    stt = STTModule(language=current_language)
    tts = TTSModule(language=current_language)
    audio_out = AudioOutput()
    video_in = VideoInput(camera_index=0, fps_limit=5) # Lower FPS for vision processing
    vision = VisionModule()
    print("All modules initialized (or attempted). Check for errors above.")
except Exception as e:
    print(f"Critical error during module initialization: {e}")
    print("Please ensure all dependencies are installed and configurations (models, API keys) are correct.")
    exit(1)

def check_model_files():
    """Checks for the existence of STT and TTS model files and provides guidance."""
    models_ok = True
    print("\n--- Checking for STT (Vosk) and TTS (Piper) model files ---")

    # Vosk STT Models
    vosk_models = {
        "en": config.VOSK_MODEL_PATH_EN,
        "zh": config.VOSK_MODEL_PATH_ZH
    }
    for lang, path in vosk_models.items():
        if not os.path.exists(path):
            print(f"STTWarning: Vosk model for {lang} not found at 	hemed_text_is_not_recognized_by_the_user_facing_tool}. Please download from https://alphacephei.com/vosk/models and update config.py.")
            models_ok = False
        else:
            print(f"STT Info: Vosk model for {lang} found at {path}.")

    # Piper TTS Models
    piper_models = {
        "en": (config.PIPER_MODEL_PATH_EN, config.PIPER_CONFIG_PATH_EN),
        "zh": (config.PIPER_MODEL_PATH_ZH, config.PIPER_CONFIG_PATH_ZH)
    }
    for lang, (model_path, config_path) in piper_models.items():
        if not (os.path.exists(model_path) and os.path.exists(config_path)):
            # Piper can auto-download if model name (not path) is given. If path is given, it must exist.
            # This check assumes paths in config are actual paths to downloaded files.
            print(f"TTSWarning: Piper model for {lang} not found (model: {model_path}, config: {config_path}). Please download from https://rhasspy.github.io/piper-samples/ or use model names for auto-download, and update config.py.")
            models_ok = False
        else:
            print(f"TTS Info: Piper model for {lang} found (model: {model_path}, config: {config_path}).")
    
    if not models_ok:
        print("Warning: Some STT/TTS models are missing. Functionality will be limited or fail.")
        print("Please ensure models are downloaded and paths in multimodal_assistant/config.py are correct.")
    else:
        print("All configured STT/TTS model paths seem to exist.")
    print("--- Model check finished ---\n")
    return models_ok

def switch_language(new_lang):
    global current_language, stt, tts
    if new_lang not in config.SUPPORTED_LANGUAGES:
        print(f"Language {new_lang} not supported.")
        return False
    if new_lang == current_language:
        print(f"Language is already {new_lang}.")
        return True
    
    print(f"Switching language to {new_lang}...")
    current_language = new_lang
    try:
        stt.set_language(new_lang)
        tts.set_language(new_lang)
        print(f"Successfully switched language to {new_lang}.")
        speak_response(f"Language switched to {new_lang}." if new_lang == "en" else "语言已切换到中文。")
        return True
    except Exception as e:
        print(f"Error switching language: {e}")
        # Revert to default if switching fails badly
        current_language = config.DEFAULT_LANGUAGE
        stt.set_language(config.DEFAULT_LANGUAGE)
        tts.set_language(config.DEFAULT_LANGUAGE)
        return False

def speak_response(text_to_speak):
    if not text_to_speak:
        return
    print(f"Assistant: {text_to_speak}")
    temp_wav_file = "temp_tts_output.wav"
    if tts.speak(text_to_speak, temp_wav_file):
        audio_out.play_wav_file(temp_wav_file)
        if os.path.exists(temp_wav_file):
            try:
                os.remove(temp_wav_file)
            except OSError as e:
                print(f"Error deleting temp WAV file: {e}")
    else:
        print("TTS synthesis failed.")

def process_command(text_input):
    global current_language
    print(f"User: {text_input}")
    text_input_lower = text_input.lower()

    # Language switching commands
    if any(cmd in text_input_lower for cmd in ["switch to chinese", "切换到中文"]):
        switch_language("zh")
        return
    elif any(cmd in text_input_lower for cmd in ["switch to english", "切换到英文"]):
        switch_language("en")
        return
    
    # Vision related commands
    vision_prompt_addition = ""
    if any(cmd in text_input_lower for cmd in ["what do you see", "describe the scene", "look around", "这是什么", "看见什么了"]):
        print("Vision command detected. Capturing and analyzing frame...")
        if not video_in.running:
            video_in.start_capture()
            time.sleep(1) # Give camera time to start
        
        frame = video_in.get_frame()
        if frame is not None:
            vision_description = vision.analyze_frame_for_prompt(frame)
            print(f"Vision analysis: {vision_description}")
            vision_prompt_addition = f" Current visual context: {vision_description}"
            # Optionally, save or show the annotated frame for debugging
            # annotated_frame, _ = vision.detect_objects(frame)
            # if annotated_frame is not None: cv2.imwrite("last_vision_capture.jpg", annotated_frame)
        else:
            vision_prompt_addition = " Could not get a frame from the camera."
            print("Vision: Could not get frame.")

    # Prepare prompt for LLM
    full_prompt = text_input + vision_prompt_addition
    if current_language == "zh":
        # Simple prompt engineering for Chinese if needed, or rely on Gemini's multilingual capabilities
        # full_prompt = f"用户用中文说：	hemed_text_is_not_recognized_by_the_user_facing_tool} {vision_prompt_addition}"
        pass # Assuming Gemini handles mixed language prompts or language is clear

    print(f"Sending to LLM: {full_prompt}")
    llm_response = get_llm_response(full_prompt) # Image path can be added here if LLM supports direct image input and vision module provides it
    
    speak_response(llm_response)

    # Exit command
    if any(cmd in text_input_lower for cmd in ["exit", "quit", "stop listening", "再见", "退出"]):
        speak_response("Goodbye!" if current_language == "en" else "再见！")
        stop_interaction_flag.set()

def main_interaction_loop():
    """Main loop to handle voice and vision interaction."""
    if not (stt.model and tts.model_path):
        print("STT or TTS models not loaded properly. Interaction loop cannot start.")
        speak_response("Critical error: Speech models not loaded. Please check configuration and restart.")
        return

    audio_in.start_listening()
    if not audio_in.running:
        print("Failed to start audio input. Interaction loop cannot start.")
        speak_response("Critical error: Microphone not working. Please check connection and restart.")
        return

    # Optional: Start video capture if always-on vision is desired, or start on demand.
    # video_in.start_capture() 

    speak_response("Hello! How can I help you today?" if current_language == "en" else "你好！今天我能帮你做些什么？")
    print("Assistant is listening... Say 'exit' or '再见' to stop.")

    active_utterance = ""
    silence_start_time = None
    SILENCE_THRESHOLD_S = 2.0 # Seconds of silence to consider an utterance complete

    try:
        while not stop_interaction_flag.is_set():
            chunk = audio_in.get_audio_chunk(timeout=0.1) # Non-blocking
            if chunk:
                text, is_final = stt.recognize_chunk(chunk)
                if text:
                    active_utterance += text + (" " if is_final else "")
                    print(f"STT Partial/Final: {text} -> Current: 	hemed_text_is_not_recognized_by_the_user_facing_tool}", end=\'\r\', flush=True)
                    silence_start_time = None # Reset silence timer on activity
                
                if is_final and active_utterance.strip():
                    print(f"\nSTT Final segment: {active_utterance.strip()}")
                    # Process immediately after a final segment from Vosk if desired
                    # process_command(active_utterance.strip())
                    # active_utterance = "" 
                    # For now, we wait for silence to confirm end of full command

            else: # No audio chunk, indicates silence
                if active_utterance.strip(): # If there was prior speech
                    if silence_start_time is None:
                        silence_start_time = time.time()
                    elif time.time() - silence_start_time > SILENCE_THRESHOLD_S:
                        final_command = active_utterance.strip()
                        # Additional final recognition from Vosk if any buffered
                        final_buffered = stt.get_final_recognition()
                        if final_buffered:
                            final_command += " " + final_buffered.strip()
                        final_command = final_command.strip()
                        
                        print(f"\nUser (end of utterance): {final_command}")
                        if final_command:
                            process_command(final_command)
                        active_utterance = ""
                        silence_start_time = None
                        if stop_interaction_flag.is_set(): break
                        print("\nAssistant is listening...") # Prompt for next command
            
            time.sleep(0.05) # Small delay to prevent busy loop

    except KeyboardInterrupt:
        print("\nInteraction interrupted by user (Ctrl+C).")
        speak_response("Shutting down." if current_language == "en" else "正在关机。")
    finally:
        print("Cleaning up resources...")
        audio_in.stop_listening()
        if video_in.running:
            video_in.stop_capture()
        if hasattr(vision, 'close'): vision.close()
        # audio_out and other modules with __del__ will clean up automatically
        print("Assistant stopped.")

if __name__ == "__main__":
    models_ready = check_model_files()
    if not models_ready:
        print("Please address the model issues above before running the main application.")
        # Optionally, prevent main_interaction_loop if critical models are missing
        # For now, it will try to run and fail gracefully within the loop if models aren't loaded.

    # Check Gemini API Key
    if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        print("Error: Gemini API key not configured in multimodal_assistant/config.py.")
        print("Please obtain an API key and set it in the config file.")
        # exit(1) # Or allow to run with LLM errors handled

    main_interaction_loop()

