import tkinter as tk
from tkinter import messagebox as mb, StringVar, OptionMenu
from spellchecker import SpellChecker  # Using the pyspellchecker library

class SpellCheckerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("800x600")  # Increased height for a larger text area
        self.root.title("Spell Checker")

        # Configure styles for dark mode
        self.bg_color = "#2E2E2E"  # Dark background color
        self.fg_color = "#FFFFFF"  # Light text color
        self.font = ("Helvetica", 14)
        self.highlight_color = "#FF69B4"  # Highlight color

        # Set the background color for the main window
        self.root.configure(bg=self.bg_color)

        # Textbox for user input
        self.textbox = tk.Text(self.root, height=20, font=self.font, wrap=tk.WORD, bg="#3C3C3C", fg=self.fg_color)
        self.textbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Frame for buttons
        self.button_frame = tk.Frame(self.root, bg=self.bg_color)
        self.button_frame.pack(pady=10)

        # Check spelling button
        self.check_button = tk.Button(self.button_frame, text="Check Spelling", font=self.font, command=self.check_spelling, bg="#4CAF50", fg=self.fg_color)
        self.check_button.pack(side=tk.LEFT, padx=5)

        # Clear text button
        self.clear_button = tk.Button(self.button_frame, text="Clear Text", font=self.font, command=self.clear_text, bg="#f44336", fg=self.fg_color)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Skip button (always available)
        self.skip_button = tk.Button(self.button_frame, text="Skip", font=self.font, command=self.skip_word, bg="#9E9E9E", fg=self.fg_color)
        self.skip_button.pack(side=tk.LEFT, padx=5)

        self.spell_checker = SpellChecker()  # Initialize the spell checker
        self.suggestions_var = StringVar()  # For dropdown menu
        self.dropdown = None  # Dropdown for suggestions
        self.current_word_index = 0  # To track the current word being processed
        self.original_string = ""  # To keep track of the original text
        self.incorrect_words = []  # To keep track of incorrect words
        self.suggestions = {}  # To keep track of suggestions
        self.root.mainloop()

    def get_text(self):
        self.original_string = self.textbox.get('1.0', tk.END).strip()
        return self.original_string

    def check_spelling(self):
        self.original_string = self.get_text()
        self.typed_words = self.original_string.split()
        self.incorrect_words = [word for word in self.typed_words if word not in self.spell_checker]

        for word in self.incorrect_words:
            candidates = self.spell_checker.candidates(word)
            if candidates:
                # Filter candidates based on length
                candidates = [w for w in candidates if abs(len(w) - len(word)) <= 2]
                if candidates:
                    self.suggestions[word] = candidates  # Store filtered candidates
                else:
                    self.suggestions[word] = []  # No valid suggestions
            else:
                self.suggestions[word] = []  # No suggestions available

        self.current_word_index = 0
        self.highlight_word()
        self.process_next_word()

    def highlight_word(self):
        self.textbox.tag_remove("highlight", "1.0", tk.END)  # Remove previous highlights
        if self.current_word_index < len(self.incorrect_words):
            word = self.incorrect_words[self.current_word_index]
            start_idx = self.original_string.find(word)
            end_idx = start_idx + len(word)

            # Highlight the current misspelled word
            self.textbox.tag_add("highlight", f"1.0 + {start_idx} chars", f"1.0 + {end_idx} chars")
            self.textbox.tag_config("highlight", background=self.highlight_color)

    def process_next_word(self):
        if self.current_word_index < len(self.incorrect_words):
            word = self.incorrect_words[self.current_word_index]
            suggestions = self.suggestions.get(word)
            if suggestions:
                self.suggestions_var.set(suggestions[0])  # Set default to the first suggestion

                # Create dropdown for suggestions
                if self.dropdown:
                    self.dropdown.destroy()  # Remove old dropdown if it exists

                self.dropdown = OptionMenu(self.root, self.suggestions_var, *suggestions)
                self.dropdown.pack(pady=5)

                confirm_button = tk.Button(self.root, text="Replace with Selected", command=lambda: self.replace_word(word), bg="#FF9800", fg=self.fg_color)
                confirm_button.pack(pady=5)

                # The skip button is always available
            else:
                # If no suggestions are available, show a message
                mb.showinfo("No Suggestions", f"No suggestions available for the word: '{word}'.")
                self.skip_button.config(command=self.skip_word)  # Ensure skip button works

        else:
            mb.showinfo("Completed", "All words checked.")

    def get_case_preserved_word(self, original, suggestion):
        # Preserve the case of the original word
        if original.islower():
            return suggestion.lower()
        elif original.isupper():
            return suggestion.upper()
        elif original.istitle():
            return suggestion.capitalize()
        return suggestion  # Return suggestion as is if none of the cases match

    def replace_word(self, word):
        selected_word = self.suggestions_var.get()
        case_preserved_word = self.get_case_preserved_word(word, selected_word)

        self.original_string = self.original_string.replace(word, case_preserved_word)

        self.textbox.delete('1.0', tk.END)
        self.textbox.insert(tk.END, self.original_string)

        # Remove dropdown and buttons after replacing
        self.dropdown.destroy()
        self.remove_buttons()
        self.current_word_index += 1
        self.highlight_word()  # Highlight the next word
        self.process_next_word()

    def skip_word(self):
        if self.dropdown:
            self.dropdown.destroy()  # Remove the dropdown if it exists
        self.remove_buttons()
        self.current_word_index += 1
        self.highlight_word()  # Highlight the next word
        self.process_next_word()

    def remove_buttons(self):
        for widget in self.root.pack_slaves():
            if isinstance(widget, tk.Button) and (widget['text'] == "Replace with Selected"):
                widget.destroy()

    def clear_text(self):
        self.textbox.delete('1.0', tk.END)  # Clear the text box

SpellCheckerApp()
