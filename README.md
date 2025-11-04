# Arby - Betting Arbitrage App

## Overview

This application is designed to provide sports betting arbitrage opportunities. It fetches odds from various bookmakers and calculates potential arbitrage situations.

## Disclaimer

This tool is for informational purposes only and should not be considered as financial advice. Betting involves financial risks; please use this application responsibly.

## Features

-   Fetches and displays live sports betting odds.
-   Fetches and displays live horse racing odds from multiple regions.
-   Identifies and calculates arbitrage opportunities for both sports and horse racing.
-   Filters sports and racing regions based on user preferences.

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
API=your_odds_api_key
RACING_API_USER=your_racing_api_username
RACING_API_PASSWORD=your_racing_api_password
PORT=port (5000 reserved for hosting on the cloud)
BASE_URL=http://localhost
```

### API Keys

-   **The Odds API**: Get your API key from [https://the-odds-api.com/](https://the-odds-api.com/) for sports betting odds.
-   **The Racing API**: Get your credentials from [https://www.theracingapi.com/](https://www.theracingapi.com/) for horse racing odds. You'll receive a username and password via email after subscription.

## Contributing

Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.
