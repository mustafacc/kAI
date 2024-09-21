import pya
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from typing import List, Dict

# Helper function for OpenAI API call
def generate_ai_response(api_key: str, model_name: str, messages: List[Dict[str, str]]) -> str:
    """
    Generate AI response using OpenAI's API.

    Args:
        api_key (str): The API key for OpenAI.
        model_name (str): The model name to be used.
        messages (List[Dict[str, str]]): The conversation history with user input and AI responses.

    Returns:
        str: The content of the AI response.
    """
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,  # Pass the entire chat history
        max_tokens=150
    )
    return response.choices[0].message.content.strip()


class kai_ui(pya.QDialog):
    """
    A PyQt-based UI for interacting with an AI assistant.

    Attributes:
        api_key (str): The OpenAI API key.
        model_name (str): The model name for AI response generation.
        config_data (dict): Configuration data from the config file.
        chat_history (list): List to store user and AI messages.
        history_dir (Path): Directory for storing chat history files.
    """

    def __init__(self):
        """Initialize the UI and load configuration."""
        super().__init__()
        self.api_key = None
        self.setWindowTitle("kAI Assistant")
        self.resize(800, 400)
        self.setStyleSheet(self.get_stylesheet())
        self.config_data = self.load_config()
        self.chat_history = []
        self.history_dir = Path(__file__).parent.parent / 'history'
        self.init_ui()

    def get_stylesheet(self) -> str:
        """
        Define and return the stylesheet for the UI.

        Returns:
            str: The CSS style rules.
        """
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
                min-width: 200px;
                max-width: 100px;
            }
        """

    def init_ui(self) -> None:
        """Initialize the UI layout with input/output fields and history panel."""
        layout = pya.QHBoxLayout(self)

        # Create input and output areas
        left_layout = self.setup_left_panel()
        right_layout = self.setup_right_panel()

        # Add layouts
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)
        self.setLayout(layout)

    def setup_left_panel(self) -> pya.QVBoxLayout:
        """
        Set up the left panel for user input and AI output.

        Returns:
            pya.QVBoxLayout: The layout with input and output fields.
        """
        left_layout = pya.QVBoxLayout()

        self.user_input = pya.QLineEdit(self)
        self.user_input.setPlaceholderText("Enter your prompt here...")
        left_layout.addWidget(self.user_input)

        self.output_area = pya.QTextEdit(self)
        self.output_area.setReadOnly(True)
        left_layout.addWidget(self.output_area)

        submit_button = pya.QPushButton("Submit", self)
        submit_button.clicked.connect(self.on_submit)
        left_layout.addWidget(submit_button)

        self.config_display = pya.QLabel(self)
        left_layout.addWidget(self.config_display)
        self.update_config_display()

        return left_layout

    def setup_right_panel(self) -> pya.QVBoxLayout:
        """
        Set up the right panel for displaying and loading chat history.

        Returns:
            pya.QVBoxLayout: The layout with history elements.
        """
        right_layout = pya.QVBoxLayout()

        right_layout.addWidget(pya.QLabel("Chat History (Complete)"))
        self.history_list = pya.QListWidget(self)
        self.load_history_files()
        right_layout.addWidget(self.history_list)

        load_button = pya.QPushButton("Load Selected", self)
        load_button.clicked.connect(self.load_selected_history)
        right_layout.addWidget(load_button)

        view_config_button = pya.QPushButton("View Config", self)
        view_config_button.clicked.connect(self.view_config_file)
        right_layout.addWidget(view_config_button)

        return right_layout

    def load_config(self) -> Dict[str, str]:
        """
        Load configuration data from a YAML file.

        Returns:
            dict: Configuration data including API key and model name.
        """
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

    def update_config_display(self) -> None:
        """
        Update the UI to display the current API key and model configuration status.
        """
        api_key_display = "API Key: Configured" if self.api_key != 'null' and self.api_key != 'Not set' else "API Key: Not Configured"
        self.config_display.setText(f"{api_key_display}\nModel Name: {self.config_data.get('model_name', 'Not set')}")
        self.config_display.setStyleSheet("color: black;" if api_key_display != "API Key: Not Configured" else "color: red;")

    def on_submit(self) -> None:
        """
        Handle the submit button click event, sending user input to OpenAI and updating the UI with the response.
        """
        prompt = self.user_input.text
        if prompt and self.api_key != 'Not set':
            self.chat_history.append({"role": "user", "content": prompt})
            user_entry = f"User [{self.get_timestamp()}]: {prompt}"
            self.append_to_output(user_entry)

            response = generate_ai_response(self.api_key, self.model_name, self.chat_history)

            self.chat_history.append({"role": "assistant", "content": response})
            ai_entry = f"AI [{self.get_timestamp()}]: {response}"
            self.append_to_output(ai_entry, is_ai=True)

            self.append_to_output("===")
            self.store_chat_history(user_entry, ai_entry)

    def append_to_output(self, text: str, is_ai: bool = False) -> None:
        """
        Append text to the output display with optional AI-specific formatting.

        Args:
            text (str): The text to append.
            is_ai (bool): Whether the text is from AI, applying color formatting if True.
        """
        cursor = self.output_area.textCursor
        cursor.movePosition(pya.QTextCursor.End)
        if is_ai:
            self.output_area.setTextColor(pya.QColor("green"))
        else:
            self.output_area.setTextColor(pya.QColor("black"))
        cursor.insertText(text + '\n')
        self.output_area.setTextCursor(cursor)

    def get_timestamp(self) -> str:
        """
        Get the current timestamp formatted as a string.

        Returns:
            str: The current timestamp in 'YYYY-MM-DD HH:MM:SS' format.
        """
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def store_chat_history(self, user_entry: str, ai_entry: str) -> None:
        """
        Save the current chat history entries to a file.

        Args:
            user_entry (str): The user's message entry.
            ai_entry (str): The AI's message entry.
        """
        self.history_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = self.history_dir / f'kai_{timestamp}.txt'

        with open(file_path, 'a') as file:
            file.write(user_entry + '\n')
            file.write(ai_entry + '\n')
            file.write("===\n")

    def load_history_files(self) -> None:
        """Load chat history files from the history directory."""
        self.history_list.clear()
        if self.history_dir.exists():
            for file in self.history_dir.glob("*complete*.txt"):
                self.history_list.addItem(file.stem)

    def load_selected_history(self) -> None:
        """Load the selected chat history file and display its contents in a new dialog."""
        selected_item = self.history_list.currentItem
        if selected_item:
            file_name = selected_item.text
            file_path = self.history_dir / f"{file_name}.txt"
            if file_path.exists():
                with open(file_path, 'r') as file:
                    history_content = file.read()

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

    def view_config_file(self) -> None:
        """Display the contents of the config.yml file in a new dialog."""
        config_path = Path(__file__).parent.parent / 'config.yml'
        if config_path.exists():
            with open(config_path, 'r') as file:
                config_content = file.read()

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

    def closeEvent(self, event: pya.QCloseEvent) -> None:
        """Handle the close event by saving the complete chat history."""
        if self.chat_history:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = self.history_dir / f'kai_complete_{timestamp}.txt'

            formatted_history = [
                f"{message['role'].capitalize()} [{self.get_timestamp()}]: {message['content']}"
                for message in self.chat_history
            ]

            with open(file_path, 'w') as file:
                file.write("\n".join(formatted_history))

        event.accept()


# Run the UI if this script is executed directly
if __name__ == "__main__":
    app = pya.Application.instance()
    if not app:
        app = pya.Application.create()
    main_window = kai_ui()
    main_window.exec_()
