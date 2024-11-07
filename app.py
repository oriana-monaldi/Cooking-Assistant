import speech_recognition as sr
import pyttsx3
import json

def initialize_engine():
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)    
    engine.setProperty('volume', 0.9)  
    voices = engine.getProperty('voices')
    
    english_voice = None
    for voice in voices:
        if "english" in voice.name.lower():
            english_voice = voice.id
            break
    
    if english_voice:
        engine.setProperty('voice', english_voice)
    else:
        print("No specific English voice found. Using default voice.")
    
    return engine

def speak(engine, text):
    """Function to convert text to speech"""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Function to listen and convert speech to text"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        
        try:
            text = recognizer.recognize_google(audio, language="en-US")
            print(f"You said: {text}")
            return text.lower()
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            return ""
        except sr.RequestError:
            print("Sorry, there was an error connecting to the speech recognition service.")
            return ""
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return ""

def load_recipes(filename):
    """Load recipes from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: {filename} is not properly formatted.")
        return []

def get_recipe(query, recipes):
    """Search for a recipe in the recipes list"""
    for recipe in recipes:
        if query in recipe['name'].lower():
            return recipe['name'], recipe['ingredients'], recipe['instructions']
    return None, "Sorry, I couldn't find a recipe matching your request.", ""

def get_user_choice():
    """Get user's choice between specific or suggested recipe"""
    while True:
        speak(engine, "Would you like to cook a specific recipe or would you like a suggested recipe? Please say 'specific' or 'suggested'")
        choice = listen()
        
        if 'specific' in choice:
            return 'specific'
        elif 'suggested' in choice:
            return 'suggested'
        else:
            speak(engine, "I didn't catch that. Please say either 'specific' or 'suggested'")

def repeat_recipe(engine, recipe_name, ingredients, instructions):
    """Handle recipe repetition in a loop until user says no"""
    while True:
        speak(engine, "Would you like me to repeat the recipe? Say 'yes' or 'no'")
        response = listen()
        
        if 'yes' in response:
            speak(engine, f"Here's the recipe for {recipe_name} again.")
            speak(engine, "The ingredients you'll need are:")
            speak(engine, ", ".join(ingredients))
            speak(engine, "And here are the instructions:")
            speak(engine, instructions)
        elif 'no' in response:
            speak(engine, "Have fun cooking! Good luck and goodbye!")
            return True 
        else:
            speak(engine, "I didn't understand. Please say 'yes' to repeat or 'no' to finish.")

def handle_specific_recipe(engine, recipes):
    """Handle the specific recipe flow"""
    speak(engine, "What recipe would you like to know about?")
    while True:
        user_input = listen()
        
        if user_input in ["exit", "quit", "goodbye", "bye"]:
            speak(engine, "Goodbye! Happy cooking!")
            return True
            
        elif user_input:
            recipe_name, ingredients, instructions = get_recipe(user_input, recipes)
            
            if recipe_name:
                speak(engine, f"I found the recipe for {recipe_name}.")
                speak(engine, "You'll need the following ingredients:")
                speak(engine, ", ".join(ingredients))
                speak(engine, "Here are the instructions:")
                speak(engine, instructions)
                
                should_exit = repeat_recipe(engine, recipe_name, ingredients, instructions)
                if should_exit:
                    return True
            else:
                speak(engine, ingredients)  
                speak(engine, "Please try another recipe.")
    return False

def handle_suggested_recipe(engine):
    """Handle the suggested recipe flow"""
    speak(engine, "The suggested recipe feature will be available soon. Please check back later!")
    return False

def main():
    global engine
    engine = initialize_engine()
    
    recipes = load_recipes('recipes.json')
    if not recipes:
        speak(engine, "Error loading recipes. Please check your recipes file.")
        return

    speak(engine, "Hello! I'm your kitchen assistant.")
    
    while True:
        choice = get_user_choice()
        should_exit = False
        
        if choice == 'specific':
            should_exit = handle_specific_recipe(engine, recipes)
        elif choice == 'suggested':
            should_exit = handle_suggested_recipe(engine)
            
        if should_exit:
            break

if __name__ == "__main__":
    main()