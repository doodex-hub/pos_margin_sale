# Instantiated from migration-tool/templates/Dockerfile.template
# Target: odoo:18.0 — needed because pos_margin_threshold and pin_message have
# Fase E/F (Owl/JS) applicable and get Tour tests written for Step 6/9 (Mode D).
FROM odoo:18.0
USER root
RUN apt-get update && apt-get install -y --no-install-recommends wget gnupg ca-certificates \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* \
    && (pip3 install --break-system-packages websocket-client || pip3 install websocket-client)
USER odoo
