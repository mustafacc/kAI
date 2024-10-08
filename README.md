![kAI Logo](klayout/kAI.png)

# kAI 0.1.0
kAI is a KLayout package that adds an interface to an AI assistant in the UI.

## Requirements
- [KLayout](https://www.klayout.de/)

## Documentation 
[kAI Documentation](https://mustafacc.github.io/kAI/)

## Installation
(coming soon) open KLayout. Open the package manger under `Tools -> Manage Packages`. In the package manager, search for `kAI`,
double-click and ensure a green checkmark appears on the kAI package icon. click `Apply` on the bottom left. When asked to run the initial script click
`Yes`. 


(for developers)
1. Fork the repository from [GitHub](https://github.com/mustafacc/kAI).
2. Clone the repository.
3. Add the repository to a new $KLAYOUT_HOME/salt/kAI directory. Using symbolic links is recommended.

Once the package is added to KLayout, edit the config.yml to include the API key to your preferred public or personal model.

![kAI Logo](docs/_static/kAI_ui.png)

Credits: Thanks to [klive](https://github.com/gdsfactory/klive) for codebase and package structure!

