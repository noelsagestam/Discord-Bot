#!/bin/bash
apt-get update && apt-get install -y ffmpeg
python Bot.py
```

**Uppdatera sedan Procfile till:**
```
worker: bash start.sh
