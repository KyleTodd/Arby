# Arby - Betting Arbitrage App

## Overview

This application is designed to provide sports betting arbitrage opportunities. It fetches odds from various bookmakers and calculates potential arbitrage situations.

## Disclaimer

This tool is for informational purposes only and should not be considered as financial advice. Betting involves financial risks; please use this application responsibly.

## Features

-   Fetches and displays live sports betting odds.
-   Identifies and calculates arbitrage opportunities.
-   Filters sports based on user preferences.

## Installation

To set up this project locally, follow these steps:

1. Clone the repository:

```
git clone https://github.com/KyleTodd/Arby.git
```

2. Navigate to the project directory:

```
cd Arby
```

3. Create a virtual environment:

```
python -m venv venv
```

4. Activate the virtual environment:

```
- Windows: `venv\Scripts\activate`
- Unix/Mac: `source venv/bin/activate`
```

5. Install required packages:

```
pip install -r requirements.txt
```

## Usage

To run the application:

```
python app.py
```

Access the application at `http://localhost:[PORT]/`.

## Configuration

Set your API keys and other configurations in a `.env` file:

```
API_KEY=your_api_key
PORT=port (5000 reserved for hosting on the cloud)
```

## Contributing

Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.
