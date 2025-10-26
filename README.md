# EV Charge Monitor Bot (Telegram)

A simple Telegram bot designed to monitor the availability of Electric Vehicle (EV) charging stations.

This bot periodically polls specific API endpoints for charging stations and sends a notification to all subscribers when a previously occupied station becomes available.

✨ Features

User Subscriptions: Any user can start the bot to subscribe to (and stop to unsubscribe from) availability notifications.

Smart Notifications: The bot sends an alert only when a station's status changes from "Fully Occupied" (0 available) to "Available" (>0 available), preventing notification spam.

On-Demand Status: Users can request the current status of all monitored stations at any time.

Multi-Station Support: Easily configurable to monitor several charging locations at once.

🤖 How It Works

The bot uses python-telegram-bot's JobQueue to run a background task at a set interval (e.g., every 5 minutes). This task performs the following steps:

It iterates through a list of predefined charging station API endpoints.

It makes an HTTP GET request to each station's URL.

It parses the JSON response to find the number of available charging spots.

It compares this count to the previously stored count for that station.

If the count has changed from 0 to > 0, it sends a notification message to all subscribed users.

A simple subscribers.txt file is used to persist the list of chat_ids.

🛠️ Installation & Configuration

To run this bot yourself, follow these steps:

Clone the repository:

git clone [https://github.com/dgluhotorenko/PublicChargeMonitorBot.git](https://github.com/dgluhotorenko/PublicChargeMonitorBot.git)
cd your-repo-name


Create and activate a virtual environment:

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate


Install the dependencies:

pip install -r requirements.txt


Configure the Bot (Crucial Step):

Open ChargerMonitorBot.py and edit the configuration variables at the top of the file:

BOT_TOKEN: Set this to the token string you received from @BotFather on Telegram.

BOT_TOKEN = "123456:ABC-DEF123456789" # <-- REPLACE WITH YOUR TOKEN


CHARGING_STATIONS: Add your station information here. The dictionary key is a unique ID, and the name is what will be shown to the user.

CHARGING_STATIONS = {
    "station_one_id": {
        "name": "Hotel Station",
        "url": "[https://api.example.com/station/1/status](https://api.example.com/station/1/status)" # <-- REPLACE WITH YOUR URL
    },
    "station_two_id": {
        "name": "City Hall Station",
        "url": "[https://api.example.com/station/2/status](https://api.example.com/station/2/status)" # <-- REPLACE WITH YOUR URL
    }
}


Modify Parsing Logic (Important!): This bot was written to parse a specific JSON structure. You must modify the _parse_station_data function in the script to correctly parse the JSON response from your API endpoints.

🚀 Running the Bot

Once configured, you can run the bot locally:

python ChargerMonitorBot.py


The bot will create a subscribers.txt file in the same directory to store user IDs.

🤖 Bot Commands

/start - Subscribes you to notifications and welcomes you.

/stop - Unsubscribes you from all notifications.

/status - Immediately fetches and sends the current availability of all monitored stations.

🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

📄 License

This project is licensed under the MIT License.
