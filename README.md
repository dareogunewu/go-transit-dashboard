# GO Transit Live Dashboard

Real-time dashboard for GO Transit trains and buses in the Greater Toronto Area.

## Features

- 🚆 Live train and bus tracking
- 🚉 Union Station departure board
- 📊 Performance metrics and statistics
- 🔄 Auto-refresh every 60 seconds
- 📱 Responsive design

## Data Source

Data powered by [Metrolinx Open API](https://www.metrolinx.com/en/about-us/open-data)

## Deployment

Deploy to Streamlit Cloud:
1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Set main file path: `app.py`
6. Deploy!

## Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

## API Endpoints

- Statistics: `/api/go?type=stats`
- Union Station: `/api/go?type=union`
- Train Lines: `/api/go?type=lines&vehicleType=trains`
- Bus Routes: `/api/go?type=lines&vehicleType=buses`

## License

Data used in this product is provided with the permission of Metrolinx.
