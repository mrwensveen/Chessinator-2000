## LAN play: UFW firewall

Run these rules on both machines so either player can host or join:

```bash
sudo ufw allow in on wlan0 from 192.168.10.0/24 to any port 20002 proto udp
sudo ufw allow in on wlan0 from 192.168.10.0/24 to any port 20003 proto tcp
```

Replace `wlan0` with your LAN interface and `192.168.10.0/24` with your LAN
subnet. UDP port `20002` is for discovery; TCP port `20003` is for game
connections. No outgoing rules are needed with UFW's default allow-outgoing
policy.
