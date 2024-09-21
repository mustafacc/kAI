import pya
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# Helper function for OpenAI API call
def generate_ai_response(api_key, model_name, messages):
    client = OpenAI(api_key=api_key)      
    # OpenAI Chat completion call with full chat history
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,  # Pass the entire chat history
        max_tokens=150
    )
    return response.choices[0].message.content.strip()


class kai_ui(pya.QDialog):
    def __init__(self):
        super().__init__()
        self.api_key = None
        self.setWindowTitle("kAI Assistant")
        self.resize(800, 400)
        self.setStyleSheet(self.get_stylesheet())  # Apply stylesheet
        self.config_data = self.load_config()
        self.chat_history = []
        self.history_dir = Path(__file__).parent.parent / 'history'
        self.init_ui()

    # Define get_stylesheet method
    def get_stylesheet(self):
        """Apply a modern stylesheet with clean fonts and spacing."""
        return """
            QDialog {
                background-color: #f0f0f0;
            }
            QLineEdit, QTextEdit {
                font-size: 14px;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #f15025;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QLabel {
                font-size: 14px;
                color: #333333;
            }
            QListWidget {
                min-width: 200px;  /* Adjust panel size */
                max-width: 100px;
            }
        """

    # Modular UI initialization
    def init_ui(self):
        layout = pya.QHBoxLayout(self)

        # Create input and output areas
        left_layout = self.setup_left_panel()
        right_layout = self.setup_right_panel()

        # Add layouts
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)

        self.setLayout(layout)

    # UI Setup: Left panel for input/output
    def setup_left_panel(self):
        left_layout = pya.QVBoxLayout()

        # Input field
        self.user_input = pya.QLineEdit(self)
        self.user_input.setPlaceholderText("Enter your prompt here...")
        left_layout.addWidget(self.user_input)

        # Output field
        self.output_area = pya.QTextEdit(self)
        self.output_area.setReadOnly(True)
        left_layout.addWidget(self.output_area)

        # Submit button
        submit_button = pya.QPushButton("Submit", self)
        submit_button.clicked.connect(self.on_submit)
        left_layout.addWidget(submit_button)

        # Display config
        self.config_display = pya.QLabel(self)
        left_layout.addWidget(self.config_display)
        self.update_config_display()

        return left_layout

    # UI Setup: Right panel for history
    def setup_right_panel(self):
        right_layout = pya.QVBoxLayout()

        # Chat history list (only loads "complete" txt files)
        right_layout.addWidget(pya.QLabel("Chat History (Complete)"))
        self.history_list = pya.QListWidget(self)
        self.load_history_files()
        right_layout.addWidget(self.history_list)

        # Load button
        load_button = pya.QPushButton("Load Selected", self)
        load_button.clicked.connect(self.load_selected_history)
        right_layout.addWidget(load_button)

        # View config button
        view_config_button = pya.QPushButton("View Config", self)
        view_config_button.clicked.connect(self.view_config_file)
        right_layout.addWidget(view_config_button)

        return right_layout

    # Function to load config.yml
    def load_config(self):
        config_path = Path(__file__).parent.parent / 'config.yml'
        config_data = {}
        if config_path.exists():
            with open(config_path, 'r') as file:
                for line in file:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        config_data[key.strip()] = value.strip()
        self.api_key = config_data.get('api_key', 'Not set')
        self.model_name = config_data.get('model_name', 'Not set')
        return config_data

    # Update config display
    def update_config_display(self):
        api_key_display = "API Key: Configured" if self.api_key != 'null' and self.api_key != 'Not set' else "API Key: Not Configured"
        self.config_display.setText(f"{api_key_display}\nModel Name: {self.config_data.get('model_name', 'Not set')}")
        if self.api_key == 'null' or self.api_key == 'Not set':
            self.config_display.setStyleSheet("color: red;")
        else:
            self.config_display.setStyleSheet("color: black;")

    # Event handler for submit button
    def on_submit(self):
        prompt = self.user_input.text
        if prompt and self.api_key != 'Not set':
            # Add user message to chat history
            self.chat_history.append({"role": "user", "content": prompt})
            user_entry = f"User [{self.get_timestamp()}]: {prompt}"
            self.append_to_output(user_entry)

            # Call OpenAI with the entire chat history
            response = generate_ai_response(self.api_key, self.model_name, self.chat_history)

            # Add AI response to chat history
            self.chat_history.append({"role": "assistant", "content": response})
            ai_entry = f"AI [{self.get_timestamp()}]: {response}"
            self.append_to_output(ai_entry, is_ai=True)

            # Add separator for visual clarity
            self.append_to_output("===")

            # Store individual chat entry immediately
            self.store_chat_history(user_entry, ai_entry)


    # Append output to display
    def append_to_output(self, text, is_ai=False):
        cursor = self.output_area.textCursor
        cursor.movePosition(pya.QTextCursor.End)
        if is_ai:
            self.output_area.setTextColor(pya.QColor("green"))
        else:
            self.output_area.setTextColor(pya.QColor("black"))
        cursor.insertText(text + '\n')
        self.output_area.setTextCursor(cursor)

    # Helper to generate a timestamp
    def get_timestamp(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Store chat history after each user entry and AI response
    def store_chat_history(self, user_entry, ai_entry):
        self.history_dir.mkdir(exist_ok=True)  # Ensure history directory exists
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = self.history_dir / f'kai_{timestamp}.txt'

        # Save both user entry and AI response immediately
        with open(file_path, 'a') as file:
            file.write(user_entry + '\n')
            file.write(ai_entry + '\n')
            file.write("===\n")

    # Load history files into the list (only "complete" txt files)
    def load_history_files(self):
        self.history_list.clear()
        if self.history_dir.exists():
            for file in self.history_dir.glob("*complete*.txt"):
                self.history_list.addItem(str(file.stem))  # Show file name without extension

    # Load selected history file
    def load_selected_history(self):
        selected_item = self.history_list.currentItem()
        if selected_item:
            file_name = selected_item.text()
            file_path = self.history_dir / f"{file_name}.txt"
            if file_path.exists():
                with open(file_path, 'r') as file:
                    history_content = file.read()

                # Open a new dialog to display the chat history
                history_dialog = pya.QDialog(self)
                history_dialog.setWindowTitle(f"Chat History - {file_name}")
                history_dialog.resize(600, 400)

                history_text = pya.QTextEdit(history_dialog)
                history_text.setReadOnly(True)
                history_text.setText(history_content)

                dialog_layout = pya.QVBoxLayout(history_dialog)
                dialog_layout.addWidget(history_text)
                history_dialog.setLayout(dialog_layout)

                history_dialog.exec_()

    # Display the config.yml file content in a new window
    def view_config_file(self):
        config_path = Path(__file__).parent.parent / 'config.yml'
        if config_path.exists():
            with open(config_path, 'r') as file:
                config_content = file.read()

            # Open a new dialog to display the config.yml contents
            config_dialog = pya.QDialog(self)
            config_dialog.setWindowTitle(f"Config - {str(config_path)}")
            config_dialog.resize(600, 400)

            config_text = pya.QTextEdit(config_dialog)
            config_text.setReadOnly(True)
            config_text.setText(config_content)

            dialog_layout = pya.QVBoxLayout(config_dialog)
            dialog_layout.addWidget(config_text)
            config_dialog.setLayout(dialog_layout)

            config_dialog.exec_()

    # Store the complete chat history upon closing
    def closeEvent(self, event):
        if self.chat_history:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = self.history_dir / f'kai_complete_{timestamp}.txt'
    
            # Convert chat history into a readable format
            formatted_history = []
            for message in self.chat_history:
                role = message["role"]
                content = message["content"]
                formatted_message = f"{role.capitalize()} [{self.get_timestamp()}]: {content}"
                formatted_history.append(formatted_message)
    
            # Save the entire chat history in a human-readable format
            with open(file_path, 'w') as file:
                file.write("\n".join(formatted_history))  # Save the entire session
    
            event.accept()  # Ensure the app closes after saving the history


# Run the UI if this script is executed directly
if __name__ == "__main__":
    app = pya.Application.instance()
    if not app:
        app = pya.Application.create()
    main_window = kai_ui()
    main_window.exec_()
