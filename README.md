# vCenter vMon Service Checker

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![vCenter](https://img.shields.io/badge/vCenter-8.0%20U3-green.svg)
![Release Date](https://img.shields.io/badge/release-January%202025-orange.svg)

A web-based tool for checking and analyzing VMware vCenter service status and dependencies.

## Version Information

- **Current Version**: v1.0.0
- **Supported vCenter Version**: 8.0 U3
- **Release Date**: January 2025

## Features

- Service status matrix view
- Service dependency analysis
- Log file analysis
- Service details view with descriptions and log paths
- Local log file upload and remote download support
- Automatic service dependency highlighting
- Modern and responsive user interface

## Prerequisites

Before using this tool, ensure you have:

1. Access to vCenter with root privileges
2. Python 3.x installed on your system
3. Web browser with JavaScript enabled

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yxyj1919/306-vmw-vcenter-vmon-checker-new.git
cd 306-vmw-vcenter-vmon-checker-new
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Follow the on-screen instructions to:
   - SSH into vCenter
   - Restart services
   - Download and analyze log files

## Directory Structure

```
.
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── matrix.html       # Service matrix view
│   └── upload.html       # File upload interface
├── utils/               # Utility functions
│   ├── config.py        # Configuration settings
│   ├── log_processor.py # Log processing logic
│   └── __init__.py
├── vmon-json-services/  # Service configuration files
│   ├── vcsa8-service.json
│   └── vcsa-8U3-profile-all-default.yaml
└── uploads/            # Directory for uploaded files
```

## Bug Report & Support

If you encounter any issues or have suggestions, please feel free to:
- Email: chang.wang@broadcom.com
- GitHub: [https://github.com/yxyj1919/306-vmw-vcenter-vmon-checker-new](https://github.com/yxyj1919/306-vmw-vcenter-vmon-checker-new)

## License

[License Type] - See LICENSE file for details 